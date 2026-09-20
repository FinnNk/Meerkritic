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
