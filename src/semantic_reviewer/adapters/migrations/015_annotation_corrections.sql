-- depends: 014_source_context
-- Originals remain untouched. Corrections are immutable versions of the same result.
CREATE TABLE annotation_correction (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES job(id),
    observation_id TEXT NOT NULL,
    result_sha256 TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision='edit'),
    interpretation_sha256 TEXT NOT NULL,
    notes TEXT NOT NULL CHECK (length(notes)<=4000),
    created_at TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version=1),
    context_sha256 TEXT REFERENCES source_context(sha256),
    supersedes_id TEXT NOT NULL UNIQUE,
    reason TEXT NOT NULL CHECK (length(trim(reason)) BETWEEN 1 AND 4000),
    curator TEXT NOT NULL CHECK (length(trim(curator)) BETWEEN 1 AND 200)
);
CREATE VIEW annotation_version AS
    SELECT * FROM annotation
    UNION ALL
    SELECT id, job_id, observation_id, result_sha256, decision,
        interpretation_sha256, notes, created_at, schema_version, context_sha256
    FROM annotation_correction;
CREATE VIEW current_annotation AS
    SELECT v.* FROM annotation_version v WHERE NOT EXISTS
        (SELECT 1 FROM annotation_correction c WHERE c.supersedes_id=v.id);
CREATE TRIGGER correction_valid BEFORE INSERT ON annotation_correction
WHEN EXISTS (SELECT 1 FROM annotation_version WHERE id=NEW.id)
    OR NOT EXISTS (
        SELECT 1 FROM current_annotation a
        JOIN artefact edited ON edited.sha256=NEW.interpretation_sha256
        WHERE a.id=NEW.supersedes_id AND a.job_id=NEW.job_id
          AND a.observation_id=NEW.observation_id AND a.result_sha256=NEW.result_sha256
          AND a.context_sha256 IS NEW.context_sha256
          AND edited.job_id=a.job_id AND edited.type='human_edit'
    )
BEGIN SELECT RAISE(ABORT, 'Correction requires the current version and same-result provenance'); END;
CREATE TRIGGER correction_no_update BEFORE UPDATE ON annotation_correction
BEGIN SELECT RAISE(ABORT, 'Corrections are immutable'); END;
CREATE TRIGGER correction_no_delete BEFORE DELETE ON annotation_correction
BEGIN SELECT RAISE(ABORT, 'Corrections retain their event history'); END;
CREATE TRIGGER correction_event_subject BEFORE INSERT ON event
WHEN NEW.kind='annotation_corrected' AND NOT EXISTS
    (SELECT 1 FROM annotation_correction WHERE id=NEW.subject_id)
BEGIN SELECT RAISE(ABORT, 'Correction event subject does not exist'); END;
