"""Validate human decisions against immutable result and source evidence."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import uuid4

from semantic_reviewer.application.artefacts import Publication
from semantic_reviewer.application.jobs import JobService
from semantic_reviewer.domain.normalisation import IssueInterpretation, ground


@dataclass(frozen=True)
class Annotation:
    """Retain one terminal decision for one result; bodies remain in artefact storage."""

    id: str
    job_id: str
    observation_id: str
    result_sha256: str
    decision: Literal["accept", "edit", "reject"]
    interpretation_sha256: str | None
    notes: str
    created_at: str
    schema_version: int = 1


class AnnotationStore(Protocol):
    """Own atomic decision/event insertion, idempotence and bounded review queries."""

    def record(self, annotation: Annotation) -> Annotation:
        """Return an identical existing decision or reject a conflicting submission."""
        ...

    def get(self, job_id: str) -> Annotation | None:
        """Return the terminal decision, if this result has been reviewed."""
        ...

    def progress(self, dataset_id: str) -> dict:
        """Count result decisions and distinct reviewed sources independently."""
        ...

    def pending(self, dataset_id: str, page: int) -> tuple[str, ...]:
        """Return a page of at most 20 successful, unreviewed result identities."""
        ...

    def history(self, observation_id: str) -> tuple[Annotation, ...]:
        """Return at most the latest 100 decisions for a source across model runs."""
        ...


class AnnotationService:
    """Hide edit validation and evidence publication from UI and command-line callers."""

    def __init__(self, jobs: JobService, store: AnnotationStore) -> None:
        """Bind source/result access and the transactional decision store."""
        self.jobs = jobs
        self.store = store

    def decide(
        self, job_id: str, decision: str, notes: str = "", edited_json: str | None = None
    ) -> Annotation:
        """Immediately persist Accept/Edit/Reject, preserving original model provenance.

        Edits must satisfy the original schema and exact source grounding. Identical
        retries are safe; changing a completed decision requires a future workflow.
        An interrupted database write may leave an unreferenced immutable edit file.
        """
        if decision not in ("accept", "edit", "reject") or len(notes) > 4000:
            raise ValueError(
                "Choose Accept, Edit or Reject; notes must be at most 4000 characters."
            )
        if (decision == "edit") != (edited_json is not None):
            raise ValueError("Only Edit requires a replacement interpretation.")
        job, result = self.jobs.inspect(job_id)
        if job.status != "succeeded" or not result or not result.get("interpretation"):
            raise ValueError("Only a successful interpretation can be reviewed.")
        digest = None
        if edited_json is not None:
            if len(edited_json.encode("utf-8")) > 256_000:
                raise ValueError("Edited interpretation is too large.")
            interpretation = IssueInterpretation.model_validate_json(edited_json)
            source = self.jobs.datasets.browse(job.dataset_id, job.source_index + 1, 1).items[0]
            spans = ground(interpretation, source)
            digest = self.jobs.results.publish(
                {
                    "schema_version": 1,
                    "job_id": job.id,
                    "original_result_sha256": job.artefact_sha256,
                    "observation_id": job.observation_id,
                    "interpretation": interpretation.model_dump(mode="json"),
                    "evidence_spans": [asdict(span) for span in spans],
                },
                Publication(job.id, "human_edit"),
            )
        return self.store.record(
            Annotation(
                str(uuid4()),
                job.id,
                job.observation_id,
                job.artefact_sha256,
                decision,
                digest,
                notes,
                datetime.now(UTC).isoformat(),
            )
        )

    def review(self, job_id: str) -> tuple[Annotation | None, dict | None]:
        """Read the decision and verified edited body, when present."""
        annotation = self.store.get(job_id)
        edited = (
            self.jobs.results.read(annotation.interpretation_sha256)
            if annotation and annotation.interpretation_sha256
            else None
        )
        return annotation, edited
