"""Own reproducible corpus jobs, independent of transport, framework and storage formats."""

import hashlib
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from typing import Annotated, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from semantic_reviewer.application.embeddings import EmbeddingInput, EmbeddingRuntime
from semantic_reviewer.application.routing import RoutingJournal, RoutingService
from semantic_reviewer.application.selections import SelectionStore
from semantic_reviewer.domain.grouping import cluster_vectors, validate_vectors
from semantic_reviewer.routing.selection import TaskRequirements
from semantic_reviewer.routing.usage import Measurement, usage_summary

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class DiscoveryRequest(BaseModel):
    """Pin one selection and, for clustering, its exact successful vector artefact."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["embedding", "clustering", "synthesis"]
    selection_id: Digest
    embedding_run: str | None = None
    embedding_digest: Digest | None = None
    cluster_run: str | None = Field(default=None, min_length=1, max_length=200)
    cluster_digest: Digest | None = None
    cluster: int | None = Field(default=None, ge=0, strict=True)
    threshold: float = Field(default=0.85, ge=-1, le=1, allow_inf_nan=False)
    minimum_size: int = Field(default=2, ge=2, le=100, strict=True)

    @model_validator(mode="after")
    def coherent(self) -> Self:
        """Reject incomplete or irrelevant upstream references."""
        if (self.kind == "clustering") != bool(self.embedding_run and self.embedding_digest):
            raise ValueError("Clustering requires an exact embedding run and digest.")
        if self.kind != "clustering" and (self.embedding_run or self.embedding_digest):
            raise ValueError("Only clustering inputs reference an embedding run.")
        has_cluster = bool(self.cluster_run and self.cluster_digest and self.cluster is not None)
        if (self.kind == "synthesis") != has_cluster:
            raise ValueError("Synthesis requires an exact cluster run, digest and group.")
        if self.kind != "synthesis" and any(
            x is not None for x in (self.cluster_run, self.cluster_digest, self.cluster)
        ):
            raise ValueError("Only synthesis inputs reference a cluster group.")
        return self


@dataclass(frozen=True)
class DiscoveryRun:
    """Retain small operational state; request and result bodies are immutable references."""

    id: str
    request: DiscoveryRequest
    status: Literal["queued", "running", "succeeded", "failed"]
    queued_at: str
    worker_id: str | None = None
    decision_id: str | None = None
    result_digest: str | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


class DiscoveryStore(Protocol):
    """Own atomic queue transitions/events and fencing; never hold transactions over models."""

    def enqueue(self, request: DiscoveryRequest) -> DiscoveryRun:
        """Atomically register a validated request and event as a distinct queued invocation."""
        ...

    def get(self, run_id: str) -> DiscoveryRun:
        """Return metadata; raise LookupError for an unknown identity."""
        ...

    def recent(self) -> tuple[DiscoveryRun, ...]:
        """Return at most 100 metadata records, newest first, without verifying bodies."""
        ...

    def claim(self, worker_id: str) -> DiscoveryRun | None:
        """Claim the oldest queued run under the process lock; None means no claim available."""
        ...

    def bind_route(self, run: DiscoveryRun, decision_id: str) -> None:
        """Bind a persisted decision once; reject duplicate binding or lost worker ownership."""
        ...

    def finish(self, run: DiscoveryRun, digest: str | None, error: str | None) -> None:
        """Commit terminal state/event; success needs a digest, failure a non-blank error.

        Invalid combinations or lost ownership raise ValueError without changing state.
        The execution owner must publish a complete artefact before supplying its digest.
        """
        ...

    def recover_interrupted(self) -> int:
        """Fail running jobs under the exclusive process lock; return count, never replay."""
        ...


class DiscoveryFiles(Protocol):
    """Publish complete immutable analytical bodies before registering terminal state."""

    def write_json(self, body: dict) -> str:
        """Publish finite canonical JSON up to 32 MB; return SHA-256 without SQL registration."""
        ...

    def read_json(self, digest: str) -> dict:
        """Verify hash and object shape; ValueError on corruption, OSError on missing files."""
        ...

    def write_vectors(self, ids: tuple[str, ...], texts: tuple[str, ...], vectors: tuple) -> str:
        """Publish 1..100 unique aligned identities, texts and finite unit vectors (1..4096D)."""
        ...

    def read_vectors(self, digest: str) -> tuple[tuple[str, str, tuple[float, ...]], ...]:
        """Verify analytical bytes, identity/order and shape before returning bounded rows."""
        ...

    def write_members(self, members: tuple[dict, ...]) -> str:
        """Publish 1..100 distinct ordered annotation/cluster/representative assignments."""
        ...

    def read_members(self, digest: str) -> tuple[dict, ...]:
        """Return verified ordered memberships; missing/corrupt evidence fails closed."""
        ...


class DiscoveryService:
    """Hide input identity checks and queue publication behind explicit user operations."""

    def __init__(
        self,
        selections: SelectionStore,
        store: DiscoveryStore,
        files: DiscoveryFiles,
        journal: RoutingJournal | None = None,
    ) -> None:
        """Bind ports for one external runtime; construction never invokes inference."""
        self.selections, self.store, self.files = selections, store, files
        self.journal = journal

    def telemetry(self, run: DiscoveryRun) -> str:
        """Show recorded usage or honest unknown token counts while a routed call is running."""
        record = self.journal.get(run.decision_id) if self.journal and run.decision_id else None
        if not record or record[0].selected is None:
            return (
                "Awaiting an eligible route"
                if run.request.kind != "clustering"
                else "No model call"
            )
        decision, usage = record
        if usage:
            return usage_summary(decision, usage)
        elapsed = (datetime.now(UTC) - datetime.fromisoformat(run.queued_at)).total_seconds()
        location = "local" if decision.selected.locality == "local" else "spend pending"
        return f"{decision.selected.id} · ? in / ? out · {location} · {elapsed:.1f}s"

    def embed(self, selection_id: str) -> DiscoveryRun:
        """Verify a non-empty eligible selection, then queue a distinct invocation."""
        summary, _ = self.selections.read(selection_id)
        if summary.included == 0:
            raise ValueError("Selection has no eligible inputs.")
        return self.store.enqueue(DiscoveryRequest(kind="embedding", selection_id=selection_id))

    def cluster(self, embedding_run: str, threshold: float, minimum_size: int = 2) -> DiscoveryRun:
        """Pin a successful embedding result; explicit parameters are exploratory, not adopted."""
        run, body = self.inspect(embedding_run)
        if run.status != "succeeded" or run.request.kind != "embedding":
            raise ValueError("Clustering requires a successful embedding run.")
        self.files.read_vectors(body["vectors_digest"])
        return self.store.enqueue(
            DiscoveryRequest(
                kind="clustering",
                selection_id=run.request.selection_id,
                embedding_run=run.id,
                embedding_digest=run.result_digest,
                threshold=threshold,
                minimum_size=minimum_size,
            )
        )

    def inspect(self, run_id: str) -> tuple[DiscoveryRun, dict | None]:
        """Read metadata and verified result; no source selection or model call occurs."""
        run = self.store.get(run_id)
        body = self.files.read_json(run.result_digest) if run.result_digest else None
        if body is not None and (
            body.get("run_id") != run.id
            or DiscoveryRequest.model_validate(body.get("request")) != run.request
        ):
            raise ValueError("Discovery result disagrees with its queued request.")
        return run, body

    def synthesise(self, cluster_run: str, cluster: int) -> DiscoveryRun:
        """Pin a successful clustering result for worker synthesis; never invoke a model here.

        The synthesis owner resolves eligible membership in the worker. Unknown or
        failed upstream runs are rejected before queueing; invalid groups fail visibly
        during execution. Each explicit call creates a distinct invocation.
        """
        run, _ = self.inspect(cluster_run)
        if run.status != "succeeded" or run.request.kind != "clustering":
            raise ValueError("Synthesis requires a successful cluster run.")
        return self.store.enqueue(
            DiscoveryRequest(
                kind="synthesis",
                selection_id=run.request.selection_id,
                cluster_run=run.id,
                cluster_digest=run.result_digest,
                cluster=cluster,
            )
        )


@dataclass(frozen=True)
class SynthesisPublication:
    """Return immutable proposal provenance separately from its optional registered candidate."""

    rule_version: str | None
    trace_digest: str
    error: str | None
    insufficiency_reason: str | None
    telemetry: str


class SynthesisExecutor(Protocol):
    """Own rule-specific resolution, runtime validation and registry publication."""

    def execute(self, run: DiscoveryRun) -> SynthesisPublication:
        """Execute an already claimed synthesis run under the corpus worker's process lock."""
        ...


class DiscoveryExecution:
    """Resolve, execute and publish one corpus job under the shared exclusive worker lock."""

    def __init__(
        self,
        service: DiscoveryService,
        routing: RoutingService,
        runtime: EmbeddingRuntime,
        synthesis: SynthesisExecutor | None = None,
    ) -> None:
        """Bind idle dependencies; the owning Worker controls recovery and execution."""
        self.service, self.routing, self.runtime = service, routing, runtime
        self.synthesis = synthesis

    def recover_interrupted(self) -> int:
        """Fail unfinished calls without replay; caller must already own the process lock."""
        return self.service.store.recover_interrupted()

    def run_once(self, worker_id: str) -> bool:
        """Process one claimed job; safe input/model failures become inspectable terminal data."""
        service = self.service
        run = service.store.claim(worker_id)
        if run is None:
            return False
        body = {
            "schema_version": 1,
            "run_id": run.id,
            "request": run.request.model_dump(mode="json"),
        }
        error = None
        try:
            summary, snapshot = service.selections.read(run.request.selection_id)
            records = tuple(item for item in snapshot.records if item.exclusion is None)
            ids = tuple(item.annotation.id for item in records)
            body.update(
                eligible=summary.included, excluded=summary.excluded, purpose=summary.purpose
            )
            if run.request.kind == "embedding":
                texts = tuple(
                    "\n".join(
                        (
                            item.interpretation.issue_statement,
                            item.interpretation.proposed_invariant or "",
                            ", ".join(item.interpretation.coarse_categories),
                        )
                    )
                    for item in records
                )
                if any(len(text) > 12000 for text in texts):
                    raise ValueError("An embedding input exceeds the 12,000-character bound.")
                decision = self.routing.route(
                    TaskRequirements(
                        task_id=run.id,
                        task_class="embedding",
                        capabilities=("embeddings",),
                        privacy="local_only",
                    )
                )
                service.store.bind_route(run, decision.id)
                body["routing"] = decision.model_dump(mode="json")
                if decision.selected is None:
                    raise ValueError("Routing refused: " + ", ".join(decision.reasons))
                outcome = self.runtime.run(
                    EmbeddingInput(texts, decision, datetime.fromisoformat(run.queued_at))
                )
                if outcome.error is None:
                    try:
                        vectors = validate_vectors(outcome.vectors, len(ids))
                        if outcome.measurement.outcome != "success":
                            raise ValueError("Success disagrees with runtime measurement.")
                    except (ValueError, TypeError):
                        outcome = replace(
                            outcome,
                            error="Embedding runtime returned invalid vectors.",
                            measurement=Measurement(
                                **{
                                    **outcome.measurement.model_dump(),
                                    "outcome": "semantic_failure",
                                }
                            ),
                        )
                usage = self.routing.complete(decision.id, outcome.measurement)
                body.update(
                    usage=usage.model_dump(mode="json"),
                    telemetry=usage_summary(decision, usage),
                    framework=asdict(outcome.framework) if outcome.framework else None,
                    model_provenance=outcome.provenance,
                    preprocessing="issue-invariant-categories-v1",
                    text_sha256=[hashlib.sha256(t.encode()).hexdigest() for t in texts],
                )
                error = outcome.error
                if error is None:
                    body.update(
                        vectors_digest=service.files.write_vectors(ids, texts, vectors),
                        dimensions=len(vectors[0]),
                        normalisation="l2-v1",
                    )
            elif run.request.kind == "clustering":
                parent, embedding = service.inspect(run.request.embedding_run)
                if (
                    parent.status != "succeeded"
                    or parent.result_digest != run.request.embedding_digest
                ):
                    raise ValueError("Embedding result differs from the pinned input.")
                rows = service.files.read_vectors(embedding["vectors_digest"])
                if tuple(row[0] for row in rows) != ids:
                    raise ValueError("Vector identities differ from selected annotations.")
                members = cluster_vectors(
                    ids,
                    tuple(row[2] for row in rows),
                    run.request.threshold,
                    run.request.minimum_size,
                )
                body.update(
                    members_digest=service.files.write_members(members),
                    algorithm="cosine-components-v1",
                    seed=None,
                    outliers=sum(row["cluster"] == -1 for row in members),
                    clusters=len({row["cluster"] for row in members if row["cluster"] >= 0}),
                )
            else:
                if self.synthesis is None:
                    raise ValueError("This worker has no configured synthesis runtime.")
                publication = self.synthesis.execute(run)
                body.update(asdict(publication))
                error = publication.error
        except (ValueError, LookupError, OSError) as failure:
            # Do not leak filesystem paths or source/provider payloads into operational errors.
            error = f"Discovery input or output validation failed ({type(failure).__name__})."
            body["failure_stage"] = "input/output integrity"
        body["error"] = error
        body["failed"] = body.get("eligible", 0) if error else 0
        body["completed_at"] = datetime.now(UTC).isoformat()
        body["turnaround_ms"] = (
            datetime.now(UTC) - datetime.fromisoformat(run.queued_at)
        ).total_seconds() * 1000
        digest = service.files.write_json(body)
        service.store.finish(run, digest, error)
        return True
