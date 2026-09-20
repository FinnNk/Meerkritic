"""Coordinate durable normalisation jobs without web, framework or storage types."""

import time
from collections.abc import Callable
from contextlib import AbstractContextManager
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
        """Publish an immutable committed-event snapshot and return catalogue metadata.

        Raise LookupError for an unknown job; integrity/publication errors propagate.
        This writes a content-addressed log and catalogue row, not a new job event.
        """
        ...

    def claim(self, worker_id: str) -> Job | None:
        """Atomically claim the oldest queued job, only when no job is running.

        Return None when no claim is available. The Worker must hold its process
        lock across recovery, claims and execution; a claim is not that lock.
        """
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
        """Validate a registered source and enqueue one explicit invocation.

        source_index is zero-based and must identify a stored row. Missing dataset
        or row raises LookupError; source integrity/storage errors propagate. Each
        call creates a distinct job and event; inference never runs in this call.
        """
        _, source = self.datasets.observation(dataset_id, source_index)
        return self.jobs.enqueue(
            Job(
                str(uuid4()),
                dataset_id,
                source_index,
                source.id,
                "queued",
                datetime.now(UTC).isoformat(),
            )
        )

    def inspect(self, job_id: str) -> tuple[Job, dict[str, object] | None]:
        """Return metadata and verified output, raising LookupError for an unknown job.

        Output is None when no artefact is attached, including early failures.
        Corrupt output raises ValueError; filesystem failures propagate. Reading
        does not change state or trigger model work.
        """
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
        return f"{decision.selected.id} | ? in / ? out | local | {elapsed:.1f}s"

    def _run_once(self, routing: RoutingService, workflow: WorkflowRunner, worker_id: str) -> bool:
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
            dataset, source = self.datasets.observation(job.dataset_id, job.source_index)
            if source.id != job.observation_id:
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
                NormalisationInput(source, decision, datetime.fromisoformat(job.queued_at))
            )
            usage = routing.complete(decision.id, outcome.measurement)
            bundle = {
                "schema_version": 1,
                "job_id": job.id,
                "dataset": asdict(dataset),
                "source": asdict(source),
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


class WorkQueue(Protocol):
    """Expose bounded queue execution without leaking task-specific orchestration."""

    def recover_interrupted(self) -> int:
        """Fail interrupted work under the caller's exclusive lock, without replay."""
        ...

    def run_once(self, worker_id: str) -> bool:
        """Process at most one item under the same lock; return whether an item was claimed."""
        ...


class Worker:
    """Own exclusive execution, restart recovery and the lifetime of queue processing.

    Callers provide dependencies, not lock/recovery choreography. Each run acquires
    a fresh process lock before recovery or claims; the lock remains held through
    inference and is released even when execution fails. Heartbeats never grant
    permission to evict a live worker or replay uncertain work.
    """

    def __init__(
        self,
        jobs: JobService,
        routing: RoutingService,
        workflow: WorkflowRunner,
        lock: Callable[[], AbstractContextManager[None]],
        discovery: WorkQueue | None = None,
        guidance: WorkQueue | None = None,
    ) -> None:
        """Bind execution and an exclusive-lock factory without starting or recovering work."""
        self._jobs = jobs
        self._routing = routing
        self._workflow = workflow
        self._lock = lock
        self._queues = tuple(queue for queue in (discovery, guidance) if queue is not None)

    def run(self, *, once: bool = False) -> int:
        """Recover under exclusivity, then process work; return the number completed.

        once=True returns after at most one claim, including zero for an empty queue.
        Otherwise poll until interrupted. Lock contention and storage/runtime failures
        propagate; unfinished work remains for a later exclusive recovery. This call
        must run outside web requests. No uncertain invocation is automatically retried.
        """
        completed = 0
        with self._lock():
            self._jobs.jobs.recover_interrupted()
            for queue in self._queues:
                queue.recover_interrupted()
            worker_id = str(uuid4())
            operations = [queue.run_once for queue in self._queues]
            operations.append(
                lambda owner: self._jobs._run_once(self._routing, self._workflow, owner)
            )
            cursor = 0
            while True:
                # Rotate after each claimed item so no continuously populated queue starves another.
                worked = False
                for offset in range(len(operations)):
                    index = (cursor + offset) % len(operations)
                    if operations[index](worker_id):
                        worked = True
                        cursor = (index + 1) % len(operations)
                        break
                completed += int(worked)
                if once:
                    return completed
                if not worked:
                    time.sleep(1)
