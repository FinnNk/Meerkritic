"""Generate the canonical typed architecture data and local harness projection."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from semantic_reviewer.adapters.architecture import Import as Import
from semantic_reviewer.adapters.architecture import delta as delta
from semantic_reviewer.adapters.architecture import interfaces as interfaces
from semantic_reviewer.adapters.architecture import snapshot as snapshot
from semantic_reviewer.adapters.architecture_projection import ArchitectureProjection


def main() -> None:
    """Generate snapshots/deltas or explicitly publish a verified local before/after view."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("snapshot")
    capture.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    compare = commands.add_parser("delta")
    compare.add_argument("before", type=Path)
    compare.add_argument("after", type=Path)
    publish = commands.add_parser("publish-view")
    publish.add_argument("before", type=Path)
    publish.add_argument("after", type=Path)
    publish.add_argument("--data-root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "snapshot":
        result = asdict(snapshot(args.root))
    else:
        before = json.loads(args.before.read_text(encoding="utf-8-sig"))
        after = json.loads(args.after.read_text(encoding="utf-8-sig"))
        if args.command == "delta":
            result = delta(before, after)
        else:
            from semantic_reviewer.bootstrap import runtime_path

            projection = ArchitectureProjection(
                runtime_path(args.data_root) / "architecture", Path(__file__).resolve().parents[1]
            )
            result = {"projection_digest": projection.publish(before, after)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
