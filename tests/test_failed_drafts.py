"""Challenge failed-draft decisions and selection provenance with real immutable stores."""

import json
import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import patch

import test_selections

from semantic_reviewer.adapters.annotations import SQLiteAnnotations
from semantic_reviewer.adapters.selections import JsonSelections
from semantic_reviewer.application.annotations import AnnotationService, review_actions
from semantic_reviewer.application.artefacts import Publication
from semantic_reviewer.application.selections import SelectionSnapshot


class FailedDraftTest(unittest.TestCase):
    setUp = test_selections.SelectionsTest.setUp
    complete = test_selections.SelectionsTest.complete
    request = test_selections.SelectionsTest.request

    def failed(self, index=0, outcome="semantic_failure", output=None):
        """Publish an explicitly synthetic failed model draft without a model call."""
        job = self.queue.enqueue(self.source.id, index)
        claimed = self.jobs.claim("fixture")
        raw = json.dumps(self.issue) if output is None else output
        body = {
            "job_id": job.id,
            "interpretation": None,
            "error": "Synthetic evidence validation failure",
            "model_output": raw,
            "usage": {"measurement": {"outcome": outcome}},
        }
        digest = self.results.publish(body, Publication(job.id, "normalisation"))
        self.jobs.finish(claimed, digest, body["error"])
        return self.jobs.get(job.id)

    def test_corrected_failure_survives_restart_and_freezes_exact_human_body(self):
        job = self.failed()
        original = self.results.read(job.artefact_sha256)
        self.issue["issue_statement"] = "Human correction of synthetic draft"
        edited = json.dumps(self.issue)
        annotation = self.annotations.decide(job.id, "edit", "Corrected source quotes", edited)
        self.assertEqual(self.jobs.get(job.id), job)
        self.assertEqual(self.results.read(job.artefact_sha256), original)
        self.assertEqual(annotation.result_sha256, job.artefact_sha256)
        restarted = AnnotationService(
            self.queue, SQLiteAnnotations(self.database), self.service, self.results
        )
        self.assertEqual(restarted.review(job.id)[1]["interpretation"], self.issue)
        selection = self.selections.freeze(self.request(annotation))
        _, snapshot = JsonSelections(self.root / "selections", self.database).read(selection.id)
        self.assertEqual((selection.included, selection.excluded), (1, 0))
        self.assertEqual(
            snapshot.records[0].interpretation.issue_statement, self.issue["issue_statement"]
        )
        self.assertEqual(snapshot.records[0].annotation.result_sha256, job.artefact_sha256)

    def test_invalid_schema_or_quote_cannot_create_a_decision(self):
        job = self.failed()
        for value in (
            "{}",
            json.dumps(
                self.issue
                | {
                    "actionable_engineering_concern": "yes",
                    "evidence_quotes": [{"source": "comment", "quote": "invented quote"}],
                }
            ),
        ):
            with self.assertRaises(ValueError):
                self.annotations.decide(job.id, "edit", edited_json=value)
            self.assertIsNone(self.store.get(job.id))
        self.assertEqual(self.jobs.get(job.id), job)

    def test_accept_provider_interrupted_and_missing_drafts_fail_closed(self):
        job = self.failed()
        with self.assertRaises(ValueError):
            self.annotations.decide(job.id, "accept")
        for outcome, output in (("provider_failure", "{}"), ("semantic_failure", " ")):
            failed = self.failed(outcome=outcome, output=output)
            for decision in ("edit", "reject"):
                with self.assertRaises(ValueError):
                    self.annotations.decide(
                        failed.id,
                        decision,
                        edited_json=json.dumps(self.issue) if decision == "edit" else None,
                    )
        original = self.results.read(job.artefact_sha256)
        for malformed in (
            None,
            [],
            original | {"job_id": "wrong"},
            original | {"usage": "invalid"},
            original | {"error": "different"},
        ):
            self.assertEqual(review_actions(job, malformed), ())

    def test_concurrent_retry_is_one_event_and_conflict_cannot_overwrite(self):
        job = self.failed()

        def submit(_):
            return self.annotations.decide(job.id, "edit", edited_json=json.dumps(self.issue))

        with ThreadPoolExecutor(2) as pool:
            decisions = list(pool.map(submit, range(2)))
        self.assertEqual(decisions[0], decisions[1])
        with self.store.state.connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM event WHERE kind='annotation_recorded'"
                ).fetchone()[0],
                1,
            )
        with self.assertRaises(ValueError):
            self.annotations.decide(job.id, "reject")
        self.assertEqual(self.jobs.get(job.id), job)

    def test_event_failure_rolls_back_correction(self):
        job = self.failed()
        with self.store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER fail_edit BEFORE INSERT ON event "
                "WHEN NEW.kind='annotation_recorded' "
                "BEGIN SELECT RAISE(ABORT, 'fixture failure'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.annotations.decide(job.id, "edit", edited_json=json.dumps(self.issue))
        self.assertIsNone(self.store.get(job.id))
        self.assertEqual(self.jobs.get(job.id), job)

    def test_rejected_failure_is_explicit_exclusion_without_invented_interpretation(self):
        job = self.failed()
        rejected = self.annotations.decide(job.id, "reject", "Not usable")
        summary = self.selections.freeze(self.request(rejected))
        _, snapshot = self.selection_store.read(summary.id)
        self.assertEqual((summary.included, summary.excluded), (0, 1))
        self.assertEqual(snapshot.records[0].exclusion, "rejected_interpretation")
        self.assertIsNone(snapshot.records[0].interpretation)
        self.assertEqual(snapshot.schema_version, 2)
        from fastapi.testclient import TestClient

        from semantic_reviewer.web.app import create_app

        client = TestClient(
            create_app(self.service, self.queue, self.annotations, selections=self.selection_store),
            base_url="http://127.0.0.1",
        )
        page = client.get(f"/selections/{summary.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Rejected failed draft", page.text)

    def test_legacy_selection_still_reads_but_null_eligible_or_v1_record_is_rejected(self):
        annotation = self.annotations.decide(self.complete().id, "accept")
        summary = self.selections.freeze(self.request(annotation))
        _, snapshot = self.selection_store.read(summary.id)
        legacy = snapshot.model_dump(mode="json")
        legacy.update(schema_version=1, eligibility_policy="explicit-accept-edit-v1")
        old = self.selection_store.publish(
            SelectionSnapshot.model_validate_json(json.dumps(legacy))
        )
        self.assertEqual(self.selection_store.read(old.id)[1].schema_version, 1)
        for version in (1, 2):
            body = snapshot.model_dump(mode="json")
            body.update(
                schema_version=version, eligibility_policy=f"explicit-accept-edit-v{version}"
            )
            body["records"][0]["interpretation"] = None
            with self.assertRaises(ValueError):
                SelectionSnapshot.model_validate_json(json.dumps(body))
        invalid = snapshot.model_copy(
            update={"records": (snapshot.records[0].model_copy(update={"interpretation": None}),)}
        )
        with self.assertRaises(ValueError):
            self.selection_store.publish(invalid)

    def test_selection_rechecks_original_and_edit_identity_not_just_annotation_flag(self):
        job = self.failed()
        annotation = self.annotations.decide(job.id, "edit", edited_json=json.dumps(self.issue))
        with patch.object(self.store, "by_id", return_value=replace(annotation, decision="accept")):
            with self.assertRaises(ValueError):
                self.selections.freeze(self.request(annotation))
        body = self.results.read(annotation.interpretation_sha256)
        read = self.results.read
        with patch.object(
            self.results,
            "read",
            side_effect=lambda digest: (
                body | {"original_result_sha256": "wrong"}
                if digest == annotation.interpretation_sha256
                else read(digest)
            ),
        ):
            with self.assertRaises(ValueError):
                self.selections.freeze(self.request(annotation))
        (self.results.root / (job.artefact_sha256 + ".json")).write_text("{}")
        with self.assertRaises(ValueError):
            self.selections.freeze(self.request(annotation))

    def test_progress_preserves_failure_count_and_separates_reviewed_denominators(self):
        failed = self.failed()
        waiting = self.failed(1)
        success = self.complete(2)
        self.assertIn(waiting.id, self.store.pending(self.source.id, 1))
        self.annotations.decide(failed.id, "edit", edited_json=json.dumps(self.issue))
        self.annotations.decide(success.id, "accept")
        counts = self.store.progress(self.source.id)
        self.assertEqual(
            (
                counts["reviewed_results"],
                counts["reviewed_successful_results"],
                counts["reviewed_failed_results"],
            ),
            (2, 1, 1),
        )
        self.assertEqual((counts["successful_results"], counts["failed"]), (1, 2))
        self.assertEqual(self.store.pending(self.source.id, 1), (waiting.id,))

    def test_database_fences_failed_accept_and_foreign_edit_publication(self):
        first = self.failed()
        original = self.annotations.decide(first.id, "edit", edited_json=json.dumps(self.issue))
        other = self.failed(1)
        foreign = replace(
            original,
            id="foreign",
            job_id=other.id,
            observation_id=other.observation_id,
            result_sha256=other.artefact_sha256,
        )
        for invalid in (
            foreign,
            replace(foreign, decision="accept", interpretation_sha256=None),
            replace(foreign, decision="reject", interpretation_sha256=None, result_sha256="0" * 64),
        ):
            with self.assertRaises(sqlite3.IntegrityError):
                self.store.record(invalid)
        self.assertIsNone(self.store.get(other.id))
