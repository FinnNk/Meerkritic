"""Bind human guidance and advisory responses to explicit immutable rule versions."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from semantic_reviewer.domain.rules import Digest, Identity, Text


class GuidanceTarget(BaseModel):
    """Pin one current version/revision and the discussion notes deliberately included."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    version_id: Digest
    expected_revision: int = Field(ge=1, strict=True)
    discussion_ids: tuple[Identity, ...] = Field(default=(), max_length=20)


class GuidanceRequest(BaseModel):
    """Identify one coherent replay-safe send; a new send requires a new batch identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Identity
    actor: Identity
    instruction: Text
    targets: tuple[GuidanceTarget, ...] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def distinct(self) -> Self:
        """Prevent duplicate targets or notes from inflating context."""
        if len({t.version_id for t in self.targets}) != len(self.targets):
            raise ValueError("Guidance targets must be distinct.")
        if any(len(set(t.discussion_ids)) != len(t.discussion_ids) for t in self.targets):
            raise ValueError("Discussion references must be distinct.")
        return self


class GuidanceAdvice(BaseModel):
    """Return advice for every supplied target without changing any human decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    version_id: Digest
    advice: Text


class GuidanceResponse(BaseModel):
    """Make source coverage explicit; advice is neither a submitted decision nor an applied edit."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    summary: Text
    responses: tuple[GuidanceAdvice, ...] = Field(min_length=1, max_length=6)

    def validate_targets(self, targets: tuple[str, ...]) -> None:
        """Require exactly one response per supplied version, rejecting invented or omitted IDs."""
        ids = tuple(item.version_id for item in self.responses)
        if len(set(ids)) != len(ids) or set(ids) != set(targets):
            raise ValueError("Advice must cover every supplied version exactly once.")
