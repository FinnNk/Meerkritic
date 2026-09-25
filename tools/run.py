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
    worker = commands.add_parser("worker")
    worker.add_argument("--routing", type=Path, required=True)
    worker.add_argument("--endpoint", default="http://127.0.0.1:8081")
    worker.add_argument("--once", action="store_true")
    worker.add_argument("--embedding-endpoint")
    worker.add_argument("--embedding-profile", type=Path)
    worker.add_argument("--embedding-model", type=Path)
    embed = commands.add_parser("embed")
    embed.add_argument("selection_id")
    cluster = commands.add_parser("cluster")
    cluster.add_argument("embedding_run")
    cluster.add_argument("--threshold", type=float, required=True)
    cluster.add_argument("--minimum-size", type=int, default=2)
    discovery = commands.add_parser("discovery")
    discovery.add_argument("run_id", nargs="?")
    synthesise = commands.add_parser("synthesise")
    synthesise.add_argument("cluster_run")
    synthesise.add_argument("cluster", type=int)
    commands.add_parser("rules")
    rule = commands.add_parser("rule")
    rule.add_argument("version_id")
    normalise = commands.add_parser("normalise")
    normalise.add_argument("dataset_id")
    normalise.add_argument("source_index", type=int)
    commands.add_parser("jobs")
    log = commands.add_parser("job-log")
    log.add_argument("job_id")
    commands.add_parser("index-artefacts")
    review = commands.add_parser("index-review")
    review.add_argument("manifest", type=Path)
    review.add_argument("event", type=Path)
    annotate = commands.add_parser("annotate")
    annotate.add_argument("job_id")
    annotate.add_argument("decision", choices=("accept", "edit", "reject"))
    annotate.add_argument("--notes", default="")
    annotate.add_argument("--edited-json", type=Path)
    correction = commands.add_parser("correct-annotation")
    correction.add_argument("annotation_id")
    correction.add_argument("--edited-json", type=Path, required=True)
    correction.add_argument("--notes-file", type=Path, required=True)
    correction.add_argument("--reason", required=True)
    correction.add_argument("--curator", required=True)
    progress = commands.add_parser("progress")
    progress.add_argument("dataset_id")
    selection = commands.add_parser("freeze-selection")
    selection.add_argument("request", type=Path)
    inspect_selection = commands.add_parser("selection")
    inspect_selection.add_argument("selection_id")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    try:
        if args.command == "serve":
            import uvicorn

            assembly = importlib.import_module("semantic_reviewer.asgi")
            uvicorn.run(assembly.build_app(args.data_root), host="127.0.0.1", port=args.port)
        elif args.command == "worker":
            execution = importlib.import_module("semantic_reviewer.worker")
            execution.run(
                args.data_root,
                args.routing,
                args.endpoint,
                once=args.once,
                embedding_endpoint=args.embedding_endpoint,
                embedding_profile=args.embedding_profile,
                embedding_model=args.embedding_model,
            )
        elif args.command in ("embed", "cluster", "synthesise", "discovery"):
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            service = composition.build_discovery(args.data_root)
            if args.command == "embed":
                result = asdict(service.embed(args.selection_id))
            elif args.command == "cluster":
                result = asdict(
                    service.cluster(args.embedding_run, args.threshold, args.minimum_size)
                )
            elif args.command == "synthesise":
                result = asdict(service.synthesise(args.cluster_run, args.cluster))
            elif args.run_id:
                run, body = service.inspect(args.run_id)
                result = {"run": asdict(run), "result": body}
            else:
                result = [asdict(run) for run in service.store.recent()]
            print(json.dumps(result, indent=2, default=lambda item: item.model_dump(mode="json")))
        elif args.command in ("rules", "rule"):
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            registry = composition.build_rules(args.data_root)
            if args.command == "rules":
                result = [asdict(head) for head in registry.store.recent()]
            else:
                head, body, evidence, decisions = registry.store.read(args.version_id)
                result = {
                    "head": asdict(head),
                    "version": body.model_dump(mode="json"),
                    "evidence": [item.model_dump(mode="json") for item in evidence],
                    "decisions": decisions,
                }
            print(json.dumps(result, indent=2))
        elif args.command == "correct-annotation":
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            annotations = composition.build_annotations(
                args.data_root, composition.build_jobs(args.data_root)
            )
            result = annotations.correct(
                args.annotation_id,
                args.edited_json.read_text(encoding="utf-8-sig"),
                args.notes_file.read_text(encoding="utf-8-sig"),
                reason=args.reason,
                curator=args.curator,
            )
            print(json.dumps(asdict(result), indent=2))
        elif args.command in ("annotate", "progress"):
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            annotations = composition.build_annotations(
                args.data_root, composition.build_jobs(args.data_root)
            )
            result = (
                annotations.store.progress(args.dataset_id)
                if args.command == "progress"
                else asdict(
                    annotations.decide(
                        args.job_id,
                        args.decision,
                        args.notes,
                        args.edited_json.read_text(encoding="utf-8") if args.edited_json else None,
                    )
                )
            )
            print(json.dumps(result, indent=2))
        elif args.command in ("freeze-selection", "selection"):
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            selection_types = importlib.import_module("semantic_reviewer.application.selections")
            selections = composition.build_selections(args.data_root)
            if args.command == "freeze-selection":
                with args.request.open("rb") as stream:
                    body = stream.read(256_001)
                if len(body) > 256_000:
                    raise ValueError("Selection request exceeds 256 KB.")
                result = asdict(
                    selections.freeze(selection_types.SelectionRequest.model_validate_json(body))
                )
            else:
                summary, snapshot = selections.store.read(args.selection_id)
                result = {"summary": asdict(summary), "snapshot": snapshot.model_dump(mode="json")}
            print(json.dumps(result, indent=2))
        elif args.command == "index-review":
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            result = composition.build_review_index(args.data_root).index(args.manifest, args.event)
            print(json.dumps(asdict(result), indent=2))
        elif args.command in ("job-log", "index-artefacts"):
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            jobs = composition.build_jobs(args.data_root)
            result = (
                jobs.jobs.log(args.job_id)
                if args.command == "job-log"
                else {
                    "indexed": composition.build_artefact_index(args.data_root).index_referenced()
                }
            )
            print(json.dumps(result, indent=2))
        elif args.command in ("normalise", "jobs"):
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            jobs = composition.build_jobs(args.data_root)
            result = (
                asdict(jobs.enqueue(args.dataset_id, args.source_index))
                if args.command == "normalise"
                else [asdict(job) for job in jobs.jobs.recent()]
            )
            print(json.dumps(result, indent=2))
        else:
            composition = importlib.import_module("semantic_reviewer.bootstrap")
            service = composition.build_datasets(args.data_root)
            result = (
                [asdict(source) for source in service.catalogue]
                if args.command == "catalogue"
                else asdict(service.register(args.dataset_id))
            )
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, LookupError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
