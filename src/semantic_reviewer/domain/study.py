"""Own the fixed EDR-0001 assessment rules without inference, storage or human judgements."""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Text = Annotated[str, Field(min_length=1, max_length=12000, pattern=r"\S")]
Identity = Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]


class Item(BaseModel):
    """Retain one eligible annotation's exact shared text and repository identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: Identity
    text: Text
    repository: Identity


class Group(BaseModel):
    """Describe a complete group, including its deterministic representative."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    members: tuple[Identity, ...] = Field(min_length=2, max_length=100)
    representative: Identity


class Attempt(BaseModel):
    """Retain execution outcomes; a retry needs a diagnosed implementation failure.

    Elapsed time excludes model loading, queueing and human rating. Provenance
    references remain in the application record, rather than entering rating packs.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    status: Literal["succeeded", "failed"]
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    error: Text | None = None
    retry_reason: Text | None = None

    @model_validator(mode="after")
    def consistent(self) -> Self:
        """Require a failure reason exactly when execution failed."""
        if (self.status == "failed") != (self.error is not None):
            raise ValueError("Attempt status and error disagree.")
        return self


class Method(BaseModel):
    """Keep every attempt and the final partition, without hiding failed executions."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    attempts: tuple[Attempt, ...] = Field(min_length=1, max_length=2)
    groups: tuple[Group, ...] = Field(default=(), max_length=50)
    outliers: tuple[Identity, ...] = Field(default=(), max_length=100)


class Comparison(BaseModel):
    """Validate two complete partitions over the same bounded ordered inputs.

    Fixture purpose never implies human-reviewed evidence. Research selection and
    registration references are checked at the application/command boundary.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    protocol: Literal["edr-0001-comparison-v1"] = "edr-0001-comparison-v1"
    purpose: Literal["fixture", "research"]
    items: tuple[Item, ...] = Field(min_length=1, max_length=100)
    baseline: Method
    candidate: Method

    @model_validator(mode="after")
    def complete(self) -> Self:
        """Reject mixed, duplicate or omitted identities and undisclosed retry patterns."""
        ids = [item.id for item in self.items]
        if len(set(ids)) != len(ids):
            raise ValueError("Comparison inputs must have distinct identities.")
        if self.purpose == "research" and (
            len(ids) != 40
            or max(Counter(item.repository.casefold() for item in self.items).values()) > 5
        ):
            raise ValueError("Research requires 40 inputs and at most five per repository.")
        methods = (self.baseline, self.candidate)
        if sum(len(method.attempts) - 1 for method in methods) > 1:
            raise ValueError("Only one technical rerun is allowed across the study.")
        for method in methods:
            if method.attempts[0].retry_reason is not None:
                raise ValueError("The first attempt cannot be a retry.")
            if len(method.attempts) == 2 and (
                method.attempts[0].status != "failed" or not method.attempts[1].retry_reason
            ):
                raise ValueError("A retry needs a failed predecessor and diagnosis.")
            if method.attempts[-1].status == "failed":
                if method.groups or method.outliers:
                    raise ValueError("A failed method cannot claim a complete partition.")
                continue
            members = [i for group in method.groups for i in group.members]
            all_ids = members + list(method.outliers)
            if len(all_ids) != len(ids) or set(all_ids) != set(ids):
                raise ValueError("Method partition has duplicate, unknown or missing inputs.")
            for group in method.groups:
                if group.representative not in group.members:
                    raise ValueError("Representative must belong to its group.")
        return self


class Rating(BaseModel):
    """Record a human's complete judgement and reason for one masked group."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    group_id: Identity
    judgement: Literal["coherent", "not coherent", "uncertain"]
    reason: Text


class Ratings(BaseModel):
    """Bind named human judgements to the pack's exact content identity.

    This records an attestation, not authentication. Synthetic test ratings must
    retain fixture purpose. Freeze the submitted file before revealing mappings.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    pack_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    purpose: Literal["fixture", "research"]
    rater: Identity
    suspected_unmasking: str = Field(max_length=12000)
    ratings: tuple[Rating, ...] = Field(max_length=24)


def digest(value: dict) -> str:
    """Identify finite canonical JSON, independently of whitespace and key order."""
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def assessment(value: Comparison) -> tuple[dict, dict]:
    """Return a method-masked pack and separate mapping; never fabricate ratings.

    Rank each arm's groups by SHA-256 of seed/purpose/sorted membership JSON,
    take equal budgets, deduplicate membership sets, then independently rank the
    presentation. Representatives and method-specific counts stay out of the pack.
    Failed methods produce an empty, explicitly unevaluable assessment.
    """
    value = Comparison.model_validate_json(value.model_dump_json())
    complete = all(m.attempts[-1].status == "succeeded" for m in (value.baseline, value.candidate))
    k = min(12, len(value.baseline.groups), len(value.candidate.groups)) if complete else 0
    selected = {}
    for name in ("baseline", "candidate"):
        keys = [tuple(sorted(group.members)) for group in getattr(value, name).groups]
        selected[name] = sorted(keys, key=lambda key: _rank("select", key))[:k]
    order = sorted(
        set(selected["baseline"] + selected["candidate"]), key=lambda key: _rank("present", key)
    )
    labels = {key: f"G{index + 1:02d}" for index, key in enumerate(order)}
    items = {item.id: item for item in value.items}
    pack = {
        "protocol": value.protocol,
        "purpose": value.purpose,
        "rubric": "Coherent: every member expresses one specific reusable engineering concern. "
        "A shared language, library or broad topic is insufficient. Contradictory or "
        "unrelated members: not coherent. Inadequate context: uncertain.",
        "groups": [
            {
                "group_id": labels[key],
                "members": [{"id": identity, "text": items[identity].text} for identity in key],
            }
            for key in order
        ],
    }
    mapping = {
        "status": "ready" if k >= 8 else "insufficient" if complete else "failed",
        "groups_per_method": k,
        "methods": {name: [labels[key] for key in keys] for name, keys in selected.items()},
        "shared_groups": len(set(selected["baseline"]) & set(selected["candidate"])),
    }
    return pack, mapping


def analyse(value: Comparison, ratings: Ratings) -> dict:
    """Report exact counts and fixed criteria; missing ratings cannot yield adoption.

    Uncertain ratings remain in denominators. A valid report is a recommendation,
    not the owner's adoption decision. Malformed or foreign ratings raise ValueError.
    """
    pack, mapping = assessment(value)
    ratings = Ratings.model_validate_json(ratings.model_dump_json())
    expected = {group["group_id"] for group in pack["groups"]}
    actual = [rating.group_id for rating in ratings.ratings]
    if (
        ratings.pack_sha256 != digest(pack)
        or ratings.purpose != value.purpose
        or len(set(actual)) != len(actual)
        or not set(actual) <= expected
    ):
        raise ValueError("Ratings are duplicated, foreign or bound to another pack/purpose.")
    by_id = {rating.group_id: rating.judgement for rating in ratings.ratings}
    k = mapping["groups_per_method"]
    counts = {}
    for name in ("baseline", "candidate"):
        method = getattr(value, name)
        judgements = Counter(by_id.get(i, "missing") for i in mapping["methods"][name])
        covered = sum(len(group.members) for group in method.groups)
        counts[name] = {
            "coherent": judgements["coherent"],
            "not_coherent": judgements["not coherent"],
            "uncertain": judgements["uncertain"],
            "missing": judgements["missing"],
            "assessed_denominator": k,
            "covered": covered,
            "input_denominator": len(value.items),
            "outliers": len(method.outliers),
            "failed_inputs": len(value.items) if method.attempts[-1].status == "failed" else 0,
            "groups": len(method.groups),
            "unassessed_groups": len(method.groups) - k,
            "group_sizes": [len(group.members) for group in method.groups],
            "attempts": [attempt.model_dump(mode="json") for attempt in method.attempts],
        }
    complete = set(actual) == expected
    valid = all(getattr(value, name).attempts[-1].status == "succeeded" for name in counts)
    within_cap = all(
        sum(a.elapsed_seconds for a in getattr(value, name).attempts) <= 1800 for name in counts
    )
    baseline, candidate = counts["baseline"], counts["candidate"]
    primary = None
    if complete and valid and k >= 8:
        primary = Fraction(candidate["coherent"], k) >= Fraction(3, 4) and Fraction(
            candidate["coherent"] - baseline["coherent"], k
        ) >= Fraction(1, 10)
    coverage = (
        (
            Fraction(candidate["covered"], len(value.items)) >= Fraction(3, 5)
            and Fraction(baseline["covered"] - candidate["covered"], len(value.items))
            <= Fraction(1, 10)
        )
        if valid
        else None
    )
    status = "incomplete" if not complete else mapping["status"]
    recommend = status == "ready" and primary and coverage and within_cap
    return {
        "protocol": value.protocol,
        "purpose": value.purpose,
        "status": status,
        "recommendation": "candidate" if recommend else "no adoption recommendation",
        "owner_decision": "pending",
        "pack_sha256": digest(pack),
        "rating_completeness": complete,
        "criteria": {
            "primary": primary,
            "coverage": coverage,
            "valid_outputs": valid,
            "within_resource_cap": within_cap,
        },
        "methods": counts,
        "shared_groups": mapping["shared_groups"],
        "repository_counts": dict(
            sorted(Counter(item.repository.casefold() for item in value.items).items())
        ),
        "rater": ratings.rater,
        "suspected_unmasking": ratings.suspected_unmasking,
        "limitations": [
            "Small development corpus; no population-wide superiority claim.",
            "One rater; method masking may be imperfect.",
            "Shared inputs do not imply matched output groups or independent ratings.",
            "Recorded attestations cannot prove undisclosed runs did not occur.",
        ],
    }


def _rank(stage, members):
    return digest({"seed": 20260920, "stage": stage, "members": members})
