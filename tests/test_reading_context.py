"""Verify additional source identity and what each synthetic assessment was presented."""

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

import test_annotation_web
from fastapi.testclient import TestClient
from test_assessment_form import FormPage

from semantic_reviewer.adapters.reading import GitHubReadingSources
from semantic_reviewer.adapters.selections import JsonSelections
from semantic_reviewer.application.annotations import AnnotationService
from semantic_reviewer.application.selections import SelectionRequest, SelectionService
from semantic_reviewer.web.app import create_app


class ReadingContextTest(unittest.TestCase):
    def setUp(self):
        test_annotation_web.AnnotationWebTest.setUp(self)
        self.job, _ = self.queue.inspect(self.job.id)
        _, self.observation = self.service.observation(self.job.dataset_id, self.job.source_index)
        self.readings = GitHubReadingSources(self.root / "source-context", self.database)
        self.annotations = AnnotationService(
            self.queue, self.store, self.service, self.results, self.readings
        )
        self.client = TestClient(
            create_app(self.service, self.queue, self.annotations), base_url="http://127.0.0.1"
        )

    def receipt(self, **changes):
        source = self.observation
        repo = f"{source.owner}/{source.repository}"
        url = f"https://api.github.com/repos/{repo}/pulls/comments/{source.comment_id}"
        body = {
            "id": source.comment_id,
            "url": url,
            "path": source.file_path,
            "pull_request_url": f"https://api.github.com/repos/{repo}/pulls/{source.pull_request}",
            "html_url": f"https://github.com/{repo}/pull/{source.pull_request}#discussion_r{source.comment_id}",
            "body": source.comment,
            "diff_hunk": source.code,
        } | changes
        raw = json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8") + b"\r\n"
        receipt = json.dumps(
            {
                "http_status": 200,
                "url": url,
                "effective_url": body["url"],
                "checked_at": "2026-09-21T20:00:00+00:00",
                "response_sha256": hashlib.sha256(raw).hexdigest(),
            }
        ).encode("utf-8")
        return raw, receipt

    def attach(self, **changes):
        return self.readings.attach(self.job, self.observation, *self.receipt(**changes))

    def fields(self):
        return FormPage(self.client.get(f"/jobs/{self.job.id}").text).fields

    def submit(self, fields, **action):
        return self.client.post(
            self.url,
            content=urlencode(fields | {k: [v] for k, v in action.items()}, doseq=True),
            headers=self.headers | {"Content-Type": "application/x-www-form-urlencoded"},
        )

    def test_exact_receipts_survive_restart_and_unchanged_model_input(self):
        original = self.queue.inspect(self.job.id)
        response, receipt = self.receipt(diff_hunk="  " + self.observation.code + "\r\n")
        context = self.readings.attach(self.job, self.observation, response, receipt)
        restarted = GitHubReadingSources(self.readings.root, self.database)
        self.assertEqual(restarted.read(self.job.id), context)
        data = json.loads((self.readings.root / f"{context.sha256}.json").read_bytes())
        self.assertEqual(data["response"].encode("utf-8"), response)
        self.assertEqual(data["receipt"].encode("utf-8"), receipt)
        self.assertEqual(context.code_difference, "Whitespace differs only")
        self.assertEqual(context.comment_difference, "Identical text")
        self.assertEqual(restarted.attach(self.job, self.observation, response, receipt), context)
        self.assertEqual(self.queue.inspect(self.job.id), original)
        self.assertIsNone(self.store.get(self.job.id))
        with self.store.state.connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM event WHERE kind='source_context_attached'"
                ).fetchone()[0],
                1,
            )

    def test_wrong_identity_receipt_hash_and_unsafe_url_are_rejected(self):
        for change in (
            {"id": 999},
            {"path": "wrong.py"},
            {"pull_request_url": "https://example.org"},
            {"html_url": "javascript:alert(1)"},
            {"body": None},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.attach(**change)
        response, receipt = self.receipt()
        with self.assertRaises(ValueError):
            self.readings.attach(self.job, self.observation, response + b" ", receipt)
        with self.assertRaises(ValueError):
            self.readings.attach(self.job, replace(self.observation, id="wrong"), response, receipt)
        self.assertIsNone(self.readings.read(self.job.id))

    def test_numeric_repository_redirect_retains_receipt_without_relaxing_comment_identity(self):
        raw, receipt = self.receipt()
        value = json.loads(receipt)
        value["effective_url"] = (
            f"https://api.github.com/repositories/123/pulls/comments/{self.observation.comment_id}"
        )
        context = self.readings.attach(self.job, self.observation, raw, json.dumps(value).encode())
        self.assertEqual(context.comment, self.observation.comment)
        value["effective_url"] += "0"
        with self.assertRaises(ValueError):
            self.readings.attach(self.job, self.observation, raw, json.dumps(value).encode())

    def test_import_command_uses_its_own_checkout_without_pythonpath(self):
        raw, receipt = self.receipt()
        response_path, receipt_path = self.root / "response.json", self.root / "receipt.json"
        response_path.write_bytes(raw)
        receipt_path.write_bytes(receipt)
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        command = Path(__file__).resolve().parents[1] / "tools/import_source_context.py"
        result = subprocess.run(
            [
                sys.executable,
                str(command),
                "--data-root",
                str(self.root),
                "--job",
                self.job.id,
                "--response",
                str(response_path),
                "--receipt",
                str(receipt_path),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.readings.read(self.job.id).sha256)

    def test_changed_missing_and_corrupt_context_fail_closed(self):
        context = self.attach()
        with self.assertRaises(ValueError):
            self.attach(body="different")
        path = self.readings.root / f"{context.sha256}.json"
        data = path.read_bytes()
        path.write_bytes(data + b" ")
        self.assertEqual(self.client.get(f"/jobs/{self.job.id}").status_code, 409)
        path.unlink()
        with self.assertRaises(OSError):
            self.annotations.decide(self.job.id, "reject", context_sha256=context.sha256)
        self.assertIsNone(self.store.get(self.job.id))

    def test_both_views_escape_source_and_label_additional_text(self):
        context = self.attach(body="<script>unsafe</script>", diff_hunk="-before\n+after\n")
        page = self.client.get(f"/jobs/{self.job.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Preserved GitHub source", page.text)
        self.assertIn("Dataset text supplied to the model", page.text)
        self.assertIn("Other text differences", page.text)
        self.assertIn("-before\n+after\n", page.text)
        self.assertNotIn("<script>unsafe", page.text)
        self.assertIn("&lt;script&gt;unsafe", page.text)
        self.assertEqual(FormPage(page.text).fields["context_sha256"], [context.sha256])

    def test_stale_form_retains_edits_without_silently_adopting_context(self):
        fields = self.fields() | {"notes": ["Unsaved notes"]}
        self.attach()
        response = self.submit(fields, decision="reject")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(FormPage(response.text).fields, fields)
        self.assertIsNone(self.store.get(self.job.id))
        legacy = self.client.post(self.url, data={"decision": "reject"}, headers=self.headers)
        self.assertEqual(legacy.status_code, 409)

    def test_form_context_survives_row_actions_and_is_saved_atomically(self):
        context = self.attach()
        fields = self.fields()
        response = self.submit(fields, form_action="add:category")
        fields = FormPage(response.text).fields
        self.assertEqual(fields["context_sha256"], [context.sha256])
        self.assertIsNone(self.store.get(self.job.id))
        response = self.submit(fields, decision="edit")
        self.assertEqual(response.status_code, 200)
        annotation = self.store.get(self.job.id)
        self.assertEqual(annotation.context_sha256, context.sha256)
        self.assertIn(context.sha256, response.text)
        self.assertEqual(self.submit(fields, decision="edit").status_code, 200)
        with self.store.state.connect() as db:
            events = db.execute(
                "SELECT details_json FROM event WHERE kind='annotation_recorded'"
            ).fetchall()
            self.assertEqual(len(events), 1)
            self.assertEqual(json.loads(events[0][0])["context_sha256"], context.sha256)

    def test_extra_source_quotes_cannot_replace_dataset_grounding(self):
        self.attach(body="Only in the external source")
        fields = self.fields() | {
            "evidence_source": ["comment"],
            "evidence_quote": ["Only in the external source"],
        }
        self.assertEqual(self.submit(fields, decision="edit").status_code, 409)
        self.assertIsNone(self.store.get(self.job.id))

    def test_existing_decision_is_not_backfilled_and_sql_fences_omitted_context(self):
        self.annotations.decide(self.job.id, "reject")
        with self.assertRaises(ValueError):
            self.attach()
        self.assertIsNone(self.store.get(self.job.id).context_sha256)
        with self.store.state.connect() as db, self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO source_context VALUES (?, ?, ?, ?)",
                (self.job.id, "a" * 64, self.job.observation_id, self.job.artefact_sha256),
            )

    def test_attachment_race_cannot_commit_an_unattributed_decision(self):
        original = self.store.record

        def attach_before_record(annotation):
            self.attach()
            return original(annotation)

        with patch.object(self.store, "record", side_effect=attach_before_record):
            with self.assertRaises(ValueError):
                self.annotations.decide(self.job.id, "reject")
        self.assertIsNone(self.store.get(self.job.id))

    def test_selection_preserves_context_and_refuses_missing_evidence(self):
        context = self.attach()
        annotation = self.annotations.decide(self.job.id, "accept", context_sha256=context.sha256)
        selections = SelectionService(
            self.store,
            self.queue,
            self.service,
            self.results,
            JsonSelections(self.root / "selections", self.database),
            self.readings,
        )
        request = SelectionRequest(
            dataset_id=self.job.dataset_id,
            annotation_ids=(annotation.id,),
            purpose="fixture",
            holdout_repositories=(),
        )
        summary = selections.freeze(request)
        _, snapshot = selections.store.read(summary.id)
        self.assertEqual(snapshot.records[0].annotation.context_sha256, context.sha256)
        (self.readings.root / f"{context.sha256}.json").unlink()
        with self.assertRaises(OSError):
            selections.freeze(request)


if __name__ == "__main__":
    unittest.main()
