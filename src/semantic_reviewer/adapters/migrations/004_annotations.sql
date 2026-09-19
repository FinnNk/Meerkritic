-- depends: 003_jobs
CREATE TABLE annotation (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL UNIQUE REFERENCES job(id),
    observation_id TEXT NOT NULL,
    result_sha256 TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('accept', 'edit', 'reject')),
    interpretation_sha256 TEXT,
    notes TEXT NOT NULL CHECK (length(notes) <= 4000),
    created_at TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version=1),
    CHECK ((decision='edit') = (interpretation_sha256 IS NOT NULL))
);
CREATE INDEX annotation_observation ON annotation(observation_id, created_at);
CREATE TRIGGER annotation_valid_result BEFORE INSERT ON annotation
WHEN NOT EXISTS (SELECT 1 FROM job WHERE id=NEW.job_id AND status='succeeded'
    AND observation_id=NEW.observation_id AND artefact_sha256=NEW.result_sha256)
BEGIN SELECT RAISE(ABORT, 'Annotation requires the exact successful result'); END;
CREATE TRIGGER annotation_no_update BEFORE UPDATE ON annotation
BEGIN SELECT RAISE(ABORT, 'Annotations are immutable'); END;
CREATE TRIGGER annotation_no_delete BEFORE DELETE ON annotation
BEGIN SELECT RAISE(ABORT, 'Annotations retain their event history'); END;
CREATE TRIGGER annotation_event_subject BEFORE INSERT ON event
WHEN NEW.kind='annotation_recorded' AND NOT EXISTS
    (SELECT 1 FROM annotation WHERE id=NEW.subject_id)
BEGIN SELECT RAISE(ABORT, 'Annotation event subject does not exist'); END;
