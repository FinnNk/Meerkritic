"""Verify dataset-to-human-decision composition through real MAF and persistence."""

import json
import unittest
from datetime import UTC, datetime

import duckdb
import test_annotations
from fastapi.testclient import TestClient
from test_routing_selection import EXAMPLE

from semantic_reviewer.adapters.annotations import SQLiteAnnotations
from semantic_reviewer.adapters.jobs import SQLiteJobs
from semantic_reviewer.adapters.maf import MafWorkflowRunner
from semantic_reviewer.adapters.results import JsonResults
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.adapters.worker_lock import worker_lock
from semantic_reviewer.application.annotations import AnnotationService
from semantic_reviewer.application.jobs import JobService, Worker
from semantic_reviewer.application.model import ModelReply
from semantic_reviewer.application.routing import RoutingService
from semantic_reviewer.routing.selection import RoutingConfig
from semantic_reviewer.routing.usage import Measurement, TokenUsage
from semantic_reviewer.web.app import create_app


class SlicePathTest(unittest.TestCase):
    def test_all_three_decisions_survive_restart_with_source_usage_and_artefact_links(self):
        test_annotations.AnnotationsTest.setUp(self)
        journal = SQLiteRoutingJournal(self.database)
        queue = JobService(
            self.service, self.jobs, JsonResults(self.results.root, self.database), journal
        )
        annotations = AnnotationService(queue, self.store, self.service, self.results)
        client = TestClient(
            create_app(self.service, queue, annotations), base_url="http://127.0.0.1"
        )
        routing = RoutingService(RoutingConfig.model_validate_json(EXAMPLE.read_bytes()), journal)
        issue = self.issue

        class Model:
            def generate(self, decision, request, queued_at):
                return ModelReply(
                    json.dumps(issue),
                    Measurement(
                        started_at=queued_at,
                        completed_at=datetime.now(UTC),
                        outcome="success",
                        tokens=TokenUsage(input_tokens=20, output_tokens=30),
                    ),
                    "request",
                    "response",
                )

        jobs = []
        for action in ("accept", "edit", "reject"):
            response = client.post(
                f"/datasets/{self.source.id}/observations/0/normalise",
                headers={"Origin": "http://127.0.0.1"},
                follow_redirects=False,
            )
            self.assertEqual(response.status_code, 303)
            job_id = response.headers["location"].split("/")[-1]
            self.assertEqual(self.jobs.get(job_id).status, "queued")
            self.assertTrue(
                Worker(
                    queue, routing, MafWorkflowRunner(Model()), lambda: worker_lock(self.root)
                ).run(once=True)
            )
            job, result = queue.inspect(job_id)
            self.assertEqual(job.status, "succeeded")
            self.assertEqual(result["framework"]["outcome"], "completed")
            self.assertEqual(result["source"]["id"], job.observation_id)
            self.assertIn("20 in / 30 out", client.get(f"/jobs/{job_id}").text)
            form = {"decision": action, "notes": "Synthetic integration verification"}
            if action == "edit":
                form["edited_json"] = json.dumps(issue | {"issue_statement": "Human correction"})
            self.assertEqual(
                client.post(
                    f"/jobs/{job_id}/annotation", data=form, headers={"Origin": "http://127.0.0.1"}
                ).status_code,
                200,
            )
            jobs.append(job_id)

        restarted = AnnotationService(
            JobService(
                self.service,
                SQLiteJobs(self.database),
                JsonResults(self.results.root, self.database),
                journal,
            ),
            SQLiteAnnotations(self.database),
            self.service,
            self.results,
        )
        self.assertEqual(
            [restarted.review(job)[0].decision for job in jobs], ["accept", "edit", "reject"]
        )
        progress = restarted.store.progress(self.source.id)
        self.assertEqual((progress["reviewed_results"], progress["reviewed_sources"]), (3, 1))
        target = self.root / "usage.parquet"
        self.assertEqual(journal.export_usage(target), 3)
        with duckdb.connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT sum(input_tokens), sum(output_tokens) FROM read_parquet(?)",
                    [str(target)],
                ).fetchone(),
                (60, 90),
            )
        with self.store.state.connect() as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM artefact WHERE type='normalisation'").fetchone()[
                    0
                ],
                3,
            )
            self.assertEqual(db.execute("SELECT count(*) FROM job_log").fetchone()[0], 3)
