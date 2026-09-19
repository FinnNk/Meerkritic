-- Dataset metadata and append-only operational events.
CREATE TABLE dataset (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    revision TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    parquet_sha256 TEXT NOT NULL,
    row_count INTEGER NOT NULL CHECK (row_count > 0),
    registered_at TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version = 1)
);
CREATE TABLE event (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    subject_id TEXT NOT NULL REFERENCES dataset(id),
    occurred_at TEXT NOT NULL,
    details_json TEXT NOT NULL
);
CREATE TRIGGER event_no_update BEFORE UPDATE ON event
BEGIN SELECT RAISE(ABORT, 'Events are append-only'); END;
CREATE TRIGGER event_no_delete BEFORE DELETE ON event
BEGIN SELECT RAISE(ABORT, 'Events are append-only'); END;
