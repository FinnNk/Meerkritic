"""Publish hash-bound architecture views and compare exact source fingerprints on read."""

import json
import os
import re
from pathlib import Path
from uuid import uuid4

from semantic_reviewer.adapters.architecture import delta, source_fingerprint
from semantic_reviewer.adapters.discovery import ParquetDiscovery


def _validate(value):
    if not isinstance(value, dict) or value.get("schema_version") != 3:
        raise ValueError("Harness projections require architecture schema 3 on both sides.")
    if not re.fullmatch(r"[0-9a-f]{64}", str(value.get("source_digest", ""))):
        raise ValueError("Snapshot lacks a valid source fingerprint.")
    for name in ("boundaries", "contracts", "modules", "imports", "interfaces"):
        if not isinstance(value.get(name), (list, tuple)) or not all(
            isinstance(x, dict) for x in value[name]
        ):
            raise ValueError("Snapshot lacks typed architecture records.")


class ArchitectureProjection:
    """Keep immutable view payloads external and an explicitly refreshed local pointer."""

    def __init__(self, root: Path, checkout: Path) -> None:
        """Bind external projection storage and the current checkout; do not generate snapshots."""
        self.files, self.checkout = ParquetDiscovery(root), checkout
        self.pointer = root / "current.json"

    def publish(self, before: dict, after: dict) -> str:
        """Publish a complete same-schema pair/delta before atomically switching the view pointer.

        This is an explicit maintenance operation, never a hidden refresh on read.
        A failed pointer write may leave a complete orphan payload; prior view survives.
        """
        _validate(before)
        _validate(after)
        body = {
            "schema_version": 1,
            "before": before,
            "after": after,
            "delta": delta(before, after),
        }
        digest = self.files.write_json(body)
        temporary = self.pointer.with_name(".pointer-" + str(uuid4()))
        try:
            with temporary.open("x", encoding="utf-8") as stream:
                json.dump({"digest": digest}, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.pointer)
        finally:
            temporary.unlink(missing_ok=True)
        return digest

    def read(self) -> dict | None:
        """Verify payload/delta and label source changes, including behaviour-only edits."""
        if not self.pointer.exists():
            return None
        with self.pointer.open("rb") as stream:
            encoded = stream.read(1001)
        if len(encoded) > 1000:
            raise ValueError("Architecture pointer is oversized.")
        pointer = json.loads(encoded)
        if not isinstance(pointer, dict) or not isinstance(pointer.get("digest"), str):
            raise ValueError("Architecture pointer is invalid.")
        body = self.files.read_json(pointer["digest"])
        if body.get("schema_version") != 1:
            raise ValueError("Unsupported architecture projection schema.")
        try:
            _validate(body["before"])
            _validate(body["after"])
            if body["delta"] != delta(body["before"], body["after"]):
                raise ValueError("Architecture delta disagrees with its source snapshots.")
        except (KeyError, TypeError) as error:
            raise ValueError("Architecture projection lacks required snapshot fields.") from error
        current = source_fingerprint(self.checkout)
        return {
            "digest": pointer["digest"],
            "body": body,
            "current_source": current,
            "stale": current != body["after"]["source_digest"],
        }
