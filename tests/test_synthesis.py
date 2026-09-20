"""Challenge real MAF synthesis, exact context references and inspectable negative outcomes."""

import json
import unittest
from dataclasses import asdict
from datetime import UTC, datetime
from unittest.mock import patch

import test_rules

from semantic_reviewer.adapters.maf_synthesis import MafSynthesisRuntime
from semantic_reviewer.application.model import ModelFailure, ModelReply
from semantic_reviewer.application.synthesis import RuleSynthesisExecution, SynthesisInput
from semantic_reviewer.routing.selection import TaskRequirements
from semantic_reviewer.routing.usage import Measurement, TokenUsage


class FixtureSynthesis:
    def __init__(self, mode="candidate"):
        self.mode, self.calls = mode, 0

    def generate(self, decision, request, queued_at):
        self.calls += 1
        measurement = Measurement(
            started_at=queued_at,
            completed_at=datetime.now(UTC),
            outcome="provider_failure" if self.mode == "provider_failure" else "success",
            tokens=TokenUsage(input_tokens=50, output_tokens=80),
        )
        if self.mode == "provider_failure":
            raise ModelFailure("Fixture provider unavailable", measurement)
        examples = json.loads(request.user)["examples"]
        candidate = {
            "statement": "Close resources on every exit",
            "scope": "function",
            "applicability": "The function acquires a resource",
            "violation": "A resource remains open",
            "exclusions": ["Ownership explicitly transferred"],
            "supporting_annotations": [
                "invented" if self.mode == "invented" else examples[0]["annotation_id"]
            ],
        }
        payload = {
            "candidate": None if self.mode == "insufficient" else candidate,
            "insufficiency_reason": "No coherent shared rule"
            if self.mode == "insufficient"
            else None,
        }
        content = "invalid JSON" if self.mode == "invalid" else json.dumps(payload)
        return ModelReply(
            content, measurement, json.dumps(asdict(request)), json.dumps({"content": content})
        )


class SynthesisTest(unittest.TestCase):
    complete = test_rules.RulesTest.complete
    selection = test_rules.RulesTest.selection
    embed = test_rules.RulesTest.embed

    def setUp(self):
        test_rules.RulesTest.setUp(self)
        self.model = FixtureSynthesis()
        self.runtime = MafSynthesisRuntime(self.model)
        self.execution.synthesis = RuleSynthesisExecution(
            self.discovery, self.rules, self.routing, self.runtime
        )

    def synthesise(self):
        run = self.discovery.synthesise(self.cluster.id, 0)
        self.worker.run(once=True)
        return self.discovery.inspect(run.id)

    def test_full_routed_maf_proposal_retains_trace_and_weak_support(self):
        run, result = self.synthesise()
        self.assertEqual(run.status, "succeeded")
        head, body, evidence, _ = self.rule_store.read(result["rule_version"])
        trace = self.files.read_json(result["trace_digest"])
        self.assertEqual(body.origin.trace_digest, result["trace_digest"])
        self.assertEqual(body.origin.kind, "model")
        self.assertEqual(head.status, "candidate")
        self.assertEqual({item.verification for item in evidence}, {"weak"})
        self.assertEqual(trace["routing"]["policy"]["version"], "2")
        self.assertEqual(trace["framework"]["outcome"], "completed")
        self.assertEqual(trace["usage"]["measurement"]["outcome"], "success")
        self.assertIn("rule-synthesis-v2", trace["provider_request"])
        self.assertEqual(trace["cluster_digest"], body.cluster_digest)
        self.assertEqual(self.model.calls, 1)

    def test_invented_references_and_invalid_json_retain_raw_output_without_candidates(self):
        for mode in ("invented", "invalid"):
            self.model.mode = mode
            run, result = self.synthesise()
            self.assertEqual(run.status, "failed")
            self.assertIsNone(result["rule_version"])
            trace = self.files.read_json(result["trace_digest"])
            self.assertEqual(trace["usage"]["measurement"]["outcome"], "semantic_failure")
            self.assertTrue(trace["model_output"])
        self.assertEqual(len(self.rule_store.recent()), 1)

    def test_provider_failure_is_not_semantic_failure_or_automatic_escalation(self):
        self.model.mode = "provider_failure"
        run, result = self.synthesise()
        self.assertEqual(run.status, "failed")
        trace = self.files.read_json(result["trace_digest"])
        self.assertEqual(trace["usage"]["measurement"]["outcome"], "provider_failure")
        self.worker.run(once=True)
        self.assertEqual(self.model.calls, 1)

    def test_insufficient_evidence_is_an_inspectable_success_without_an_invented_rule(self):
        self.model.mode = "insufficient"
        run, result = self.synthesise()
        self.assertEqual(run.status, "succeeded")
        self.assertIsNone(result["rule_version"])
        self.assertEqual(result["insufficiency_reason"], "No coherent shared rule")
        self.assertEqual(len(self.rule_store.recent()), 1)

    def test_context_overflow_and_missing_group_fail_before_provider_calls(self):
        record = self.records[0]
        large = record.model_copy(
            update={
                "interpretation": record.interpretation.model_copy(
                    update={"issue_statement": "a" * 4000, "proposed_invariant": "b" * 4000}
                )
            }
        )
        decision = self.routing.route(
            TaskRequirements(
                task_id="context-probe",
                task_class="rule_synthesis",
                capabilities=("structured_output",),
                expected_output_tokens=768,
            )
        )
        outcome = self.runtime.run(SynthesisInput((large, large), decision, datetime.now(UTC)))
        self.assertEqual(outcome.measurement.outcome, "context_failure")
        run = self.discovery.synthesise(self.cluster.id, 999)
        self.worker.run(once=True)
        self.assertEqual(self.discovery_store.get(run.id).status, "failed")
        self.assertEqual(self.model.calls, 0)

    def test_published_candidate_survives_interruption_without_model_replay(self):
        run = self.discovery.synthesise(self.cluster.id, 0)
        with patch.object(self.discovery.store, "finish", side_effect=RuntimeError("interrupted")):
            with self.assertRaises(RuntimeError):
                self.worker.run(once=True)
        self.assertEqual(self.discovery.store.get(run.id).status, "running")
        self.worker.run(once=True)
        self.assertEqual(self.discovery.store.get(run.id).status, "failed")
        self.assertEqual(self.model.calls, 1)
        candidates = [self.rule_store.read(head.version_id) for head in self.rule_store.recent()]
        body = next(body for _, body, _, _ in candidates if body.origin.kind == "model")
        self.assertEqual(self.files.read_json(body.origin.trace_digest)["run_id"], run.id)

    def test_live_telemetry_uses_routing_record_before_final_manifest(self):
        self.discovery.journal = self.routing.journal
        run = self.discovery.synthesise(self.cluster.id, 0)
        claimed = self.discovery.store.claim("fixture-worker")
        decision = self.routing.route(
            TaskRequirements(
                task_id=run.id,
                task_class="rule_synthesis",
                capabilities=("structured_output",),
                expected_output_tokens=768,
            )
        )
        self.discovery.store.bind_route(claimed, decision.id)
        line = self.discovery.telemetry(self.discovery.store.get(run.id))
        self.assertIn(decision.selected.id, line)
        self.assertIn("? in / ? out", line)
        self.assertIn("local", line)
