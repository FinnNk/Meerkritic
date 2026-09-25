"""Verify append-only corrections without replacing source or model evidence."""

import json
import sqlite3
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import test_annotations

from semantic_reviewer.adapters.annotations import SQLiteAnnotations
from semantic_reviewer.adapters.selections import JsonSelections
from semantic_reviewer.application.selections import SelectionRequest, SelectionService


class AnnotationCorrectionsTest(unittest.TestCase):
    def setUp(self):
        test_annotations.AnnotationsTest.setUp(self)
        self.job = test_annotations.AnnotationsTest.complete(self)
        self.original = self.annotations.decide(self.job.id, "reject", "Original notes")
        self.issue["issue_statement"] = "Approved correction"

    def correct(self, predecessor=None, **overrides):
        values = dict(
            edited_json=json.dumps(self.issue),
            notes="Approved notes",
            reason="Wrong tab saved",
            curator="Owner via authorised operator",
        )
        values.update(overrides)
        return self.annotations.correct(predecessor or self.original.id, **values)

    def test_restart_retains_original_and_selection_versions_without_double_counting(self):
        selections = SelectionService(
            self.store,
            self.queue,
            self.service,
            self.results,
            JsonSelections(self.root / "selections", self.database),
        )
        request = SelectionRequest(
            dataset_id=self.source.id,
            annotation_ids=(self.original.id,),
            purpose="fixture",
            holdout_repositories=(),
        )
        frozen = selections.freeze(request)
        corrected = self.correct()
        fresh = SQLiteAnnotations(self.database)
        self.assertEqual(fresh.get(self.job.id), corrected)
        self.assertEqual(fresh.by_id(self.original.id), self.original)
        self.assertEqual(fresh.by_id(corrected.id), corrected)
        self.assertEqual(len(fresh.history(self.job.observation_id)), 2)
        self.assertEqual(fresh.progress(self.source.id)["reviewed_results"], 1)
        self.assertEqual(fresh.progress(self.source.id)["edit"], 1)
        self.assertEqual(fresh.progress(self.source.id)["reject"], 0)
        self.assertEqual(selections.freeze(request), frozen)
        replacement = selections.freeze(
            request.model_copy(update={"annotation_ids": (corrected.id,)})
        )
        self.assertEqual(replacement.included, 1)
        self.assertEqual(
            selections.store.read(replacement.id)[1].records[0].interpretation.issue_statement,
            "Approved correction",
        )
        self.assertEqual(self.jobs.get(self.job.id).artefact_sha256, self.original.result_sha256)

    def test_concurrent_replay_conflicts_and_stale_original_forms(self):
        with ThreadPoolExecutor(2) as pool:
            records = list(pool.map(lambda _: self.correct(), range(2)))
        self.assertEqual(records[0], records[1])
        with self.assertRaisesRegex(ValueError, "differently"):
            self.correct(notes="Conflicting correction")
        with self.assertRaisesRegex(ValueError, "already has"):
            self.annotations.decide(self.job.id, "reject", "Original notes")
        next_version = self.correct(records[0].id, notes="Later approved correction")
        self.assertEqual(self.store.get(self.job.id), next_version)
        self.assertEqual(self.correct(), records[0])
        self.assertEqual(self.store.get(self.job.id), next_version)
        with self.store.state.connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM event WHERE kind='annotation_corrected'"
                ).fetchone()[0],
                2,
            )
            for table in ("annotation", "annotation_correction"):
                for sql in (f"DELETE FROM {table}", f"UPDATE {table} SET notes='lost'"):
                    with self.assertRaises(sqlite3.IntegrityError):
                        db.execute(sql)

    def test_invalid_requests_and_event_failure_leave_current_version_unchanged(self):
        for kwargs in (
            {"reason": " "},
            {"curator": ""},
            {"notes": "x" * 4001},
            {"edited_json": "{}"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.correct(**kwargs)
        with self.assertRaises(LookupError):
            self.correct("unknown")
        self.issue["evidence_quotes"] = [{"source": "code", "quote": "invented"}]
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            self.correct()
        self.issue["evidence_quotes"] = []
        with self.store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER fail_correction BEFORE INSERT ON event "
                "WHEN NEW.kind='annotation_corrected' "
                "BEGIN SELECT RAISE(ABORT, 'test failure'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.correct()
        self.assertEqual(self.store.get(self.job.id), self.original)
        self.assertEqual(len(self.store.history(self.job.observation_id)), 1)

    def test_competing_edits_commit_only_one_version(self):
        def attempt(notes):
            try:
                return self.correct(notes=notes)
            except ValueError:
                return None

        with ThreadPoolExecutor(2) as pool:
            records = list(pool.map(attempt, ("A", "B")))
        self.assertEqual(sum(item is not None for item in records), 1)
        self.assertEqual(len(self.store.history(self.job.observation_id)), 2)

    def test_store_rejects_cross_result_and_context_substitution(self):
        other = test_annotations.AnnotationsTest.complete(self, 1)
        approved = self.annotations.decide(other.id, "edit", edited_json=json.dumps(self.issue))
        forged = replace(
            approved,
            id="forged",
            job_id=self.job.id,
            observation_id=self.original.observation_id,
            result_sha256=self.original.result_sha256,
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.correct(forged, self.original.id, "reason", "curator")
        valid = self.correct()
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.correct(
                replace(valid, id="bad-context", context_sha256="x" * 64),
                valid.id,
                "reason",
                "curator",
            )
        self.assertEqual(self.store.get(self.job.id), valid)

    def test_cli_preserves_unicode_notes_and_reports_replay_identity(self):
        body = self.root / "approved.json"
        notes = self.root / "notes.txt"
        body.write_text(json.dumps(self.issue), encoding="utf-8")
        notes.write_text("Approved judgement — assisted", encoding="utf-8")
        command = [
            sys.executable,
            str(Path(__file__).parents[1] / "tools/run.py"),
            "--data-root",
            str(self.root),
            "correct-annotation",
            self.original.id,
            "--edited-json",
            str(body),
            "--notes-file",
            str(notes),
            "--reason",
            "Wrong tab",
            "--curator",
            "Owner via operator",
        ]
        first = subprocess.run(command, check=True, capture_output=True, text=True)
        replay = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(first.stdout), json.loads(replay.stdout))
        self.assertEqual(json.loads(first.stdout)["notes"], "Approved judgement — assisted")
