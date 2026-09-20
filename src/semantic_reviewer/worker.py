"""Run normalisation outside web requests through the owned worker lifecycle."""

from pathlib import Path

from semantic_reviewer.bootstrap import build_worker


def run(data_root: Path, routing_file: Path, endpoint: str, *, once: bool = False) -> None:
    """Run the configured worker; once processes at most one job before returning.

    Worker owns exclusivity, interruption recovery and cleanup. Configuration,
    lock and execution errors propagate; no failed invocation is replayed.
    """
    build_worker(data_root, routing_file, endpoint).run(once=once)
