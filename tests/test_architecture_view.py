"""Architecture views must verify their exact sources and identify stale projections."""

import json
import shutil
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from fastapi.testclient import TestClient

from semantic_reviewer.adapters.architecture import snapshot
from semantic_reviewer.adapters.architecture_projection import ArchitectureProjection
from semantic_reviewer.web.app import create_app

ROOT = Path(__file__).resolve().parents[1]


class ArchitectureViewTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.source = root / "checkout"
        self.source.mkdir()
        for name in ("tach.toml", "pyproject.toml", "uv.lock"):
            shutil.copyfile(ROOT / name, self.source / name)
        (self.source / "src/example").mkdir(parents=True)
        (self.source / "src/example/__init__.py").write_text('VALUE = "before"\n')
        self.view = ArchitectureProjection(root / "external", self.source)

    def test_exact_pair_and_behaviour_only_change_have_distinct_freshness(self):
        before = asdict(snapshot(self.source))
        digest = self.view.publish(before, before)
        self.assertFalse(self.view.read()["stale"])
        (self.source / "src/example/__init__.py").write_text('VALUE = "after"\n')
        view = self.view.read()
        self.assertTrue(view["stale"])
        self.assertEqual(view["digest"], digest)
        # Public interface/dependency records did not change; freshness still must change.
        after = asdict(snapshot(self.source))
        self.assertEqual(before["interfaces"], after["interfaces"])
        self.view.publish(before, after)
        self.assertFalse(self.view.read()["stale"])

    def test_corrupt_projection_and_incorrect_delta_are_not_presented(self):
        value = asdict(snapshot(self.source))
        digest = self.view.publish(value, value)
        path = self.view.files.root / (digest + ".json")
        original = path.read_bytes()
        path.write_text("{}")
        with self.assertRaises(ValueError):
            self.view.read()
        path.write_bytes(original)
        body = json.loads(original)
        body["delta"]["changes"]["modules"]["added"].append({"name": "invented"})
        wrong = self.view.files.write_json(body)
        self.view.pointer.write_text(json.dumps({"digest": wrong}))
        with self.assertRaisesRegex(ValueError, "delta"):
            self.view.read()

    def test_browser_labels_missing_fresh_and_stale_views(self):
        client = TestClient(create_app(None, architecture=self.view), base_url="http://localhost")
        self.assertIn("No architecture projection", client.get("/architecture").text)
        value = asdict(snapshot(self.source))
        digest = self.view.publish(value, value)
        page = client.get("/architecture")
        self.assertEqual(page.status_code, 200)
        self.assertIn(digest, page.text)
        self.assertIn("matches the current source fingerprint", page.text)
        (self.source / "src/example/new.py").write_text("import sqlite3\n")
        self.assertIn("Stale projection", client.get("/architecture").text)

    def test_newline_normalisation_but_lock_or_template_changes_affect_fingerprint(self):
        value = asdict(snapshot(self.source))
        self.view.publish(value, value)
        source = self.source / "src/example/__init__.py"
        source.write_bytes(source.read_text().replace("\n", "\r\n").encode())
        self.assertFalse(self.view.read()["stale"])
        (self.source / "src/example/view.html").write_text("Updated view")
        self.assertTrue(self.view.read()["stale"])
        with self.assertRaises(ValueError):
            self.view.publish({**value, "schema_version": 2}, value)
