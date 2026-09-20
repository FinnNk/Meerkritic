"""Challenge immutable rule identity, retained evidence and atomic research decisions."""

import json
import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import test_discovery
from fastapi.testclient import TestClient

from semantic_reviewer.adapters.rules import SQLiteRules
from semantic_reviewer.application.rules import RuleService
from semantic_reviewer.domain.rules import (
    RuleDecisionRequest,
    RuleDefinition,
    RuleEvidence,
    RuleOrigin,
)
from semantic_reviewer.web.app import create_app


class RulesTest(unittest.TestCase):
    complete = test_discovery.DiscoveryTest.complete
    selection = test_discovery.DiscoveryTest.selection
    embed = test_discovery.DiscoveryTest.embed

    def setUp(self):
        test_discovery.DiscoveryTest.setUp(self)
        embedded, _ = self.embed()
        self.cluster = self.discovery.cluster(embedded.id, 0.8)
        self.worker.run(once=True)
        self.rule_store = SQLiteRules(self.database, self.files)
        self.rules = RuleService(self.discovery, self.rule_store, self.files)
        self.records = self.rules.cluster_inputs(self.cluster.id, 0)[3]
        self.definition = RuleDefinition(
            statement="Close acquired resources",
            scope="function",
            applicability="A function acquires a resource",
            violation="The resource remains open on an exit path",
            exclusions=("Ownership is explicitly transferred",),
            supporting_annotations=(self.records[0].annotation.id,),
        )
        self.version = self.rules.propose(
            self.cluster.id,
            0,
            self.definition,
            RuleOrigin(
                kind="human", actor="Fixture author", rationale="Synthetic contract exercise"
            ),
        )

    def decision(self, version=None, revision=1, **overrides):
        return RuleDecisionRequest(
            operation_id=str(uuid4()),
            version_id=version or self.version,
            expected_revision=revision,
            action="promote",
            actor="Fixture reviewer",
            rationale="Synthetic research decision; not validation",
            **overrides,
        )

    def counterexample(self, **overrides):
        return RuleEvidence(
            **{
                "id": str(uuid4()),
                "version_id": self.version,
                "annotation_id": self.records[1].annotation.id,
                "kind": "counterexample",
                "verification": "verified",
                "actor": "Fixture reviewer",
                "rationale": "Explicit test attestation for this version",
                **overrides,
            }
        )

    def test_revision_retains_counterexamples_but_does_not_inherit_verification(self):
        counter = self.counterexample()
        self.rules.add_evidence(counter, 1)
        self.rules.add_evidence(counter, 1)
        decision = self.decision(revision=2)
        first = self.rule_store.decide(decision)
        replacement = self.rules.revise(
            self.version,
            self.definition.model_copy(
                update={"statement": "Close acquired resources on every exit"}
            ),
            "Fixture author",
            "Clarify scope",
            3,
        )
        head, body, evidence, decisions = self.rule_store.read(replacement)
        self.assertEqual((head.revision, head.status), (4, "candidate"))
        self.assertEqual(body.parent_version, self.version)
        inherited = next(item for item in evidence if item.kind == "counterexample")
        self.assertEqual((inherited.inherited_from, inherited.verification), (counter.id, "weak"))
        self.assertEqual(self.rule_store.read(self.version)[2][-1].verification, "verified")
        self.assertEqual(self.rule_store.decide(decision), first)
        self.assertEqual(decisions, ())
        self.assertEqual(len(self.rule_store.read(self.version)[3]), 1)
        with self.assertRaises(ValueError):
            self.rule_store.decide(self.decision(revision=4))
        with self.rule_store.state.connect() as db:
            for table in ("rule_version", "rule_evidence", "rule_decision"):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute("DELETE FROM " + table)

    def test_invented_support_and_evidence_fail_before_registration(self):
        with self.assertRaises(ValueError):
            self.rules.propose(
                self.cluster.id,
                0,
                self.definition.model_copy(update={"supporting_annotations": ("invented",)}),
                RuleOrigin(kind="human", actor="Fixture", rationale="Invalid support test"),
            )
        with self.assertRaises(ValueError):
            self.rules.add_evidence(self.counterexample(annotation_id="invented"), 1)
        self.assertEqual(len(self.rule_store.recent()), 1)
        self.assertEqual(self.rule_store.read(self.version)[0].revision, 1)

    def test_concurrent_decisions_fence_one_winner_and_retry_is_idempotent(self):
        requests = [self.decision(), self.decision()]

        def apply(request):
            try:
                return self.rule_store.decide(request)
            except ValueError:
                return None

        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(apply, requests))
        self.assertEqual(sum(item is not None for item in results), 1)
        winner = requests[next(i for i, item in enumerate(results) if item is not None)]
        self.assertEqual(self.rule_store.decide(winner), next(item for item in results if item))
        with self.assertRaises(ValueError):
            self.rule_store.decide(winner.model_copy(update={"rationale": "Changed intent"}))
        self.assertEqual(self.rule_store.read(self.version)[0].status, "promoted")

    def test_event_failure_rolls_back_decision_and_restart_preserves_candidate(self):
        with self.rule_store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER reject_rule_event BEFORE INSERT ON event "
                "WHEN NEW.kind='rule_decided' BEGIN SELECT RAISE(ABORT,'fixture'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.rule_store.decide(self.decision())
        head, _, _, decisions = SQLiteRules(self.database, self.files).read(self.version)
        self.assertEqual((head.status, head.revision), ("candidate", 1))
        self.assertEqual(decisions, ())

    def test_corrupt_body_is_not_presented_as_a_verified_candidate(self):
        (self.files.root / (self.version + ".json")).write_text("{}")
        with self.assertRaises(ValueError):
            self.rule_store.read(self.version)
        with self.assertRaises(ValueError):
            self.rule_store.decide(self.decision())
        with self.rule_store.state.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM rule_decision").fetchone()[0], 0)

    def test_rule_browser_labels_claims_and_preserves_stale_submission_values(self):
        client = TestClient(
            create_app(self.service, discovery=self.discovery, rules=self.rules),
            base_url="http://localhost",
        )
        page = client.get("/rules/" + self.version)
        self.assertEqual(page.status_code, 200)
        self.assertIn("not validation, enforcement or deployment", page.text)
        fields = {
            "operation_id": str(uuid4()),
            "revision": "1",
            "action": "promote",
            "actor": "Fixture reviewer",
            "rationale": "Keep this submitted rationale",
        }
        self.assertEqual(
            client.post("/rules/" + self.version + "/decide", data=fields).status_code, 403
        )
        self.rules.add_evidence(self.counterexample(), 1)
        response = client.post(
            "/rules/" + self.version + "/decide",
            data=fields,
            headers={"Origin": "http://localhost"},
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn(fields["rationale"], response.text)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "candidate")
        fields["revision"] = "2"
        response = client.post(
            "/rules/" + self.version + "/decide",
            data=fields,
            headers={"Origin": "http://localhost"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "promoted")

    def test_wrong_model_trace_cannot_be_registered(self):
        digest = self.files.write_json({"cluster_run": self.cluster.id, "cluster_digest": "a" * 64})
        with self.assertRaises(ValueError):
            self.rules.propose(
                self.cluster.id,
                0,
                self.definition,
                RuleOrigin(
                    kind="model",
                    actor="fixture model",
                    rationale="Wrong input trace",
                    trace_digest=digest,
                ),
            )

    def test_revision_bound_retains_every_counterexample_without_partial_publication(self):
        # Populate the storage boundary directly: exercising 999 UI transactions is incidental.
        with self.rule_store.state.connect() as db:
            for _ in range(999):
                self.rule_store._insert_evidence(db, self.counterexample())
        replacement = self.definition.model_copy(
            update={"supporting_annotations": (self.records[1].annotation.id,)}
        )
        with self.assertRaisesRegex(ValueError, "1000-link"):
            self.rules.revise(self.version, replacement, "Fixture", "New support", 1)
        head, _, evidence, _ = self.rule_store.read(self.version)
        self.assertEqual((head.version_id, head.revision, len(evidence)), (self.version, 1, 1000))
        with self.rule_store.state.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM rule_version").fetchone()[0], 1)

    def test_invalid_revision_cannot_be_coerced_into_a_current_write(self):
        for revision in (True, 1.0, "1", 0):
            with self.assertRaises(ValueError):
                self.rules.add_evidence(self.counterexample(), revision)
        self.assertEqual(self.rule_store.read(self.version)[0].revision, 1)

    def test_old_rule_version_stays_readable_after_definition_changes(self):
        original = (self.files.root / (self.version + ".json")).read_bytes()
        replacement = self.rules.revise(
            self.version,
            self.definition.model_copy(update={"statement": "Close resources before returning"}),
            "Fixture author",
            "Revision fixture",
            1,
        )
        self.assertNotEqual(self.version, replacement)
        self.assertEqual((self.files.root / (self.version + ".json")).read_bytes(), original)
        self.assertEqual(self.rule_store.read(self.version)[1].definition, self.definition)
        self.assertEqual(json.loads(original)["origin"]["kind"], "human")
