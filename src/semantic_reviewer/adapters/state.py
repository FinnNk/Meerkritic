"""Own operational SQLite connections and migrations for metadata repositories."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from yoyo import get_backend, read_migrations


class SQLiteState:
    """Share WAL setup and transaction lifetime without exposing a global connection."""

    def __init__(self, database: Path) -> None:
        """Create or migrate operational storage and enable WAL."""
        self.database = database
        database.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
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
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a row-mapped connection; commit on success, roll back on error, then close."""
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            # A SQLite connection context ends the transaction but does not close the handle.
            connection.close()
