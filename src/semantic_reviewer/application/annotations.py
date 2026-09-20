"""Validate human decisions against immutable result and source evidence."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol, TypedDict
from uuid import uuid4

from semantic_reviewer.application.artefacts import Publication, ResultStore
from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.application.jobs import Job
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


class JobReader(Protocol):
    """Expose verified job results without revealing queue or storage dependencies."""

    def inspect(self, job_id: str) -> tuple[Job, dict[str, object] | None]:
        """Return metadata and verified body, or None before publication.

        Unknown jobs raise LookupError; corrupt evidence raises ValueError and
        filesystem failures raise OSError. Reading does not change job state.
        """
        ...


class AnnotationProgress(TypedDict):
    """Count one consistent snapshot; source and result denominators remain distinct.

    source_total includes all registered source rows; reviewed_sources counts each
    source once. successful_results counts model runs; reviewed_results includes
    every terminal human decision, including Reject. All counts are non-negative.
    """

    source_total: int
    reviewed_sources: int
    successful_results: int
    reviewed_results: int
    accept: int
    edit: int
    reject: int
    failed: int
    queued: int
    running: int


class AnnotationStore(Protocol):
    """Own atomic decision/event insertion, idempotence and bounded review queries."""

    def record(self, annotation: Annotation) -> Annotation:
        """Atomically insert decision/event or return an identical existing decision.

        Identity/time may differ on retries; all substantive fields must match.
        A conflicting decision raises ValueError and writes neither row nor event.
        """
        ...

    def get(self, job_id: str) -> Annotation | None:
        """Return the terminal decision, if this result has been reviewed."""
        ...

    def by_id(self, annotation_id: str) -> Annotation | None:
        """Return exactly this immutable annotation version, or None when unknown."""
        ...

    def progress(self, dataset_id: str) -> AnnotationProgress:
        """Return coherent source/result counts; raise LookupError for an unknown dataset."""
        ...

    def pending(self, dataset_id: str, page: int) -> tuple[str, ...]:
        """Return up to 20 unreviewed successful IDs in completion-time/ID order.

        page is one-based, at most 1,000,000; invalid bounds raise ValueError.
        Unknown/empty datasets return (). Offset pages can shift after decisions.
        """
        ...

    def history(self, observation_id: str) -> tuple[Annotation, ...]:
        """Return at most 100 decisions in descending creation-time/ID order.

        Include all runs for the source; return () when no decisions exist.
        """
        ...


class AnnotationService:
    """Hide edit validation and evidence publication from UI and command-line callers."""

    def __init__(
        self,
        jobs: JobReader,
        store: AnnotationStore,
        datasets: DatasetService,
        results: ResultStore,
    ) -> None:
        """Bind source/result access and the transactional decision store."""
        self._jobs = jobs
        self.store = store
        self._datasets = datasets
        self._results = results

    def decide(
        self, job_id: str, decision: str, notes: str = "", edited_json: str | None = None
    ) -> Annotation:
        """Immediately persist Accept/Edit/Reject, preserving original model provenance.

        Edits must satisfy the original schema and exact source grounding. Identical
        retries are safe; changing a completed decision requires a future workflow.
        An interrupted database write may leave an unreferenced immutable edit file.

        Args:
            job_id: Successful job whose result is being reviewed.
            decision: Lower-case accept, edit or reject.
            notes: At most 4,000 characters, retained verbatim.
            edited_json: Required only for edit; at most 256,000 UTF-8 bytes.

        Returns:
            The persisted decision, including its original identity/time on a retry.

        Raises:
            LookupError: The job or its source does not exist.
            ValueError: The request, schema, grounding, evidence integrity or decision
                conflicts with the contract. No annotation/event is committed.
            OSError: Evidence access/publication fails. Storage errors propagate;
                an edit file may already exist when decision persistence fails.
        """
        if decision not in ("accept", "edit", "reject") or len(notes) > 4000:
            raise ValueError(
                "Choose Accept, Edit or Reject; notes must be at most 4000 characters."
            )
        if (decision == "edit") != (edited_json is not None):
            raise ValueError("Only Edit requires a replacement interpretation.")
        job, result = self._jobs.inspect(job_id)
        if job.status != "succeeded" or not result or not result.get("interpretation"):
            raise ValueError("Only a successful interpretation can be reviewed.")
        digest = None
        if edited_json is not None:
            if len(edited_json.encode("utf-8")) > 256_000:
                raise ValueError("Edited interpretation is too large.")
            interpretation = IssueInterpretation.model_validate_json(edited_json)
            _, source = self._datasets.observation(job.dataset_id, job.source_index)
            spans = ground(interpretation, source)
            digest = self._results.publish(
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

    def review(self, job_id: str) -> tuple[Annotation | None, dict[str, object] | None]:
        """Read the decision and verified edited body, when present.

        Return (None, None) for an unreviewed or unknown job; this query does not
        establish job existence. Corrupt edited evidence raises ValueError and
        filesystem failures propagate. Reading does not record a decision.
        """
        annotation = self.store.get(job_id)
        edited = (
            self._results.read(annotation.interpretation_sha256)
            if annotation and annotation.interpretation_sha256
            else None
        )
        return annotation, edited
