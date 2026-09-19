"""Preview, record or inspect routing provenance without making model calls."""

import argparse
import importlib
import json
import sys
from pathlib import Path


def main() -> int:
    """Run a routing command; refuse invalid configuration and return 2 for no eligible model."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preview", "record"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--task", type=Path, required=True)
        command.add_argument("--model")
        command.add_argument("--policy-id")
        command.add_argument("--policy-version")
        if name == "record":
            command.add_argument("--data-root", type=Path, required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--data-root", type=Path, required=True)
    inspect.add_argument("decision_id")
    export = commands.add_parser("export-usage")
    export.add_argument("--data-root", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    routing = importlib.import_module("semantic_reviewer.routing.selection")
    try:
        if args.command in {"preview", "record"}:
            config = routing.RoutingConfig.model_validate_json(args.config.read_bytes())
            task = routing.TaskRequirements.model_validate_json(args.task.read_bytes())
            if bool(args.policy_id) != bool(args.policy_version):
                raise ValueError("Policy ID and version must be supplied together.")
            override = (
                routing.Version(id=args.policy_id, version=args.policy_version)
                if args.policy_id
                else None
            )
            options = {"invocation_policy": override, "model_override": args.model}
            if args.command == "preview":
                decision = routing.select_route(config, task, **options)
            else:
                service = importlib.import_module("semantic_reviewer.application.routing")
                journal = _journal(args.data_root)
                decision = service.RoutingService(config, journal).route(task, **options)
            print(decision.model_dump_json(indent=2))
            return 0 if decision.selected is not None else 2
        journal = _journal(args.data_root)
        if args.command == "inspect":
            record = journal.get(args.decision_id)
            if record is None:
                raise ValueError("Routing decision is unknown.")
            decision, usage = record
            print(
                json.dumps(
                    {
                        "decision": decision.model_dump(mode="json"),
                        "usage": usage.model_dump(mode="json") if usage else None,
                    },
                    indent=2,
                )
            )
        else:
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            count = journal.export_usage(composition.runtime_path(args.output))
            print(json.dumps({"completed_invocations": count, "output": str(args.output)}))
    except (ValueError, OSError) as error:
        # Validation errors can embed input values. Keep the CLI error free of task contents.
        from pydantic import ValidationError

        detail = (
            "Invalid routing input; check field names, types and references."
            if isinstance(error, ValidationError)
            else str(error)
        )
        parser.exit(1, detail + "\n")
    return 0


def _journal(data_root: Path):
    """Construct migrated runtime storage outside Git worktrees."""
    composition = importlib.import_module("semantic_reviewer.bootstrap")
    adapter = importlib.import_module("semantic_reviewer.adapters.routing_journal")
    return adapter.SQLiteRoutingJournal(composition.runtime_path(data_root) / "state.sqlite3")


if __name__ == "__main__":
    raise SystemExit(main())
