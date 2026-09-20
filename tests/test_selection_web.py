"""Verify frozen input inspection, HTML escaping and honest evidence failures."""

import unittest

import test_selections
from fastapi.testclient import TestClient

from semantic_reviewer.asgi import build_app


class SelectionWebTest(unittest.TestCase):
    setUp = test_selections.SelectionsTest.setUp
    complete = test_selections.SelectionsTest.complete
    choose = test_selections.SelectionsTest.choose
    request = test_selections.SelectionsTest.request

    def test_restart_browses_frozen_source_exclusions_and_annotation_identity(self):
        first, rejected = self.choose(), self.choose(1, "reject")
        summary = self.selections.freeze(self.request(first, rejected))
        with TestClient(build_app(self.root), base_url="http://127.0.0.1") as client:
            catalogue = client.get("/selections")
            self.assertEqual(catalogue.status_code, 200)
            self.assertIn(summary.id, catalogue.text)
            detail = client.get(f"/selections/{summary.id}")
            self.assertEqual(detail.status_code, 200)
            for text in (
                "1 included",
                "1 excluded",
                "not human research labels",
                "uncertain",
                "Excluded: rejected interpretation",
                first.id,
                "&lt;script&gt;x()&lt;/script&gt;",
            ):
                self.assertIn(text, detail.text)
            self.assertNotIn("<script>x()</script>", detail.text)
            self.assertIn(first.id, client.get(f"/jobs/{first.job_id}").text)
            self.assertIn("No records", client.get(f"/selections/{summary.id}?page=2").text)
            self.assertEqual(client.get(f"/selections/{summary.id}?page=0").status_code, 422)
            self.assertEqual(client.get("/selections?page=1000001").status_code, 422)

    def test_unknown_missing_and_corrupt_snapshot_are_distinct_failures(self):
        summary = self.selections.freeze(self.request(self.choose()))
        path = self.selection_store.root / (summary.id + ".json")
        with TestClient(build_app(self.root), base_url="http://127.0.0.1") as client:
            self.assertEqual(client.get("/selections/" + "a" * 64).status_code, 404)
            path.write_bytes(b"{}")
            response = client.get(f"/selections/{summary.id}")
            self.assertEqual(response.status_code, 409)
            self.assertNotIn(str(self.root), response.text)
            path.unlink()
            self.assertEqual(client.get(f"/selections/{summary.id}").status_code, 409)
            self.assertEqual(client.post("/selections").status_code, 405)
