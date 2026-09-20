-- depends: 007_job_completion
CREATE TABLE annotation_selection (
    id TEXT PRIMARY KEY CHECK (length(id)=64 AND id NOT GLOB '*[^0-9a-f]*'),
    dataset_id TEXT NOT NULL REFERENCES dataset(id),
    purpose TEXT NOT NULL CHECK (purpose IN ('fixture', 'research')),
    included INTEGER NOT NULL CHECK (included>=0),
    excluded INTEGER NOT NULL CHECK (excluded>=0),
    created_at TEXT NOT NULL,
    CHECK (included+excluded BETWEEN 1 AND 100)
);
CREATE TRIGGER selection_no_update BEFORE UPDATE ON annotation_selection
BEGIN SELECT RAISE(ABORT, 'Selections are immutable'); END;
CREATE TRIGGER selection_no_delete BEFORE DELETE ON annotation_selection
BEGIN SELECT RAISE(ABORT, 'Selections retain their event history'); END;
CREATE TRIGGER selection_event_subject BEFORE INSERT ON event
WHEN NEW.kind='selection_frozen' AND NOT EXISTS
    (SELECT 1 FROM annotation_selection WHERE id=NEW.subject_id)
BEGIN SELECT RAISE(ABORT, 'Selection event subject does not exist'); END;
