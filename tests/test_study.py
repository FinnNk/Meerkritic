"""Challenge masking, completeness and exact empirical decision thresholds on synthetic inputs."""

import unittest

from semantic_reviewer.domain.study import Comparison, Ratings, analyse, assessment, digest


def comparison(groups=10):
    """Build distinct synthetic partitions with equal coverage, without model calls."""
    items = [
        {"id": str(i), "text": f"Synthetic concern {i}", "repository": f"fixture/{i // 4}"}
        for i in range(40)
    ]
    methods = {}
    for name, offset in (("baseline", 0), ("candidate", 1)):
        members = [[str(3 * group + offset + j) for j in range(3)] for group in range(groups)]
        used = {i for group in members for i in group}
        methods[name] = {
            "attempts": [{"status": "succeeded", "elapsed_seconds": 2}],
            "groups": [{"members": group, "representative": group[0]} for group in members],
            "outliers": [item["id"] for item in items if item["id"] not in used],
        }
    return Comparison.model_validate({"purpose": "fixture", "items": items, **methods})


def ratings(value, baseline=7, candidate=8):
    """Generate explicitly synthetic test judgements for known criterion boundaries."""
    pack, mapping = assessment(value)
    positive = set(
        mapping["methods"]["baseline"][:baseline] + mapping["methods"]["candidate"][:candidate]
    )
    return Ratings.model_validate(
        {
            "pack_sha256": digest(pack),
            "purpose": "fixture",
            "rater": "synthetic test",
            "suspected_unmasking": "",
            "ratings": [
                {
                    "group_id": group["group_id"],
                    "judgement": "coherent" if group["group_id"] in positive else "uncertain",
                    "reason": "Synthetic test only",
                }
                for group in pack["groups"]
            ],
        }
    )


class StudyTest(unittest.TestCase):
    def test_review_cap_reports_unassessed_groups(self):
        value = comparison(13)
        pack, mapping = assessment(value)
        self.assertEqual(mapping["groups_per_method"], 12)
        self.assertEqual(len(pack["groups"]), 24)
        report = analyse(value, ratings(value, 12, 12))
        self.assertEqual(report["methods"]["candidate"]["unassessed_groups"], 1)

    def test_coverage_loss_inclusive_boundary(self):
        body = comparison(8).model_dump()
        baseline = body["baseline"]
        for count in (4, 5):
            extra = tuple(str(i) for i in range(32, 32 + count))
            baseline["groups"][0]["members"] = ("0", "1", "2", *extra)
            baseline["outliers"] = tuple(str(i) for i in range(24, 40) if str(i) not in extra)
            value = Comparison.model_validate(body)
            report = analyse(value, ratings(value, 0, 8))
            self.assertEqual(report["criteria"]["coverage"], count == 4)

    def test_deterministic_masking_and_equal_budget(self):
        value = comparison()
        pack, mapping = assessment(value)
        self.assertEqual(assessment(value), (pack, mapping))
        self.assertEqual(mapping["groups_per_method"], 10)
        self.assertEqual(mapping["shared_groups"], 0)
        self.assertNotIn("baseline", str(pack))
        self.assertNotIn("candidate", str(pack))
        self.assertTrue(all("representative" not in group for group in pack["groups"]))
        self.assertEqual(len(pack["groups"]), 20)

    def test_identical_memberships_rated_once_even_with_reversed_order(self):
        body = comparison().model_dump()
        body["candidate"] = body["baseline"]
        body["candidate"]["groups"] = list(reversed(body["candidate"]["groups"]))
        value = Comparison.model_validate(body)
        pack, mapping = assessment(value)
        self.assertEqual(len(pack["groups"]), 10)
        self.assertEqual(mapping["shared_groups"], 10)
        report = analyse(value, ratings(value, 10, 10))
        self.assertFalse(report["criteria"]["primary"])

    def test_exact_thresholds_and_uncertain_denominator(self):
        value = comparison()
        report = analyse(value, ratings(value))
        self.assertEqual(report["recommendation"], "candidate")
        self.assertEqual(report["owner_decision"], "pending")
        self.assertEqual(report["methods"]["candidate"]["uncertain"], 2)
        self.assertEqual(report["methods"]["candidate"]["assessed_denominator"], 10)
        self.assertEqual(report["methods"]["candidate"]["input_denominator"], 40)
        self.assertFalse(analyse(value, ratings(value, 6, 7))["criteria"]["primary"])
        self.assertFalse(analyse(value, ratings(value, 8, 8))["criteria"]["primary"])
        boundary = comparison(8)
        self.assertEqual(analyse(boundary, ratings(boundary, 5, 6))["recommendation"], "candidate")

    def test_missing_is_incomplete_not_dropped(self):
        value = comparison()
        body = ratings(value).model_dump()
        body["ratings"] = body["ratings"][:-1]
        report = analyse(value, Ratings.model_validate(body))
        self.assertEqual(report["status"], "incomplete")
        self.assertIsNone(report["criteria"]["primary"])
        self.assertEqual(sum(m["missing"] for m in report["methods"].values()), 1)

    def test_too_few_groups_is_insufficient_even_if_all_are_coherent(self):
        value = comparison(7)
        report = analyse(value, ratings(value, 0, 7))
        self.assertEqual(report["status"], "insufficient")
        self.assertIsNone(report["criteria"]["primary"])
        self.assertEqual(report["recommendation"], "no adoption recommendation")

    def test_resource_cap_and_retained_failed_retry(self):
        body = comparison().model_dump()
        body["candidate"]["attempts"] = [
            {"status": "failed", "elapsed_seconds": 1798, "error": "Implementation failure"},
            {"status": "succeeded", "elapsed_seconds": 2, "retry_reason": "Fixed parser"},
        ]
        value = Comparison.model_validate(body)
        self.assertTrue(analyse(value, ratings(value))["criteria"]["within_resource_cap"])
        body["candidate"]["attempts"][0]["elapsed_seconds"] = 1798.01
        value = Comparison.model_validate(body)
        report = analyse(value, ratings(value))
        self.assertFalse(report["criteria"]["within_resource_cap"])
        self.assertEqual(len(report["methods"]["candidate"]["attempts"]), 2)

    def test_failed_run_cannot_claim_partition_or_adoption(self):
        body = comparison().model_dump()
        body["candidate"] = {
            "attempts": [{"status": "failed", "elapsed_seconds": 2, "error": "Unavailable"}]
        }
        value = Comparison.model_validate(body)
        report = analyse(value, ratings(value))
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["methods"]["candidate"]["failed_inputs"], 40)
        self.assertFalse(report["criteria"]["valid_outputs"])
        body["candidate"]["outliers"] = ["1"]
        with self.assertRaises(ValueError):
            Comparison.model_validate(body)

    def test_duplicate_missing_unknown_and_wrong_representative_fail(self):
        for change in ("duplicate", "missing", "unknown", "representative"):
            body = comparison().model_dump()
            group = body["candidate"]["groups"][0]
            if change == "duplicate":
                group["members"] = ("1", "1", "3")
            elif change == "missing":
                body["candidate"]["outliers"] = ()
            elif change == "unknown":
                group["members"] = ("unknown", "2", "3")
            else:
                group["representative"] = "0"
            with self.subTest(change=change), self.assertRaises(ValueError):
                Comparison.model_validate(body)

    def test_foreign_duplicate_and_purpose_mismatched_ratings_fail(self):
        value = comparison()
        for change in ("digest", "duplicate", "foreign", "purpose"):
            body = ratings(value).model_dump()
            if change == "digest":
                body["pack_sha256"] = "0" * 64
            elif change == "duplicate":
                body["ratings"] = (*body["ratings"], body["ratings"][0])
            elif change == "foreign":
                body["ratings"][0]["group_id"] = "unknown"
            else:
                body["purpose"] = "research"
            with self.subTest(change=change), self.assertRaises(ValueError):
                analyse(value, Ratings.model_validate(body))

    def test_no_undisclosed_or_successful_attempt_reruns(self):
        for change in ("success", "missing_diagnosis", "two_reruns"):
            body = comparison().model_dump()
            attempts = [
                {"status": "failed", "elapsed_seconds": 1, "error": "Broken"},
                {"status": "succeeded", "elapsed_seconds": 1, "retry_reason": "Fixed"},
            ]
            body["candidate"]["attempts"] = attempts
            if change == "success":
                attempts[0] = {"status": "succeeded", "elapsed_seconds": 1}
            elif change == "missing_diagnosis":
                attempts[1].pop("retry_reason")
            else:
                body["baseline"]["attempts"] = attempts
            with self.subTest(change=change), self.assertRaises(ValueError):
                Comparison.model_validate(body)

    def test_research_requires_exact_sample_size_and_repository_quota(self):
        body = comparison().model_dump()
        body["purpose"] = "research"
        Comparison.model_validate(body)
        for item in body["items"]:
            item["repository"] = "same/repo"
        with self.assertRaises(ValueError):
            Comparison.model_validate(body)
