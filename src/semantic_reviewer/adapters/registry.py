"""Small operational records with migrations and short SQLite transactions."""

import json
from dataclasses import asdict
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.domain.datasets import Dataset, DatasetError


class SQLiteRegistry:
    """SQLite-backed metadata and append-only events with short transactions."""

    def __init__(self, database: Path) -> None:
        """Create or migrate the registry and enable WAL before accepting operations."""
        self.database = database
        self.state = SQLiteState(database)

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
        with self.state.connect() as connection:
            # Serialise identity comparison and insertion so concurrent imports cannot race.
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM dataset WHERE id=?", (dataset.id,)).fetchone()
            if row:
                existing = Dataset(**dict(row))
                old, new = asdict(existing), asdict(dataset)
                # Re-import time is not part of evidence identity; retain the original timestamp.
                old.pop("registered_at")
                new.pop("registered_at")
                if old != new:
                    raise DatasetError("Dataset identity already refers to different content.")
                return existing
            connection.execute(
                "INSERT INTO dataset VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(asdict(dataset).values()),
            )
            connection.execute(
                "INSERT INTO event(kind, subject_id, occurred_at, details_json) "
                "VALUES (?, ?, ?, ?)",
                (
                    "dataset_registered",
                    dataset.id,
                    dataset.registered_at,
                    json.dumps({"source_sha256": dataset.source_sha256, "schema_version": 1}),
                ),
            )
            return dataset

    def list(self) -> tuple[Dataset, ...]:
        """Return registered metadata ordered by dataset ID."""
        with self.state.connect() as connection:
            return tuple(
                Dataset(**dict(row))
                for row in connection.execute("SELECT * FROM dataset ORDER BY id").fetchall()
            )

    def get(self, dataset_id: str) -> Dataset | None:
        """Return registered metadata, or None if the ID has not been registered."""
        with self.state.connect() as connection:
            row = connection.execute("SELECT * FROM dataset WHERE id=?", (dataset_id,)).fetchone()
            return Dataset(**dict(row)) if row else None
