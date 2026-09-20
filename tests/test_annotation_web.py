"""Verify immediate browser decisions, error retention and local mutation boundaries."""

import json
import unittest
from threading import get_ident
from unittest.mock import patch

import test_annotations
from fastapi.testclient import TestClient

from semantic_reviewer.web.app import create_app


class AnnotationWebTest(unittest.TestCase):
    def setUp(self):
        test_annotations.AnnotationsTest.setUp(self)
        self.job = test_annotations.AnnotationsTest.complete(self)
        self.client = TestClient(
            create_app(self.service, self.queue, self.annotations), base_url="http://127.0.0.1"
        )
        self.url = f"/jobs/{self.job.id}/annotation"
        self.headers = {"Origin": "http://127.0.0.1"}

    def test_actions_persist_immediately_and_progress_survives_new_app(self):
        page = self.client.get(f"/jobs/{self.job.id}")
        for action in ("Accept", "Edit", "Reject"):
            self.assertIn(f">{action}</button>", page.text)
        response = self.client.post(
            self.url,
            data={"decision": "reject", "notes": "Unsupported claim"},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("This decision is recorded", response.text)
        self.assertNotIn('value="accept"', response.text)
        restarted = TestClient(
            create_app(self.service, self.queue, self.annotations), base_url="http://127.0.0.1"
        )
        progress = restarted.get(f"/datasets/{self.source.id}/progress")
        self.assertIn("1 / 1", progress.text)
        self.assertIn("Unsupported claim", restarted.get(f"/jobs/{self.job.id}").text)
        conflict = self.client.post(self.url, data={"decision": "accept"}, headers=self.headers)
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(self.store.get(self.job.id).decision, "reject")

    def test_review_explains_field_meanings_without_changing_original_draft(self):
        original = self.queue.inspect(self.job.id)
        page = self.client.get(f"/jobs/{self.job.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn('class="source-panel" open', page.text)
        self.assertIn("Your task: assess the interpretation", page.text)
        self.assertIn("Impact scope", page.text)
        self.assertIn("Assessment notes and evidence limitations", page.text)
        self.assertIn("Put missing evidence and investigation needs in notes", page.text)
        self.assertEqual(self.queue.inspect(self.job.id), original)
        self.assertIsNone(self.store.get(self.job.id))

    def test_unknown_scope_and_separate_notes_survive_edit_and_restart(self):
        original_job, original_body = self.queue.inspect(self.job.id)
        self.issue.update(scope="unknown", exclusions=["Caller already checks the condition."])
        notes = "Evidence limitation: caller not supplied. Investigation: inspect callers."
        response = self.client.post(
            self.url,
            data={"decision": "edit", "edited_json": json.dumps(self.issue), "notes": notes},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        restarted = TestClient(
            create_app(self.service, self.queue, self.annotations), base_url="http://127.0.0.1"
        )
        self.assertIn(notes, restarted.get(f"/jobs/{self.job.id}").text)
        annotation, edited = self.annotations.review(self.job.id)
        self.assertEqual(annotation.notes, notes)
        self.assertEqual(edited["interpretation"], self.issue)
        self.assertNotIn("Evidence limitation", json.dumps(edited["interpretation"]))
        self.assertEqual(self.queue.inspect(self.job.id), (original_job, original_body))
        self.assertEqual(self.store.progress(self.source.id)["edit"], 1)

    def test_invalid_edit_preserves_draft_and_escapes_model_and_human_text(self):
        response = self.client.post(
            self.url,
            data={
                "decision": "edit",
                "edited_json": "<script>draft</script>",
                "notes": "<script>note</script>",
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("&lt;script&gt;draft", response.text)
        self.assertNotIn("<script>", response.text)
        self.issue["issue_statement"] = "<script>human</script>"
        response = self.client.post(
            self.url,
            data={"decision": "edit", "edited_json": json.dumps(self.issue)},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Human interpretation", response.text)
        self.assertNotIn("<script>", response.text)

    def test_rejects_cross_origin_oversized_duplicate_and_invalid_forms(self):
        for headers in ({}, {"Origin": "https://evil.example"}):
            self.assertEqual(
                self.client.post(
                    self.url, data={"decision": "accept"}, headers=headers
                ).status_code,
                403,
            )
        headers = self.headers | {"Content-Type": "application/x-www-form-urlencoded"}
        for body in ("decision=accept&decision=reject", "unknown=value", "%FF=value"):
            self.assertEqual(
                self.client.post(self.url, content=body, headers=headers).status_code, 422
            )
        self.assertEqual(
            self.client.post(self.url, content="x" * 1_000_001, headers=headers).status_code, 413
        )
        self.assertEqual(
            self.client.post(
                self.url, json={"decision": "accept"}, headers=self.headers
            ).status_code,
            415,
        )
        self.assertIsNone(self.store.get(self.job.id))

    def test_synchronous_storage_runs_outside_the_asgi_event_loop(self):
        loop_thread = []
        storage_thread = []

        @self.client.app.middleware("http")
        async def record_loop(request, call_next):
            loop_thread.append(get_ident())
            return await call_next(request)

        decide = self.annotations.decide

        def observed_decide(*args):
            storage_thread.append(get_ident())
            return decide(*args)

        with patch.object(self.annotations, "decide", observed_decide):
            response = self.client.post(
                self.url, data={"decision": "accept"}, headers=self.headers, follow_redirects=False
            )
        self.assertEqual(response.status_code, 303)
        self.assertNotEqual(loop_thread[0], storage_thread[0])
