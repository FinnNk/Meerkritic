"""Keep complete, hash-addressed result bundles outside SQLite and source control."""

import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.artefacts import Publication


class JsonResults:
    """Publish immutable bundles atomically; a crash may leave complete unreferenced files."""

    def __init__(self, root: Path, database: Path) -> None:
        """Create the artefact directory and initialise its mandatory metadata catalogue."""
        self.root = root
        self.state = SQLiteState(database)
        root.mkdir(parents=True, exist_ok=True)

    def publish(self, value: dict[str, object], publication: Publication) -> str:
        """Publish complete JSON and explicit metadata under the ResultStore contract.

        Metadata is committed after the file is flushed/linked. Catalogue failure
        may leave a complete orphan file; an existing identity is never replaced.
        """
        if not isinstance(value, dict):
            raise ValueError("Result artefact must be a JSON object.")
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
        self._catalogue(digest, publication, len(body))
        return digest

    def _catalogue(self, digest: str, publication: Publication, size: int) -> None:
        # Existing bytes keep their hash even if their JSON formatting is non-canonical.
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            metadata = (
                publication.job_id,
                publication.kind,
                str((self.root / (digest + ".json")).resolve()),
                size,
            )
            existing = db.execute(
                "SELECT job_id, type, path, size FROM artefact WHERE sha256=?", (digest,)
            ).fetchone()
            if existing is not None and tuple(existing) != metadata:
                raise ValueError("Artefact identity has conflicting catalogue metadata.")
            db.execute(
                "INSERT OR IGNORE INTO artefact VALUES (?, ?, ?, ?, ?, ?)",
                (digest, *metadata, datetime.now(UTC).isoformat()),
            )

    def index_referenced(self) -> int:
        """Verify and index existing result/edit references after upgrading an older runtime."""
        with self.state.connect() as db:
            rows = db.execute(
                "SELECT artefact_sha256, id, 'normalisation' FROM job "
                "WHERE artefact_sha256 IS NOT NULL UNION "
                "SELECT interpretation_sha256, job_id, 'human_edit' FROM annotation_version "
                "WHERE interpretation_sha256 IS NOT NULL"
            ).fetchall()
        for digest, job_id, kind in rows:
            self.read(digest)
            self._catalogue(
                digest, Publication(job_id, kind), (self.root / (digest + ".json")).stat().st_size
            )
        return len(rows)

    def read(self, digest: str) -> dict[str, object]:
        """Verify the expected hash before exposing any source or model output."""
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid result identity.")
        body = (self.root / (digest + ".json")).read_bytes()
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError("Result artefact checksum mismatch.")
        value = json.loads(body)
        if not isinstance(value, dict):
            raise ValueError("Result artefact must be a JSON object.")
        return value
