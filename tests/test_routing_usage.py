"""Exercise historical pricing and incomplete/failure telemetry without model calls."""

import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from pydantic import ValidationError
from test_routing_selection import EXAMPLE

from semantic_reviewer.routing.selection import (
    RoutingConfig,
    TaskRequirements,
    Version,
    select_route,
)
from semantic_reviewer.routing.usage import (
    Measurement,
    Price,
    PriceCatalogue,
    TokenUsage,
    account_usage,
    usage_summary,
)


class UsageTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 9, 19, tzinfo=UTC)
        self.config = RoutingConfig.model_validate_json(EXAMPLE.read_text(encoding="utf-8"))
        self.remote = select_route(
            self.config, TaskRequirements(task_id="1", task_class="normalisation", privacy="public")
        )
        self.price = PriceCatalogue(
            identity=Version(id="synthetic", version="1"),
            currency="USD",
            effective_from=self.start,
            effective_until=self.start + timedelta(days=1),
            source="Synthetic rates for contract tests, not provider pricing.",
            prices=(
                Price(
                    model_id="example-remote",
                    provider="example-host",
                    input_per_million=Decimal("2"),
                    output_per_million=Decimal("8"),
                    cached_input_per_million=Decimal("0.5"),
                ),
            ),
        )

    def measurement(self, **kwargs):
        return Measurement(
            started_at=self.start,
            completed_at=self.start + timedelta(seconds=2),
            outcome=kwargs.pop("outcome", "success"),
            **kwargs,
        )

    def test_cached_and_reasoning_subsets_are_not_double_billed(self):
        measurement = self.measurement(
            tokens=TokenUsage(
                input_tokens=1000, output_tokens=100, cached_input_tokens=400, reasoning_tokens=60
            ),
            queue_ms=10.0,
            time_to_first_token_ms=300.0,
            generation_ms=1500.0,
        )
        usage = account_usage(self.remote, measurement, self.price)
        self.assertEqual(usage.estimated_cost, Decimal("0.0022"))
        self.assertEqual(usage.price_catalogue.version, "1")
        self.assertEqual(usage.measurement.total_turnaround_ms, 2000)
        self.assertIn("~0.002200 USD", usage_summary(self.remote, usage))

    def test_unknown_tokens_cache_and_rates_remain_unknown(self):
        for tokens in (TokenUsage(), TokenUsage(input_tokens=1000, output_tokens=100)):
            usage = account_usage(self.remote, self.measurement(tokens=tokens), self.price)
            self.assertIsNone(usage.estimated_cost)
        usage = account_usage(self.remote, self.measurement())
        self.assertIn("? in / ? out", usage_summary(self.remote, usage))
        self.assertIn("spend unknown", usage_summary(self.remote, usage))

    def test_local_zero_api_spend_does_not_require_token_counts(self):
        local = select_route(self.config, TaskRequirements(task_id="1", task_class="normalisation"))
        usage = account_usage(local, self.measurement())
        self.assertEqual(usage.estimated_cost, Decimal(0))
        self.assertIsNone(usage.price_catalogue)
        self.assertIn(" · local · ", usage_summary(local, usage))

    def test_price_version_must_be_effective_at_start(self):
        for start in (self.start - timedelta(seconds=1), self.start + timedelta(days=1)):
            measurement = Measurement(started_at=start, completed_at=start, outcome="success")
            with self.assertRaisesRegex(ValueError, "not effective"):
                account_usage(self.remote, measurement, self.price)

    def test_invalid_observations_are_rejected(self):
        for kwargs in (
            {"input_tokens": -1},
            {"input_tokens": 1, "cached_input_tokens": 2},
            {"output_tokens": 1, "reasoning_tokens": 2},
            {"input_tokens": True},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                TokenUsage(**kwargs)
        for kwargs in (
            {"provider_reported_cost": Decimal("1")},
            {"queue_ms": 2001.0},
            {"generation_ms": float("nan")},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                self.measurement(**kwargs)

    def test_provider_failure_and_reported_spend_are_not_semantic_failure_or_estimates(self):
        usage = account_usage(
            self.remote,
            self.measurement(
                outcome="provider_failure",
                provider_reported_cost=Decimal("0.03"),
                provider_currency="USD",
            ),
            self.price,
        )
        self.assertEqual(usage.measurement.outcome, "provider_failure")
        self.assertEqual(usage.measurement.provider_reported_cost, Decimal("0.03"))
        self.assertIsNone(usage.estimated_cost)

    def test_refusal_cannot_be_misrepresented_as_model_execution(self):
        refused = select_route(self.config, TaskRequirements(task_id="1", task_class="unknown"))
        with self.assertRaisesRegex(ValueError, "refused"):
            account_usage(refused, self.measurement())
