"""Run normalisation outside web requests with one OS-owned worker per local data root."""

import time
from pathlib import Path
from uuid import uuid4

from semantic_reviewer.bootstrap import build_worker


def run(data_root: Path, routing_file: Path, endpoint: str, *, once: bool = False) -> None:
    """Recover interrupted work after acquiring exclusivity, then execute queued jobs.

    ``once`` processes at most one job. Otherwise poll until interrupted; unexpected
    storage failures stop this process so a later restart can identify unfinished work.
    """
    jobs, routing, workflow, lock = build_worker(data_root, routing_file, endpoint)
    with lock:
        jobs.jobs.recover_interrupted()
        worker_id = str(uuid4())
        while True:
            worked = jobs.run_once(routing, workflow, worker_id)
            if once:
                return
            if not worked:
                time.sleep(1)
