"""Dataset use cases and their storage contracts."""

from dataclasses import dataclass
from typing import Protocol

from semantic_reviewer.domain.datasets import Dataset, DatasetError


@dataclass(frozen=True)
class PublicDataset:
    """A pinned public source specification, not a registered dataset.

    Attributes:
        id: Stable catalogue key chosen by the project.
        revision: Upstream revision from which the source bytes were obtained.
        source_sha256: Expected SHA-256 of the complete source file.
        expected_rows: Required source-record count, including repeated comments.
    """

    id: str
    title: str
    revision: str
    source_url: str
    source_sha256: str
    expected_rows: int


class DatasetRegistry(Protocol):
    """The operational metadata and atomic registration-event boundary."""

    def register(self, dataset: Dataset) -> Dataset:
        """Register verified metadata and its event as one transaction.

        Args:
            dataset: Metadata for artefacts that have already been published.

        Returns:
            The original metadata on an identical repeat, preserving its registration
            timestamp without appending another event; otherwise the new metadata.

        Raises:
            DatasetError: The ID already refers to different evidence.
        """
        ...

    def list(self) -> tuple[Dataset, ...]:
        """Return registered metadata in dataset-ID order."""
        ...

    def get(self, dataset_id: str) -> Dataset | None:
        """Return registered metadata, or None when the ID is unknown."""
        ...


class ObservationStore(Protocol):
    """Immutable dataset evidence behind application-owned storage contracts."""

    def prepare(self, source: PublicDataset) -> Dataset:
        """Verify pinned source bytes and publish immutable Parquet.

        Args:
            source: Catalogue entry identifying the revision, checksum and row count.

        Returns:
            Metadata ready for registration. Preparation does not write the registry.

        Raises:
            DatasetError: Source size, checksum or records violate the import contract,
                or an existing immutable artefact conflicts with the prepared bytes.
        """
        ...


class DatasetService:
    """Dataset use cases coordinating immutable evidence and metadata.

    Attributes:
        catalogue: Sources available to import; these need not be registered yet.
    """

    def __init__(
        self,
        catalogue: tuple[PublicDataset, ...],
        registry: DatasetRegistry,
        observations: ObservationStore,
    ) -> None:
        """Bind the public catalogue and storage ports without importing data."""
        self.catalogue = catalogue
        self._registry = registry
        self._observations = observations

    def register(self, dataset_id: str) -> Dataset:
        """Verify and register a source from the public catalogue.

        Preparation may download data and publish files before metadata is committed.
        A repeat verifies the local artefact and retains the original registration;
        it does not append another registration event. Failed registration may leave
        unreferenced, complete artefacts.

        Args:
            dataset_id: Catalogue identifier to import.

        Returns:
            Registered metadata with source and Parquet identities.

        Raises:
            DatasetError: The ID is unknown, evidence fails validation, or registration
                conflicts with existing content.
            OSError: Download or filesystem access fails.
        """
        source = next((item for item in self.catalogue if item.id == dataset_id), None)
        if source is None:
            raise DatasetError("Unknown public dataset; choose an ID from the catalogue.")
        # Publish verified artefacts before metadata can make them discoverable.
        # Repeated registration still checks the bytes already on disk.
        return self._registry.register(self._observations.prepare(source))

    def datasets(self) -> tuple[Dataset, ...]:
        """List registered metadata without loading observation bodies."""
        return self._registry.list()
