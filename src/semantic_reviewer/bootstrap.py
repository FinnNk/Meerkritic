"""Shared dependency composition; must not import the web application."""

import json
from functools import partial
from pathlib import Path

from semantic_reviewer.adapters.annotations import SQLiteAnnotations
from semantic_reviewer.adapters.jobs import SQLiteJobs
from semantic_reviewer.adapters.observations import ParquetObservations
from semantic_reviewer.adapters.registry import SQLiteRegistry
from semantic_reviewer.adapters.results import JsonResults
from semantic_reviewer.adapters.reviews import SQLiteReviewIndex
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.adapters.selections import JsonSelections
from semantic_reviewer.application.annotations import AnnotationService
from semantic_reviewer.application.architecture import ArchitectureView
from semantic_reviewer.application.artefacts import ArtefactIndex
from semantic_reviewer.application.datasets import DatasetService, PublicDataset
from semantic_reviewer.application.discovery import DiscoveryService
from semantic_reviewer.application.guidance import GuidanceService
from semantic_reviewer.application.interaction import ReviewWorkspace
from semantic_reviewer.application.jobs import JobService, Worker
from semantic_reviewer.application.rules import RuleService
from semantic_reviewer.application.selections import SelectionService


def build_datasets(data_root: Path) -> DatasetService:
    """Assemble dataset services and initialise their storage.

    Args:
        data_root: Runtime directory outside the application repository and all
            Git worktrees; relative paths are resolved from the working directory.

    Returns:
        A service using the project's versioned source manifests and the supplied
        runtime directory. Missing directories and the migrated registry are
        created; no dataset is downloaded or registered by this call.

    Raises:
        ValueError: The resolved data root is inside the repository or a Git worktree.
        OSError: Manifest or filesystem access fails.
    """
    root = runtime_path(data_root)
    repository = Path(__file__).resolve().parents[2]
    sources = tuple(
        PublicDataset(**json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((repository / "config" / "datasets").glob("*.json"))
    )
    return DatasetService(
        sources, SQLiteRegistry(root / "state.sqlite3"), ParquetObservations(root / "datasets")
    )


def runtime_path(path: Path) -> Path:
    """Resolve an external runtime path; reject application and other Git worktrees."""
    root = path.expanduser().resolve()
    repository = Path(__file__).resolve().parents[2]
    if root == repository or repository in root.parents:
        raise ValueError("Choose a runtime path outside the application repository.")
    if any((parent / ".git").exists() for parent in (root, *root.parents)):
        raise ValueError("Runtime data must be outside Git worktrees.")
    return root


def build_jobs(data_root: Path) -> JobService:
    """Assemble queue and result access without loading the inference runtime.

    data_root follows runtime_path's external-directory rules. This creates missing
    directories and migrates shared SQLite state, but does not register datasets,
    recover jobs or invoke a model. Invalid paths raise ValueError; I/O errors propagate.
    """
    root = runtime_path(data_root)
    return JobService(
        build_datasets(root),
        SQLiteJobs(root / "state.sqlite3"),
        JsonResults(root / "results", root / "state.sqlite3"),
        SQLiteRoutingJournal(root / "state.sqlite3"),
    )


def build_worker(
    data_root: Path,
    routing_file: Path,
    endpoint: str,
    *,
    embedding_endpoint: str | None = None,
    embedding_profile: Path | None = None,
    embedding_model: Path | None = None,
) -> Worker:
    """Compose an idle worker owning exclusivity/recovery; run it outside HTTP.

    Initialise external storage and validate routing configuration without invoking
    a model. Invalid paths/configuration raise ValueError; storage errors propagate.
    """
    from semantic_reviewer.adapters.llama import LlamaClient
    from semantic_reviewer.adapters.maf import MafWorkflowRunner
    from semantic_reviewer.adapters.maf_guidance import MafGuidanceRuntime
    from semantic_reviewer.adapters.worker_lock import worker_lock
    from semantic_reviewer.application.guidance import GuidanceExecution
    from semantic_reviewer.application.routing import RoutingService
    from semantic_reviewer.routing.selection import RoutingConfig

    root = runtime_path(data_root)
    config = RoutingConfig.model_validate_json(routing_file.read_bytes())
    routing = RoutingService(config, SQLiteRoutingJournal(root / "state.sqlite3"))
    discovery = None
    if any((embedding_endpoint, embedding_profile, embedding_model)):
        if not all((embedding_endpoint, embedding_profile, embedding_model)):
            raise ValueError(
                "Discovery requires embedding endpoint, profile and model file together."
            )
        from semantic_reviewer.adapters.embedding import EmbeddingProfile, LlamaEmbeddingClient
        from semantic_reviewer.adapters.maf_embedding import MafEmbeddingRuntime
        from semantic_reviewer.adapters.maf_synthesis import MafSynthesisRuntime
        from semantic_reviewer.application.discovery import DiscoveryExecution
        from semantic_reviewer.application.synthesis import RuleSynthesisExecution

        profile = EmbeddingProfile.model_validate_json(embedding_profile.read_bytes())
        discovery_service = build_discovery(root)
        discovery = DiscoveryExecution(
            discovery_service,
            routing,
            MafEmbeddingRuntime(LlamaEmbeddingClient(embedding_endpoint, profile, embedding_model)),
            RuleSynthesisExecution(
                discovery_service,
                build_rules(root),
                routing,
                MafSynthesisRuntime(LlamaClient(endpoint)),
            ),
        )
    return Worker(
        build_jobs(root),
        routing,
        MafWorkflowRunner(LlamaClient(endpoint)),
        partial(worker_lock, root),
        discovery,
        GuidanceExecution(build_guidance(root), routing, MafGuidanceRuntime(LlamaClient(endpoint))),
    )


def build_annotations(data_root: Path, jobs: JobService) -> AnnotationService:
    """Compose human review without loading the model runtime.

    jobs must have been composed for the same external data_root. Initialise/migrate
    the annotation store without making a decision. Invalid paths raise ValueError;
    storage errors propagate. The service exposes its bounded store query interface.
    """
    root = runtime_path(data_root)
    return AnnotationService(
        jobs, SQLiteAnnotations(root / "state.sqlite3"), jobs.datasets, jobs.results
    )


def build_review_index(data_root: Path) -> SQLiteReviewIndex:
    """Compose read-only harness references to an external DER evidence store."""
    return SQLiteReviewIndex(runtime_path(data_root) / "state.sqlite3")


def build_artefact_index(data_root: Path) -> ArtefactIndex:
    """Initialise external storage and expose explicit result/edit indexing maintenance."""
    root = runtime_path(data_root)
    return JsonResults(root / "results", root / "state.sqlite3")


def build_selections(data_root: Path) -> SelectionService:
    """Compose frozen input validation and inspection for one external runtime.

    Migrate storage without selecting records, loading models or changing annotations.
    Path and storage failures follow runtime_path/build_jobs; publication is explicit.
    """
    root = runtime_path(data_root)
    jobs = build_jobs(root)
    return SelectionService(
        SQLiteAnnotations(root / "state.sqlite3"),
        jobs,
        jobs.datasets,
        jobs.results,
        JsonSelections(root / "selections", root / "state.sqlite3"),
    )


def build_discovery(data_root: Path) -> DiscoveryService:
    """Compose queue and verified analytical inspection; models load only in the worker."""
    from semantic_reviewer.adapters.discovery import ParquetDiscovery, SQLiteDiscovery

    root = runtime_path(data_root)
    return DiscoveryService(
        JsonSelections(root / "selections", root / "state.sqlite3"),
        SQLiteDiscovery(root / "state.sqlite3"),
        ParquetDiscovery(root / "discovery"),
        SQLiteRoutingJournal(root / "state.sqlite3"),
    )


def build_rules(data_root: Path) -> RuleService:
    """Compose versioned rule inspection and research decisions without loading model runtimes."""
    from semantic_reviewer.adapters.rules import SQLiteRules

    root = runtime_path(data_root)
    discovery = build_discovery(root)
    return RuleService(
        discovery, SQLiteRules(root / "state.sqlite3", discovery.files), discovery.files
    )


def build_workspace(data_root: Path) -> ReviewWorkspace:
    """Compose saved intent and review transitions; no decisions or model work occur."""
    from semantic_reviewer.adapters.interaction import SQLiteReviewWorkspace

    root = runtime_path(data_root)
    return SQLiteReviewWorkspace(root / "state.sqlite3", build_discovery(root).files)


def build_guidance(data_root: Path) -> GuidanceService:
    """Compose frozen guidance submission and inspection without starting agent work."""
    from semantic_reviewer.adapters.guidance import SQLiteGuidance

    root = runtime_path(data_root)
    return GuidanceService(
        build_rules(root),
        build_workspace(root),
        SQLiteGuidance(root / "state.sqlite3"),
        build_discovery(root).files,
        SQLiteRoutingJournal(root / "state.sqlite3"),
    )


def build_architecture(data_root: Path) -> ArchitectureView:
    """Compose verified architecture inspection without generating or refreshing evidence."""
    from semantic_reviewer.adapters.architecture_projection import ArchitectureProjection

    return ArchitectureProjection(
        runtime_path(data_root) / "architecture", Path(__file__).resolve().parents[2]
    )
