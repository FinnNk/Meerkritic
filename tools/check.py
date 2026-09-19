"""Run the required quality gates in this checkout and interpreter environment."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run checkout-local quality gates, stopping at the first failure.

    Run tools in this interpreter environment against this checkout's source.
    Progress and tool diagnostics go to the process output streams.

    Returns:
        Zero when every gate passes, the failing tool's status otherwise, or one
        when a required executable is missing.
    """
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    # Check this checkout even when another worktree has an editable package installed.
    environment["PYTHONPATH"] = str(root / "src")
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment["PATH"]
    commands = [
        ["ruff", "format", "--check", "."],
        ["ruff", "check", "."],
        ["lint-imports", "--no-cache"],
        ["tach", "check"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
    ]
    for command in commands:
        print("Running: " + " ".join(command), flush=True)
        executable = shutil.which(command[0], path=environment["PATH"])
        if executable is None:
            print(f"Missing tool: {command[0]}; run uv sync --locked.", file=sys.stderr)
            return 1
        command = [executable, *command[1:]]
        result = subprocess.run(command, cwd=root, env=environment, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
