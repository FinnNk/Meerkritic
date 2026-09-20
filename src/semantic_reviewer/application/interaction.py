"""Own research interaction contracts; saving, applying and sending are distinct operations."""

from typing import Protocol

from semantic_reviewer.domain.interaction import DiscussionNote, ReviewDraft


class ReviewWorkspace(Protocol):
    """Own durable drafts, atomic decisions and exact-version discussion.

    Unknown identities raise LookupError; invalid/stale intent raises ValueError.
    Store implementations retain failed drafts and commit decisions/events together.
    These operations never invoke a model. I/O errors propagate without implicit retry.
    """

    def save(self, draft_id: str, expected_revision: int | None, body: ReviewDraft) -> dict:
        """Save immutable payload and move a draft pointer with CAS; no decisions apply.

        New drafts require no expected revision. Identical saved content can replay;
        applied drafts cannot be edited. Return id, revision, digest and status.
        """
        ...

    def read(self, draft_id: str) -> tuple[dict, ReviewDraft]:
        """Return metadata and verified immutable payload, including applied receipts."""
        ...

    def recent(self) -> tuple[dict, ...]:
        """Return at most 100 newest draft pointers without reading their bodies."""
        ...

    def apply(self, draft_id: str, expected_revision: int) -> dict:
        """Apply every intent atomically or none; identical retry returns original receipt.

        A stale target reports its version identity and leaves the saved draft intact.
        expected_revision fences the draft itself, independently of target revisions.
        """
        ...

    def task(self, version_id: str) -> dict:
        """Return pending/answered/deferred/reopened/superseded state and replacement link."""
        ...

    def history(self, version_id: str) -> tuple[dict, ...]:
        """Return up to 1,000 append-only interaction events for the selected version."""
        ...

    def discuss(self, note: DiscussionNote) -> None:
        """Append one replay-safe message to an existing version; never invoke an agent."""
        ...

    def discussion(self, version_id: str) -> tuple[DiscussionNote, ...]:
        """Return all messages within the enforced 1,000-note bound, oldest first."""
        ...
