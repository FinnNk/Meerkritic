"""Validate human decisions against immutable result and source evidence."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol, TypedDict
from uuid import uuid4

from semantic_reviewer.application.artefacts import Publication, ResultStore
from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.application.jobs import Job
from semantic_reviewer.application.reading import ReadingContext, SourceReader
from semantic_reviewer.domain.normalisation import IssueInterpretation, ground


@dataclass(frozen=True)
class Annotation:
    """Retain one immutable decision version; bodies remain in artefact storage."""

    id: str
    job_id: str
    observation_id: str
    result_sha256: str
    decision: Literal["accept", "edit", "reject"]
    interpretation_sha256: str | None
    notes: str
    created_at: str
    schema_version: int = 1
    context_sha256: str | None = None


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
    every terminal human decision, including Reject and corrected failures.
    reviewed_successful_results and reviewed_failed_results separate the original
    execution outcomes. A human edit never increases model successes. All counts are non-negative.
    """

    source_total: int
    reviewed_sources: int
    successful_results: int
    reviewed_results: int
    reviewed_successful_results: int
    reviewed_failed_results: int
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

        The caller verifies body eligibility via review_actions and source grounding.
        Storage fences terminal result and same-job edit identity.
        Identity/time may differ on retries; all substantive fields must match.
        A conflicting decision raises ValueError and writes neither row nor event.
        """
        ...

    def get(self, job_id: str) -> Annotation | None:
        """Return the current decision, if this result has been reviewed."""
        ...

    def correct(
        self, annotation: Annotation, supersedes_id: str, reason: str, curator: str
    ) -> Annotation:
        """Append a same-result Edit and event, fenced by the current version ID.

        Preserve all earlier versions. Replay identical requests without an event;
        reject stale/conflicting requests with ValueError. Reason and curator are
        retained claims, not authentication. The service validates and grounds edits.
        """
        ...

    def by_id(self, annotation_id: str) -> Annotation | None:
        """Return exactly this immutable annotation version, or None when unknown."""
        ...

    def progress(self, dataset_id: str) -> AnnotationProgress:
        """Return coherent source/result counts; raise LookupError for an unknown dataset."""
        ...

    def pending(self, dataset_id: str, page: int) -> tuple[str, ...]:
        """Return up to 20 unreviewed successful or published failed job IDs.

        Completion-time/ID order is for general inspection, not study sampling.
        A published failure may be ineligible for correction; inspect its evidence.

        page is one-based, at most 1,000,000; invalid bounds raise ValueError.
        Unknown/empty datasets return (). Offset pages can shift after decisions.
        """
        ...

    def history(self, observation_id: str) -> tuple[Annotation, ...]:
        """Return at most 100 decisions in descending creation-time/ID order.

        Include all runs for the source; return () when no decisions exist.
        """
        ...


def review_actions(job: Job, result: dict | None) -> tuple[str, ...]:
    """Return admissible decisions without trusting a caller's claimed job status.

    A successful interpretation supports Accept/Edit/Reject. A retained semantic
    failure supports only Edit/Reject; provider and interrupted failures do not.
    The caller must first verify the result bytes against the job's artefact hash.
    No action changes the original execution outcome. Malformed evidence fails closed.
    """
    if not job.artefact_sha256 or not isinstance(result, dict):
        return ()
    # Older successful bodies omit job_id; their verified job hash and catalogue
    # retain ownership. An explicitly conflicting identity is never compatible.
    if (
        job.status == "succeeded"
        and result.get("job_id", job.id) == job.id
        and isinstance(result.get("interpretation"), dict)
    ):
        return ("accept", "edit", "reject")
    usage = result.get("usage")
    measurement = usage.get("measurement") if isinstance(usage, dict) else None
    output = result.get("model_output")
    if (
        job.status == "failed"
        and result.get("job_id") == job.id
        and job.error
        and result.get("error") == job.error
        and result.get("interpretation") is None
        and isinstance(measurement, dict)
        and measurement.get("outcome") == "semantic_failure"
        and isinstance(output, str)
        and output.strip()
        and len(output.encode("utf-8")) <= 256_000
    ):
        return ("edit", "reject")
    return ()


class AnnotationService:
    """Hide edit validation and evidence publication from UI and command-line callers."""

    def __init__(
        self,
        jobs: JobReader,
        store: AnnotationStore,
        datasets: DatasetService,
        results: ResultStore,
        sources: SourceReader | None = None,
    ) -> None:
        """Bind source/result access and the transactional decision store."""
        self._jobs = jobs
        self.store = store
        self._datasets = datasets
        self._results = results
        self._sources = sources

    def reading_context(self, job_id: str) -> ReadingContext | None:
        """Read verified additional human context without fetching or changing evidence."""
        context = self._sources.read(job_id) if self._sources else None
        if context:
            job, _ = self._jobs.inspect(job_id)
            if (context.job_id, context.observation_id) != (job.id, job.observation_id):
                raise ValueError("Preserved source does not belong to this assessment.")
        return context

    def decide(
        self,
        job_id: str,
        decision: str,
        notes: str = "",
        edited_json: str | None = None,
        *,
        context_sha256: str | None = None,
    ) -> Annotation:
        """Immediately persist Accept/Edit/Reject, preserving original model provenance.

        Edits must satisfy the current compatible schema and exact source grounding. Identical
        retries are safe; changing a completed decision requires explicit correction.
        An interrupted database write may leave an unreferenced immutable edit file.

        Args:
            job_id: Successful interpretation or retained semantic-failure draft.
            decision: Lower-case accept, edit or reject.
            notes: At most 4,000 characters, retained verbatim.
            edited_json: Required only for edit; at most 256,000 UTF-8 bytes.
            context_sha256: Additional source identity presented by this form, or
                None when none was presented. Must match the current attachment.

        Returns:
            The persisted decision, including its original identity/time on a retry.

        Raises:
            LookupError: The job or its source does not exist.
            ValueError: The request, schema, grounding, evidence integrity or decision
                conflicts with the contract. No annotation/event is committed.
            OSError: Evidence access/publication fails. Storage errors propagate;
                an edit file may already exist when decision persistence fails.
        """
        return self.store.record(
            self._prepare(job_id, decision, notes, edited_json, context_sha256)
        )

    def correct(
        self,
        supersedes_id: str,
        edited_json: str,
        notes: str,
        *,
        reason: str,
        curator: str,
    ) -> Annotation:
        """Record an explicitly approved replacement without erasing the original.

        Name the exact current annotation and provide the complete approved edit and
        notes. Preserve its model/source context; never run a model. Identical retries
        return the original correction. Unknown IDs raise LookupError; stale versions,
        invalid provenance/grounding and empty reason/curator raise ValueError.
        Curator identifies responsibility, not an authenticated human submission.
        """
        if not reason.strip() or len(reason) > 4000 or not curator.strip() or len(curator) > 200:
            raise ValueError("Provide a reason (1–4000 characters) and curator (1–200 characters).")
        previous = self.store.by_id(supersedes_id)
        if previous is None:
            raise LookupError("Annotation does not exist.")
        replacement = self._prepare(
            previous.job_id, "edit", notes, edited_json, previous.context_sha256
        )
        return self.store.correct(replacement, supersedes_id, reason, curator)

    def _prepare(
        self,
        job_id: str,
        decision: str,
        notes: str,
        edited_json: str | None,
        context_sha256: str | None,
    ) -> Annotation:
        # Both initial decisions and corrections share eligibility, context and
        # grounding checks. Only the transactional storage operation differs.
        if decision not in ("accept", "edit", "reject") or len(notes) > 4000:
            raise ValueError(
                "Choose Accept, Edit or Reject; notes must be at most 4000 characters."
            )
        if (decision == "edit") != (edited_json is not None):
            raise ValueError("Only Edit requires a replacement interpretation.")
        job, result = self._jobs.inspect(job_id)
        context = self.reading_context(job_id)
        if context_sha256 != (context.sha256 if context else None):
            raise ValueError(
                "Source context changed since this form opened. Keep your edits, "
                "reload the assessment and review both source views before saving."
            )
        if decision not in review_actions(job, result):
            raise ValueError(
                "This result does not support that decision. Failed drafts require Edit or Reject."
            )
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
        return Annotation(
            str(uuid4()),
            job.id,
            job.observation_id,
            job.artefact_sha256,
            decision,
            digest,
            notes,
            datetime.now(UTC).isoformat(),
            context_sha256=context_sha256,
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
