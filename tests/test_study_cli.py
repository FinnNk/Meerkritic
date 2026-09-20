"""Verify command publication and prospective registration checks without research judgements."""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_comparison

from semantic_reviewer.adapters.discovery import ParquetDiscovery
from semantic_reviewer.domain.study import digest
from tools import study_compare


class StudyCommandTest(unittest.TestCase):
    setUp = test_comparison.ComparisonTest.setUp
    complete = test_comparison.ComparisonTest.complete
    selection = test_comparison.ComparisonTest.selection
    embed = test_comparison.ComparisonTest.embed
    prepare = test_comparison.ComparisonTest.prepare

    def command(self, *arguments):
        """Exercise argument parsing and real immutable files over the synthetic runtime."""
        output = io.StringIO()
        args = [
            "study_compare.py",
            "--data-root",
            str(self.root),
            "--evidence",
            str(self.root / "study"),
            *map(str, arguments),
        ]
        with (
            patch.object(sys, "argv", args),
            contextlib.redirect_stdout(output),
            patch.object(study_compare, "build_discovery", return_value=self.discovery),
        ):
            code = study_compare.main()
        return code, json.loads(output.getvalue()) if output.getvalue() else None

    def test_complete_fixture_flow_freezes_ratings_and_reports_insufficiency(self):
        lexical, attempts, _ = self.prepare()
        code, first = self.command("baseline", lexical["selection_id"])
        self.assertEqual(code, 0)
        request = self.root / "attempts.json"
        request.write_text(json.dumps(attempts))
        code, packed = self.command("pack", first["baseline_sha256"], "--attempts", request)
        self.assertEqual(code, 0)
        self.assertEqual(packed["status"], "insufficient")
        files = ParquetDiscovery(self.root / "study")
        ratings = files.read_json(packed["ratings_template_sha256"])
        ratings["rater"] = "Synthetic fixture"
        for item in ratings["ratings"]:
            item.update(judgement="uncertain", reason="Synthetic test only")
        supplied = self.root / "ratings.json"
        supplied.write_text(json.dumps(ratings))
        code, analysed = self.command("analyse", packed["comparison_sha256"], "--ratings", supplied)
        self.assertEqual(code, 0)
        self.assertEqual(files.read_json(analysed["ratings_sha256"]), ratings)
        report = files.read_json(analysed["report_sha256"])["report"]
        self.assertEqual(report["status"], "insufficient")
        self.assertEqual(report["purpose"], "fixture")
        self.assertEqual(report["recommendation"], "no adoption recommendation")
        # A modified rating pack cannot silently become the evidence behind the old digest.
        (self.root / "study" / (packed["pack_sha256"] + ".json")).write_text("{}")
        with self.assertRaises(ValueError):
            files.read_json(packed["pack_sha256"])


class RegistrationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git("init")
        self.git("config", "user.name", "Synthetic test")
        self.git("config", "user.email", "test@example.invalid")
        self.document = self.root / study_compare.EDR
        self.document.parent.mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "src/module.py").write_text("# Fixture\n")
        self.profile = {"dimensions": 768}
        self.selection = "a" * 64
        self.plan_text = (
            f"- Status: draft\n- Selection: `{self.selection}`\n"
            f"- Embedding profile: `{digest(self.profile)}`\n"
        )
        self.document.write_text(self.plan_text)
        self.git("add", ".")
        self.git("commit", "-m", "test: complete prospective plan")
        self.plan = self.git("rev-parse", "HEAD").strip()
        self.document.write_text(
            self.plan_text.replace("draft", "registered") + f"- Registered plan: `{self.plan}`\n"
        )
        self.git("add", ".")
        self.git("commit", "-m", "test: register completed plan")
        self.commit = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        """Use isolated local fixture Git state, never a project remote or credential."""
        return subprocess.run(
            ["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True
        ).stdout

    def test_two_commit_registration_and_profile_binding(self):
        record = study_compare.registration(
            "research", self.selection, self.commit, self.profile, self.root
        )
        self.assertEqual(record["plan_commit"], self.plan)
        for selection, commit, profile in (
            ("b" * 64, self.commit, self.profile),
            (self.selection, self.plan, self.profile),
            (self.selection, None, self.profile),
            (self.selection, self.commit, {"dimensions": 3}),
        ):
            with self.subTest(commit=commit), self.assertRaises(ValueError):
                study_compare.registration("research", selection, commit, profile, self.root)

    def test_changed_or_untracked_implementation_cannot_claim_registered_code(self):
        (self.root / "src/new.py").write_text("# Unregistered\n")
        with self.assertRaises(ValueError):
            study_compare.registration("research", self.selection, self.commit, root=self.root)
        (self.root / "src/new.py").unlink()
        (self.root / "src/module.py").write_text("# Changed\n")
        with self.assertRaises(subprocess.CalledProcessError):
            study_compare.registration("research", self.selection, self.commit, root=self.root)

    def test_fixtures_do_not_claim_registration(self):
        self.assertIsNone(study_compare.registration("fixture", self.selection, None))
        with self.assertRaises(ValueError):
            study_compare.registration("fixture", self.selection, self.commit)

    def test_execution_before_registration_is_not_eligible(self):
        with self.assertRaises(ValueError):
            study_compare._after_registration(
                {"registered_at": "2026-09-20T12:00:00+00:00"}, "2026-09-20T11:00:00+00:00"
            )
