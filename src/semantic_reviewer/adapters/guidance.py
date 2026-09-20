"""Persist replay-safe guidance identity and explicit uncertain completion."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.domain.guidance import GuidanceRequest


def _now():
    return datetime.now(UTC).isoformat()


def _event(db, subject, kind, details):
    db.execute(
        "INSERT INTO event(kind,subject_id,occurred_at,details_json) VALUES(?,?,?,?)",
        ("guidance_" + kind, subject, _now(), json.dumps(details)),
    )


class SQLiteGuidance:
    """Own queue transactions and fencing; immutable context/results remain in external files."""

    def __init__(self, database: Path) -> None:
        """Migrate metadata without sending, claiming or recovering work."""
        self.state = SQLiteState(database)

    def enqueue(self, request: GuidanceRequest, digest: str) -> dict:
        """Queue a complete submitted snapshot once; verify all current target revisions."""
        request = GuidanceRequest.model_validate_json(request.model_dump_json())
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid guidance context digest.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT * FROM guidance_batch WHERE id=?", (request.id,)
            ).fetchone()
            if existing:
                if existing["request_digest"] != digest:
                    raise ValueError("Guidance identity already refers to different content.")
                return dict(existing)
            for target in request.targets:
                if not db.execute(
                    "SELECT 1 FROM rule_head WHERE version_id=? AND revision=?",
                    (target.version_id, target.expected_revision),
                ).fetchone():
                    raise ValueError(
                        f"Guidance target {target.version_id} changed; inspect before sending."
                    )
            db.execute(
                "INSERT INTO guidance_batch(id,request_digest,status,queued_at) "
                "VALUES(?,?,'queued',?)",
                (request.id, digest, _now()),
            )
            _event(db, request.id, "submitted", {"request_digest": digest, "actor": request.actor})
        return self.get(request.id)

    def get(self, batch_id: str) -> dict:
        """Return metadata for an existing submitted identity; unknown IDs raise LookupError."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM guidance_batch WHERE id=?", (batch_id,)).fetchone()
        if row is None:
            raise LookupError("Guidance batch does not exist.")
        return dict(row)

    def recent(self) -> tuple[dict, ...]:
        """List at most 100 submissions without reading context or response bodies."""
        with self.state.connect() as db:
            return tuple(
                dict(row)
                for row in db.execute(
                    "SELECT * FROM guidance_batch ORDER BY queued_at DESC,id DESC LIMIT 100"
                )
            )

    def claim(self, worker_id: str) -> dict | None:
        """Claim one queued submission under the caller's shared process lock."""
        if not worker_id.strip():
            raise ValueError("Worker identity is required.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM guidance_batch WHERE status='running'").fetchone():
                return None
            row = db.execute(
                "SELECT * FROM guidance_batch WHERE status='queued' ORDER BY queued_at,id LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            db.execute(
                "UPDATE guidance_batch SET status='running',worker_id=? WHERE id=?",
                (worker_id, row["id"]),
            )
            _event(db, row["id"], "started", {"worker_id": worker_id})
            return dict(
                db.execute("SELECT * FROM guidance_batch WHERE id=?", (row["id"],)).fetchone()
            )

    @staticmethod
    def _owned(db, run):
        if not db.execute(
            "SELECT 1 FROM guidance_batch WHERE id=? AND worker_id=? AND status='running'",
            (run["id"], run["worker_id"]),
        ).fetchone():
            raise ValueError("Worker no longer owns this guidance submission.")

    def bind_route(self, run: dict, decision_id: str) -> None:
        """Bind one persisted route to a claimed submission before model invocation."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, run)
            if db.execute(
                "SELECT decision_id FROM guidance_batch WHERE id=?", (run["id"],)
            ).fetchone()[0]:
                raise ValueError("Guidance already has a route.")
            db.execute(
                "UPDATE guidance_batch SET decision_id=? WHERE id=?", (decision_id, run["id"])
            )
            _event(db, run["id"], "routed", {"decision_id": decision_id})

    def finish(self, run: dict, digest: str | None, error: str | None) -> None:
        """Publish responded/failed with an event under the original worker's fence."""
        if digest is not None and not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid guidance response digest.")
        if (digest is None and error is None) or (error is not None and not error.strip()):
            raise ValueError("Guidance completion needs a response or non-blank failure.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, run)
            status = "failed" if error else "responded"
            db.execute(
                "UPDATE guidance_batch SET status=?,result_digest=?,error=?,completed_at=? "
                "WHERE id=?",
                (status, digest, error, _now(), run["id"]),
            )
            _event(db, run["id"], status, {"result_digest": digest, "error": error})

    def recover_interrupted(self) -> int:
        """Retain unknown completion on restart; never replay automatically."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT id FROM guidance_batch WHERE status='running'").fetchall()
            for row in rows:
                error = (
                    "Worker interrupted; external completion is unknown. "
                    "Inspect before a new explicit send."
                )
                db.execute(
                    "UPDATE guidance_batch SET status='unknown',error=?,completed_at=? WHERE id=?",
                    (error, _now(), row["id"]),
                )
                _event(db, row["id"], "unknown", {"error": error})
            return len(rows)
