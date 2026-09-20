"""Shared dependency composition; must not import the web application."""

import json
from pathlib import Path

from semantic_reviewer.adapters.annotations import SQLiteAnnotations
from semantic_reviewer.adapters.jobs import SQLiteJobs
from semantic_reviewer.adapters.observations import ParquetObservations
from semantic_reviewer.adapters.registry import SQLiteRegistry
from semantic_reviewer.adapters.results import JsonResults
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.application.annotations import AnnotationService
from semantic_reviewer.application.datasets import DatasetService, PublicDataset
from semantic_reviewer.application.jobs import JobService


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
    """Assemble queue and result access without loading the inference runtime."""
    root = runtime_path(data_root)
    return JobService(
        build_datasets(root),
        SQLiteJobs(root / "state.sqlite3"),
        JsonResults(root / "results", root / "state.sqlite3"),
        SQLiteRoutingJournal(root / "state.sqlite3"),
    )


def build_worker(data_root: Path, routing_file: Path, endpoint: str):
    """Compose a configured local workflow; the caller must hold the returned process lock."""
    from semantic_reviewer.adapters.llama import LlamaClient
    from semantic_reviewer.adapters.maf import MafWorkflowRunner
    from semantic_reviewer.adapters.worker_lock import worker_lock
    from semantic_reviewer.application.routing import RoutingService
    from semantic_reviewer.routing.selection import RoutingConfig

    root = runtime_path(data_root)
    config = RoutingConfig.model_validate_json(routing_file.read_bytes())
    return (
        build_jobs(root),
        RoutingService(config, SQLiteRoutingJournal(root / "state.sqlite3")),
        MafWorkflowRunner(LlamaClient(endpoint)),
        worker_lock(root),
    )


def build_annotations(data_root: Path) -> AnnotationService:
    """Compose human review without loading the model runtime."""
    root = runtime_path(data_root)
    return AnnotationService(build_jobs(root), SQLiteAnnotations(root / "state.sqlite3"))
