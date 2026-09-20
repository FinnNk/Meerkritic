"""Challenge corpus identities, real MAF orchestration, durable state and analytical integrity."""

import json
import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import test_selections
from fastapi.testclient import TestClient

from semantic_reviewer.adapters.discovery import ParquetDiscovery, SQLiteDiscovery
from semantic_reviewer.adapters.maf_embedding import MafEmbeddingRuntime
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.adapters.worker_lock import worker_lock
from semantic_reviewer.application.discovery import (
    DiscoveryExecution,
    DiscoveryService,
)
from semantic_reviewer.application.embeddings import EmbeddingOutcome
from semantic_reviewer.application.jobs import Worker
from semantic_reviewer.application.routing import RoutingService
from semantic_reviewer.domain.grouping import cluster_vectors, validate_vectors
from semantic_reviewer.routing.selection import RoutingConfig
from semantic_reviewer.routing.usage import Measurement
from semantic_reviewer.web.app import create_app

ROOT = Path(__file__).resolve().parents[1]


class FakeEmbedding:
    def __init__(self, *, failure=False):
        self.calls = 0
        self.failure = failure

    def run(self, value):
        self.calls += 1
        return EmbeddingOutcome(
            () if self.failure else tuple((1.0, 0.0) for _ in value.texts),
            Measurement(
                started_at=value.queued_at,
                completed_at=datetime.now(UTC),
                outcome="provider_failure" if self.failure else "success",
            ),
            {"fixture": True},
            "Provider unavailable" if self.failure else None,
        )


class DiscoveryTest(unittest.TestCase):
    def setUp(self):
        test_selections.SelectionsTest.setUp(self)
        self.discovery_store = SQLiteDiscovery(self.database)
        self.files = ParquetDiscovery(self.root / "discovery")
        self.discovery = DiscoveryService(self.selection_store, self.discovery_store, self.files)
        self.routing = RoutingService(
            RoutingConfig.model_validate_json(
                (ROOT / "config/routing/discovery-local.json").read_bytes()
            ),
            SQLiteRoutingJournal(self.database),
        )
        self.model = FakeEmbedding()
        self.execution = DiscoveryExecution(
            self.discovery, self.routing, MafEmbeddingRuntime(self.model)
        )
        self.worker = Worker(
            self.queue, self.routing, None, lambda: worker_lock(self.root), self.execution
        )

    def complete(self, index=0):
        return test_selections.SelectionsTest.complete(self, index)

    def selection(self):
        annotations = [
            test_selections.SelectionsTest.choose(self, i, "reject" if i == 2 else "accept")
            for i in range(3)
        ]
        return self.selections.freeze(test_selections.SelectionsTest.request(self, *annotations))

    def embed(self):
        selection = self.selection()
        run = self.discovery.embed(selection.id)
        self.assertEqual(self.worker.run(once=True), 1)
        return self.discovery.inspect(run.id)

    def test_end_to_end_maf_vectors_restart_and_denominators(self):
        run, body = self.embed()
        self.assertEqual(run.status, "succeeded")
        self.assertEqual((body["eligible"], body["excluded"], body["failed"]), (2, 1, 0))
        self.assertEqual(body["framework"]["framework"], "Microsoft Agent Framework")
        self.assertEqual(body["usage"]["measurement"]["outcome"], "success")
        rows = self.files.read_vectors(body["vectors_digest"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][2], (1, 0))
        self.assertEqual(SQLiteDiscovery(self.database).get(run.id).status, "succeeded")

    def test_clustering_replay_preserves_membership_and_terminal_state(self):
        run, _ = self.embed()
        first = self.discovery.cluster(run.id, 0.9)
        self.worker.run(once=True)
        _, clustered = self.discovery.inspect(first.id)
        self.assertEqual((clustered["clusters"], clustered["outliers"]), (1, 0))
        members = self.files.read_members(clustered["members_digest"])
        self.assertEqual(sum(m["representative"] for m in members), 1)
        repeated = self.discovery.cluster(run.id, 0.9)
        self.worker.run(once=True)
        self.assertNotEqual(first.id, repeated.id)
        self.assertEqual(
            self.discovery.inspect(repeated.id)[1]["members_digest"], clustered["members_digest"]
        )
        self.assertEqual(SQLiteDiscovery(self.database).get(first.id).status, "succeeded")
        with self.discovery_store.state.connect() as db:
            self.assertLess(
                max(len(row[0]) for row in db.execute("SELECT request_json FROM discovery_run")),
                4096,
            )
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE discovery_run SET status='queued' WHERE id=?", (first.id,))

    def test_provider_failure_is_terminal_without_automatic_replay(self):
        self.model.failure = True
        run, body = self.embed()
        self.assertEqual(run.status, "failed")
        self.assertEqual(body["failed"], 2)
        self.assertNotIn("vectors_digest", body)
        self.worker.run(once=True)
        self.assertEqual(self.model.calls, 1)

    def test_failed_embedding_cannot_supply_clustering(self):
        self.model.failure = True
        run, _ = self.embed()
        with self.assertRaises(ValueError):
            self.discovery.cluster(run.id, 0.9)

    def test_bad_runtime_vectors_are_semantic_failures_before_usage_is_completed(self):
        def malformed(value):
            return EmbeddingOutcome(
                ((1.0, 0.0),),
                Measurement(
                    started_at=value.queued_at, completed_at=datetime.now(UTC), outcome="success"
                ),
                {},
            )

        with patch.object(self.model, "run", side_effect=malformed):
            run, body = self.embed()
        self.assertEqual(run.status, "failed")
        self.assertEqual(body["usage"]["measurement"]["outcome"], "semantic_failure")
        self.assertNotIn("vectors_digest", body)

    def test_orphan_publication_does_not_make_a_job_successful_after_event_failure(self):
        selection = self.selection()
        run = self.discovery.embed(selection.id)
        with self.discovery_store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER reject_completion BEFORE INSERT ON event "
                "WHEN NEW.kind='discovery_succeeded' BEGIN SELECT RAISE(ABORT,'fixture'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.worker.run(once=True)
        self.assertEqual(self.discovery_store.get(run.id).status, "running")
        self.assertTrue(list(self.files.root.glob("*.parquet")))
        self.worker.run(once=True)
        self.assertEqual(self.discovery_store.get(run.id).status, "failed")
        self.assertEqual(self.model.calls, 1)

    def test_corrupt_selection_fails_before_model_and_corrupt_vectors_before_clustering(self):
        selection = self.selection()
        run = self.discovery.embed(selection.id)
        (self.selection_store.root / (selection.id + ".json")).write_text("{}")
        self.worker.run(once=True)
        self.assertEqual(self.discovery_store.get(run.id).status, "failed")
        self.assertEqual(self.model.calls, 0)

    def test_vector_checksum_fails_before_clustering(self):
        run, body = self.embed()
        path = self.files.root / (body["vectors_digest"] + ".parquet")
        path.write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            self.discovery.cluster(run.id, 0.8)

    def test_request_manifest_disagreement_fails_closed(self):
        run, body = self.embed()
        body["run_id"] = "another"
        with (
            patch.object(self.files, "read_json", return_value=body),
            self.assertRaises(ValueError),
        ):
            self.discovery.inspect(run.id)

    def test_prior_request_manifests_remain_readable_without_new_optional_fields(self):
        run, body = self.embed()
        for field in ("cluster_run", "cluster_digest", "cluster"):
            body["request"].pop(field, None)
        with patch.object(self.files, "read_json", return_value=body):
            self.assertEqual(self.discovery.inspect(run.id)[0].id, run.id)

    def test_atomic_event_failure_rolls_back_and_claims_are_exclusive(self):
        selection = self.selection()
        with self.discovery_store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER reject_discovery BEFORE INSERT ON event "
                "WHEN NEW.kind='discovery_queued' BEGIN SELECT RAISE(ABORT,'fixture'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.discovery.embed(selection.id)
        self.assertEqual(self.discovery_store.recent(), ())
        with self.discovery_store.state.connect() as db:
            db.execute("DROP TRIGGER reject_discovery")
        run = self.discovery.embed(selection.id)
        with ThreadPoolExecutor(2) as pool:
            claimed = list(pool.map(self.discovery_store.claim, ("one", "two")))
        self.assertEqual(sum(r is not None for r in claimed), 1)
        owner = next(r for r in claimed if r is not None)
        with worker_lock(self.root), self.assertRaises(RuntimeError):
            self.worker.run(once=True)
        self.assertEqual(self.discovery_store.get(run.id).status, "running")
        self.assertEqual(self.worker.run(once=True), 0)
        self.assertEqual(self.discovery_store.get(run.id).status, "failed")
        with self.assertRaises(ValueError):
            self.discovery_store.finish(owner, "a" * 64, None)
        self.assertEqual(self.model.calls, 0)

    def test_local_only_route_refuses_remote_embedding_without_a_model_call(self):
        config = self.routing.config.model_dump(mode="json")
        config["inventory"]["identity"]["version"] = "remote-negative-control"
        config["inventory"]["models"][1]["locality"] = "remote"
        for policy in config["policies"]:
            policy["inventory"] = config["inventory"]["identity"]
        config["policies"][0]["identity"]["version"] = "remote-negative-control"
        config["system_default"] = config["policies"][0]["identity"]
        self.execution.routing = RoutingService(
            RoutingConfig.model_validate_json(json.dumps(config)),
            SQLiteRoutingJournal(self.database),
        )
        run, _ = self.embed()
        self.assertEqual(run.status, "failed")
        self.assertEqual(self.model.calls, 0)

    def test_browser_submits_only_same_origin_and_shows_verified_groups(self):
        run, _ = self.embed()
        clustered = self.discovery.cluster(run.id, 0.8)
        self.worker.run(once=True)
        client = TestClient(
            create_app(self.service, selections=self.selection_store, discovery=self.discovery),
            base_url="http://localhost",
        )
        response = client.get("/discovery/" + clustered.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn("2 eligible", response.text)
        self.assertIn("Representative", response.text)
        self.assertIn("not human research labels", response.text)

    def test_embedding_browser_preserves_same_origin_submission_boundary(self):
        run, _ = self.embed()
        client = TestClient(
            create_app(self.service, selections=self.selection_store, discovery=self.discovery),
            base_url="http://localhost",
        )
        self.assertIn("2 eligible", client.get("/discovery/" + run.id).text)
        self.assertEqual(
            client.post(
                "/discovery/embed", data={"selection_id": run.request.selection_id}
            ).status_code,
            403,
        )
        response = client.post(
            "/discovery/embed",
            data={"selection_id": run.request.selection_id},
            headers={"Origin": "http://localhost"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)


class VectorTest(unittest.TestCase):
    def test_shape_finiteness_zero_norm_and_outliers(self):
        for vectors in ((), ((0, 0),), ((float("nan"), 1),), ((True, 1),), ((1, 0), (1,))):
            with self.subTest(vectors=vectors), self.assertRaises(ValueError):
                validate_vectors(vectors, max(1, len(vectors)))
        vectors = ((1, 0), (1, 0), (0, 1))
        members = cluster_vectors(("a", "b", "c"), vectors, 0.9, 2)
        self.assertEqual([r["cluster"] for r in members], [0, 0, -1])
        self.assertEqual([r["representative"] for r in members], [True, False, False])
