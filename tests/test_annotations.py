"""Exercise durable human judgement, edit grounding and transactional retries."""

import json
import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import patch

import test_jobs

from semantic_reviewer.adapters.annotations import SQLiteAnnotations
from semantic_reviewer.application.annotations import AnnotationService
from semantic_reviewer.application.artefacts import Publication


class AnnotationsTest(unittest.TestCase):
    def setUp(self):
        test_jobs.JobsTest.setUp(self)
        self.store = SQLiteAnnotations(self.database)
        self.annotations = AnnotationService(self.queue, self.store)
        self.issue = {
            "actionable_engineering_concern": "uncertain",
            "issue_statement": "Needs assessment",
            "coarse_categories": ["maintainability"],
            "scope": "function",
            "generalisable": "uncertain",
            "proposed_invariant": None,
            "evidence_quotes": [],
            "exclusions": [],
        }

    def complete(self, index=0):
        job = self.queue.enqueue(self.source.id, index)
        claimed = self.jobs.claim("test")
        digest = self.results.publish(
            {"job_id": job.id, "interpretation": self.issue}, Publication(job.id, "normalisation")
        )
        self.jobs.finish(claimed, digest, None)
        return job

    def test_concurrent_identical_submission_is_one_decision_and_event_after_restart(self):
        job = self.complete()
        with ThreadPoolExecutor(2) as pool:
            records = list(pool.map(lambda _: self.annotations.decide(job.id, "accept"), range(2)))
        self.assertEqual(records[0], records[1])
        self.assertEqual(SQLiteAnnotations(self.database).get(job.id), records[0])
        with self.store.state.connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM event WHERE kind='annotation_recorded'"
                ).fetchone()[0],
                1,
            )
            for sql in ("DELETE FROM annotation", "UPDATE annotation SET decision='reject'"):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute(sql)
        with self.assertRaisesRegex(ValueError, "already has"):
            self.annotations.decide(job.id, "reject")

    def test_edit_preserves_model_result_and_checks_source_evidence(self):
        job = self.complete()
        original = self.jobs.get(job.id).artefact_sha256
        source = self.service.browse(self.source.id, 1, 1).items[0]
        self.issue.update(
            issue_statement="Human correction",
            actionable_engineering_concern="yes",
            evidence_quotes=[{"source": "comment", "quote": source.comment}],
        )
        annotation = self.annotations.decide(job.id, "edit", "Corrected", json.dumps(self.issue))
        self.assertEqual(self.jobs.get(job.id).artefact_sha256, original)
        self.assertNotEqual(annotation.interpretation_sha256, original)
        self.assertEqual(self.annotations.review(job.id)[1]["evidence_spans"][0]["start"], 0)
        other = self.complete()
        self.issue["evidence_quotes"][0]["quote"] = "invented source evidence"
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            self.annotations.decide(other.id, "edit", edited_json=json.dumps(self.issue))
        self.assertIsNone(self.store.get(other.id))

    def test_progress_distinguishes_runs_from_sources_and_reject_is_reviewed(self):
        for decision in ("accept", "edit", "reject"):
            job = self.complete()
            self.annotations.decide(
                job.id, decision, edited_json=json.dumps(self.issue) if decision == "edit" else None
            )
        waiting = self.complete(1)
        progress = self.store.progress(self.source.id)
        self.assertEqual(progress["reviewed_sources"], 1)
        self.assertEqual(progress["reviewed_results"], 3)
        self.assertEqual(progress["successful_results"], 4)
        self.assertEqual([progress[key] for key in ("accept", "edit", "reject")], [1, 1, 1])
        self.assertEqual(self.store.pending(self.source.id, 1), (waiting.id,))
        self.assertEqual(len(self.store.history(job.observation_id)), 3)

    def test_reject_nonterminal_invalid_or_corrupt_submissions_without_event(self):
        job = self.queue.enqueue(self.source.id, 0)
        for decision in ("accept", "uncertain"):
            with self.assertRaises(ValueError):
                self.annotations.decide(job.id, decision)
        self.jobs.finish(self.jobs.claim("test"), None, "provider unavailable")
        with self.assertRaises(ValueError):
            self.annotations.decide(job.id, "reject")
        job = self.complete()
        for action, edit in (("edit", None), ("accept", "{}"), ("edit", "{}")):
            with self.assertRaises(ValueError):
                self.annotations.decide(job.id, action, edited_json=edit)
        digest = self.jobs.get(job.id).artefact_sha256
        (self.results.root / (digest + ".json")).write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.annotations.decide(job.id, "accept")
        self.assertIsNone(self.store.get(job.id))

    def test_event_failure_rolls_back_the_annotation(self):
        job = self.complete()
        with self.store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER fail_annotation_event BEFORE INSERT ON event "
                "WHEN NEW.kind='annotation_recorded' BEGIN SELECT RAISE(ABORT, 'test failure'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.annotations.decide(job.id, "accept")
        self.assertIsNone(self.store.get(job.id))

    def test_progress_uses_one_snapshot_while_new_decisions_commit(self):
        job = self.complete()
        separate = AnnotationService(self.queue, SQLiteAnnotations(self.database))
        original_connect = self.store.state.connect

        class Interleave:
            def __init__(self, db):
                self.db = db

            def execute(self, sql, parameters=()):
                if sql.startswith("SELECT a.decision"):
                    separate.decide(job.id, "accept")
                return self.db.execute(sql, parameters)

        @contextmanager
        def interleaved_connect():
            with original_connect() as db:
                yield Interleave(db)

        with patch.object(self.store.state, "connect", interleaved_connect):
            progress = self.store.progress(self.source.id)
        self.assertEqual(progress["reviewed_results"], 0)
        self.assertEqual(progress["reviewed_sources"], 0)
        self.assertEqual(self.store.progress(self.source.id)["reviewed_results"], 1)
