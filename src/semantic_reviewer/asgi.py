"""Web assembly kept separate from worker-compatible dependency composition."""

from pathlib import Path

from fastapi import FastAPI

from semantic_reviewer.bootstrap import (
    build_annotations,
    build_jobs,
    build_review_index,
    build_selections,
)
from semantic_reviewer.web.app import create_app


def build_app(data_root: Path) -> FastAPI:
    """Initialise operational storage and assemble the local web application.

    Args:
        data_root: Runtime directory outside Git worktrees, as required by
            build_datasets. Creating the app may create directories and migrate SQLite.

    Returns:
        The FastAPI application with dataset, job, annotation, frozen input and review-reference
        access; this does not start a server, import datasets or execute inference.
    """
    jobs = build_jobs(data_root)
    annotations = build_annotations(data_root, jobs)
    return create_app(
        jobs.datasets,
        jobs,
        annotations,
        build_review_index(data_root),
        build_selections(data_root).store,
    )
