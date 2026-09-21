"""Describe additional human reading context independently of model input."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReadingContext:
    """Identify preserved source presented to a human, without claiming it was read."""

    sha256: str
    job_id: str
    observation_id: str
    url: str
    retrieved_at: str
    response_sha256: str
    comment: str
    code: str
    comment_difference: str
    code_difference: str


class SourceReader(Protocol):
    """Hide source storage and identity verification from annotation consumers."""

    def read(self, job_id: str) -> ReadingContext | None:
        """Return verified context, or None when unattached; damaged evidence raises.

        ValueError reports identity/integrity failures; OSError reports unavailable
        files. Never fetch a source, repair text or silently ignore an attachment.
        """
        ...
