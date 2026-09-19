"""Shared dependency composition; must not import the web application."""

import json
from pathlib import Path

from semantic_reviewer.adapters.observations import ParquetObservations
from semantic_reviewer.adapters.registry import SQLiteRegistry
from semantic_reviewer.application.datasets import DatasetService, PublicDataset


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
