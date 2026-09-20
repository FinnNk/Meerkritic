-- depends: 004_annotations
CREATE TABLE artefact (
    sha256 TEXT PRIMARY KEY CHECK (length(sha256)=64),
    job_id TEXT NOT NULL REFERENCES job(id),
    type TEXT NOT NULL CHECK (type IN ('normalisation', 'human_edit', 'job_log')),
    path TEXT NOT NULL,
    size INTEGER NOT NULL CHECK (size>=0),
    created_at TEXT NOT NULL
);
CREATE INDEX artefact_job ON artefact(job_id, type);
CREATE TRIGGER artefact_no_update BEFORE UPDATE ON artefact
BEGIN SELECT RAISE(ABORT, 'Artefact metadata is immutable'); END;
CREATE TRIGGER artefact_no_delete BEFORE DELETE ON artefact
BEGIN SELECT RAISE(ABORT, 'Artefact metadata is retained'); END;
CREATE TABLE job_log (
    job_id TEXT PRIMARY KEY REFERENCES job(id),
    artefact_sha256 TEXT NOT NULL REFERENCES artefact(sha256),
    last_event_id INTEGER NOT NULL
);
