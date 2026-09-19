"""Validate invocation observations and calculate versioned API spend estimates."""

from decimal import Decimal
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import AwareDatetime, Field, model_validator

from semantic_reviewer.routing.selection import Count, Money, Name, Record, RoutingDecision, Version

Milliseconds = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Outcome = Literal[
    "success",
    "provider_failure",
    "semantic_failure",
    "deterministic_failure",
    "context_failure",
    "budget_failure",
    "policy_failure",
]


class TokenUsage(Record):
    """Retain unknown counts as None; cached/reasoning counts are subsets of totals.

    Provider adapters must normalise totals to include cached input and reasoning
    output before constructing this record. Accounting never bills a subset twice.
    """

    input_tokens: Count | None = None
    output_tokens: Count | None = None
    cached_input_tokens: Count | None = None
    reasoning_tokens: Count | None = None

    @model_validator(mode="after")
    def subsets(self) -> "TokenUsage":
        """Reject subset counts larger than known totals."""
        for part, total in (
            (self.cached_input_tokens, self.input_tokens),
            (self.reasoning_tokens, self.output_tokens),
        ):
            if part is not None and total is not None and part > total:
                raise ValueError("Token subset cannot exceed its total.")
        return self


class Measurement(Record):
    """Describe one completed invocation, including failures and partial telemetry."""

    started_at: AwareDatetime
    completed_at: AwareDatetime
    outcome: Outcome
    tokens: TokenUsage = TokenUsage()
    queue_ms: Milliseconds | None = None
    time_to_first_token_ms: Milliseconds | None = None
    generation_ms: Milliseconds | None = None
    provider_reported_cost: Money | None = None
    provider_currency: Name | None = None

    @model_validator(mode="after")
    def consistent(self) -> "Measurement":
        """Reject reversed time and provider costs without a currency."""
        if self.completed_at < self.started_at:
            raise ValueError("Completion cannot precede invocation start.")
        if (self.provider_reported_cost is None) != (self.provider_currency is None):
            raise ValueError("Provider cost and currency must be supplied together.")
        for timing in (self.queue_ms, self.time_to_first_token_ms, self.generation_ms):
            if timing is not None and timing > self.total_turnaround_ms:
                raise ValueError("A timing component cannot exceed total turnaround.")
        return self

    @property
    def total_turnaround_ms(self) -> float:
        """Return elapsed time from queue entry through invocation completion."""
        return (self.completed_at - self.started_at).total_seconds() * 1000


class Price(Record):
    """Express token rates per million; output includes reasoning tokens."""

    model_id: Name
    provider: Name
    input_per_million: Money
    output_per_million: Money
    cached_input_per_million: Money | None = None


class PriceCatalogue(Record):
    """Retain rates effective in a half-open UTC-aware time interval."""

    identity: Version
    currency: Name
    effective_from: AwareDatetime
    effective_until: AwareDatetime | None = None
    source: Name
    prices: tuple[Price, ...]

    @model_validator(mode="after")
    def consistent(self) -> "PriceCatalogue":
        """Reject duplicate prices and inverted effective intervals."""
        if self.effective_until is not None and self.effective_until <= self.effective_from:
            raise ValueError("Price interval must have positive duration.")
        keys = [(price.provider, price.model_id) for price in self.prices]
        if len(set(keys)) != len(keys):
            raise ValueError("Price entries must be unique.")
        return self


class ModelUsage(Record):
    """Bind measurements and optional spend estimate to one routing decision."""

    id: Name
    decision_id: Name
    measurement: Measurement
    price_catalogue: Version | None
    estimated_cost: Money | None
    currency: Name | None
    spend_basis: Literal["local", "catalogue", "unknown"]


def account_usage(
    decision: RoutingDecision, measurement: Measurement, catalogue: PriceCatalogue | None = None
) -> ModelUsage:
    """Estimate API spend without replacing unknown counts or provider-reported cost.

    Local execution has zero API spend. Remote estimates require complete token
    totals, matching rates and a catalogue effective at invocation start. Unknown
    cached counts produce an unknown estimate when cache rates differ. Missing
    rates or counts remain unknown; an out-of-period catalogue is an error.

    Raises:
        ValueError: The decision has no selected model or the catalogue is out of period.
    """
    if decision.selected is None:
        raise ValueError("A refused routing decision cannot have model usage.")
    estimate = None
    currency = None
    basis = "unknown"
    version = None
    if decision.selected.locality == "local":
        estimate, basis = Decimal(0), "local"
    elif catalogue is not None:
        start = measurement.started_at
        if start < catalogue.effective_from or (
            catalogue.effective_until is not None and start >= catalogue.effective_until
        ):
            raise ValueError("Price catalogue was not effective at invocation start.")
        version, currency = catalogue.identity, catalogue.currency
        price = next(
            (
                price
                for price in catalogue.prices
                if price.model_id == decision.selected.id
                and price.provider == decision.selected.provider
            ),
            None,
        )
        tokens = measurement.tokens
        if (
            price is not None
            and tokens.input_tokens is not None
            and tokens.output_tokens is not None
        ):
            cached_rate = price.cached_input_per_million
            cached = tokens.cached_input_tokens
            if cached is None and (cached_rate is None or cached_rate == price.input_per_million):
                cached = 0
            if cached is not None:
                estimate = (
                    (tokens.input_tokens - cached) * price.input_per_million
                    + cached * (cached_rate if cached_rate is not None else price.input_per_million)
                    + tokens.output_tokens * price.output_per_million
                ) / Decimal(1_000_000)
                basis = "catalogue"
    return ModelUsage(
        id=str(uuid4()),
        decision_id=decision.id,
        measurement=measurement,
        price_catalogue=version,
        estimated_cost=estimate,
        currency=currency,
        spend_basis=basis,
    )


def usage_summary(decision: RoutingDecision, usage: ModelUsage) -> str:
    """Return the terse model, token, spend and elapsed display; preserve unknowns."""
    if usage.decision_id != decision.id or decision.selected is None:
        raise ValueError("Usage does not belong to a selected routing decision.")
    tokens = usage.measurement.tokens
    counts = f"{tokens.input_tokens if tokens.input_tokens is not None else '?'} in / "
    counts += f"{tokens.output_tokens if tokens.output_tokens is not None else '?'} out"
    spend = "spend unknown"
    if usage.spend_basis == "local":
        spend = "local"
    elif usage.estimated_cost is not None:
        spend = f"~{usage.estimated_cost:.6f} {usage.currency}"
    return (
        f"{decision.selected.id} · {counts} · {spend} · "
        f"{usage.measurement.total_turnaround_ms / 1000:.1f}s"
    )
