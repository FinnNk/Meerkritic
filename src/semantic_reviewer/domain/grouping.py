"""Validate bounded vectors and apply a deterministic exploratory grouping method."""

import math
import re
from fractions import Fraction

from semantic_reviewer.domain.normalisation import IssueInterpretation


def interpretation_text(value: IssueInterpretation) -> str:
    """Build the shared issue/invariant/category text without source taxonomy labels.

    This is the versioned issue-invariant-categories-v1 representation. Preserve
    empty invariant lines and category order so both methods consume identical text.
    """
    return "\n".join(
        (value.issue_statement, value.proposed_invariant or "", ", ".join(value.coarse_categories))
    )


def cluster_texts(ids: tuple[str, ...], texts: tuple[str, ...]) -> tuple[dict, ...]:
    """Apply the fixed EDR lexical baseline, including empty-token outliers.

    Use ASCII token sets after case-folding, Jaccard >= 1/4, connected components
    of at least two members and summed-similarity representatives. No fitting or
    stop-word removal occurs. Reject misaligned, duplicate or oversized inputs.
    """
    if (
        not 1 <= len(ids) <= 100
        or len(ids) != len(texts)
        or len(set(ids)) != len(ids)
        or any(not isinstance(i, str) or not i.strip() for i in ids)
        or any(not isinstance(t, str) or len(t) > 12000 for t in texts)
    ):
        raise ValueError("Lexical inputs must be unique, aligned and bounded.")
    tokens = [set(re.findall(r"[a-z0-9]+", text.casefold())) for text in texts]
    similarities = [
        [Fraction(len(a & b), len(a | b)) if a | b else Fraction(0) for b in tokens] for a in tokens
    ]
    return _components(ids, similarities, Fraction(1, 4), 2)


def validate_vectors(vectors: tuple, count: int) -> tuple[tuple[float, ...], ...]:
    """Require finite rectangular non-zero vectors; return deterministic unit vectors."""
    if len(vectors) != count or not 1 <= count <= 100:
        raise ValueError("Embedding row count differs from the selected inputs.")
    dimension = len(vectors[0])
    if not 1 <= dimension <= 4096:
        raise ValueError("Embedding dimensions are outside the supported range.")
    result = []
    for row in vectors:
        if len(row) != dimension or any(
            isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
            for x in row
        ):
            raise ValueError("Embedding shape or finite-number contract failed.")
        norm = math.sqrt(sum(x * x for x in row))
        if not math.isfinite(norm) or norm == 0:
            raise ValueError("Embedding norm is zero or non-finite.")
        result.append(tuple(x / norm for x in row))
    return tuple(result)


def cluster_vectors(ids: tuple[str, ...], vectors: tuple, threshold: float, minimum: int) -> tuple:
    """Prototype cosine connected components; stable medoids, explicit small-group outliers.

    Edges are inclusive at threshold. Transitive chaining is intentional and does
    not assert semantic coherence. Seed is not used. Ties follow frozen input order.
    """
    vectors = validate_vectors(vectors, len(ids))
    if len(set(ids)) != len(ids) or not -1 <= threshold <= 1 or not 2 <= minimum <= 100:
        raise ValueError("Invalid clustering identities or parameters.")
    similarities = [
        [sum(a * b for a, b in zip(x, y, strict=True)) for y in vectors] for x in vectors
    ]
    return _components(ids, similarities, threshold, minimum)


def _components(ids, similarities, threshold, minimum):
    remaining = set(range(len(ids)))
    result = []
    group = 0
    while remaining:
        component = {min(remaining)}
        frontier = list(component)
        remaining -= component
        while frontier:
            index = frontier.pop()
            neighbours = {j for j in remaining if similarities[index][j] >= threshold}
            remaining -= neighbours
            component |= neighbours
            frontier.extend(sorted(neighbours))
        ordered = sorted(component)
        eligible = len(ordered) >= minimum
        representative = max(ordered, key=lambda i: (sum(similarities[i][j] for j in ordered), -i))
        for i in ordered:
            result.append(
                {
                    "annotation_id": ids[i],
                    "cluster": group if eligible else -1,
                    "representative": eligible and i == representative,
                }
            )
        group += int(eligible)
    return tuple(sorted(result, key=lambda row: ids.index(row["annotation_id"])))
