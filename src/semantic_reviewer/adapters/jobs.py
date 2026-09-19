"""Persist short job transitions and append-only events in the shared SQLite database."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

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
            return Job(**dict(db.execute("SELECT * FROM job WHERE id=?", (row["id"],)).fetchone()))

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

    def finish(self, job: Job, digest: str | None, error: str | None) -> None:
        """Atomically publish a terminal reference and event, rejecting old-worker writes."""
        if error is None and digest is None:
            raise ValueError("Successful jobs require a complete artefact.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, job)
            status = "failed" if error else "succeeded"
            db.execute(
                "UPDATE job SET status=?, completed_at=?, artefact_sha256=?, error=? WHERE id=?",
                (status, _now(), digest, error, job.id),
            )
            _event(db, job.id, "job_" + status, {"artefact_sha256": digest, "error": error})

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
            return len(rows)
