import hashlib
import json
import unittest

from semantic_reviewer.domain.study_preparation import prepare_sample


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
