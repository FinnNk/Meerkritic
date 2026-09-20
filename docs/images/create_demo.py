"""Create synthetic screenshot data in a new external directory, without model calls."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from semantic_reviewer.adapters.observations import ParquetObservations
from semantic_reviewer.adapters.registry import SQLiteRegistry
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.adapters.worker_lock import worker_lock
from semantic_reviewer.application.artefacts import Publication
from semantic_reviewer.application.datasets import DatasetService, PublicDataset
from semantic_reviewer.application.discovery import DiscoveryExecution
from semantic_reviewer.application.embeddings import EmbeddingOutcome
from semantic_reviewer.application.routing import RoutingService
from semantic_reviewer.application.selections import SelectionRequest
from semantic_reviewer.bootstrap import (
    build_annotations,
    build_discovery,
    build_jobs,
    build_rules,
    build_selections,
    build_workspace,
    runtime_path,
)
from semantic_reviewer.domain.interaction import DiscussionNote, ReviewDraft, ReviewIntent
from semantic_reviewer.domain.rules import RuleDefinition, RuleOrigin
from semantic_reviewer.routing.selection import RoutingConfig
from semantic_reviewer.routing.usage import Measurement


class IllustrationVectors:
    """Supply identical vectors for the two synthetic resource examples; no inference."""

    def run(self, value):
        """Return labelled fixture output; this does not measure a model's quality."""
        return EmbeddingOutcome(
            tuple((1.0, 0.0) for _ in value.texts),
            Measurement(
                started_at=value.queued_at,
                completed_at=datetime.now(UTC),
                outcome="success",
            ),
            {"fixture": "Manually supplied screenshot vectors; no model or MAF call"},
        )


def main():
    """Seed a new external runtime and print routes; refuse any existing destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    args = parser.parse_args()
    root = runtime_path(args.data_root)
    root.mkdir(parents=True, exist_ok=False)
    repository = Path(__file__).resolve().parents[2]
    examples = [
        ("Close the file even when parsing fails.", "handle = open(path)\nreturn parse(handle)"),
        (
            "Use a context manager so the report file is always closed.",
            "report = open(path)\nreturn report.read()",
        ),
        ("Could this local variable have a shorter name?", "report_contents = read_report(path)"),
        ("Close the file even when parsing fails.", "handle = open(path)\nreturn parse(handle)"),
    ]
    rows = [
        {
            "owner": "documentation",
            "repo": "synthetic-example",
            "pr_number": 1,
            "comment_id": i + 1,
            "file_path": "reports.py",
            "comment": comment,
            "code": code,
            "category": "discussion",
            "subcategory": "question",
            "comment_created_at": "2026-01-01T00:00:00Z",
            "enriched": "Synthetic documentation example; not a real review.",
            "line_number": None,
        }
        for i, (comment, code) in enumerate(examples)
    ]
    raw = json.dumps(rows).encode()
    source = PublicDataset(
        "documentation-demo",
        "Documentation demo (synthetic)",
        "a" * 40,
        "https://example.invalid/documentation-demo.json",
        hashlib.sha256(raw).hexdigest(),
        len(rows),
    )
    observations = ParquetObservations(root / "datasets")
    (observations.root / (source.source_sha256 + ".json")).write_bytes(raw)
    datasets = DatasetService((source,), SQLiteRegistry(root / "state.sqlite3"), observations)
    datasets.register(source.id)
    jobs = build_jobs(root)
    annotations = build_annotations(root, jobs)
    chosen = []
    for i, (comment, _) in enumerate(examples):
        job = jobs.enqueue(source.id, i)
        claimed = jobs.jobs.claim("documentation-fixture")
        issue = {
            "actionable_engineering_concern": "yes" if i != 2 else "uncertain",
            "issue_statement": "A file can remain open if processing raises an exception."
            if i != 2
            else "The reviewer suggests a shorter variable name.",
            "coarse_categories": ["reliability"] if i != 2 else ["readability"],
            "scope": "function",
            "generalisable": "uncertain",
            "proposed_invariant": "Close files on normal and exceptional exits."
            if i != 2
            else None,
            "evidence_quotes": [{"source": "comment", "quote": comment}],
            "exclusions": [],
        }
        digest = jobs.results.publish(
            {
                "job_id": job.id,
                "interpretation": issue,
                "evidence_spans": [
                    {"source": "comment", "quote": comment, "start": 0, "end": len(comment)}
                ],
                "fixture": (
                    "Manually prepared interpretation; no model call or human research judgement"
                ),
            },
            Publication(job.id, "normalisation"),
        )
        jobs.jobs.finish(claimed, digest, None)
        if i < 3:
            chosen.append(
                annotations.decide(
                    job.id,
                    "reject" if i == 2 else "accept",
                    "Synthetic screenshot decision; not human research",
                )
            )
    selection = build_selections(root).freeze(
        SelectionRequest(
            dataset_id=source.id,
            annotation_ids=tuple(a.id for a in chosen),
            purpose="fixture",
            holdout_repositories=(),
        )
    )
    discovery = build_discovery(root)
    routing = RoutingService(
        RoutingConfig.model_validate_json(
            (repository / "config/routing/discovery-local.json").read_bytes()
        ),
        SQLiteRoutingJournal(root / "state.sqlite3"),
    )
    execution = DiscoveryExecution(discovery, routing, IllustrationVectors())
    with worker_lock(root):
        embedded = discovery.embed(selection.id)
        execution.run_once("documentation-fixture")
        grouped = discovery.cluster(embedded.id, 0.85)
        execution.run_once("documentation-fixture")
    rules = build_rules(root)
    version = rules.propose(
        grouped.id,
        0,
        RuleDefinition(
            statement="Close files on every exit path",
            scope="function",
            applicability="A function opens and owns a file.",
            violation="An exception can leave the owned file open.",
            exclusions=("Ownership is explicitly transferred to the caller.",),
            supporting_annotations=(chosen[0].id, chosen[1].id),
        ),
        RuleOrigin(
            kind="human",
            actor="Documentation fixture",
            rationale="Manually prepared illustration; not a research judgement",
        ),
    )
    workspace = build_workspace(root)
    workspace.discuss(
        DiscussionNote(
            id="documentation-note",
            version_id=version,
            actor="Documentation fixture",
            text="Should this exclude files returned to the caller?",
        )
    )
    workspace.save(
        "documentation-draft",
        None,
        ReviewDraft(
            actor="Documentation fixture",
            intents=(
                ReviewIntent(
                    version_id=version,
                    expected_revision=1,
                    action="defer",
                    rationale="Clarify ownership transfer before deciding.",
                ),
            ),
        ),
    )
    routes = {
        "observations": f"/datasets/{source.id}?page_size=1",
        "annotation": f"/jobs/{job.id}",
        "progress": f"/datasets/{source.id}/progress",
        "selection": f"/selections/{selection.id}",
        "discovery": f"/discovery/{grouped.id}",
        "rule": f"/rules/{version}",
        "workspace": "/review-workspace?draft_id=documentation-draft",
        "guidance": f"/guidance?version={version}",
    }
    (root / "screenshot-routes.json").write_text(json.dumps(routes, indent=2), encoding="utf-8")
    print(json.dumps(routes, indent=2))


if __name__ == "__main__":
    main()
