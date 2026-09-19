-- depends: 002_routing
CREATE TABLE job (
    id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES dataset(id),
    source_index INTEGER NOT NULL CHECK (source_index >= 0),
    observation_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    queued_at TEXT NOT NULL,
    started_at TEXT,
    heartbeat_at TEXT,
    completed_at TEXT,
    worker_id TEXT,
    decision_id TEXT REFERENCES routing_decision(id),
    artefact_sha256 TEXT,
    error TEXT
);
CREATE INDEX job_queue ON job(status, queued_at);
CREATE UNIQUE INDEX job_single_running ON job(status) WHERE status='running';
CREATE TRIGGER job_no_delete BEFORE DELETE ON job
BEGIN SELECT RAISE(ABORT, 'Jobs retain their event history'); END;
CREATE TRIGGER job_final_no_update BEFORE UPDATE ON job WHEN OLD.status IN ('succeeded', 'failed')
BEGIN SELECT RAISE(ABORT, 'Completed jobs are immutable'); END;
CREATE TRIGGER job_event_subject BEFORE INSERT ON event
WHEN NEW.kind LIKE 'job_%' AND NOT EXISTS (SELECT 1 FROM job WHERE id=NEW.subject_id)
BEGIN SELECT RAISE(ABORT, 'Job event subject does not exist'); END;
