-- depends: 001_registry
-- Versioned configuration is small operational metadata, never prompt or dataset bodies.
CREATE TABLE routing_version (
    kind TEXT NOT NULL CHECK (kind IN ('inventory', 'policy', 'prices')),
    id TEXT NOT NULL,
    version TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (kind, id, version)
);
CREATE TABLE routing_decision (
    id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL
);
CREATE TABLE model_usage (
    id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL UNIQUE REFERENCES routing_decision(id),
    payload_json TEXT NOT NULL
);
CREATE TRIGGER routing_version_no_update BEFORE UPDATE ON routing_version
BEGIN SELECT RAISE(ABORT, 'Routing versions are immutable'); END;
CREATE TRIGGER routing_version_no_delete BEFORE DELETE ON routing_version
BEGIN SELECT RAISE(ABORT, 'Routing versions are immutable'); END;
CREATE TRIGGER routing_decision_no_update BEFORE UPDATE ON routing_decision
BEGIN SELECT RAISE(ABORT, 'Routing decisions are immutable'); END;
CREATE TRIGGER routing_decision_no_delete BEFORE DELETE ON routing_decision
BEGIN SELECT RAISE(ABORT, 'Routing decisions are immutable'); END;
CREATE TRIGGER model_usage_no_update BEFORE UPDATE ON model_usage
BEGIN SELECT RAISE(ABORT, 'Completed usage is immutable'); END;
CREATE TRIGGER model_usage_no_delete BEFORE DELETE ON model_usage
BEGIN SELECT RAISE(ABORT, 'Completed usage is immutable'); END;

-- Existing event identities/content survive; subjects now include routing and usage.
CREATE TABLE event_expanded (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    details_json TEXT NOT NULL
);
INSERT INTO event_expanded SELECT * FROM event;
DROP TABLE event;
ALTER TABLE event_expanded RENAME TO event;
CREATE TRIGGER event_no_update BEFORE UPDATE ON event
BEGIN SELECT RAISE(ABORT, 'Events are append-only'); END;
CREATE TRIGGER event_no_delete BEFORE DELETE ON event
BEGIN SELECT RAISE(ABORT, 'Events are append-only'); END;
CREATE TRIGGER event_valid_subject BEFORE INSERT ON event
WHEN (NEW.kind = 'dataset_registered' AND NOT EXISTS (SELECT 1 FROM dataset WHERE id=NEW.subject_id))
  OR (NEW.kind = 'routing_decision_recorded' AND NOT EXISTS (SELECT 1 FROM routing_decision WHERE id=NEW.subject_id))
  OR (NEW.kind = 'model_usage_recorded' AND NOT EXISTS (SELECT 1 FROM model_usage WHERE id=NEW.subject_id))
BEGIN SELECT RAISE(ABORT, 'Event subject does not exist'); END;
-- Retain the old FK's restriction on deleting/renaming a referenced dataset.
CREATE TRIGGER dataset_event_no_delete BEFORE DELETE ON dataset
WHEN EXISTS (SELECT 1 FROM event WHERE kind='dataset_registered' AND subject_id=OLD.id)
BEGIN SELECT RAISE(ABORT, 'Dataset is referenced by history'); END;
CREATE TRIGGER dataset_event_no_rename BEFORE UPDATE OF id ON dataset
WHEN NEW.id != OLD.id AND EXISTS (
    SELECT 1 FROM event WHERE kind='dataset_registered' AND subject_id=OLD.id
)
BEGIN SELECT RAISE(ABORT, 'Dataset is referenced by history'); END;
