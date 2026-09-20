"""Describe proposed engineering rules and explicit evidence without claiming validation."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
Identity = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class RuleDefinition(BaseModel):
    """State applicability and violation explicitly, with proposed supporting input references."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    statement: Text
    scope: Literal["expression", "statement", "function", "class", "file", "module", "repository"]
    applicability: Text
    violation: Text
    exclusions: tuple[Text, ...] = Field(max_length=10)
    supporting_annotations: tuple[Identity, ...] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def distinct_support(self) -> Self:
        """Reject duplicate support rather than inflate the apparent evidence count."""
        if len(set(self.supporting_annotations)) != len(self.supporting_annotations):
            raise ValueError("Supporting annotation identities must be distinct.")
        return self


class RuleProposal(BaseModel):
    """Make insufficient evidence a valid model outcome rather than inventing a rule."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    candidate: RuleDefinition | None
    insufficiency_reason: Text | None

    @model_validator(mode="after")
    def exclusive_outcome(self) -> Self:
        """Require exactly a proposed candidate or an explanation of insufficient evidence."""
        if (self.candidate is None) == (self.insufficiency_reason is None):
            raise ValueError("Provide a candidate or an insufficiency explanation, not both.")
        return self

    def validate_support(self, supplied: tuple[str, ...]) -> None:
        """Reject references outside the actual model context, even if another cluster has them."""
        if self.candidate and not set(self.candidate.supporting_annotations) <= set(supplied):
            raise ValueError("Rule proposal references an annotation outside the supplied context.")


class RuleOrigin(BaseModel):
    """Record a declared author and rationale; model proposals retain their synthesis trace."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["human", "model"]
    actor: Identity
    rationale: Text
    trace_digest: Digest | None = None

    @model_validator(mode="after")
    def model_trace(self) -> Self:
        """Require model provenance; a human revision can retain its parent's trace separately."""
        if self.kind == "model" and self.trace_digest is None:
            raise ValueError("A model proposal requires an immutable synthesis trace.")
        return self


class RuleVersionBody(BaseModel):
    """Keep one immutable definition and exact discovery/source lineage outside SQLite."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1] = 1
    rule_id: Identity
    parent_version: Digest | None
    selection_id: Digest
    cluster_run: Identity
    cluster_digest: Digest
    cluster: int = Field(ge=0, strict=True)
    purpose: Literal["fixture", "research"]
    definition: RuleDefinition
    origin: RuleOrigin


class RuleEvidence(BaseModel):
    """Retain a typed source link and an explicit verification claim, never an inferred negative."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Identity
    version_id: Digest
    annotation_id: Identity
    kind: Literal["positive", "counterexample", "false_positive", "false_negative", "unresolved"]
    verification: Literal["weak", "verified"]
    actor: Identity
    rationale: Text
    inherited_from: Identity | None = None


class RuleDecisionRequest(BaseModel):
    """Bind a replay-safe research decision to an exact current version and revision."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    operation_id: Identity
    version_id: Digest
    expected_revision: int = Field(ge=1, strict=True)
    action: Literal["promote", "reject"]
    actor: Identity
    rationale: Text
