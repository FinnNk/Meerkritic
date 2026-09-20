"""Synthetic preparation evidence must enforce order, provenance and workload limits."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from semantic_reviewer.domain.study_preparation import (
    PreparationAttempt,
    preparation_progress,
    prepare_sample,
)
from tools.study_inputs import publish_record, read_record


def source_rows(repositories=20, each=12):
    return [
        {
            "owner": "fixture",
            "repo": f"repo-{repo:02}",
            "pr_number": i + 1,
            "comment_id": repo * 100 + i + 1,
            "code": f"synthetic code {repo} {i}",
            "comment": f"synthetic concern {repo} {i}",
        }
        for repo in range(repositories)
        for i in range(each)
    ]


def prepare(rows, exposed=()):
    body = json.dumps(rows).encode()
    return body, prepare_sample(body, hashlib.sha256(body).hexdigest(), exposed)


def attempt(candidate, outcome="accept", **changes):
    index = candidate["source_index"]
    values = {
        "source_index": index,
        "outcome": outcome,
        "recorded_by": "synthetic recorder",
        "reason": "Synthetic fixture only; not a human research label.",
        "source_reference": f"https://example.invalid/fixture/{index}",
        "source_evidence_sha256": "a" * 64,
        "source_check": "Synthetic origin and context check.",
        "job_id": f"job-{index}",
        "annotation_id": f"annotation-{index}",
        "human_reviewer": "synthetic reviewer",
    }
    if outcome not in {"accept", "edit", "reject"}:
        values.update(annotation_id=None, human_reviewer=None)
    if outcome not in {"accept", "edit", "reject", "normalisation_failed"}:
        values["job_id"] = None
    if outcome == "repository_quota":
        values.update(source_reference=None, source_evidence_sha256=None, source_check=None)
    return PreparationAttempt(**(values | changes))


class StudyPreparationTest(unittest.TestCase):
    def test_reproducible_bounded_sample_accounts_for_every_source_without_text(self):
        rows = source_rows()
        body, plan = prepare(rows)
        self.assertEqual(plan, prepare_sample(body, hashlib.sha256(body).hexdigest()))
        self.assertEqual(len(plan["holdout_repositories"]), 4)
        self.assertEqual(len(plan["candidates"]), 80)
        candidates = plan["candidates"]
        # Round-robin exposes every development repository before a second from any.
        self.assertEqual(len({item["repository"] for item in candidates[:16]}), 16)
        self.assertEqual(
            [item["repository"] for item in candidates[:16]],
            sorted(item["repository"] for item in candidates[:16]),
        )
        self.assertFalse(set(plan["holdout_repositories"]) & {c["repository"] for c in candidates})
        all_indexes = [row["source_index"] for row in candidates + plan["exclusions"]]
        self.assertEqual(sorted(all_indexes), list(range(len(rows))))
        self.assertNotIn("synthetic concern", json.dumps(plan))
        self.assertNotIn("synthetic code", json.dumps(plan))
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            prepare_sample(body + b" ", plan["source_sha256"])

    def test_deduplication_retains_lowest_original_index_and_exposure_precedes_sampling(self):
        rows = source_rows(each=3)
        rows.extend([{**rows[0], "owner": "FIXTURE"}, {**rows[1], "comment_id": 999}])
        _, plan = prepare(rows, ("fixture/repo-02",))
        exclusions = {item["source_index"]: item for item in plan["exclusions"]}
        self.assertEqual(exclusions[60]["duplicate_of"], 0)
        self.assertEqual(exclusions[61]["duplicate_of"], 1)
        self.assertEqual(exclusions[6]["reason"], "prior_exposure")
        self.assertNotIn("fixture/repo-02", plan["holdout_repositories"])
        self.assertIn("django/django", plan["prior_exposure"])

    def test_invalid_records_fail_instead_of_silently_reducing_pool(self):
        for update in (
            {"owner": "bad/name"},
            {"comment_id": True},
            {"code": None},
            {"pr_number": 0},
        ):
            with self.subTest(update=update), self.assertRaises(ValueError):
                prepare([{**source_rows(1, 1)[0], **update}])

    def test_order_and_explicit_human_source_and_job_evidence_are_required(self):
        _, plan = prepare(source_rows())
        first, second = plan["candidates"][:2]
        with self.assertRaisesRegex(ValueError, "order"):
            preparation_progress(plan, (attempt(second),))
        for changes in (
            {"human_reviewer": None},
            {"annotation_id": None},
            {"job_id": None},
            {"source_evidence_sha256": None},
            {"source_check": None},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                preparation_progress(plan, (attempt(first, **changes),))
        with self.assertRaisesRegex(ValueError, "annotation"):
            preparation_progress(
                plan,
                (
                    attempt(first),
                    attempt(second, annotation_id=f"annotation-{first['source_index']}"),
                ),
            )
        with self.assertRaisesRegex(ValueError, "job"):
            preparation_progress(
                plan, (attempt(first), attempt(second, job_id=f"job-{first['source_index']}"))
            )
        pending = preparation_progress(plan, (attempt(first, "reject"),))
        self.assertEqual((pending["state"], pending["usable"]), ("pending", 0))
        self.assertEqual(pending["next_candidate"], second)

    def test_exact_target_stops_and_quota_does_not_silently_drop_attempts(self):
        _, plan = prepare(source_rows())
        attempts = tuple(attempt(item) for item in plan["candidates"][:40])
        progress = preparation_progress(plan, attempts)
        self.assertEqual((progress["state"], progress["usable"]), ("ready", 40))
        self.assertIsNone(progress["next_candidate"])
        with self.assertRaisesRegex(ValueError, "stop"):
            preparation_progress(plan, (*attempts, attempt(plan["candidates"][40])))
        _, small = prepare(source_rows(2, 12))
        self.assertEqual(len(small["candidates"]), 10)
        candidates = small["candidates"]
        prefix = tuple(attempt(item) for item in candidates[:5])
        with self.assertRaisesRegex(ValueError, "five"):
            preparation_progress(small, (*prefix, attempt(candidates[5])))
        full = prefix + tuple(attempt(item, "repository_quota") for item in candidates[5:])
        shortfall = preparation_progress(small, full)
        self.assertEqual(
            (shortfall["state"], shortfall["attempted"], shortfall["usable"]), ("shortfall", 10, 5)
        )

    def test_failure_and_source_exclusions_stay_in_denominator(self):
        _, plan = prepare(source_rows(3, 1))
        candidates = plan["candidates"]
        attempts = (
            attempt(candidates[0], "source_unresolved"),
            attempt(candidates[1], "normalisation_failed"),
        )
        result = preparation_progress(plan, attempts)
        self.assertEqual(
            (result["state"], result["attempted"], result["usable"]), ("shortfall", 2, 0)
        )
        with self.assertRaisesRegex(ValueError, "five"):
            preparation_progress(plan, (attempt(candidates[0], "repository_quota"),))

    def test_saved_records_are_complete_immutable_and_recomputed_on_read(self):
        body, plan = prepare(source_rows())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initial = root / "0000.json"
            first = publish_record(initial, plan, ())
            record, digest = read_record(body, initial)
            self.assertEqual(digest, first["record_sha256"])
            with self.assertRaises(FileExistsError):
                publish_record(initial, plan, ())
            subsequent = root / "0001.json"
            publish_record(subsequent, plan, (attempt(plan["candidates"][0]),), digest)
            updated, _ = read_record(body, subsequent)
            self.assertEqual(updated["previous_record_sha256"], digest)
            self.assertEqual(updated["attempts"][0]["outcome"], "accept")
            updated["progress"]["usable"] = 40
            invalid = root / "invalid.json"
            invalid.write_text(json.dumps(updated), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "progress disagrees"):
                read_record(body, invalid)
            updated["previous_record_sha256"] = None
            invalid.write_text(json.dumps(updated), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "predecessor digest"):
                read_record(body, invalid)
            record["plan"]["candidates"].reverse()
            tampered = root / "tampered.json"
            tampered.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "plan differs"):
                read_record(body, tampered)
            self.assertEqual(
                sorted(path.name for path in root.iterdir()),
                ["0000.json", "0001.json", "invalid.json", "tampered.json"],
            )

    def test_cli_preserves_prior_bytes_and_refuses_out_of_order_append(self):
        body, plan = prepare(source_rows())
        command = [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "tools/study_inputs.py"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, initial, next_record = (
                root / "source.json",
                root / "0000.json",
                root / "0001.json",
            )
            source.write_bytes(body)
            command += ["--source", str(source)]
            created = subprocess.run(
                [
                    *command,
                    "plan",
                    "--source-sha256",
                    plan["source_sha256"],
                    "--output",
                    str(initial),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            digest = json.loads(created.stdout)["record_sha256"]
            entry = root / "attempt.json"
            entry.write_text(attempt(plan["candidates"][1]).model_dump_json(), encoding="utf-8")
            append = [*command, "record", str(initial), str(entry), "--output", str(next_record)]
            rejected = subprocess.run(append, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("fixed candidate order", rejected.stderr)
            self.assertFalse(next_record.exists())
            entry.write_text(
                attempt(plan["candidates"][0], "source_unresolved").model_dump_json(),
                encoding="utf-8",
            )
            subprocess.run(append, capture_output=True, text=True, check=True)
            checked = subprocess.run(
                [*command, "progress", str(next_record)], capture_output=True, text=True, check=True
            )
            self.assertEqual(json.loads(checked.stdout)["attempted"], 1)
            self.assertEqual(hashlib.sha256(initial.read_bytes()).hexdigest(), digest)
            self.assertEqual(source.read_bytes(), body)

    def test_publication_rejects_application_worktree(self):
        _, plan = prepare(source_rows(1, 1))
        with self.assertRaisesRegex(ValueError, "outside the application"):
            publish_record(Path(__file__).resolve().parents[1] / "unwanted.json", plan, ())


if __name__ == "__main__":
    unittest.main()
