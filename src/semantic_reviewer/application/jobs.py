"""Coordinate durable normalisation jobs without web, framework or storage types."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from threading import Event, Thread
from typing import Literal, Protocol
from uuid import uuid4

from semantic_reviewer.application.artefacts import ArtefactMetadata, Publication, ResultStore
from semantic_reviewer.application.datasets import DatasetService
from semantic_reviewer.application.normalisation import NormalisationInput, WorkflowRunner
from semantic_reviewer.application.routing import RoutingJournal, RoutingService
from semantic_reviewer.routing.selection import TaskRequirements
from semantic_reviewer.routing.usage import usage_summary


@dataclass(frozen=True)
class Job:
    """Keep small operational metadata separate from immutable result bodies."""

    id: str
    dataset_id: str
    source_index: int
    observation_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    queued_at: str
    started_at: str | None = None
    heartbeat_at: str | None = None
    completed_at: str | None = None
    worker_id: str | None = None
    decision_id: str | None = None
    artefact_sha256: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.status not in ("queued", "running", "succeeded", "failed"):
            raise ValueError("Unknown job state.")
        if self.status == "succeeded" and (not self.artefact_sha256 or self.error is not None):
            raise ValueError("Successful jobs require an artefact and no error.")
        if self.status == "failed" and (not self.error or not self.error.strip()):
            raise ValueError("Failed jobs require an explanation.")

    @property
    def stale(self) -> bool:
        """Flag a late heartbeat for inspection without assuming that the worker is dead."""
        return (
            self.status == "running"
            and self.heartbeat_at is not None
            and (datetime.now(UTC) - datetime.fromisoformat(self.heartbeat_at)).total_seconds() > 60
        )


class JobStore(Protocol):
    """Own atomic queue transitions and events; calls never hold a transaction during inference."""

    def enqueue(self, job: Job) -> Job:
        """Insert a new job and its event atomically."""
        ...

    def get(self, job_id: str) -> Job | None:
        """Read current metadata, returning None for an unknown identity."""
        ...

    def recent(self) -> tuple[Job, ...]:
        """Read at most the latest 100 jobs in reverse queue order."""
        ...

    def log(self, job_id: str) -> ArtefactMetadata:
        """Export a structured snapshot of committed events and return artefact metadata."""
        ...

    def claim(self, worker_id: str) -> Job | None:
        """Atomically claim the oldest queued job, only when no job is running."""
        ...

    def heartbeat(self, job: Job) -> None:
        """Refresh liveness only for this job's current worker ownership."""
        ...

    def bind_route(self, job: Job, decision_id: str) -> None:
        """Associate a persisted route before inference; reject lost ownership."""
        ...

    def finish(self, job: Job, digest: str | None, error: str | None) -> None:
        """Commit completion and event atomically, fencing old workers.

        error=None means success and requires a lower-case SHA-256 digest. Failure
        requires a non-blank error and may retain a digest. Invalid combinations
        and lost ownership raise ValueError without changing state or events.
        """
        ...

    def recover_interrupted(self) -> int:
        """Fail unfinished work after the caller obtains the exclusive process lock.

        Never call on the basis of heartbeat age alone. Do not retry uncertain calls.
        """
        ...


class JobService:
    """Bridge source evidence, routing, execution and persisted outcomes."""

    def __init__(
        self,
        datasets: DatasetService,
        jobs: JobStore,
        results: ResultStore,
        journal: RoutingJournal | None = None,
    ) -> None:
        """Bind read/queue dependencies without loading models or starting workers."""
        self.datasets = datasets
        self.jobs = jobs
        self.results = results
        self.journal = journal

    def enqueue(self, dataset_id: str, source_index: int) -> Job:
        """Validate a registered source and enqueue one explicit invocation; never run it here."""
        page = self.datasets.browse(dataset_id, source_index + 1, 1)
        if not page.items:
            raise LookupError("Source record does not exist.")
        return self.jobs.enqueue(
            Job(
                str(uuid4()),
                dataset_id,
                source_index,
                page.items[0].id,
                "queued",
                datetime.now(UTC).isoformat(),
            )
        )

    def inspect(self, job_id: str) -> tuple[Job, dict | None]:
        """Return metadata and verified output, raising LookupError for an unknown job."""
        job = self.jobs.get(job_id)
        if job is None:
            raise LookupError("Job does not exist.")
        return job, self.results.read(job.artefact_sha256) if job.artefact_sha256 else None

    def telemetry(self, job: Job) -> str:
        """Summarise available usage, retaining unknown counts while a local call is running."""
        record = self.journal.get(job.decision_id) if self.journal and job.decision_id else None
        if not record or record[0].selected is None:
            return "Awaiting an eligible route"
        decision, usage = record
        if usage:
            return usage_summary(decision, usage)
        elapsed = (datetime.now(UTC) - datetime.fromisoformat(job.queued_at)).total_seconds()
        return f"{decision.selected.id} · ? in / ? out · local · {elapsed:.1f}s"

    def run_once(self, routing: RoutingService, workflow: WorkflowRunner, worker_id: str) -> bool:
        """Run at most one queued item, under the caller's exclusive worker process lock.

        Unexpected storage/runtime errors terminate the worker and leave the job running
        for explicit restart recovery. No uncertain invocation is automatically repeated.
        """
        job = self.jobs.claim(worker_id)
        if job is None:
            return False
        stop = Event()
        heartbeat_errors = []

        def keep_alive():
            while not stop.wait(5):
                try:
                    self.jobs.heartbeat(job)
                except Exception as error:
                    heartbeat_errors.append(error)
                    return

        pulse = Thread(target=keep_alive, daemon=True)
        pulse.start()
        try:
            page = self.datasets.browse(job.dataset_id, job.source_index + 1, 1)
            if not page.items or page.items[0].id != job.observation_id:
                raise ValueError("Queued source identity no longer matches stored evidence.")
            decision = routing.route(
                TaskRequirements(
                    task_id=job.id,
                    task_class="normalisation",
                    capabilities=("structured_output",),
                    privacy="local_only",
                    expected_output_tokens=512,
                )
            )
            self.jobs.bind_route(job, decision.id)
            if decision.selected is None:
                self.jobs.finish(job, None, "Routing refused: " + ", ".join(decision.reasons))
                return True
            outcome = workflow.run(
                NormalisationInput(page.items[0], decision, datetime.fromisoformat(job.queued_at))
            )
            usage = routing.complete(decision.id, outcome.measurement)
            bundle = {
                "schema_version": 1,
                "job_id": job.id,
                "dataset": asdict(page.dataset),
                "source": asdict(page.items[0]),
                "routing": decision.model_dump(mode="json"),
                "usage": usage.model_dump(mode="json"),
                "telemetry": usage_summary(decision, usage),
                "framework": asdict(outcome.framework) if outcome.framework else None,
                "interpretation": outcome.interpretation.model_dump(mode="json")
                if outcome.interpretation
                else None,
                "evidence_spans": [asdict(span) for span in outcome.spans],
                "request": asdict(outcome.request) if outcome.request else None,
                "provider_request": outcome.reply.request_json if outcome.reply else None,
                "model_output": outcome.reply.content if outcome.reply else None,
                "response": outcome.reply.response_json if outcome.reply else None,
                "error": outcome.error,
            }
            digest = self.results.publish(bundle, Publication(job.id, "normalisation"))
            if heartbeat_errors:
                raise RuntimeError("Worker heartbeat failed.") from heartbeat_errors[0]
            self.jobs.finish(job, digest, outcome.error)
            return True
        finally:
            stop.set()
            pulse.join()
