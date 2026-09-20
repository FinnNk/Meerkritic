-- depends: 011_review_workspace
CREATE TABLE guidance_batch (
    id TEXT PRIMARY KEY,
    request_digest TEXT NOT NULL CHECK(length(request_digest)=64),
    status TEXT NOT NULL CHECK(status IN ('queued','running','responded','failed','unknown')),
    queued_at TEXT NOT NULL,
    worker_id TEXT,
    decision_id TEXT REFERENCES routing_decision(id),
    result_digest TEXT CHECK(result_digest IS NULL OR length(result_digest)=64),
    error TEXT,
    completed_at TEXT,
    CHECK(status<>'responded' OR (result_digest IS NOT NULL AND error IS NULL)),
    CHECK(status NOT IN ('failed','unknown') OR
        (error IS NOT NULL AND length(trim(error,char(9)||char(10)||char(13)||' '))>0))
);
CREATE TRIGGER guidance_request_immutable BEFORE UPDATE OF id,request_digest,queued_at ON guidance_batch
BEGIN SELECT RAISE(ABORT,'Guidance submissions are immutable'); END;
CREATE TRIGGER guidance_terminal BEFORE UPDATE ON guidance_batch
WHEN OLD.status IN ('responded','failed','unknown')
BEGIN SELECT RAISE(ABORT,'Guidance completion is immutable'); END;
CREATE TRIGGER guidance_no_delete BEFORE DELETE ON guidance_batch
BEGIN SELECT RAISE(ABORT,'Guidance submissions retain history'); END;
