"""Interpret source evidence without importing routing, storage or workflow frameworks."""

from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from semantic_reviewer.domain.datasets import Observation

Text = Annotated[str, Field(min_length=1, max_length=4000)]
Judgement = Literal["yes", "no", "uncertain"]


class EvidenceQuote(BaseModel):
    """Identify an exact, unambiguous substring of supplied comment or code."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    source: Literal["comment", "code"]
    quote: Text


class IssueInterpretation(BaseModel):
    """Represent a proposed issue, not an accepted rule or verified judgement."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    actionable_engineering_concern: Judgement
    issue_statement: Text
    coarse_categories: Annotated[tuple[Text, ...], Field(min_length=1, max_length=8)]
    scope: Literal["expression", "statement", "function", "class", "file", "module", "repository"]
    generalisable: Judgement
    proposed_invariant: Text | None
    evidence_quotes: Annotated[tuple[EvidenceQuote, ...], Field(max_length=16)]
    exclusions: Annotated[tuple[Text, ...], Field(max_length=16)]

    @model_validator(mode="after")
    def actionable_evidence(self) -> "IssueInterpretation":
        """Require source evidence for an affirmative engineering concern."""
        if self.actionable_engineering_concern == "yes" and not self.evidence_quotes:
            raise ValueError("An actionable concern needs source evidence.")
        return self


@dataclass(frozen=True)
class EvidenceSpan:
    """Locate a verified quote using zero-based, half-open Unicode character offsets."""

    source: str
    start: int
    end: int
    quote: str


def ground(interpretation: IssueInterpretation, source: Observation) -> tuple[EvidenceSpan, ...]:
    """Resolve exact quotes to unique source spans; reject invented or ambiguous evidence.

    Matching text establishes provenance, not the correctness of the interpretation.
    Offsets refer to the supplied source record, without whitespace normalisation.
    """
    spans = []
    for evidence in interpretation.evidence_quotes:
        text = source.comment if evidence.source == "comment" else source.code
        start = text.find(evidence.quote)
        if start < 0 or text.find(evidence.quote, start + 1) >= 0:
            raise ValueError("Evidence quote is missing or ambiguous in the source.")
        spans.append(
            EvidenceSpan(evidence.source, start, start + len(evidence.quote), evidence.quote)
        )
    return tuple(spans)
