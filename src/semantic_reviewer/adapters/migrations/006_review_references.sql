-- depends: 005_artefacts
CREATE TABLE review_reference (
    pair_id TEXT NOT NULL,
    round_id TEXT NOT NULL,
    sequence INTEGER NOT NULL CHECK (sequence>0),
    stage TEXT NOT NULL,
    diary TEXT NOT NULL,
    semantic TEXT NOT NULL,
    manifest_path TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL,
    event_path TEXT NOT NULL,
    event_sha256 TEXT NOT NULL,
    indexed_at TEXT NOT NULL,
    PRIMARY KEY (pair_id, round_id, sequence)
);
CREATE TRIGGER review_reference_no_update BEFORE UPDATE ON review_reference
BEGIN SELECT RAISE(ABORT, 'Review references are immutable'); END;
CREATE TRIGGER review_reference_no_delete BEFORE DELETE ON review_reference
BEGIN SELECT RAISE(ABORT, 'Review reference history is retained'); END;
