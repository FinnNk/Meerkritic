"""Index explicit local DER references and detect subsequent evidence-file changes."""

import hashlib
import json
import re
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.application.reviews import ReviewReference


def _read(path: Path) -> tuple[dict, str]:
    path = path.resolve()
    if any((parent / ".git").exists() for parent in (path.parent, *path.parents)):
        raise ValueError("Canonical DER evidence must be outside application worktrees.")
    with path.open("rb") as stream:
        body = stream.read(1_000_001)
    if len(body) > 1_000_000:
        raise ValueError("DER reference file exceeds the index limit.")
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("DER evidence must be a JSON object.")
    return value, hashlib.sha256(body).hexdigest()


class SQLiteReviewIndex:
    """Retain small immutable reference records; external DER remains authoritative."""

    def __init__(self, database: Path) -> None:
        """Migrate the operational reference index."""
        self.state = SQLiteState(database)

    def index(self, manifest_path: Path, event_path: Path) -> ReviewReference:
        """Bind an explicit readiness event to its exact round manifest and source heads.

        This checks identities and retained-file hashes, not the truth of the review
        assertion, Git bundle, ledger chain or platform approval. Run DER qualification
        separately before importing its status. No command or URL from a file is run.
        """
        manifest, manifest_hash = _read(manifest_path)
        event, event_hash = _read(event_path)
        try:
            pair, round_id = manifest["pair_id"], manifest["round_id"]
            diary, semantic = manifest["diary"]["tip"], manifest["semantic"]["tip"]
            payload = event["payload"]
            stage = payload["stage"]
            sequence = event["sequence"]
            valid = (
                all(
                    isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", value)
                    for value in (pair, round_id)
                )
                and all(
                    isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value)
                    for value in (diary, semantic)
                )
                and event["pair_id"] == pair
                and event["round_id"] == round_id
                and type(sequence) is int
                and sequence > 0
                and payload["diary"] == diary
                and payload["semantic"] == semantic
                and stage
                in {
                    "locally_prepared",
                    "published_for_qualification",
                    "hosted_qualified",
                    "owner_review_ready",
                    "integrated",
                    "blocked",
                }
            )
        except (KeyError, TypeError) as error:
            raise ValueError("DER manifest/event lacks required identity fields.") from error
        if not valid:
            raise ValueError("DER manifest/event identities or readiness do not match.")
        record = ReviewReference(
            pair,
            round_id,
            sequence,
            stage,
            diary,
            semantic,
            str(manifest_path.resolve()),
            manifest_hash,
            str(event_path.resolve()),
            event_hash,
            datetime.now(UTC).isoformat(),
        )
        with self.state.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute(
                "SELECT * FROM review_reference WHERE pair_id=? AND round_id=? AND sequence=?",
                (pair, round_id, sequence),
            ).fetchone()
            if old:
                existing = ReviewReference(**dict(old))
                if any(
                    getattr(existing, key) != value
                    for key, value in asdict(record).items()
                    if key != "indexed_at"
                ):
                    raise ValueError("An indexed evidence identity cannot be replaced.")
                return existing
            values = asdict(record)
            db.execute(
                "INSERT INTO review_reference VALUES (" + ",".join("?" for _ in values) + ")",
                tuple(values.values()),
            )
        return record

    def references(self) -> tuple[tuple[ReviewReference, str], ...]:
        """Show latest indexed assertions, flagging unavailable or changed canonical files."""
        with self.state.connect() as db:
            rows = db.execute(
                "SELECT r.* FROM review_reference r WHERE sequence=(SELECT max(sequence) "
                "FROM review_reference WHERE pair_id=r.pair_id AND round_id=r.round_id) "
                "ORDER BY indexed_at DESC LIMIT 100"
            ).fetchall()
        result = []
        for row in rows:
            record = ReviewReference(**dict(row))
            try:
                matches = (
                    _read(Path(record.manifest_path))[1] == record.manifest_sha256
                    and _read(Path(record.event_path))[1] == record.event_sha256
                )
                status = "unchanged" if matches else "changed"
            except (ValueError, OSError):
                status = "unavailable"
            result.append((record, status))
        return tuple(result)
