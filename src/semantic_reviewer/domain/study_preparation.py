"""Own the fixed EDR-0001 sampling order and input-review stopping rules.

These functions prepare inputs; they neither judge source authenticity nor run a
grouping method. Recorded source checks and human reviews remain attestations.
"""

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Text = Annotated[str, Field(min_length=1, max_length=4000, pattern=r"\S")]
PILOTS = ("django/django", "paperless-ngx/paperless-ngx")
SEED = "20260920"


def content_digest(value: dict) -> str:
    """Identify finite JSON content independently of file indentation or key order."""
    body = json.dumps(
        value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )
    return hashlib.sha256(body.encode()).hexdigest()


def prepare_sample(source: bytes, expected_digest: str, exposed: tuple[str, ...] = ()) -> dict:
    """Return a metadata-only plan tied to original bytes, without rewriting records.

    Fixed pilot exclusions cannot be removed. Extra exposure is explicit. Partition
    repositories before considering source bodies; deduplicate by original position
    before the seeded round-robin. Hash text only for exact duplicate detection.
    Invalid input fails the whole preparation, rather than silently altering the pool.
    """
    if hashlib.sha256(source).hexdigest() != expected_digest:
        raise ValueError("Source SHA-256 does not match the pinned bytes.")
    rows = json.loads(source)
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100_000:
        raise ValueError("Source must contain 1..100000 records.")
    pilots = sorted(set(PILOTS) | {_repository(item) for item in exposed})
    metadata = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError("Source records must be objects.")
        if any(not isinstance(row.get(key), str) for key in ("owner", "repo", "code", "comment")):
            raise ValueError("Source owner, repo, code and comment must be strings.")
        repository = _repository(f"{row['owner']}/{row['repo']}")
        if any(
            type(row.get(key)) is not int or row[key] <= 0 for key in ("pr_number", "comment_id")
        ):
            raise ValueError("Source PR and comment identities must be positive integers.")
        metadata.append(
            {
                "source_index": index,
                "repository": repository,
                "pull_request": row["pr_number"],
                "comment_id": row["comment_id"],
            }
        )
    repositories = sorted({row["repository"] for row in metadata} - set(pilots))
    holdout = sorted(repositories, key=lambda repo: _hash(f"{SEED}:holdout:{repo}"))[
        : math.ceil(len(repositories) / 5)
    ]
    seen_identity, seen_text = {}, {}
    exclusions, eligible = [], defaultdict(list)
    for row, original in zip(metadata, rows, strict=True):
        index, repository = row["source_index"], row["repository"]
        identity = (repository, row["comment_id"])
        text = content_digest({"code": original["code"], "comment": original["comment"]})
        duplicate = seen_identity.get(identity, seen_text.get(text))
        seen_identity.setdefault(identity, index)
        seen_text.setdefault(text, index)
        reason = None
        if repository in pilots:
            reason = "prior_exposure"
        elif repository in holdout:
            reason = "holdout"
        if reason or duplicate is not None:
            exclusions.append({**row, "reason": reason or "duplicate", "duplicate_of": duplicate})
        else:
            eligible[repository].append(row)
    for candidates in eligible.values():
        candidates.sort(
            key=lambda row: _hash(f"{SEED}:sample:{expected_digest}:{row['source_index']}")
        )
    ordered = [
        eligible[repo][round_index]
        for round_index in range(10)
        for repo in sorted(eligible)
        if round_index < len(eligible[repo])
    ][:80]
    chosen = {row["source_index"] for row in ordered}
    for candidates in eligible.values():
        exclusions.extend(
            {**row, "reason": "outside_candidate_budget", "duplicate_of": None}
            for row in candidates
            if row["source_index"] not in chosen
        )
    return {
        "schema_version": 1,
        "procedure": "edr-0001-inputs-v1",
        "source_sha256": expected_digest,
        "source_rows": len(rows),
        "seed": SEED,
        "prior_exposure": pilots,
        "holdout_repositories": holdout,
        "candidates": ordered,
        "exclusions": sorted(exclusions, key=lambda row: row["source_index"]),
    }


class PreparationAttempt(BaseModel):
    """One terminal preparation outcome, explicitly attributed to its recorder.

    Source evidence identifies a retained response/record, not a claim that a URL
    alone proves authenticity. Human review is claimed only by explicit reviewer
    and annotation identities. The application selection verifies those versions
    later; this external ledger does not authenticate a person or read live state.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    source_index: int = Field(ge=0, strict=True)
    outcome: Literal[
        "source_unresolved",
        "context_unusable",
        "normalisation_failed",
        "reject",
        "accept",
        "edit",
        "repository_quota",
    ]
    recorded_by: Text
    reason: Text
    source_reference: Text | None = None
    source_evidence_sha256: Digest | None = None
    source_check: Text | None = None
    job_id: Text | None = None
    annotation_id: Text | None = None
    human_reviewer: Text | None = None


def preparation_progress(plan: dict, attempts: tuple[PreparationAttempt, ...]) -> dict:
    """Validate an ordered attempt prefix and return progress without making decisions.

    Callers must supply the plan returned by prepare_sample for the pinned source.
    Every candidate consumes one of the 80 positions, including quota skips; stop
    immediately at 40 usable reviews. Five accepted/edited records per repository
    is a hard limit. A depleted smaller candidate pool is also an explicit shortfall.
    """
    candidates = plan["candidates"]
    accepted, counts, annotation_ids, job_ids = [], Counter(), set(), set()
    if len(attempts) > len(candidates):
        raise ValueError("Attempt log extends beyond the fixed candidate pool.")
    for candidate, attempt in zip(candidates[: len(attempts)], attempts, strict=True):
        if len(accepted) == 40:
            raise ValueError("Preparation must stop at 40 usable human reviews.")
        if attempt.source_index != candidate["source_index"]:
            raise ValueError("Attempts must follow the fixed candidate order without gaps.")
        repository = candidate["repository"]
        if (counts[repository] == 5) != (attempt.outcome == "repository_quota"):
            raise ValueError("Skip a repository only after its five usable reviews.")
        human = attempt.outcome in {"accept", "edit", "reject"}
        normalised = human or attempt.outcome == "normalisation_failed"
        if human != bool(attempt.annotation_id and attempt.human_reviewer):
            raise ValueError("Human outcomes require both annotation and named human reviewer.")
        if not human and (attempt.annotation_id or attempt.human_reviewer):
            raise ValueError("Non-human outcomes cannot claim a human annotation.")
        if normalised != bool(attempt.job_id):
            raise ValueError("Normalisation outcomes require a job ID; other outcomes forbid it.")
        if attempt.outcome != "repository_quota":
            if not all(
                (attempt.source_reference, attempt.source_evidence_sha256, attempt.source_check)
            ):
                raise ValueError(
                    "Retain source reference, evidence digest and check for every attempt."
                )
        elif any((attempt.source_reference, attempt.source_evidence_sha256, attempt.source_check)):
            raise ValueError("Quota skips do not claim source inspection.")
        if attempt.annotation_id:
            if attempt.annotation_id in annotation_ids:
                raise ValueError("An annotation cannot supply two research inputs.")
            annotation_ids.add(attempt.annotation_id)
        if attempt.job_id:
            if attempt.job_id in job_ids:
                raise ValueError("A normalisation job cannot supply two candidates.")
            job_ids.add(attempt.job_id)
        if attempt.outcome in {"accept", "edit"}:
            accepted.append(attempt.annotation_id)
            counts[repository] += 1
    state = "pending"
    if len(accepted) == 40:
        state = "ready"
    elif len(attempts) == len(candidates):
        state = "shortfall"
    return {
        "state": state,
        "attempted": len(attempts),
        "usable": len(accepted),
        "annotation_ids": accepted,
        "usable_by_repository": dict(sorted(counts.items())),
        "next_candidate": candidates[len(attempts)] if state == "pending" else None,
        "registration": "not established by preparation",
    }


def _repository(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Repository identity must use owner/name without whitespace.")
    return value.casefold()


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
