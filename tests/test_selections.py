"""Challenge frozen input provenance, exclusions and durable publication with real stores."""

import json
import sqlite3
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import test_annotations

from semantic_reviewer.adapters.selections import JsonSelections
from semantic_reviewer.application.selections import SelectionRequest, SelectionService


class SelectionsTest(unittest.TestCase):
    def setUp(self):
        test_annotations.AnnotationsTest.setUp(self)
        self.selection_store = JsonSelections(self.root / "selections", self.database)
        self.selections = SelectionService(
            self.store, self.queue, self.service, self.results, self.selection_store
        )

    def complete(self, index=0):
        return test_annotations.AnnotationsTest.complete(self, index)

    def choose(self, index=0, decision="accept"):
        return self.annotations.decide(
            self.complete(index).id,
            decision,
            edited_json=json.dumps(self.issue) if decision == "edit" else None,
        )

    def request(self, *annotations, **overrides):
        return SelectionRequest.model_validate(
            {
                "dataset_id": self.source.id,
                "annotation_ids": [a.id for a in annotations],
                "purpose": "fixture",
                "holdout_repositories": [],
                **overrides,
            }
        )

    def test_effective_edit_source_identity_uncertainty_and_exclusions_survive_restart(self):
        accepted = self.choose()
        edit_job = self.complete(1)
        self.issue["issue_statement"] = "Human correction"
        edited = self.annotations.decide(edit_job.id, "edit", edited_json=json.dumps(self.issue))
        rejected = self.choose(2, "reject")
        request = self.request(accepted, edited, rejected)
        first = self.selections.freeze(request)
        self.assertEqual((first.included, first.excluded), (2, 1))
        self.choose(0)  # A later version must not silently enter an existing selection.
        self.assertEqual(self.selections.freeze(request), first)
        summary, snapshot = JsonSelections(self.root / "selections", self.database).read(first.id)
        self.assertEqual(summary, first)
        self.assertEqual([r.annotation.id for r in snapshot.records], list(request.annotation_ids))
        self.assertEqual(snapshot.records[1].interpretation.issue_statement, "Human correction")
        self.assertEqual(
            self.results.read(edited.result_sha256)["interpretation"]["issue_statement"],
            "Needs assessment",
        )
        self.assertEqual(snapshot.records[0].interpretation.generalisable, "uncertain")
        self.assertEqual(snapshot.records[2].exclusion, "rejected_interpretation")
        self.assertEqual(
            snapshot.records[1].annotation.interpretation_sha256, edited.interpretation_sha256
        )
        self.assertEqual(snapshot.dataset.source_sha256, self.source.source_sha256)
        self.assertEqual(snapshot.records[0].source.comment, self.rows[0]["comment"])

    def test_research_attestation_is_explicit_and_holdouts_are_excluded(self):
        chosen = self.choose()
        for overrides in (
            {"purpose": "research"},
            {"purpose": "research", "curator": " ", "human_review_attested": True},
            {"human_review_attested": True},
            {"curator": "someone"},
            {"holdout_repositories": ["invalid"]},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.request(chosen, **overrides)
        request = self.request(
            chosen,
            purpose="research",
            curator="Fixture curator",
            human_review_attested=True,
            holdout_repositories=["EXAMPLE/SYNTHETIC"],
        )
        summary = self.selections.freeze(request)
        self.assertEqual((summary.included, summary.excluded), (0, 1))
        self.assertEqual(
            self.selection_store.read(summary.id)[1].records[0].exclusion, "holdout_repository"
        )

    def test_duplicate_versions_missing_records_and_wrong_dataset_fail_without_publication(self):
        first, second = self.choose(), self.choose()
        with self.assertRaises(ValueError):
            self.request(first, first)
        for request, exception in (
            (self.request(first, second), ValueError),
            (self.request(first, annotation_ids=["missing"]), LookupError),
            (self.request(first, dataset_id="another"), ValueError),
        ):
            with self.subTest(request=request), self.assertRaises(exception):
                self.selections.freeze(request)
        self.assertEqual(self.selection_store.recent(), ())
        self.assertEqual(list(self.selection_store.root.iterdir()), [])

    def test_changed_original_edit_or_source_fails_before_registration(self):
        chosen = self.choose(0, "edit")
        for path in (
            self.results.root / (chosen.result_sha256 + ".json"),
            self.results.root / (chosen.interpretation_sha256 + ".json"),
            self.root
            / "datasets"
            / (self.registry.get(self.source.id).parquet_sha256 + ".parquet"),
        ):
            original = path.read_bytes()
            try:
                path.write_bytes(b"corrupted")
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.selections.freeze(self.request(chosen))
                self.assertEqual(self.selection_store.recent(), ())
            finally:
                path.write_bytes(original)

    def test_concurrent_identical_freeze_is_one_event_and_changed_input_has_new_identity(self):
        first, second = self.choose(), self.choose(1)
        request = self.request(first)
        with ThreadPoolExecutor(2) as pool:
            summaries = list(pool.map(self.selections.freeze, [request, request]))
        self.assertEqual(summaries[0], summaries[1])
        with self.selection_store.state.connect() as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM event WHERE kind='selection_frozen'").fetchone()[
                    0
                ],
                1,
            )
            for sql in (
                "DELETE FROM annotation_selection",
                "UPDATE annotation_selection SET included=0",
            ):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute(sql)
        self.assertNotEqual(self.selections.freeze(self.request(first, second)).id, summaries[0].id)

    def test_event_failure_leaves_only_complete_orphan_then_retry_registers_once(self):
        chosen = self.choose()
        with self.selection_store.state.connect() as db:
            db.execute(
                "CREATE TRIGGER fail_selection BEFORE INSERT ON event "
                "WHEN NEW.kind='selection_frozen' BEGIN SELECT RAISE(ABORT, 'test'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.selections.freeze(self.request(chosen))
        self.assertEqual(self.selection_store.recent(), ())
        self.assertEqual(len(list(self.selection_store.root.glob("*.json"))), 1)
        with self.selection_store.state.connect() as db:
            db.execute("DROP TRIGGER fail_selection")
        summary = self.selections.freeze(self.request(chosen))
        self.assertEqual(self.selection_store.read(summary.id)[0], summary)

    def test_corrupt_snapshot_read_and_retry_fail_closed_without_repair(self):
        request = self.request(self.choose())
        summary = self.selections.freeze(request)
        path = self.selection_store.root / (summary.id + ".json")
        path.write_bytes(b"{}")
        for operation in (
            lambda: self.selection_store.read(summary.id),
            lambda: self.selections.freeze(request),
        ):
            with self.assertRaises(ValueError):
                operation()
        self.assertEqual(path.read_bytes(), b"{}")
        with self.assertRaises(ValueError):
            self.selection_store.read("../elsewhere")
        with self.assertRaises(LookupError):
            self.selection_store.read("a" * 64)

    def test_only_declared_job_port_is_needed_and_source_pagination_does_not_leak(self):
        chosen = self.choose()
        inspect = self.queue.inspect

        class Reader:
            def inspect(self, job_id):
                return inspect(job_id)

        service = SelectionService(
            self.store, Reader(), self.service, self.results, self.selection_store
        )
        with patch.object(self.service, "browse", side_effect=AssertionError("paging leaked")):
            self.assertEqual(service.freeze(self.request(chosen)).included, 1)

    def test_conflicting_edit_metadata_is_not_accepted_as_an_effective_interpretation(self):
        chosen = self.choose(0, "edit")
        read = self.results.read

        def conflicting(digest):
            body = read(digest)
            if digest == chosen.interpretation_sha256:
                body["original_result_sha256"] = "a" * 64
            return body

        with patch.object(self.results, "read", side_effect=conflicting):
            with self.assertRaisesRegex(ValueError, "conflicting provenance"):
                self.selections.freeze(self.request(chosen))
        self.assertEqual(self.selection_store.recent(), ())

    def test_body_limit_and_file_publication_failure_leave_no_registered_selection(self):
        request = self.request(self.choose())
        with patch("semantic_reviewer.adapters.selections.MAX_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "32 MB"):
                self.selections.freeze(request)
        with patch("semantic_reviewer.adapters.selections.os.link", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                self.selections.freeze(request)
        self.assertEqual(self.selection_store.recent(), ())
        self.assertEqual(list(self.selection_store.root.iterdir()), [])

    def test_cli_freezes_and_reads_the_same_snapshot(self):
        request_file = self.root / "request.json"
        request_file.write_text(self.request(self.choose()).model_dump_json(), encoding="utf-8")
        command = [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "tools/run.py"),
            "--data-root",
            str(self.root),
        ]
        frozen = subprocess.run(
            [*command, "freeze-selection", str(request_file)], capture_output=True, text=True
        )
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        summary = json.loads(frozen.stdout)
        read = subprocess.run(
            [*command, "selection", summary["id"]], capture_output=True, text=True
        )
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(json.loads(read.stdout)["summary"], summary)
