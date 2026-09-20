"""Describe explicit review intent independently of persistence and model execution."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from semantic_reviewer.domain.rules import Digest, Identity, Text


class ReviewIntent(BaseModel):
    """Bind one human action to an exact rule version and operational revision."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    version_id: Digest
    expected_revision: int = Field(ge=1, strict=True)
    action: Literal["promote", "reject", "defer", "reopen"]
    rationale: Text


class ReviewDraft(BaseModel):
    """Keep a bounded coherent set of decisions separate from their eventual application."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    actor: Identity
    intents: tuple[ReviewIntent, ...] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def unique_targets(self) -> Self:
        """Reject ambiguous competing actions for one version in the same batch."""
        if len({item.version_id for item in self.intents}) != len(self.intents):
            raise ValueError("A draft may contain only one action per rule version.")
        return self


class DiscussionNote(BaseModel):
    """Retain a named message on an exact historical rule version without applying it."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Identity
    version_id: Digest
    actor: Identity
    text: Text
