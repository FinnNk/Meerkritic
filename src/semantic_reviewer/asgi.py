"""Web assembly kept separate from worker-compatible dependency composition."""

from pathlib import Path

from semantic_reviewer.bootstrap import build_jobs
from semantic_reviewer.web.app import create_app


def build_app(data_root: Path):
    """Initialise dataset storage and assemble the local web application.

    Args:
        data_root: Runtime directory outside Git worktrees, as required by
            build_datasets. Creating the app may create directories and migrate SQLite.

    Returns:
        The FastAPI application; this does not start a server or import datasets.
    """
    jobs = build_jobs(data_root)
    return create_app(jobs.datasets, jobs)
