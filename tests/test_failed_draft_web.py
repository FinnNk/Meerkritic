"""Exercise correction controls on synthetic failures without producing research judgements."""

import json
import unittest

import test_failed_drafts
from fastapi.testclient import TestClient

from semantic_reviewer.web.app import create_app


class FailedDraftWebTest(unittest.TestCase):
    def setUp(self):
        test_failed_drafts.FailedDraftTest.setUp(self)
        self.client = TestClient(
            create_app(self.service, self.queue, self.annotations), base_url="http://127.0.0.1"
        )
        self.headers = {"Origin": "http://127.0.0.1"}

    failed = test_failed_drafts.FailedDraftTest.failed

    def test_failed_draft_exposes_source_and_edit_reject_but_never_accept(self):
        job = self.failed(output="<script>untrusted draft</script>")
        page = self.client.get(f"/jobs/{job.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Source for your assessment", page.text)
        self.assertIn("&lt;script&gt;untrusted draft", page.text)
        self.assertNotIn("<script>", page.text)
        self.assertIn('value="edit"', page.text)
        self.assertIn('value="reject"', page.text)
        self.assertNotIn('value="accept"', page.text)
        self.assertEqual(
            self.client.post(
                f"/jobs/{job.id}/annotation", data={"decision": "accept"}, headers=self.headers
            ).status_code,
            409,
        )
        self.assertIsNone(self.store.get(job.id))

    def test_invalid_edit_stays_visible_then_valid_correction_preserves_failure(self):
        job = self.failed()
        url = f"/jobs/{job.id}/annotation"
        response = self.client.post(
            url,
            data={
                "decision": "edit",
                "edited_json": "<script>my draft</script>",
                "notes": "Keep my note",
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("&lt;script&gt;my draft", response.text)
        self.assertIn("Keep my note", response.text)
        self.assertIsNone(self.store.get(job.id))
        response = self.client.post(
            url,
            data={"decision": "edit", "edited_json": json.dumps(self.issue)},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Human interpretation", response.text)
        self.assertIn("Synthetic evidence validation failure", response.text)
        self.assertIn("This decision is recorded", response.text)
        self.assertNotIn('value="edit"', response.text)
        self.assertEqual(self.jobs.get(job.id), job)

    def test_rejection_updates_failed_review_count_without_inventing_success(self):
        job = self.failed()
        response = self.client.post(
            f"/jobs/{job.id}/annotation",
            data={"decision": "reject", "notes": "Synthetic rejection"},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        progress = self.client.get(f"/datasets/{self.source.id}/progress")
        self.assertIn("<strong>0 / 0</strong> successful", progress.text)
        self.assertIn("<strong>1 / 1</strong> failed", progress.text)
        self.assertEqual(self.jobs.get(job.id), job)

    def test_infrastructure_failure_has_inspection_but_no_decision_controls(self):
        job = self.failed(outcome="provider_failure")
        page = self.client.get(f"/jobs/{job.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("No reviewable model draft", page.text)
        for action in ("accept", "edit", "reject"):
            self.assertNotIn(f'value="{action}"', page.text)
