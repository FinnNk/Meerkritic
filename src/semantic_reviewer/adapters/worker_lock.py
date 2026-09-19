"""Use an OS-held lock to prove exclusive local worker ownership across process death."""

import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def worker_lock(root: Path):
    """Hold one local worker slot until exit; raise RuntimeError when another process owns it.

    The lock file remains on disk. Its existence and contents are not liveness
    evidence; only operating-system lock ownership is authoritative. Use local disks.
    """
    root.mkdir(parents=True, exist_ok=True)
    with (root / "worker.lock").open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError("Another worker owns this data root.") from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
