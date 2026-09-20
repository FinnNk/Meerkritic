"""Challenge coherent sends, advisory-only MAF execution and explicit uncertain completion."""

import json
import sqlite3
import unittest
from dataclasses import asdict, replace
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import test_interaction
from fastapi.testclient import TestClient

from semantic_reviewer.adapters.guidance import SQLiteGuidance
from semantic_reviewer.adapters.maf_guidance import MafGuidanceRuntime
from semantic_reviewer.adapters.worker_lock import worker_lock
from semantic_reviewer.application.guidance import GuidanceExecution, GuidanceService
from semantic_reviewer.application.jobs import Worker
from semantic_reviewer.application.model import ModelFailure, ModelReply
from semantic_reviewer.domain.guidance import GuidanceRequest, GuidanceTarget
from semantic_reviewer.domain.interaction import DiscussionNote
from semantic_reviewer.routing.usage import Measurement
from semantic_reviewer.web.app import create_app


class AdvisoryModel:
    def __init__(self):
        self.calls, self.mode, self.requests = 0, "success", []

    def generate(self, decision, request, queued_at):
        self.calls += 1
        self.requests.append(request)
        measurement = Measurement(
            started_at=queued_at,
            completed_at=datetime.now(UTC),
            outcome="provider_failure" if self.mode == "provider" else "success",
        )
        if self.mode == "provider":
            raise ModelFailure("Fixture provider failure", measurement)
        context = json.loads(request.user)
        response = {
            "summary": "Consider the exceptions before revising.",
            "responses": [
                {
                    "version_id": "a" * 64 if self.mode == "invented" else target["version_id"],
                    "advice": "Inspect ownership transfer; no edits have been applied.",
                }
                for target in context["targets"]
            ],
        }
        content = "bad JSON" if self.mode == "invalid" else json.dumps(response)
        return ModelReply(content, measurement, json.dumps(asdict(request)), json.dumps(response))


class GuidanceTest(unittest.TestCase):
    complete = test_interaction.InteractionTest.complete
    selection = test_interaction.InteractionTest.selection
    embed = test_interaction.InteractionTest.embed

    def setUp(self):
        test_interaction.InteractionTest.setUp(self)
        self.guidance_store = SQLiteGuidance(self.database)
        self.guidance = GuidanceService(
            self.rules, self.workspace, self.guidance_store, self.files, self.routing.journal
        )
        self.advisor = AdvisoryModel()
        self.guidance_execution = GuidanceExecution(
            self.guidance, self.routing, MafGuidanceRuntime(self.advisor)
        )
        self.worker = Worker(
            self.queue,
            self.routing,
            None,
            lambda: worker_lock(self.root),
            self.execution,
            self.guidance_execution,
        )
        self.note = DiscussionNote(
            id="first-note",
            version_id=self.version,
            actor="Fixture reviewer",
            text="How should ownership transfer be described?",
        )
        self.workspace.discuss(self.note)

    def request(self, **overrides):
        return GuidanceRequest(
            **{
                "id": str(uuid4()),
                "actor": "Fixture reviewer",
                "instruction": "Respond to the selected comments without applying edits.",
                "targets": (
                    GuidanceTarget(
                        version_id=self.version, expected_revision=1, discussion_ids=(self.note.id,)
                    ),
                    GuidanceTarget(version_id=self.other, expected_revision=1),
                ),
                **overrides,
            }
        )

    def test_exact_context_is_frozen_and_response_does_not_apply_human_decisions(self):
        request = self.request()
        run = self.guidance.submit(request)
        self.workspace.discuss(
            self.note.model_copy(update={"id": "later", "text": "Later unsent message"})
        )
        replacement = self.rules.revise(
            self.version, self.definition, "Fixture", "Version changed after send", 1
        )
        self.assertEqual(self.guidance.submit(request)["request_digest"], run["request_digest"])
        self.assertEqual(self.worker.run(once=True), 1)
        final, snapshot, result = self.guidance.inspect(run["id"])
        self.assertEqual(final["status"], "responded")
        self.assertEqual(snapshot["targets"][0]["discussion"], [self.note.model_dump(mode="json")])
        self.assertNotIn("Later unsent", self.advisor.requests[0].user)
        self.assertEqual(result["framework"]["outcome"], "completed")
        self.assertEqual(result["routing"]["policy"]["version"], "3")
        self.assertEqual(self.rule_store.read(replacement)[0].status, "candidate")
        self.assertEqual(self.rule_store.read(self.other)[3], ())
        self.assertEqual(self.guidance.submit(request)["status"], "responded")
        self.worker.run(once=True)
        self.assertEqual(self.advisor.calls, 1)

    def test_stale_or_cross_version_discussion_fails_before_queueing(self):
        for target in (
            GuidanceTarget(version_id=self.version, expected_revision=99),
            GuidanceTarget(
                version_id=self.other, expected_revision=1, discussion_ids=(self.note.id,)
            ),
        ):
            with self.assertRaises(ValueError):
                self.guidance.submit(self.request(targets=(target,)))
        self.assertEqual(self.guidance_store.recent(), ())

    def test_changed_submission_identity_and_invalid_targets_do_not_replace_original(self):
        request = self.request()
        self.guidance.submit(request)
        with self.assertRaises(ValueError):
            self.guidance.submit(request.model_copy(update={"instruction": "Different intent"}))
        with self.assertRaises(ValueError):
            self.request(targets=(request.targets[0], request.targets[0]))
        self.assertEqual(len(self.guidance_store.recent()), 1)

    def test_invalid_or_invented_output_retains_raw_trace_and_provider_failure_is_distinct(self):
        for mode in ("invalid", "invented", "provider"):
            self.advisor.mode = mode
            run = self.guidance.submit(self.request())
            self.worker.run(once=True)
            final, _, result = self.guidance.inspect(run["id"])
            self.assertEqual(final["status"], "failed")
            self.assertIsNone(result["response"])
            expected = "provider_failure" if mode == "provider" else "semantic_failure"
            self.assertEqual(result["usage"]["measurement"]["outcome"], expected)
            if mode != "provider":
                self.assertTrue(result["model_output"])
        self.assertEqual(self.advisor.calls, 3)

    def test_interrupted_response_publication_becomes_unknown_without_replay(self):
        request = self.request()
        self.guidance.submit(request)
        with patch.object(self.guidance_store, "finish", side_effect=RuntimeError("interrupted")):
            with self.assertRaises(RuntimeError):
                self.worker.run(once=True)
        self.worker.run(once=True)
        self.assertEqual(self.guidance_store.get(request.id)["status"], "unknown")
        self.assertEqual(self.advisor.calls, 1)
        self.assertEqual(self.guidance.submit(request)["status"], "unknown")

    def test_corrupt_input_and_terminal_fencing_fail_without_model_calls(self):
        run = self.guidance.submit(self.request())
        (self.files.root / (run["request_digest"] + ".json")).write_text("{}")
        self.worker.run(once=True)
        self.assertEqual(self.guidance_store.get(run["id"])["status"], "failed")
        self.assertEqual(self.advisor.calls, 0)
        with self.assertRaises(ValueError):
            self.guidance_store.finish({**run, "worker_id": "old"}, "a" * 64, None)
        with self.guidance_store.state.connect() as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE guidance_batch SET status='queued' WHERE id=?", (run["id"],))

    def test_browser_is_same_origin_and_identifies_historical_advice(self):
        client = TestClient(
            create_app(
                self.service, rules=self.rules, workspace=self.workspace, guidance=self.guidance
            ),
            base_url="http://localhost",
        )
        fields = {
            "batch_id": "browser-guidance",
            "actor": "Fixture",
            "instruction": "Explain trade-offs",
            "target_0": "yes",
            "version_0": self.version,
            "revision_0": "1",
            "note_0_0": self.note.id,
        }
        self.assertEqual(client.post("/guidance", data=fields).status_code, 403)
        response = client.post("/guidance", data=fields, headers={"Origin": "http://localhost"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("queued", response.text)
        self.worker.run(once=True)
        self.rules.revise(self.version, self.definition, "Fixture", "Later revision", 1)
        page = client.get("/guidance/browser-guidance")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Historical context", page.text)
        self.assertIn("Advisory response", page.text)

    def test_worker_lock_precedes_guidance_recovery(self):
        with (
            worker_lock(self.root),
            patch.object(self.guidance_store, "recover_interrupted") as recover,
        ):
            with self.assertRaises(RuntimeError):
                self.worker.run(once=True)
            recover.assert_not_called()

    def test_application_revalidates_schema_even_when_runtime_returns_constructed_objects(self):
        original = self.guidance_execution.runtime.run

        def inconsistent(*args):
            outcome = original(*args)
            invalid = outcome.response.responses[0].model_copy(update={"advice": ""})
            response = outcome.response.model_copy(
                update={"responses": (invalid, *outcome.response.responses[1:])}
            )
            return replace(outcome, response=response)

        run = self.guidance.submit(self.request())
        with patch.object(self.guidance_execution.runtime, "run", side_effect=inconsistent):
            self.worker.run(once=True)
        final, _, result = self.guidance.inspect(run["id"])
        self.assertEqual(final["status"], "failed")
        self.assertIsNone(result["response"])
        self.assertEqual(result["usage"]["measurement"]["outcome"], "semantic_failure")

    def test_oversized_selected_discussion_is_not_silently_truncated(self):
        notes = []
        for index in range(12):
            note = self.note.model_copy(update={"id": str(index), "text": "x" * 2000})
            self.workspace.discuss(note)
            notes.append(note.id)
        request = self.request(
            targets=(
                GuidanceTarget(
                    version_id=self.version, expected_revision=1, discussion_ids=tuple(notes)
                ),
            )
        )
        with self.assertRaisesRegex(ValueError, "18,000"):
            self.guidance.submit(request)
        self.assertEqual(self.guidance_store.recent(), ())
