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


@dataclass(frozen=True)
class Observation:
    """One imported source record, before model interpretation or annotation.

    Attributes:
        id: Source-file SHA-256 followed by a colon and the zero-based record index.
        source_index: Original position; repeated comment IDs retain distinct records.
        comment_id: Upstream identifier, not a unique key for imported observations.
        category: Source-supplied label, not an independently verified judgement.
        subcategory: Source-supplied refinement of the category.
        created_at: Timestamp supplied by the source, preserved as text.
    """

    id: str
    source_index: int
    owner: str
    repository: str
    pull_request: int
    comment_id: int
    file_path: str
    comment: str
    code: str
    category: str
    subcategory: str
    created_at: str


@dataclass(frozen=True)
class ObservationPage:
    """A source-ordered page and the metadata needed to interpret its records.

    Attributes:
        dataset: Registered provenance for every item on the page.
        items: Records on this page; empty when the requested page is beyond the end.
        page: One-based requested page number.
        page_size: Requested maximum item count, not necessarily the returned count.
        total: Total registered record count, not the length of this page.
    """

    dataset: Dataset
    items: tuple[Observation, ...]
    page: int
    page_size: int
    total: int


class DatasetError(ValueError):
    """An invalid or conflicting dataset cannot be registered or queried."""
