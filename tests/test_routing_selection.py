"""Challenge routing constraints with synthetic inventories; never call a provider."""

import json
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from pydantic import ValidationError

from semantic_reviewer.routing.selection import (
    BudgetConstraint,
    CostQuote,
    ProviderHealth,
    RoutingConfig,
    TaskRequirements,
    Version,
    select_route,
)

EXAMPLE = Path(__file__).resolve().parents[1] / "config/routing/example.json"


class RoutingTest(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.task = TaskRequirements(
            task_id="task-1", task_class="normalisation", capabilities=("structured_output",)
        )

    def config(self):
        return RoutingConfig.model_validate_json(json.dumps(self.raw))

    def test_default_privacy_and_internal_input_reject_remote_primary(self):
        for privacy in ("local_only", "internal"):
            with self.subTest(privacy=privacy):
                task = TaskRequirements(**{**self.task.model_dump(), "privacy": privacy})
                decision = select_route(self.config(), task)
                self.assertEqual(decision.selected.id, "example-local")
                self.assertEqual(decision.candidates[0].rejected_by, ("privacy",))
                self.assertEqual(decision.inventory.version, "1")
                self.assertEqual(decision.policy.version, "1")

    def test_explicit_model_override_cannot_relax_privacy_or_silently_fallback(self):
        decision = select_route(self.config(), self.task, model_override="example-remote")
        self.assertIsNone(decision.selected)
        self.assertEqual(len(decision.candidates), 1)
        self.assertIn("no_eligible_model", decision.reasons)
        self.assertEqual(decision.policy.id, "example")

    def test_project_locality_cannot_be_overridden_by_public_task(self):
        self.raw["local_only"] = True
        task = TaskRequirements(task_id="public", task_class="normalisation", privacy="public")
        self.assertEqual(select_route(self.config(), task).selected.id, "example-local")

    def test_policy_precedence_and_unknown_override_fail_closed(self):
        for name in ("project", "task", "invocation"):
            self.raw["policies"].append(
                {**self.raw["policies"][0], "identity": {"id": name, "version": "1"}}
            )
        self.assertEqual(select_route(self.config(), self.task).policy_source, "system")
        self.raw["project_default"] = {"id": "project", "version": "1"}
        self.assertEqual(select_route(self.config(), self.task).policy_source, "project")
        task = TaskRequirements(
            **{**self.task.model_dump(), "policy_override": Version(id="task", version="1")}
        )
        self.assertEqual(select_route(self.config(), task).policy_source, "task")
        decision = select_route(
            self.config(), task, invocation_policy=Version(id="invocation", version="1")
        )
        self.assertEqual(decision.policy_source, "invocation")
        with self.assertRaisesRegex(ValueError, "missing or inactive"):
            select_route(self.config(), task, invocation_policy=Version(id="task", version="2"))

    def test_capability_context_family_and_model_lifecycle_are_hard_constraints(self):
        mutations = (
            ("capabilities", [], "capabilities"),
            ("practical_input_tokens", 10, "context"),
            ("output_tokens", 10, "context"),
            ("status", "retired", "model_unavailable"),
            ("status", "unavailable", "model_unavailable"),
            ("family", "excluded", "reviewer_independence"),
        )
        task = TaskRequirements(
            **{
                **self.task.model_dump(),
                "min_input_tokens": 20,
                "excluded_families": ("excluded",),
            }
        )
        for field, value, reason in mutations:
            with self.subTest(field=field, value=value):
                original = self.raw["inventory"]["models"][1][field]
                self.raw["inventory"]["models"][1][field] = value
                decision = select_route(self.config(), task)
                self.assertIsNone(decision.selected)
                self.assertIn(reason, decision.candidates[1].rejected_by)
                self.raw["inventory"]["models"][1][field] = original

    def test_provider_failure_is_explained_without_semantic_escalation(self):
        health = ProviderHealth(
            provider="example-runtime",
            state="unavailable",
            evidence="Synthetic HTTP 503",
            observed_at=datetime.now(UTC),
        )
        decision = select_route(self.config(), self.task, health=(health,))
        self.assertIsNone(decision.selected)
        self.assertIn("provider_unavailable", decision.candidates[1].rejected_by)
        self.assertIsNone(decision.escalation_from)
        self.assertEqual(decision.health, (health,))

    def test_invalid_configuration_does_not_silently_use_defaults(self):
        for change in ("unknown", "duplicate", "inventory", "reference", "inactive"):
            raw = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            if change == "unknown":
                raw["privay"] = "public"
            elif change == "duplicate":
                raw["inventory"]["models"].append(raw["inventory"]["models"][0])
            elif change == "inventory":
                raw["policies"][0]["inventory"]["version"] = "2"
            elif change == "reference":
                raw["policies"][0]["routes"][0]["models"] = ["missing"]
            else:
                raw["policies"][0]["state"] = "retired"
            with self.subTest(change=change), self.assertRaises(ValueError):
                select_route(RoutingConfig.model_validate_json(json.dumps(raw)), self.task)

    def test_counts_and_unknown_privacy_are_strict(self):
        for update in ({"privacy": "secret"}, {"min_input_tokens": -1}, {"min_input_tokens": True}):
            with self.subTest(update=update), self.assertRaises(ValidationError):
                TaskRequirements(**{**self.task.model_dump(), **update})

    def test_soft_budget_prefers_affordable_eligible_route_hard_budget_rejects_unknown(self):
        task = TaskRequirements(task_id="public", task_class="normalisation", privacy="public")
        quote = CostQuote(
            model_id="example-local",
            amount=Decimal("0"),
            currency="USD",
            price_catalogue=Version(id="prices", version="1"),
        )
        budget = BudgetConstraint(maximum=Decimal("1"), currency="USD")
        decision = select_route(self.config(), task, budget=budget, quotes=(quote,))
        self.assertEqual(decision.selected.id, "example-local")
        self.assertIn("soft_budget_preference", decision.reasons)
        hard = BudgetConstraint(maximum=Decimal("1"), currency="USD", hard=True)
        refused = select_route(self.config(), task, budget=hard)
        self.assertIsNone(refused.selected)
        self.assertTrue(all("budget" in item.rejected_by for item in refused.candidates))

    def test_context_strategy_limits_inputs_and_reserves_output(self):
        self.raw["policies"][0]["context"] = {"max_fraction_of_context": 0.5}
        task = TaskRequirements(**{**self.task.model_dump(), "min_input_tokens": 1025})
        self.assertIsNone(select_route(self.config(), task).selected)
        self.assertEqual(select_route(self.config(), self.task).max_input_tokens, 1024)

    def test_missing_task_and_unknown_model_produce_explained_refusals(self):
        task = TaskRequirements(task_id="new", task_class="unconfigured")
        self.assertIsNone(select_route(self.config(), task).selected)
        result = select_route(self.config(), self.task, model_override="missing")
        self.assertEqual(result.candidates[0].rejected_by, ("unknown_model",))
