"""Challenge staged intent, atomic multi-target decisions and version-bound discussion."""

import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import test_rules
from fastapi.testclient import TestClient

from semantic_reviewer.adapters.interaction import SQLiteReviewWorkspace
from semantic_reviewer.domain.interaction import DiscussionNote, ReviewDraft, ReviewIntent
from semantic_reviewer.domain.rules import RuleOrigin
from semantic_reviewer.web.app import create_app


class InteractionTest(unittest.TestCase):
    complete = test_rules.RulesTest.complete
    selection = test_rules.RulesTest.selection
    embed = test_rules.RulesTest.embed
    decision = test_rules.RulesTest.decision
    counterexample = test_rules.RulesTest.counterexample

    def setUp(self):
        test_rules.RulesTest.setUp(self)
        self.workspace = SQLiteReviewWorkspace(self.database, self.files)
        self.other = self.rules.propose(
            self.cluster.id,
            0,
            self.definition,
            RuleOrigin(kind="human", actor="Fixture", rationale="Second atomic target"),
        )

    def draft(self, *intents):
        return ReviewDraft(actor="Fixture reviewer", intents=intents or (self.intent(),))

    def intent(self, version=None, revision=1, action="promote"):
        return ReviewIntent(
            version_id=version or self.version,
            expected_revision=revision,
            action=action,
            rationale="Retain this research intent",
        )

    def apply_action(self, action, revision):
        identity = str(uuid4())
        self.workspace.save(
            identity, None, self.draft(self.intent(revision=revision, action=action))
        )
        return self.workspace.apply(identity, 1)

    def test_draft_survives_restart_without_applying_and_retry_applies_once(self):
        body = self.draft(self.intent(), self.intent(self.other, action="reject"))
        self.workspace.save("first", None, body)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "candidate")
        restarted = SQLiteReviewWorkspace(self.database, self.files)
        self.assertEqual(restarted.read("first")[1], body)
        first = restarted.apply("first", 1)
        self.assertEqual(restarted.apply("first", 1), first)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "promoted")
        self.assertEqual(self.rule_store.read(self.other)[0].status, "rejected")
        self.assertEqual(len(restarted.history(self.version)), 1)
        self.assertEqual(restarted.task(self.version)["state"], "answered")
        with self.assertRaises(ValueError):
            restarted.save("first", 1, body)

    def test_later_target_conflict_rolls_back_every_decision_and_retains_draft(self):
        body = self.draft(self.intent(), self.intent(self.other, revision=99))
        self.workspace.save("conflict", None, body)
        with self.assertRaisesRegex(ValueError, self.other):
            self.workspace.apply("conflict", 1)
        for version in (self.version, self.other):
            head, _, _, decisions = self.rule_store.read(version)
            self.assertEqual((head.status, head.revision, decisions), ("candidate", 1, ()))
            self.assertEqual(self.workspace.history(version), ())
        self.assertEqual(self.workspace.read("conflict")[1], body)
        with self.workspace.state.connect() as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM event WHERE kind='rule_decided'").fetchone()[0], 0
            )

    def test_concurrent_drafts_cannot_both_apply_and_loser_remains_saved(self):
        for identity in ("a", "b"):
            self.workspace.save(identity, None, self.draft())

        def apply(identity):
            try:
                return self.workspace.apply(identity, 1)
            except ValueError:
                return None

        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(apply, ("a", "b")))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(
            sorted(item["status"] for item in self.workspace.recent()), ["applied", "saved"]
        )

    def test_event_failure_rolls_back_batch_and_restart_keeps_saved_intent(self):
        self.workspace.save("rollback", None, self.draft())
        with self.workspace.state.connect() as db:
            db.execute(
                "CREATE TRIGGER fail_apply BEFORE INSERT ON event "
                "WHEN NEW.kind='review_draft_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.workspace.apply("rollback", 1)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "candidate")
        self.assertEqual(
            SQLiteReviewWorkspace(self.database, self.files).read("rollback")[0]["status"], "saved"
        )

    def test_lifecycle_requires_explicit_reopen_and_retains_prior_answers(self):
        self.apply_action("defer", 1)
        self.assertEqual(self.workspace.task(self.version)["state"], "deferred")
        with self.assertRaises(ValueError):
            self.rule_store.decide(self.decision(revision=2))
        self.apply_action("reopen", 2)
        self.assertEqual(self.workspace.task(self.version)["state"], "reopened")
        self.apply_action("promote", 3)
        self.apply_action("reopen", 4)
        self.apply_action("reject", 5)
        self.assertEqual(len(self.rule_store.read(self.version)[3]), 2)
        replacement = self.rules.revise(
            self.version, self.definition, "Fixture", "Revision preserves prior answers", 6
        )
        self.assertEqual(
            self.workspace.task(self.version),
            {"version_id": self.version, "state": "superseded", "replacement": replacement},
        )
        self.assertEqual(self.workspace.task(replacement)["state"], "pending")
        self.assertEqual(len(self.workspace.history(self.version)), 5)

    def test_draft_revision_conflict_and_corrupt_payload_do_not_apply(self):
        self.workspace.save("editable", None, self.draft())
        changed = self.draft(self.intent(action="reject"))
        second = self.workspace.save("editable", 1, changed)
        with self.assertRaises(ValueError):
            self.workspace.apply("editable", 1)
        self.assertEqual(self.workspace.read("editable")[1], changed)
        (self.files.root / (second["digest"] + ".json")).write_text("{}")
        with self.assertRaises(ValueError):
            self.workspace.apply("editable", 2)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "candidate")

    def test_discussion_retries_and_historical_version_never_move_the_message(self):
        note = DiscussionNote(
            id="note", version_id=self.version, actor="Fixture", text="<script>question</script>"
        )
        self.workspace.discuss(note)
        self.workspace.discuss(note)
        with self.assertRaises(ValueError):
            self.workspace.discuss(note.model_copy(update={"text": "Different intent"}))
        replacement = self.rules.revise(self.version, self.definition, "Fixture", "New version", 1)
        self.assertEqual(self.workspace.discussion(self.version), (note,))
        self.assertEqual(self.workspace.discussion(replacement), ())
        with self.workspace.state.connect() as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM rule_discussion")

    def test_browser_save_apply_conflict_and_discussion_preserve_intent(self):
        client = TestClient(
            create_app(self.service, rules=self.rules, workspace=self.workspace),
            base_url="http://localhost",
        )
        fields = {
            "draft_id": "browser",
            "actor": "Fixture",
            "version_0": self.version,
            "revision_0": "1",
            "action_0": "promote",
            "rationale_0": "Keep my rationale",
        }
        self.assertEqual(client.post("/review-workspace/save", data=fields).status_code, 403)
        headers = {"Origin": "http://localhost"}
        response = client.post("/review-workspace/save", data=fields, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Save draft only", response.text)
        self.assertEqual(self.rule_store.read(self.version)[0].status, "candidate")
        self.rules.add_evidence(self.counterexample(), 1)
        response = client.post(
            "/review-workspace/apply",
            data={"draft_id": "browser", "revision": "1"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("Keep my rationale", response.text)
        self.assertIn(self.version, response.text)
        note = DiscussionNote(
            id="web-note",
            version_id=self.version,
            actor="Fixture",
            text="<script>do not execute</script>",
        )
        self.workspace.discuss(note)
        page = client.get("/rules/" + self.version)
        self.assertIn("&lt;script&gt;do not execute&lt;/script&gt;", page.text)
