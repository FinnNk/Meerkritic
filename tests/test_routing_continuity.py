"""Keep reserved transition/handoff contracts explicit without executing policy switches."""

import json
import unittest

from pydantic import ValidationError

from semantic_reviewer.routing.continuity import AgentHandoff, RoutingPolicyTransition


class ContinuityTest(unittest.TestCase):
    def test_transition_preserves_both_versions_and_requires_an_actual_change(self):
        value = {
            "id": "change",
            "agent_run_id": "run",
            "from_policy": {"id": "local", "version": "1"},
            "to_policy": {"id": "local", "version": "2"},
            "reason": "Explicit human request",
            "requested_by": "human",
            "created_at": "2026-09-20T00:00:00Z",
        }
        record = RoutingPolicyTransition.model_validate_json(json.dumps(value))
        self.assertEqual((record.from_policy.version, record.to_policy.version), ("1", "2"))
        value["to_policy"] = value["from_policy"]
        with self.assertRaises(ValidationError):
            RoutingPolicyTransition.model_validate_json(json.dumps(value))

    def test_handoff_reserves_all_context_fields_and_rejects_raw_transcript_field(self):
        value = {
            "task_objective": "Review a candidate",
            "previous_model_summary": "Needs evidence",
            **{
                key: []
                for key in (
                    "acceptance_criteria",
                    "current_plan",
                    "completed_actions",
                    "changed_files",
                    "tool_results",
                    "failing_checks",
                    "unresolved_questions",
                    "relevant_context",
                    "provenance_refs",
                )
            },
        }
        record = AgentHandoff.model_validate_json(json.dumps(value))
        self.assertEqual(record.provenance_refs, ())
        value["raw_transcript"] = "Not passed implicitly"
        with self.assertRaises(ValidationError):
            AgentHandoff.model_validate_json(json.dumps(value))
