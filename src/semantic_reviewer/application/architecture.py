"""Expose verified architecture projections without making them a competing source of truth."""

from typing import Protocol


class ArchitectureView(Protocol):
    """Read published typed before/after/delta and identify stale current source."""

    def read(self) -> dict | None:
        """Return verified projection/digest/stale state, or None when nothing is published.

        Corrupt or mismatched projection raises ValueError; filesystem failures
        propagate. Reads do not regenerate evidence or certify architecture checks.
        """
        ...
