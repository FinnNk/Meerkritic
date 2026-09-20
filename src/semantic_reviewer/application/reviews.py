"""Expose small references to external DER evidence without owning review truth."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReviewReference:
    """Identify an explicitly indexed readiness assertion and its authoritative files."""

    pair_id: str
    round_id: str
    sequence: int
    stage: str
    diary: str
    semantic: str
    manifest_path: str
    manifest_sha256: str
    event_path: str
    event_sha256: str
    indexed_at: str


class ReviewIndex(Protocol):
    """Read verified references; never infer readiness or mutate canonical evidence."""

    def references(self) -> tuple[tuple[ReviewReference, str], ...]:
        """Return up to 100 latest pair/round references with current file-integrity status."""
        ...
