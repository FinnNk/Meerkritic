-- depends: 012_guidance
-- Semantic eligibility is validated against immutable bodies by AnnotationService.
-- SQLite still fences the exact terminal job/result and same-job edit publication.
DROP TRIGGER annotation_valid_result;
CREATE TRIGGER annotation_valid_result BEFORE INSERT ON annotation
WHEN NOT EXISTS (
    SELECT 1 FROM job j JOIN artefact original ON original.sha256=j.artefact_sha256
    WHERE j.id=NEW.job_id AND j.observation_id=NEW.observation_id
      AND j.artefact_sha256=NEW.result_sha256
      AND original.job_id=j.id AND original.type='normalisation'
      AND (j.status='succeeded' OR (j.status='failed' AND NEW.decision IN ('edit','reject')))
      AND (NEW.decision!='edit' OR EXISTS (
          SELECT 1 FROM artefact edited WHERE edited.sha256=NEW.interpretation_sha256
            AND edited.job_id=j.id AND edited.type='human_edit'))
)
BEGIN SELECT RAISE(ABORT, 'Annotation requires the exact terminal result and edit provenance'); END;
