"""Validate bounded vectors and apply a deterministic exploratory grouping method."""

import math


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
