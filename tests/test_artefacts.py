"""Check immutable metadata, old-runtime indexing and regenerable structured job logs."""

import hashlib
import json
import sqlite3
import unittest
from unittest.mock import patch

import test_annotations

from semantic_reviewer.adapters.results import JsonResults
from semantic_reviewer.application.artefacts import Publication


class ArtefactsTest(unittest.TestCase):
    def setUp(self):
        test_annotations.AnnotationsTest.setUp(self)

    def test_existing_results_and_new_edits_gain_verified_metadata(self):
        # Simulate a pre-catalogue runtime; its immutable bytes have no routing keys.
        job = self.queue.enqueue(self.source.id, 0)
        claimed = self.jobs.claim("legacy")
        body = json.dumps({"interpretation": self.issue}).encode()
        digest = hashlib.sha256(body).hexdigest()
        (self.results.root / (digest + ".json")).write_bytes(body)
        self.jobs.finish(claimed, digest, None)
        indexed = JsonResults(self.results.root, self.database)
        self.assertEqual(indexed.index_referenced(), 1)
        self.assertEqual(indexed.index_referenced(), 1)
        self.assertEqual((self.results.root / (digest + ".json")).read_bytes(), body)
        with indexed.state.connect() as db:
            self.assertIsNotNone(
                db.execute("SELECT 1 FROM artefact WHERE sha256=?", (digest,)).fetchone()
            )
        self.queue.results = indexed
        annotation = self.annotations.decide(job.id, "edit", edited_json=json.dumps(self.issue))
        with self.store.state.connect() as db:
            rows = db.execute("SELECT * FROM artefact WHERE type!='job_log'").fetchall()
            self.assertEqual({row["type"] for row in rows}, {"normalisation", "human_edit"})
            self.assertTrue(all(row["size"] > 0 for row in rows))
            self.assertIn(annotation.interpretation_sha256, {row["sha256"] for row in rows})
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM artefact")

    def test_payload_keys_do_not_select_catalogue_kind_or_owner(self):
        job = self.queue.enqueue(self.source.id, 0)
        body = {"log_events": [], "original_result_sha256": "arbitrary", "job_id": "not-owner"}
        digest = self.results.publish(body, Publication(job.id, "normalisation"))
        with self.results.state.connect() as db:
            row = db.execute(
                "SELECT job_id, type FROM artefact WHERE sha256=?", (digest,)
            ).fetchone()
        self.assertEqual(tuple(row), (job.id, "normalisation"))
        self.assertEqual(self.results.read(digest), body)
        with self.assertRaises(ValueError):
            Publication(job.id, "unsupported")

    def test_logs_derive_from_committed_events_and_remain_regenerable(self):
        job = self.queue.enqueue(self.source.id, 0)
        first = self.jobs.log(job.id)
        self.jobs.finish(self.jobs.claim("test"), None, "Provider unavailable")
        final = self.jobs.log(job.id)
        self.assertNotEqual(first["sha256"], final["sha256"])
        events = self.jobs.logs.read(final["sha256"])["log_events"]
        self.assertEqual(
            [item["event"] for item in events], ["job_queued", "job_started", "job_failed"]
        )
        self.assertEqual(events[-1]["level"], "ERROR")
        self.assertNotIn("comment", json.dumps(events))
        self.assertEqual(self.jobs.log(job.id), final)
        with self.jobs.state.connect() as db:
            pointer = db.execute("SELECT * FROM job_log WHERE job_id=?", (job.id,)).fetchone()
            self.assertEqual(pointer["last_event_id"], events[-1]["event_id"])
        self.assertEqual(
            self.jobs.logs.read(first["sha256"])["log_events"][0]["event"], "job_queued"
        )

    def test_log_disk_failure_does_not_misrepresent_a_committed_transition(self):
        for error in (
            OSError("disk unavailable"),
            sqlite3.OperationalError("locked"),
            ValueError("checksum mismatch"),
        ):
            with self.subTest(error=type(error).__name__):
                with patch.object(self.jobs.logs, "publish", side_effect=error):
                    with self.assertLogs("semantic_reviewer.adapters.jobs", level="WARNING"):
                        job = self.queue.enqueue(self.source.id, 0)
                self.assertEqual(self.jobs.get(job.id).status, "queued")
                self.assertEqual(self.jobs.log(job.id)["type"], "job_log")

    def test_old_result_corruption_is_not_indexed(self):
        job = test_annotations.AnnotationsTest.complete(self)
        digest = self.jobs.get(job.id).artefact_sha256
        (self.results.root / (digest + ".json")).write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum"):
            JsonResults(self.results.root, self.database).index_referenced()

    def test_catalogue_conflicts_are_explicit_and_failed_edits_leave_only_orphan_files(self):
        job = test_annotations.AnnotationsTest.complete(self)
        indexed = JsonResults(self.results.root, self.database)
        indexed.index_referenced()
        bundle = indexed.read(self.jobs.get(job.id).artefact_sha256)
        with self.assertRaisesRegex(ValueError, "conflicting catalogue"):
            JsonResults(self.root / "another-root", self.database).publish(
                bundle, Publication(job.id, "normalisation")
            )
        self.queue.results = indexed
        before = set(self.results.root.glob("*.json"))
        with self.store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER fail_edit_catalogue BEFORE INSERT ON artefact "
                "WHEN NEW.type='human_edit' BEGIN SELECT RAISE(ABORT, 'test failure'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.annotations.decide(job.id, "edit", edited_json=json.dumps(self.issue))
        self.assertIsNone(self.store.get(job.id))
        orphan = set(self.results.root.glob("*.json")) - before
        self.assertEqual(len(orphan), 1)
        self.assertEqual(indexed.read(next(iter(orphan)).stem)["job_id"], job.id)

    def test_old_log_export_cannot_move_latest_pointer_backwards(self):
        job = self.queue.enqueue(self.source.id, 0)
        publish = self.jobs.logs.publish
        interleaved = False

        def delay_old_snapshot(value, publication):
            nonlocal interleaved
            if not interleaved:
                interleaved = True
                self.jobs.claim("concurrent-worker")
            return publish(value, publication)

        with patch.object(self.jobs.logs, "publish", delay_old_snapshot):
            old = self.jobs.log(job.id)
        with self.jobs.state.connect() as db:
            latest = db.execute(
                "SELECT artefact_sha256 FROM job_log WHERE job_id=?", (job.id,)
            ).fetchone()[0]
        self.assertNotEqual(latest, old["sha256"])
        self.assertEqual(self.jobs.logs.read(latest)["log_events"][-1]["event"], "job_started")
