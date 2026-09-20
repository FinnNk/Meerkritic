"""Keep corpus queue metadata in SQLite and immutable analytical bodies on disk."""

import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import duckdb

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.discovery import DiscoveryRequest, DiscoveryRun
from semantic_reviewer.domain.grouping import validate_vectors


def _now():
    return datetime.now(UTC).isoformat()


def _run(row):
    values = dict(row)
    values["request"] = DiscoveryRequest.model_validate_json(values.pop("request_json"))
    return DiscoveryRun(**values)


def _event(db, subject, kind, details):
    db.execute(
        "INSERT INTO event(kind,subject_id,occurred_at,details_json) VALUES(?,?,?,?)",
        ("discovery_" + kind, subject, _now(), json.dumps(details)),
    )


class SQLiteDiscovery:
    """Own request immutability, single claims and fenced terminal state with atomic events."""

    def __init__(self, database: Path) -> None:
        """Migrate the runtime database without claiming or recovering any work."""
        self.state = SQLiteState(database)

    def enqueue(self, request: DiscoveryRequest) -> DiscoveryRun:
        """Create a new explicit invocation; repeat submissions are separate experiments."""
        request = DiscoveryRequest.model_validate_json(request.model_dump_json())
        run_id = str(uuid4())
        with self.state.connect() as db:
            db.execute(
                "INSERT INTO discovery_run(id,request_json,status,queued_at) "
                "VALUES(?,?,'queued',?)",
                (run_id, request.model_dump_json(), _now()),
            )
            _event(db, run_id, "queued", {"kind": request.kind})
        return self.get(run_id)

    def get(self, run_id: str) -> DiscoveryRun:
        """Return metadata; unknown identities raise LookupError."""
        with self.state.connect() as db:
            row = db.execute("SELECT * FROM discovery_run WHERE id=?", (run_id,)).fetchone()
            if row is None:
                raise LookupError("Discovery run does not exist.")
            return _run(row)

    def recent(self) -> tuple[DiscoveryRun, ...]:
        """List the latest 100 invocations, without reading analytical bodies."""
        with self.state.connect() as db:
            return tuple(
                _run(row)
                for row in db.execute(
                    "SELECT * FROM discovery_run ORDER BY queued_at DESC,id DESC LIMIT 100"
                )
            )

    def claim(self, worker_id: str) -> DiscoveryRun | None:
        """Claim the oldest queued corpus under the caller's shared worker process lock."""
        if not worker_id.strip():
            raise ValueError("Worker identity is required.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM discovery_run WHERE status='running'").fetchone():
                return None
            row = db.execute(
                "SELECT * FROM discovery_run WHERE status='queued' ORDER BY queued_at,id LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            db.execute(
                "UPDATE discovery_run SET status='running',worker_id=?,started_at=? WHERE id=?",
                (worker_id, _now(), row["id"]),
            )
            _event(db, row["id"], "started", {"worker_id": worker_id})
            return _run(
                db.execute("SELECT * FROM discovery_run WHERE id=?", (row["id"],)).fetchone()
            )

    @staticmethod
    def _owned(db, run):
        if not db.execute(
            "SELECT 1 FROM discovery_run WHERE id=? AND worker_id=? AND status='running'",
            (run.id, run.worker_id),
        ).fetchone():
            raise ValueError("Worker no longer owns this discovery run.")

    def bind_route(self, run: DiscoveryRun, decision_id: str) -> None:
        """Bind exactly one persisted route before a model call."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, run)
            if db.execute("SELECT decision_id FROM discovery_run WHERE id=?", (run.id,)).fetchone()[
                0
            ]:
                raise ValueError("Discovery run already has a route.")
            db.execute("UPDATE discovery_run SET decision_id=? WHERE id=?", (decision_id, run.id))
            _event(db, run.id, "routed", {"decision_id": decision_id})

    def finish(self, run: DiscoveryRun, digest: str | None, error: str | None) -> None:
        """Commit a complete artefact reference and event, or a non-empty failure."""
        if digest is not None and not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid result digest.")
        if (error is None and digest is None) or (error is not None and not error.strip()):
            raise ValueError("Completion requires a result or failure explanation.")
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db, run)
            status = "failed" if error else "succeeded"
            db.execute(
                "UPDATE discovery_run SET status=?,result_digest=?,error=?,completed_at=? "
                "WHERE id=?",
                (status, digest, error, _now(), run.id),
            )
            _event(db, run.id, status, {"result_digest": digest, "error": error})

    def recover_interrupted(self) -> int:
        """Fail prior running invocations under exclusivity; uncertain calls are never replayed."""
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT id FROM discovery_run WHERE status='running'").fetchall()
            for row in rows:
                error = (
                    "Worker interrupted; external completion may be unknown. No automatic retry."
                )
                db.execute(
                    "UPDATE discovery_run SET status='failed',error=?,completed_at=? WHERE id=?",
                    (error, _now(), row["id"]),
                )
                _event(db, row["id"], "interrupted", {"error": error})
            return len(rows)


class ParquetDiscovery:
    """Publish bounded complete files with atomic no-replace links and verified reads.

    Publication may leave an unreferenced complete file if later registration fails.
    Reads check bytes before DuckDB sees a Parquet file. No arbitrary path is accepted.
    """

    def __init__(self, root: Path) -> None:
        """Create the external immutable artefact directory."""
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def _read(self, digest, suffix):
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid artefact identity.")
        path = self.root / (digest + suffix)
        with path.open("rb") as stream:
            content = stream.read(32_000_001)
        if len(content) > 32_000_000 or hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("Discovery artefact size or checksum mismatch.")
        return path, content

    def _publish(self, content, suffix):
        if len(content) > 32_000_000:
            raise ValueError("Discovery artefact exceeds 32 MB.")
        digest = hashlib.sha256(content).hexdigest()
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=self.root, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, self.root / (digest + suffix))
            except FileExistsError:
                self._read(digest, suffix)
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
        return digest

    def write_json(self, body: dict) -> str:
        """Publish canonical finite JSON; bodies remain outside operational SQLite."""
        return self._publish(
            json.dumps(
                body, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
            ).encode(),
            ".json",
        )

    def read_json(self, digest: str) -> dict:
        """Verify bytes and object shape; invalid or missing evidence fails closed."""
        body = json.loads(self._read(digest, ".json")[1])
        if not isinstance(body, dict):
            raise ValueError("Discovery manifest must be an object.")
        return body

    def _table(self, schema, rows):
        with tempfile.TemporaryDirectory(dir=self.root) as directory, duckdb.connect() as db:
            target = Path(directory) / "table.parquet"
            db.execute("CREATE TABLE output (" + schema + ")")
            db.executemany(
                "INSERT INTO output VALUES (" + ",".join("?" for _ in rows[0]) + ")", rows
            )
            db.execute("COPY output TO ? (FORMAT PARQUET)", [str(target)])
            return self._publish(target.read_bytes(), ".parquet")

    def write_vectors(self, ids: tuple[str, ...], texts: tuple[str, ...], vectors: tuple) -> str:
        """Publish ordered unique identities, exact preprocessed text and validated unit vectors."""
        vectors = validate_vectors(vectors, len(ids))
        if len(set(ids)) != len(ids) or len(texts) != len(ids):
            raise ValueError("Vector inputs require unique aligned identities.")
        rows = [
            (i, identity, text, list(vector))
            for i, (identity, text, vector) in enumerate(zip(ids, texts, vectors, strict=True))
        ]
        return self._table(
            "position INTEGER,annotation_id VARCHAR,text VARCHAR,vector DOUBLE[]", rows
        )

    def read_vectors(self, digest: str) -> tuple:
        """Verify hash, order, uniqueness and finite dimensions before exposing at most 100 rows."""
        path, _ = self._read(digest, ".parquet")
        with duckdb.connect() as db:
            rows = db.execute(
                "SELECT position,annotation_id,text,vector FROM read_parquet(?) "
                "ORDER BY position LIMIT 101",
                [str(path)],
            ).fetchall()
        if [r[0] for r in rows] != list(range(len(rows))) or len({r[1] for r in rows}) != len(rows):
            raise ValueError("Vector row identity/order is invalid.")
        vectors = validate_vectors(tuple(tuple(row[3]) for row in rows), len(rows))
        return tuple((r[1], r[2], v) for r, v in zip(rows, vectors, strict=True))
