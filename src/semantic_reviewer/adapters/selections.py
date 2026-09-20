"""Publish self-contained selection bodies, keeping only metadata and events in SQLite."""

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.selections import SelectionSnapshot, SelectionSummary

MAX_BYTES = 32_000_000


class JsonSelections:
    """Own complete immutable publication before an atomic catalogue/event transaction."""

    def __init__(self, root: Path, database: Path) -> None:
        """Create the external body directory and migrate operational state."""
        self.root = root
        self.state = SQLiteState(database)
        root.mkdir(parents=True, exist_ok=True)

    def publish(self, snapshot: SelectionSnapshot) -> SelectionSummary:
        """Register verified content once; interrupted registration may leave an orphan file."""
        # Revalidate even a model assembled with Pydantic's unchecked construction helpers.
        body = json.dumps(
            snapshot.model_dump(mode="json"),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(body) > MAX_BYTES:
            raise ValueError("Selection body exceeds the 32 MB limit.")
        snapshot = SelectionSnapshot.model_validate_json(body)
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
                self._body(digest)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        summary = self._summary(digest, snapshot, datetime.now(UTC).isoformat())
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM annotation_selection WHERE id=?", (digest,)).fetchone()
            if row:
                existing = SelectionSummary(**dict(row))
                if existing != self._summary(digest, snapshot, existing.created_at):
                    raise ValueError("Selection metadata disagrees with its body.")
                return existing
            db.execute(
                "INSERT INTO annotation_selection VALUES (?, ?, ?, ?, ?, ?)",
                tuple(asdict(summary).values()),
            )
            db.execute(
                "INSERT INTO event(kind, subject_id, occurred_at, details_json) "
                "VALUES (?, ?, ?, ?)",
                (
                    "selection_frozen",
                    digest,
                    summary.created_at,
                    json.dumps({"schema_version": 1, "purpose": summary.purpose}),
                ),
            )
        return summary

    def _body(self, digest: str) -> SelectionSnapshot:
        with (self.root / (digest + ".json")).open("rb") as stream:
            body = stream.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES or hashlib.sha256(body).hexdigest() != digest:
            raise ValueError("Selection body size or checksum mismatch.")
        return SelectionSnapshot.model_validate_json(body)

    @staticmethod
    def _summary(digest: str, snapshot: SelectionSnapshot, created_at: str) -> SelectionSummary:
        included = sum(item.exclusion is None for item in snapshot.records)
        return SelectionSummary(
            digest,
            snapshot.dataset.id,
            snapshot.request.purpose,
            included,
            len(snapshot.records) - included,
            created_at,
        )

    def read(self, selection_id: str) -> tuple[SelectionSummary, SelectionSnapshot]:
        """Check registered identity, body integrity and metadata before exposing records."""
        if not re.fullmatch(r"[0-9a-f]{64}", selection_id):
            raise ValueError("Invalid selection identity.")
        with self.state.connect() as db:
            row = db.execute(
                "SELECT * FROM annotation_selection WHERE id=?", (selection_id,)
            ).fetchone()
        if row is None:
            raise LookupError("Selection does not exist.")
        summary = SelectionSummary(**dict(row))
        snapshot = self._body(selection_id)
        if summary != self._summary(selection_id, snapshot, summary.created_at):
            raise ValueError("Selection metadata disagrees with its body.")
        return summary, snapshot

    def recent(self, page: int = 1) -> tuple[SelectionSummary, ...]:
        """Read 20 metadata summaries, newest first; body verification occurs on opening."""
        if not 1 <= page <= 1_000_000:
            raise ValueError("Page is outside the supported range.")
        with self.state.connect() as db:
            return tuple(
                SelectionSummary(**dict(row))
                for row in db.execute(
                    "SELECT * FROM annotation_selection ORDER BY created_at DESC, id DESC "
                    "LIMIT 20 OFFSET ?",
                    ((page - 1) * 20,),
                )
            )
