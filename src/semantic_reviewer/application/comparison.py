"""Bind the fixed comparison to immutable selections, exact vectors and worker results."""

import hashlib
import time
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime

from semantic_reviewer.application.discovery import DiscoveryService
from semantic_reviewer.domain.grouping import cluster_texts, cluster_vectors, interpretation_text
from semantic_reviewer.domain.study import Attempt, Comparison, Group, Item, Method


def baseline(
    service: DiscoveryService,
    selection_id: str,
    previous: dict | None = None,
    retry_reason: str | None = None,
) -> dict:
    """Run the bounded lexical method once and return its complete timed evidence.

    No model call occurs. The caller must check registration before research use
    and publish this returned record immutably, including an ordinary method failure.
    Missing/corrupt selections fail before execution and are not counted as runs.
    One retry needs the exact failed predecessor and a non-blank diagnosis.
    """
    summary, items = _inputs(service, selection_id)
    prior = ()
    if previous is not None:
        if (
            previous["selection_id"] != selection_id
            or previous["purpose"] != summary.purpose
            or previous["items"] != [item.model_dump() for item in items]
            or previous["algorithm"] != "ascii-jaccard-components-v1"
        ):
            raise ValueError("Retry inputs differ from the failed baseline.")
        old = Method.model_validate(previous["method"])
        if (
            len(old.attempts) != 1
            or old.attempts[-1].status != "failed"
            or old.groups
            or old.outliers
            or not retry_reason
        ):
            raise ValueError("Only one diagnosed retry of a failed baseline is allowed.")
        prior = old.attempts
    elif retry_reason is not None:
        raise ValueError("A retry reason needs a failed predecessor.")
    if retry_reason is not None:
        # Validate the diagnosis before executing, rather than after another run.
        Attempt(status="succeeded", elapsed_seconds=0, retry_reason=retry_reason)
    started, clock = datetime.now(UTC), time.monotonic()
    error, rows = None, ()
    try:
        rows = cluster_texts(tuple(item.id for item in items), tuple(item.text for item in items))
    except ValueError as failure:
        error = str(failure)
    elapsed = time.monotonic() - clock
    attempt = Attempt(
        status="failed" if error else "succeeded",
        elapsed_seconds=elapsed,
        error=error,
        retry_reason=retry_reason,
    )
    method = _method(rows, (*prior, attempt))
    return {
        "algorithm": "ascii-jaccard-components-v1",
        "selection_id": selection_id,
        "purpose": summary.purpose,
        "items": [item.model_dump() for item in items],
        "method": method.model_dump(mode="json"),
        "started_at": started.isoformat(),
        "completed_at": datetime.now(UTC).isoformat(),
    }


def assemble(
    service: DiscoveryService,
    lexical: dict,
    attempts: list[dict],
    expected_profile: dict | None = None,
) -> tuple[Comparison, dict]:
    """Verify the same text, fixed clustering and all supplied attempts before comparison.

    Each candidate attempt identifies an embedding run and optional clustering run;
    a retry also needs a diagnosis. Successful embedding reuse after a clustering
    failure is counted once. No model execution occurs. Research requires the exact
    pinned profile. This verifies supplied records, not undisclosed outside activity.
    Invalid, unfinished or mismatched evidence raises ValueError/LookupError/OSError.
    """
    summary, items = _inputs(service, lexical["selection_id"])
    if (
        lexical["algorithm"] != "ascii-jaccard-components-v1"
        or lexical["purpose"] != summary.purpose
        or lexical["items"] != [item.model_dump() for item in items]
    ):
        raise ValueError("Baseline inputs differ from the immutable selection.")
    lexical_method = Method.model_validate(lexical["method"])
    if lexical_method.attempts[-1].status == "succeeded":
        replay = _method(
            cluster_texts(tuple(i.id for i in items), tuple(i.text for i in items)),
            lexical_method.attempts,
        )
        if replay != lexical_method:
            raise ValueError("Baseline output differs from deterministic replay.")
    if not 1 <= len(attempts) <= 2:
        raise ValueError("Supply one candidate attempt, or one diagnosed technical retry.")
    if summary.purpose == "research" and expected_profile is None:
        raise ValueError("Research requires the registered embedding profile.")
    recorded, evidence, seen, final_rows = [], [], set(), ()
    for request in attempts:
        if set(request) - {"embedding_run", "cluster_run", "retry_reason"}:
            raise ValueError("Unknown candidate attempt fields.")
        embed, body = service.inspect(request["embedding_run"])
        _terminal(embed, "embedding", summary.id)
        elapsed = 0 if embed.id in seen else _duration(embed)
        if embed.id in seen and embed.status != "succeeded":
            raise ValueError("A failed embedding cannot be reused as a new attempt.")
        seen.add(embed.id)
        details = {"embedding": asdict(embed), "embedding_result": body}
        error = embed.error
        rows = ()
        if embed.status == "succeeded":
            _embedding(service, embed, body, items, expected_profile)
            if not request.get("cluster_run"):
                raise ValueError("A successful embedding needs its clustering attempt.")
            cluster, result = service.inspect(request["cluster_run"])
            _terminal(cluster, "clustering", summary.id)
            if cluster.id in seen:
                raise ValueError("A clustering invocation cannot be counted twice.")
            seen.add(cluster.id)
            if (
                cluster.request.embedding_run != embed.id
                or cluster.request.embedding_digest != embed.result_digest
                or cluster.request.threshold != 0.85
                or cluster.request.minimum_size != 2
            ):
                raise ValueError("Candidate differs from the pinned embedding or fixed parameters.")
            elapsed += _duration(cluster)
            details.update(clustering=asdict(cluster), clustering_result=result)
            error = cluster.error
            if cluster.status == "succeeded":
                rows = service.files.read_members(result["members_digest"])
                vectors = service.files.read_vectors(body["vectors_digest"])
                expected = cluster_vectors(
                    tuple(i.id for i in items), tuple(r[2] for r in vectors), 0.85, 2
                )
                if result.get("algorithm") != "cosine-components-v1" or rows != expected:
                    raise ValueError(
                        "Candidate membership differs from fixed deterministic replay."
                    )
        elif request.get("cluster_run"):
            raise ValueError("A failed embedding cannot have a clustering output.")
        recorded.append(
            Attempt(
                status="failed" if error else "succeeded",
                elapsed_seconds=elapsed,
                error=error,
                retry_reason=request.get("retry_reason"),
            )
        )
        evidence.append(details)
        final_rows = rows
    result = Comparison(
        purpose=summary.purpose,
        items=items,
        baseline=lexical_method,
        candidate=_method(final_rows, tuple(recorded)),
    )
    return result, {
        "selection_id": summary.id,
        "attempts": evidence,
        "expected_profile": expected_profile,
    }


def _inputs(service, selection_id):
    summary, snapshot = service.selections.read(selection_id)
    items = tuple(
        Item(
            id=item.annotation.id,
            text=interpretation_text(item.interpretation),
            repository=f"{item.source.owner}/{item.source.repository}".casefold(),
        )
        for item in snapshot.records
        if item.exclusion is None
    )
    if not items:
        raise ValueError("Comparison needs eligible inputs.")
    if summary.purpose == "research" and (
        len(items) != 40
        or summary.excluded
        or max(Counter(item.repository for item in items).values()) > 5
    ):
        raise ValueError("Freeze exactly the 40 qualified human-reviewed inputs for research.")
    return summary, items


def _method(rows, attempts):
    groups = []
    for cluster in sorted({row["cluster"] for row in rows if row["cluster"] >= 0}):
        selected = [row for row in rows if row["cluster"] == cluster]
        representatives = [row["annotation_id"] for row in selected if row["representative"]]
        if len(representatives) != 1:
            raise ValueError("Each group requires exactly one representative.")
        groups.append(
            Group(
                members=tuple(row["annotation_id"] for row in selected),
                representative=representatives[0],
            )
        )
    return Method(
        attempts=attempts,
        groups=tuple(groups),
        outliers=tuple(row["annotation_id"] for row in rows if row["cluster"] == -1),
    )


def _terminal(run, kind, selection):
    if (
        run.request.kind != kind
        or run.request.selection_id != selection
        or run.status not in ("succeeded", "failed")
        or (run.status == "failed") != bool(run.error)
    ):
        raise ValueError("Candidate attempt is unfinished or belongs to another input/kind.")


def _duration(run):
    if not run.started_at or not run.completed_at:
        raise ValueError("Attempt lacks execution timestamps; queue time is not execution time.")
    started, completed = (
        datetime.fromisoformat(run.started_at),
        datetime.fromisoformat(run.completed_at),
    )
    if started.tzinfo is None or completed.tzinfo is None or completed < started:
        raise ValueError("Invalid execution timestamps.")
    return (completed - started).total_seconds()


def _embedding(service, run, body, items, profile):
    rows = service.files.read_vectors(body["vectors_digest"])
    if tuple((r[0], r[1]) for r in rows) != tuple((i.id, i.text) for i in items):
        raise ValueError("Vector identities or texts differ from the exact shared inputs.")
    if (
        body.get("preprocessing") != "issue-invariant-categories-v1"
        or body.get("normalisation") != "l2-v1"
        or body.get("text_sha256") != [hashlib.sha256(i.text.encode()).hexdigest() for i in items]
        or body.get("error") is not None
    ):
        raise ValueError("Embedding preprocessing or result status is inconsistent.")
    if profile is not None:
        provenance = body.get("model_provenance", {})
        if (
            provenance.get("profile") != profile
            or provenance.get("model_file_digest_verified") is not True
            or len(rows[0][2]) != profile["dimensions"]
        ):
            raise ValueError("Embedding provenance differs from the pinned profile.")
