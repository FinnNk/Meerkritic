"""Keep complete, hash-addressed result bundles outside SQLite and source control."""

import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState


class JsonResults:
    """Publish immutable bundles atomically; a crash may leave complete unreferenced files."""

    def __init__(self, root: Path, database: Path | None = None) -> None:
        """Create the external artefact directory without loading any bundle."""
        self.root = root
        self.state = SQLiteState(database) if database is not None else None
        root.mkdir(parents=True, exist_ok=True)

    def publish(self, value: dict) -> str:
        """Flush and atomically link a complete bundle; never replace an existing identity."""
        body = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        digest = hashlib.sha256(body).hexdigest()
        target = self.root / (digest + ".json")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=self.root, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(body)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                self.read(digest)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        if self.state is not None:
            kind = (
                "job_log"
                if "log_events" in value
                else "human_edit"
                if "original_result_sha256" in value
                else "normalisation"
            )
            with self.state.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                metadata = (value["job_id"], kind, str(target.resolve()), len(body))
                existing = db.execute(
                    "SELECT job_id, type, path, size FROM artefact WHERE sha256=?", (digest,)
                ).fetchone()
                if existing is not None and tuple(existing) != metadata:
                    raise ValueError("Artefact identity has conflicting catalogue metadata.")
                db.execute(
                    "INSERT OR IGNORE INTO artefact VALUES (?, ?, ?, ?, ?, ?)",
                    (digest, *metadata, datetime.now(UTC).isoformat()),
                )
        return digest

    def index_referenced(self) -> int:
        """Verify and index existing result/edit references after upgrading an older runtime."""
        if self.state is None:
            raise ValueError("Artefact indexing requires an operational database.")
        with self.state.connect() as db:
            rows = db.execute(
                "SELECT artefact_sha256 FROM job WHERE artefact_sha256 IS NOT NULL "
                "UNION SELECT interpretation_sha256 FROM annotation "
                "WHERE interpretation_sha256 IS NOT NULL"
            ).fetchall()
        for row in rows:
            self.publish(self.read(row[0]))
        return len(rows)

    def read(self, digest: str) -> dict:
        """Verify the expected hash before exposing any source or model output."""
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid result identity.")
        body = (self.root / (digest + ".json")).read_bytes()
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError("Result artefact checksum mismatch.")
        return json.loads(body)
