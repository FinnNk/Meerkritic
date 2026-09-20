"""Verify external readiness references remain distinct from approval or evidence truth."""

import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from semantic_reviewer.adapters.reviews import SQLiteReviewIndex
from semantic_reviewer.web.app import create_app


class ReviewReferencesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = SQLiteReviewIndex(self.root / "runtime" / "state.sqlite3")
        self.manifest = self.root / "manifest.json"
        self.event = self.root / "event.json"
        self.m = {
            "pair_id": "example",
            "round_id": "r1",
            "diary": {"tip": "a" * 40},
            "semantic": {"tip": "b" * 40},
        }
        self.e = {
            "pair_id": "example",
            "round_id": "r1",
            "sequence": 1,
            "payload": {"stage": "locally_prepared", "diary": "a" * 40, "semantic": "b" * 40},
        }
        self.write()

    def write(self):
        self.manifest.write_text(json.dumps(self.m), encoding="utf-8")
        self.event.write_text(json.dumps(self.e), encoding="utf-8")

    def test_idempotent_reference_and_tamper_detection_without_readiness_inference(self):
        original = self.index.index(self.manifest, self.event)
        self.assertEqual(self.index.index(self.manifest, self.event), original)
        self.assertEqual(self.index.references()[0][1], "unchanged")
        self.e["payload"]["stage"] = "integrated"
        self.write()
        self.assertEqual(self.index.references()[0][1], "changed")
        with self.assertRaisesRegex(ValueError, "cannot be replaced"):
            self.index.index(self.manifest, self.event)
        self.assertEqual(self.index.references()[0][0].stage, "locally_prepared")
        self.event.unlink()
        self.assertEqual(self.index.references()[0][1], "unavailable")

    def test_rejects_wrong_round_source_heads_unbounded_input_and_git_worktree(self):
        self.e["payload"]["semantic"] = "c" * 40
        self.write()
        with self.assertRaises(ValueError):
            self.index.index(self.manifest, self.event)
        self.event.write_text("x" * 1_000_001, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "limit"):
            self.index.index(self.manifest, self.event)
        self.write()
        (self.root / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "outside"):
            self.index.index(self.manifest, self.event)

    def test_later_explicit_event_is_visible_but_not_an_owner_approval(self):
        self.index.index(self.manifest, self.event)
        self.e["sequence"] = 2
        self.e["payload"]["stage"] = "owner_review_ready"
        self.event = self.root / "event-2.json"
        self.write()
        self.index.index(self.manifest, self.event)
        self.assertEqual(len(self.index.references()), 1)
        client = TestClient(create_app(None, reviews=self.index), base_url="http://127.0.0.1")
        response = client.get("/reviews")
        self.assertEqual(response.status_code, 200)
        self.assertIn("owner_review_ready", response.text)
        self.assertIn("separate from slice status and owner approval", response.text)
        self.assertEqual(client.get("/reviews", headers={"Host": "evil.example"}).status_code, 400)
