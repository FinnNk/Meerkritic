-- depends: 013_failed_draft_annotations
CREATE TABLE source_context (
    job_id TEXT PRIMARY KEY REFERENCES job(id),
    sha256 TEXT NOT NULL UNIQUE CHECK (length(sha256)=64),
    observation_id TEXT NOT NULL,
    result_sha256 TEXT NOT NULL
);
CREATE TRIGGER source_context_valid BEFORE INSERT ON source_context
WHEN NOT EXISTS (SELECT 1 FROM job WHERE id=NEW.job_id
    AND observation_id=NEW.observation_id AND artefact_sha256=NEW.result_sha256
    AND status IN ('succeeded','failed'))
    OR EXISTS (SELECT 1 FROM annotation WHERE job_id=NEW.job_id)
BEGIN SELECT RAISE(ABORT, 'Source context requires an unreviewed terminal result'); END;
CREATE TRIGGER source_context_no_update BEFORE UPDATE ON source_context
BEGIN SELECT RAISE(ABORT, 'Source context is immutable'); END;
CREATE TRIGGER source_context_no_delete BEFORE DELETE ON source_context
BEGIN SELECT RAISE(ABORT, 'Source context is retained'); END;
ALTER TABLE annotation ADD COLUMN context_sha256 TEXT REFERENCES source_context(sha256);
CREATE TRIGGER annotation_context_valid BEFORE INSERT ON annotation
WHEN NEW.context_sha256 IS NOT (SELECT sha256 FROM source_context WHERE job_id=NEW.job_id)
BEGIN SELECT RAISE(ABORT, 'Annotation must retain the presented source context'); END;
