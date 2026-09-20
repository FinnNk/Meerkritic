-- depends: 006_review_references
-- Preserve historical records; reject contradictory terminal metadata on new writes.
CREATE TRIGGER job_completion_insert BEFORE INSERT ON job
WHEN (NEW.status='succeeded' AND (NEW.artefact_sha256 IS NULL
    OR length(NEW.artefact_sha256)!=64 OR NEW.artefact_sha256 GLOB '*[^0-9a-f]*'
    OR NEW.error IS NOT NULL))
    OR (NEW.status='failed' AND (NEW.error IS NULL
    OR length(trim(NEW.error, ' ' || char(9) || char(10) || char(13)))=0))
BEGIN SELECT RAISE(ABORT, 'Invalid job completion'); END;
CREATE TRIGGER job_completion_update BEFORE UPDATE ON job
WHEN (NEW.status='succeeded' AND (NEW.artefact_sha256 IS NULL
    OR length(NEW.artefact_sha256)!=64 OR NEW.artefact_sha256 GLOB '*[^0-9a-f]*'
    OR NEW.error IS NOT NULL))
    OR (NEW.status='failed' AND (NEW.error IS NULL
    OR length(trim(NEW.error, ' ' || char(9) || char(10) || char(13)))=0))
BEGIN SELECT RAISE(ABORT, 'Invalid job completion'); END;
