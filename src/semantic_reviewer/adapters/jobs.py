"""Persist short job transitions and append-only events in the shared SQLite database."""

import json
import logging
import re
import sqlite3
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.results import JsonResults
from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.jobs import Job


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _event(db, job_id: str, kind: str, details: dict) -> None:
    db.execute(
        "INSERT INTO event(kind, subject_id, occurred_at, details_json) VALUES (?, ?, ?, ?)",
        (kind, job_id, _now(), json.dumps(details)),
    )


class SQLiteJobs:
    """Keep ownership, terminal metadata and events consistent across worker restarts."""

    def __init__(self, database: Path) -> None:
        """Migrate operational state before accepting queue operations."""
        self.state = SQLiteState(database)
        self.logs = JsonResults(database.parent / "logs", database)

    def enqueue(self, job: Job) -> Job:
        """Insert a queued job and event together; repeated IDs are rejected."""
        if job.status != "queued" or any((job.worker_id, job.completed_at, job.decision_id)):
            raise ValueError("Only a new queued job can be submitted.")
        values = asdict(job)
        with self.state.connect() as db:
            db.execute(
                "INSERT INTO job VALUES (" + ",".join("?" for _ in values) + ")",
                tuple(values.values()),
            )
            _event(db, job.id, "job_queued", {"schema_version": 1})
        self._export_log(job.id)
        return job

    def get(self, job_id: str) -> Job | None:
        """Return current metadata without reading result bodies."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM job WHERE id=?", (job_id,)).fetchone()
            return Job(**dict(row)) if row else None

    def recent(self) -> tuple[Job, ...]:
        """Read a bounded queue/history summary in reverse submission order."""
        with self.state.connect() as db:
            return tuple(
                Job(**dict(row))
                for row in db.execute(
                    "SELECT * FROM job ORDER BY queued_at DESC, id DESC LIMIT 100"
                )
            )

    def claim(self, worker_id: str) -> Job | None:
        """Claim the oldest waiting item atomically; permit only one running heavy job."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM job WHERE status='running'").fetchone():
                return None
            row = db.execute(
                "SELECT * FROM job WHERE status='queued' ORDER BY queued_at, id LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            now = _now()
            db.execute(
                "UPDATE job SET status='running', worker_id=?, started_at=?, heartbeat_at=? "
                "WHERE id=?",
                (worker_id, now, now, row["id"]),
            )
            _event(db, row["id"], "job_started", {"worker_id": worker_id})
            job = Job(**dict(db.execute("SELECT * FROM job WHERE id=?", (row["id"],)).fetchone()))
        self._export_log(job.id)
        return job

    @staticmethod
    def _owned(db, job: Job) -> None:
        if not db.execute(
            "SELECT 1 FROM job WHERE id=? AND status='running' AND worker_id=?",
            (job.id, job.worker_id),
        ).fetchone():
            raise ValueError("Worker no longer owns this running job.")

    def heartbeat(self, job: Job) -> None:
        """Record liveness without adding noisy heartbeat events."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, job)
            db.execute("UPDATE job SET heartbeat_at=? WHERE id=?", (_now(), job.id))

    def bind_route(self, job: Job, decision_id: str) -> None:
        """Bind exactly one durable decision before model work begins."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, job)
            if db.execute("SELECT decision_id FROM job WHERE id=?", (job.id,)).fetchone()[0]:
                raise ValueError("Job already has a routing decision.")
            db.execute("UPDATE job SET decision_id=? WHERE id=?", (decision_id, job.id))
            _event(db, job.id, "job_routed", {"decision_id": decision_id})
        self._export_log(job.id)

    def finish(self, job: Job, digest: str | None, error: str | None) -> None:
        """Commit a terminal reference/event after validating the completion contract.

        None means success and requires a SHA-256 reference. Failure requires a
        non-blank explanation and may retain a result reference. Invalid arguments
        or lost ownership raise ValueError without changing the job or its events.
        """
        if error is not None and (not isinstance(error, str) or not error.strip()):
            raise ValueError("Failed jobs require a non-blank explanation.")
        if digest is not None and not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Completion requires a SHA-256 artefact identity.")
        if error is None and digest is None:
            raise ValueError("Successful jobs require a complete artefact.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, job)
            status = "succeeded" if error is None else "failed"
            db.execute(
                "UPDATE job SET status=?, completed_at=?, artefact_sha256=?, error=? WHERE id=?",
                (status, _now(), digest, error, job.id),
            )
            _event(db, job.id, "job_" + status, {"artefact_sha256": digest, "error": error})
        self._export_log(job.id)

    def recover_interrupted(self) -> int:
        """Fail prior running work only under the caller's exclusive OS process lock."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT id FROM job WHERE status='running'").fetchall()
            error = (
                "Worker stopped before recording completion; inspect evidence before resubmitting."
            )
            for row in rows:
                db.execute(
                    "UPDATE job SET status='failed', completed_at=?, error=? WHERE id=?",
                    (_now(), error, row[0]),
                )
                _event(db, row[0], "job_interrupted", {"error": error})
        for row in rows:
            self._export_log(row[0])
        return len(rows)

    def log(self, job_id: str) -> dict:
        """Publish a structured snapshot of committed job events; return its metadata."""
        with self.state.connect() as db:
            if not db.execute("SELECT 1 FROM job WHERE id=?", (job_id,)).fetchone():
                raise LookupError("Job does not exist.")
            rows = db.execute(
                "SELECT * FROM event WHERE subject_id=? AND kind LIKE 'job_%' ORDER BY sequence",
                (job_id,),
            ).fetchall()
        events = [
            {
                "event_id": row["sequence"],
                "timestamp": row["occurred_at"],
                "job_id": job_id,
                "level": "ERROR" if row["kind"] in ("job_failed", "job_interrupted") else "INFO",
                "event": row["kind"],
                "data": json.loads(row["details_json"]),
            }
            for row in rows
        ]
        digest = self.logs.publish({"schema_version": 1, "job_id": job_id, "log_events": events})
        with self.state.connect() as db:
            db.execute(
                "INSERT INTO job_log VALUES (?, ?, ?) ON CONFLICT(job_id) DO UPDATE SET "
                "artefact_sha256=excluded.artefact_sha256, last_event_id=excluded.last_event_id "
                "WHERE excluded.last_event_id>job_log.last_event_id",
                (job_id, digest, rows[-1]["sequence"]),
            )
            return dict(db.execute("SELECT * FROM artefact WHERE sha256=?", (digest,)).fetchone())

    def _export_log(self, job_id: str) -> None:
        try:
            self.log(job_id)
        except (OSError, sqlite3.Error, ValueError):
            # The authoritative transition is already committed. Logs can be
            # regenerated; a diagnostic disk failure must not imply job rollback.
            logging.getLogger(__name__).warning("Job log export unavailable for %s", job_id)
