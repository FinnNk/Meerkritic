"""Challenge exact input/run binding through real SQLite, Parquet and MAF fixture execution."""

import unittest
from dataclasses import replace
from unittest.mock import patch

import test_discovery

from semantic_reviewer.application.comparison import assemble, baseline


class ComparisonTest(unittest.TestCase):
    def test_clustering_retry_reuses_embedding_and_counts_its_time_once(self):
        embed, _ = self.embed()
        lexical = baseline(self.discovery, embed.request.selection_id)
        first = self.discovery.cluster(embed.id, 0.85)
        with patch.object(self.files, "write_members", side_effect=OSError("Synthetic failure")):
            self.worker.run(once=True)
        second = self.discovery.cluster(embed.id, 0.85)
        self.worker.run(once=True)
        value, _ = assemble(
            self.discovery,
            lexical,
            [
                {"embedding_run": embed.id, "cluster_run": first.id},
                {
                    "embedding_run": embed.id,
                    "cluster_run": second.id,
                    "retry_reason": "Fixed writer",
                },
            ],
        )
        self.assertEqual(self.model.calls, 1)
        self.assertEqual([a.status for a in value.candidate.attempts], ["failed", "succeeded"])
        run, _ = self.discovery.inspect(second.id)
        from datetime import datetime

        self.assertEqual(
            value.candidate.attempts[1].elapsed_seconds,
            (
                datetime.fromisoformat(run.completed_at) - datetime.fromisoformat(run.started_at)
            ).total_seconds(),
        )

    def test_execution_budget_excludes_queue_time(self):
        lexical, attempts, _ = self.prepare()
        original = self.discovery.inspect

        def slow_queue(run_id):
            run, body = original(run_id)
            return replace(run, queued_at="2000-01-01T00:00:00+00:00"), {
                **body,
                "turnaround_ms": 9e9,
            }

        with patch.object(self.discovery, "inspect", side_effect=slow_queue):
            value, _ = assemble(self.discovery, lexical, attempts)
        self.assertLess(value.candidate.attempts[0].elapsed_seconds, 1800)

    def test_baseline_retry_requires_failed_predecessor_and_keeps_original(self):
        selection = self.selection()
        with patch(
            "semantic_reviewer.application.comparison.cluster_texts",
            side_effect=ValueError("Synthetic implementation failure"),
        ):
            failed = baseline(self.discovery, selection.id)
        retry = baseline(self.discovery, selection.id, failed, "Synthetic parser correction")
        self.assertEqual(len(retry["method"]["attempts"]), 2)
        self.assertEqual(
            retry["method"]["attempts"][0]["error"], "Synthetic implementation failure"
        )
        self.assertEqual(retry["method"]["attempts"][1]["status"], "succeeded")
        with self.assertRaises(ValueError):
            baseline(self.discovery, selection.id, failed, " ")
        with self.assertRaises(ValueError):
            baseline(self.discovery, selection.id, retry, "Again")

    setUp = test_discovery.DiscoveryTest.setUp
    complete = test_discovery.DiscoveryTest.complete
    selection = test_discovery.DiscoveryTest.selection
    embed = test_discovery.DiscoveryTest.embed

    def prepare(self):
        """Run synthetic embedding and clustering through the ordinary worker path."""
        embedding, body = self.embed()
        lexical = baseline(self.discovery, embedding.request.selection_id)
        cluster = self.discovery.cluster(embedding.id, 0.85)
        self.worker.run(once=True)
        return lexical, [{"embedding_run": embedding.id, "cluster_run": cluster.id}], body

    def test_exact_inputs_outputs_and_provenance(self):
        lexical, attempts, _ = self.prepare()
        result, evidence = assemble(self.discovery, lexical, attempts)
        self.assertEqual(result.purpose, "fixture")
        self.assertEqual(len(result.items), 2)
        self.assertEqual(len(result.candidate.groups), 1)
        self.assertEqual(
            evidence["attempts"][0]["embedding_result"]["framework"]["framework"],
            "Microsoft Agent Framework",
        )

    def test_changed_baseline_text_or_membership_fails(self):
        lexical, attempts, _ = self.prepare()
        lexical["items"][0]["text"] = "Different interpretation"
        with self.assertRaisesRegex(ValueError, "inputs differ"):
            assemble(self.discovery, lexical, attempts)
        lexical = baseline(self.discovery, lexical["selection_id"])
        lexical["method"]["groups"][0]["representative"] = "unknown"
        with self.assertRaises(ValueError):
            assemble(self.discovery, lexical, attempts)

    def test_valid_parquet_with_changed_text_is_not_same_input(self):
        lexical, attempts, body = self.prepare()
        rows = self.files.read_vectors(body["vectors_digest"])
        with patch.object(
            self.files,
            "read_vectors",
            return_value=tuple(
                (identity, "different text", vector) for identity, _, vector in rows
            ),
        ):
            with self.assertRaisesRegex(ValueError, "texts differ"):
                assemble(self.discovery, lexical, attempts)

    def test_valid_membership_file_with_wrong_groups_is_rejected(self):
        lexical, attempts, _ = self.prepare()
        rows = tuple(
            {"annotation_id": item["id"], "cluster": -1, "representative": False}
            for item in lexical["items"]
        )
        with patch.object(self.files, "read_members", return_value=rows):
            with self.assertRaisesRegex(ValueError, "deterministic replay"):
                assemble(self.discovery, lexical, attempts)

    def test_wrong_parameters_and_unfinished_runs_fail(self):
        lexical, attempts, _ = self.prepare()
        cluster = self.discovery.cluster(attempts[0]["embedding_run"], 0.9)
        attempts[0]["cluster_run"] = cluster.id
        with self.assertRaisesRegex(ValueError, "unfinished"):
            assemble(self.discovery, lexical, attempts)
        self.worker.run(once=True)
        with self.assertRaisesRegex(ValueError, "fixed parameters"):
            assemble(self.discovery, lexical, attempts)

    def test_failure_preserved_without_inventing_partition(self):
        self.model.failure = True
        selection = self.selection()
        lexical = baseline(self.discovery, selection.id)
        embed = self.discovery.embed(selection.id)
        self.worker.run(once=True)
        result, evidence = assemble(self.discovery, lexical, [{"embedding_run": embed.id}])
        self.assertEqual(result.candidate.attempts[0].status, "failed")
        self.assertEqual(result.candidate.groups, ())
        self.assertEqual(
            evidence["attempts"][0]["embedding_result"]["usage"]["measurement"]["outcome"],
            "provider_failure",
        )

    def test_missing_timestamps_fail_instead_of_using_queue_turnaround(self):
        lexical, attempts, _ = self.prepare()
        original = self.discovery.inspect

        def missing(run_id):
            run, body = original(run_id)
            return replace(run, started_at=None), body

        with patch.object(self.discovery, "inspect", side_effect=missing):
            with self.assertRaisesRegex(ValueError, "timestamps"):
                assemble(self.discovery, lexical, attempts)

    def test_profile_mismatch_and_success_rerun_fail(self):
        lexical, attempts, _ = self.prepare()
        with self.assertRaisesRegex(ValueError, "pinned profile"):
            assemble(self.discovery, lexical, attempts, {"dimensions": 768})
        with self.assertRaises(ValueError):
            assemble(self.discovery, lexical, attempts * 2)
