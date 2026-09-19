"""Source identity and read models; no storage or framework types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dataset:
    """Metadata locating immutable imported evidence outside the registry.

    Attributes:
        id: Catalogue identity under which this evidence was registered.
        revision: Pinned upstream revision, not an inferred reviewed-code commit.
        source_sha256: Digest of the original source bytes.
        parquet_sha256: Digest identifying the canonical Parquet artefact.
        row_count: Number of source records, including repeated comments.
        registered_at: UTC ISO 8601 time of the original registration.
        schema_version: Version of the canonical observation schema.
    """

    id: str
    title: str
    revision: str
    source_url: str
    source_sha256: str
    parquet_sha256: str
    row_count: int
    registered_at: str
    schema_version: int = 1


class DatasetError(ValueError):
    """An invalid or conflicting dataset cannot be registered or queried."""
