"""Keep complete, hash-addressed result bundles outside SQLite and source control."""

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


class JsonResults:
    """Publish immutable bundles atomically; a crash may leave complete unreferenced files."""

    def __init__(self, root: Path) -> None:
        """Create the external artefact directory without loading any bundle."""
        self.root = root
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
        return digest

    def read(self, digest: str) -> dict:
        """Verify the expected hash before exposing any source or model output."""
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid result identity.")
        body = (self.root / (digest + ".json")).read_bytes()
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError("Result artefact checksum mismatch.")
        return json.loads(body)
