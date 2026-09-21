"""Exercise the rendered form through storage using synthetic decisions only."""

import json
import unittest
from dataclasses import replace
from html.parser import HTMLParser
from urllib.parse import urlencode

import test_annotation_web
import test_failed_drafts

from semantic_reviewer.web.assessment import AssessmentForm


class FormPage(HTMLParser):
    """Read actual rendered controls as a browser would, excluding submit buttons."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.fields = {}
        self.active = False
        self.control = None
        self.options = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.active = attrs.get("id") == "assessment-editor"
        if not self.active:
            return
        if tag == "input" and attrs.get("name"):
            self.fields.setdefault(attrs["name"], []).append(attrs.get("value", ""))
        elif tag in ("textarea", "select"):
            self.control = (tag, attrs["name"], [])
            self.options = []
        elif tag == "option":
            self.options.append((attrs.get("value", ""), "selected" in attrs))

    def handle_data(self, value):
        if self.control and self.control[0] == "textarea":
            self.control[2].append(value)

    def handle_endtag(self, tag):
        if tag == "form":
            self.active = False
        if self.control and tag == self.control[0]:
            _, name, chunks = self.control
            if tag == "textarea":
                # HTML discards exactly one leading LF in textarea markup.
                value = "".join(chunks).removeprefix("\n")
            else:
                value = next(
                    (value for value, selected in self.options if selected), self.options[0][0]
                )
            self.fields.setdefault(name, []).append(value)
            self.control = None


class AssessmentFormTest(unittest.TestCase):
    setUp = test_annotation_web.AnnotationWebTest.setUp
    failed = test_failed_drafts.FailedDraftTest.failed

    def submit(self, fields, **action):
        return self.client.post(
            self.url,
            content=urlencode(fields | {key: [value] for key, value in action.items()}, doseq=True),
            headers=self.headers | {"Content-Type": "application/x-www-form-urlencoded"},
        )

    def page_fields(self):
        return FormPage(self.client.get(f"/jobs/{self.job.id}").text).fields

    def test_rendered_fields_save_complete_edit_and_readable_confirmation(self):
        original = self.queue.inspect(self.job.id)
        fields = self.page_fields()
        self.assertNotIn("edited_json", fields)
        fields.update(
            issue_statement=["Human correction"],
            scope=["unknown"],
            category=["Code maintenance", "Type annotations"],
            proposed_invariant=[""],
            exclusion=["Known caller handles this."],
            notes=["Missing evidence: caller not supplied."],
        )
        response = self.submit(fields, decision="edit")
        self.assertEqual(response.status_code, 200)
        annotation, edited = self.annotations.review(self.job.id)
        self.assertEqual(
            edited["interpretation"],
            self.issue
            | {
                "issue_statement": "Human correction",
                "scope": "unknown",
                "coarse_categories": fields["category"],
                "exclusions": fields["exclusion"],
            },
        )
        self.assertEqual(annotation.notes, fields["notes"][0])
        self.assertIn("<dd>unknown</dd>", response.text)
        self.assertIn("Saved assessment notes", response.text)
        self.assertEqual(self.queue.inspect(self.job.id), original)

    def test_add_remove_rows_preserves_unsaved_values_and_does_not_record_events(self):
        fields = self.page_fields() | {
            "issue_statement": ["Unsubmitted change"],
            "notes": ["Keep me"],
        }
        before = self.store.history(self.job.observation_id)
        for action in ("add:category", "add:evidence", "add:exclusion", "remove:category:0"):
            response = self.submit(fields, form_action=action)
            self.assertEqual(response.status_code, 200)
            fields = FormPage(response.text).fields
            self.assertEqual(fields["issue_statement"], ["Unsubmitted change"])
            self.assertEqual(fields["notes"], ["Keep me"])
            self.assertIsNone(self.store.get(self.job.id))
        self.assertEqual(fields["category"], [""])
        self.assertEqual(fields["evidence_source"], ["comment"])
        self.assertEqual(self.store.history(self.job.observation_id), before)
        with self.store.state.connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT count(*) FROM event WHERE kind='annotation_recorded'"
                ).fetchone()[0],
                0,
            )

    def test_invalid_fields_and_grounding_preserve_all_input_for_correction(self):
        fields = self.page_fields() | {
            "issue_statement": ["<script>draft</script>"],
            "notes": ["Keep my notes"],
            "scope": ["search the history"],
            "category": ["one", "two"],
            "exclusion": ["exception"],
        }
        invalid = self.submit(fields, decision="edit")
        self.assertEqual(invalid.status_code, 409)
        self.assertEqual(FormPage(invalid.text).fields, fields)
        self.assertNotIn("<script>", invalid.text)
        self.assertIsNone(self.store.get(self.job.id))
        fields.update(
            scope=["unknown"], evidence_source=["code"], evidence_quote=["invented quote"]
        )
        invalid = self.submit(fields, decision="edit")
        self.assertEqual(invalid.status_code, 409)
        self.assertEqual(FormPage(invalid.text).fields, fields)
        fields.update(evidence_source=[], evidence_quote=[])
        saved = self.submit(fields, decision="edit")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(
            self.annotations.review(self.job.id)[1]["interpretation"]["issue_statement"],
            fields["issue_statement"][0],
        )

    def test_accept_and_reject_do_not_validate_or_use_edited_fields(self):
        for decision in ("accept", "reject"):
            with self.subTest(decision=decision):
                job = test_annotation_web.test_annotations.AnnotationsTest.complete(self)
                self.url = f"/jobs/{job.id}/annotation"
                fields = self.page_fields() | {
                    "issue_statement": [""],
                    "scope": [""],
                    "notes": [decision],
                }
                response = self.submit(fields, decision=decision)
                self.assertEqual(response.status_code, 200)
                record, edited = self.annotations.review(job.id)
                self.assertEqual(record.decision, decision)
                self.assertEqual(record.notes, decision)
                self.assertIsNone(edited)

    def test_failed_unparseable_draft_starts_without_guessed_judgements(self):
        job = self.failed(output="<script>malformed output</script>")
        self.url = f"/jobs/{job.id}/annotation"
        page = self.client.get(f"/jobs/{job.id}")
        self.assertIn("&lt;script&gt;malformed output", page.text)
        self.assertNotIn('value="accept"', page.text)
        fields = FormPage(page.text).fields
        self.assertEqual(fields["actionable_engineering_concern"], [""])
        fields.update(
            issue_statement=["Human supplied interpretation"],
            actionable_engineering_concern=["uncertain"],
            generalisable=["uncertain"],
            scope=["unknown"],
            category=["maintainability"],
            notes=["Synthetic correction"],
        )
        response = self.submit(fields, decision="edit")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.jobs.get(job.id), job)
        self.assertEqual(self.annotations.review(job.id)[1]["interpretation"]["scope"], "unknown")

    def test_ambiguous_or_oversized_field_protocols_cannot_record_a_decision(self):
        fields = self.page_fields()
        for additions in (
            {"decision": ["accept", "reject"]},
            {"scope": ["file", "unknown"]},
            {"edited_json": ["{}"]},
            {"category": ["x"] * 9},
            {"evidence_source": ["code"]},
            {"form_action": ["add:category"]},
            {"unexpected": ["x"]},
        ):
            response = self.submit(fields | {"decision": ["edit"]} | additions)
            self.assertEqual(response.status_code, 422)
            self.assertIsNone(self.store.get(self.job.id))
        response = self.submit(fields, form_action="remove:category:99")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(FormPage(response.text).fields, fields)

    def test_source_line_endings_and_leading_newlines_round_trip_without_trimming(self):
        _, source = self.service.observation(self.job.dataset_id, self.job.source_index)
        quote = "\nfirst\n  second\n"
        source = replace(source, code="prefix\r\nfirst\r\n  second\r\nend")
        issue = self.issue | {
            "issue_statement": "\nA leading newline",
            "coarse_categories": ["\nfirst\nsecond"],
            "evidence_quotes": [{"source": "code", "quote": quote}],
        }
        form = AssessmentForm.from_output(json.dumps(issue))
        converted = json.loads(form.interpretation_json(source))
        self.assertEqual(converted["evidence_quotes"][0]["quote"], "\r\nfirst\r\n  second\r\n")
        for newline in ("\n", "\r"):
            with self.subTest(newline=repr(newline)):
                literal = quote.replace("\n", newline)
                converted = json.loads(form.interpretation_json(replace(source, code=literal)))
                self.assertEqual(converted["evidence_quotes"][0]["quote"], literal)
        self.assertEqual(converted["coarse_categories"], issue["coarse_categories"])
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            form.interpretation_json(replace(source, code=source.code + quote))
        fields = self.page_fields() | {
            "issue_statement": ["\nA leading newline"],
            "category": ["\nfirst\nsecond"],
        }
        response = self.submit(fields, form_action="add:exclusion")
        self.assertEqual(
            FormPage(response.text).fields["issue_statement"], fields["issue_statement"]
        )
        self.assertEqual(FormPage(response.text).fields["category"], fields["category"])

    def test_stale_tab_cannot_overwrite_a_saved_decision(self):
        fields = self.page_fields()
        self.assertEqual(self.submit(fields, decision="accept").status_code, 200)
        saved = self.annotations.review(self.job.id)
        fields["issue_statement"] = ["Different stale-tab edit"]
        response = self.submit(fields, decision="edit")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.annotations.review(self.job.id), saved)
        self.assertIn("Different stale-tab edit", response.text)
