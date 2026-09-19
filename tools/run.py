"""Run imports outside HTTP, or serve the local harness from this checkout."""

import argparse
import importlib
import json
import sys
from dataclasses import asdict
from pathlib import Path


def main() -> int:
    """Run the selected local command; report import or filesystem errors through the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalogue")
    register = commands.add_parser("register")
    register.add_argument("dataset_id")
    serve = commands.add_parser("serve")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    try:
        if args.command == "serve":
            import uvicorn

            assembly = importlib.import_module("semantic_reviewer.asgi")
            uvicorn.run(assembly.build_app(args.data_root), host="127.0.0.1", port=args.port)
        else:
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            service = composition.build_datasets(args.data_root)
            result = (
                [asdict(source) for source in service.catalogue]
                if args.command == "catalogue"
                else asdict(service.register(args.dataset_id))
            )
            print(json.dumps(result, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
