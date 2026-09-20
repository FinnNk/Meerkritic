-- depends: 008_selections
CREATE TABLE discovery_run (
    id TEXT PRIMARY KEY,
    request_json TEXT NOT NULL CHECK(length(request_json)<4096),
    status TEXT NOT NULL CHECK(status IN ('queued','running','succeeded','failed')),
    queued_at TEXT NOT NULL,
    worker_id TEXT,
    decision_id TEXT REFERENCES routing_decision(id),
    result_digest TEXT CHECK(result_digest IS NULL OR
        (length(result_digest)=64 AND result_digest NOT GLOB '*[^0-9a-f]*')),
    error TEXT,
    started_at TEXT,
    completed_at TEXT,
    CHECK(status!='succeeded' OR (result_digest IS NOT NULL AND error IS NULL)),
    CHECK(status!='failed' OR (error IS NOT NULL AND length(trim(error, char(9)||char(10)||char(13)||' '))>0)),
    CHECK(status NOT IN ('succeeded','failed') OR completed_at IS NOT NULL)
);
CREATE TRIGGER discovery_identity BEFORE UPDATE ON discovery_run
WHEN NEW.id!=OLD.id OR NEW.request_json!=OLD.request_json OR NEW.queued_at!=OLD.queued_at
    OR OLD.status IN ('succeeded','failed')
BEGIN SELECT RAISE(ABORT, 'Discovery identity and terminal state are immutable'); END;
CREATE TRIGGER discovery_no_delete BEFORE DELETE ON discovery_run
BEGIN SELECT RAISE(ABORT, 'Discovery retains event history'); END;
