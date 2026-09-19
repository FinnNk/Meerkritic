"""Small operational records with migrations and short SQLite transactions."""

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from yoyo import get_backend, read_migrations

from semantic_reviewer.domain.datasets import Dataset, DatasetError


class SQLiteRegistry:
    """SQLite-backed metadata and append-only events with short transactions."""

    def __init__(self, database: Path) -> None:
        """Create or migrate the registry and enable WAL before accepting operations."""
        self.database = database
        database.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
        backend = get_backend("sqlite:///" + database.resolve().as_posix())
        try:
            with backend.lock():
                backend.apply_migrations(
                    backend.to_apply(read_migrations(str(Path(__file__).parent / "migrations")))
                )
        finally:
            backend.connection.close()

    @contextmanager
    def _connect(self):
        """Provide a connection whose transaction ends with the context.

        Returns:
            A context manager yielding a row-mapped SQLite connection. Successful exit
            commits, exceptional exit rolls back, and either exit closes the handle.
        """
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            # The SQLite context manager ends the transaction but does not close the handle.
            connection.close()

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
        with self._connect() as connection:
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
        with self._connect() as connection:
            return tuple(
                Dataset(**dict(row))
                for row in connection.execute("SELECT * FROM dataset ORDER BY id").fetchall()
            )

    def get(self, dataset_id: str) -> Dataset | None:
        """Return registered metadata, or None if the ID has not been registered."""
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM dataset WHERE id=?", (dataset_id,)).fetchone()
            return Dataset(**dict(row)) if row else None
