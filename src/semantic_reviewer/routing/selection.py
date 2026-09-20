"""Select eligible models without provider calls or application-domain knowledge."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, model_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Count = Annotated[int, Field(ge=0)]
Money = Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]


class Record(BaseModel):
    """Reject unknown fields and coercions; keep validated routing records immutable."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class Version(Record):
    """Identify an exact configuration version, never an implicit latest revision."""

    id: Name
    version: Name


class Model(Record):
    """Describe configured capabilities, not proof of current provider availability.

    Context limits are usable input and output token capacities. Evidence records
    how the operator obtained these claims; practical input takes precedence over
    advertised input when the deployment cannot support the latter.
    """

    id: Name
    provider: Name
    family: Name
    locality: Literal["local", "remote"]
    status: Literal["active_current", "active_older", "deprecated", "retired", "unavailable"]
    capabilities: tuple[
        Literal["coding", "tool_use", "structured_output", "reasoning", "embeddings"], ...
    ]
    practical_input_tokens: Annotated[int, Field(gt=0)]
    output_tokens: Annotated[int, Field(ge=0)]
    evidence: Name


class ModelInventory(Record):
    """Keep a versioned, unambiguous inventory of configured models."""

    identity: Version
    models: tuple[Model, ...]

    @model_validator(mode="after")
    def unique_models(self) -> "ModelInventory":
        """Reject duplicate model identifiers within an inventory."""
        if len({model.id for model in self.models}) != len(self.models):
            raise ValueError("Inventory model IDs must be unique.")
        return self


class ContextStrategy(Record):
    """Pass a context budget to the future builder without embedding model names."""

    id: Name = "direct-v1"
    mode: Literal["direct_large_context", "retrieval_first", "summary_then_retrieval"] = (
        "direct_large_context"
    )
    reserve_output_tokens: Count = 256
    max_fraction_of_context: Annotated[float, Field(gt=0, le=1)] = 1.0
    include_raw_transcript: bool = False


class TaskRequirements(Record):
    """Express task needs; internal and local-only input cannot route remotely."""

    task_id: Name
    task_class: Name
    capabilities: tuple[
        Literal["coding", "tool_use", "structured_output", "reasoning", "embeddings"], ...
    ] = ()
    min_input_tokens: Count = 0
    expected_output_tokens: Count = 0
    privacy: Literal["public", "internal", "local_only"] = "local_only"
    excluded_families: tuple[Name, ...] = ()
    policy_override: Version | None = None


class Route(Record):
    """Order model preferences for one task class; eligibility is checked first."""

    task_class: Name
    models: tuple[Name, ...]


class RoutingPolicy(Record):
    """Bind ordered routes and context strategy to an exact inventory revision."""

    identity: Version
    inventory: Version
    state: Literal["draft", "active", "superseded", "retired"] = "active"
    routes: tuple[Route, ...]
    local_only: bool = False
    context: ContextStrategy = ContextStrategy()

    @model_validator(mode="after")
    def unique_routes(self) -> "RoutingPolicy":
        """Reject ambiguous routes or repeated candidates."""
        if len({route.task_class for route in self.routes}) != len(self.routes):
            raise ValueError("Policy task classes must be unique.")
        if any(len(set(route.models)) != len(route.models) for route in self.routes):
            raise ValueError("Route candidates must be unique.")
        return self


class RoutingConfig(Record):
    """Resolve defaults without allowing invocation overrides to relax project privacy."""

    inventory: ModelInventory
    policies: tuple[RoutingPolicy, ...]
    system_default: Version
    project_default: Version | None = None
    local_only: bool = False

    @model_validator(mode="after")
    def valid_references(self) -> "RoutingConfig":
        """Reject ambiguous versions, missing defaults and foreign model references."""
        identities = [policy.identity for policy in self.policies]
        if len(set(identities)) != len(identities):
            raise ValueError("Policy identities must be unique.")
        if self.system_default not in identities or (
            self.project_default is not None and self.project_default not in identities
        ):
            raise ValueError("Default policy version is not configured.")
        models = {model.id for model in self.inventory.models}
        for policy in self.policies:
            if policy.inventory != self.inventory.identity:
                raise ValueError("Policy inventory version does not match.")
            if any(model not in models for route in policy.routes for model in route.models):
                raise ValueError("Policy references an unknown model.")
        return self


class ProviderHealth(Record):
    """Supply invocation-scoped infrastructure observations, not reasoning assessments."""

    provider: Name
    state: Literal["healthy", "degraded", "rate_limited", "unavailable"]
    evidence: Name
    observed_at: AwareDatetime


class BudgetConstraint(Record):
    """Constrain an invocation in one currency; absent quotes fail a hard budget."""

    maximum: Money
    currency: Name
    hard: bool = False


class CostQuote(Record):
    """Carry an invocation estimate with the price version that produced it."""

    model_id: Name
    amount: Money
    currency: Name
    price_catalogue: Version


class Candidate(Record):
    """Explain eligibility and budget preference for one considered model."""

    model_id: Name
    rejected_by: tuple[str, ...]
    over_soft_budget: bool = False


class RoutingDecision(Record):
    """Retain selection inputs and explanations; a refused route has no selected model."""

    id: Name
    created_at: AwareDatetime
    requirements: TaskRequirements
    inventory: Version
    policy: Version
    policy_source: Literal["invocation", "task", "project", "system"]
    selected: Model | None
    reasons: tuple[str, ...]
    candidates: tuple[Candidate, ...]
    context: ContextStrategy
    max_input_tokens: Count
    escalation_from: Name | None = None
    model_override: Name | None = None
    health: tuple[ProviderHealth, ...] = ()
    budget: BudgetConstraint | None = None
    quotes: tuple[CostQuote, ...] = ()
    project_local_only: bool = False


def select_route(
    config: RoutingConfig,
    task: TaskRequirements,
    *,
    invocation_policy: Version | None = None,
    model_override: str | None = None,
    health: tuple[ProviderHealth, ...] = (),
    budget: BudgetConstraint | None = None,
    quotes: tuple[CostQuote, ...] = (),
    escalation_from: str | None = None,
) -> RoutingDecision:
    """Apply hard constraints before policy order and soft budget preferences.

    An explicit model override considers only that model; refusal does not silently
    select another. Missing/inactive policy versions are configuration errors, not
    permission to fall back to a weaker policy. Provider failures never cause an
    automatic reasoning escalation. No network activity or persistence occurs.

    Returns:
        A decision, including rejected alternatives. No eligible model is a normal
        refused decision. A selected model still needs live availability checks.

    Raises:
        ValueError: Policy resolution or supplied health/quote identities are ambiguous.
    """
    choices = (
        (invocation_policy, "invocation"),
        (task.policy_override, "task"),
        (config.project_default, "project"),
        (config.system_default, "system"),
    )
    identity, source = next((identity, source) for identity, source in choices if identity)
    policy = next((item for item in config.policies if item.identity == identity), None)
    if policy is None or policy.state != "active":
        raise ValueError("Resolved policy version is missing or inactive.")
    if len({item.provider for item in health}) != len(health):
        raise ValueError("Provider health observations must be unique.")
    if len({item.model_id for item in quotes}) != len(quotes):
        raise ValueError("Cost quotes must be unique per model.")
    route = next((item for item in policy.routes if item.task_class == task.task_class), None)
    ids = (model_override,) if model_override is not None else (route.models if route else ())
    models = {item.id: item for item in config.inventory.models}
    statuses = {item.provider: item.state for item in health}
    prices = {item.model_id: item for item in quotes}
    candidates = []
    for model_id in ids:
        rejected = []
        model = models.get(model_id)
        if model is None:
            rejected.append("unknown_model")
        else:
            if (config.local_only or policy.local_only or task.privacy != "public") and (
                model.locality != "local"
            ):
                rejected.append("privacy")
            if model.status in {"retired", "unavailable"}:
                rejected.append("model_unavailable")
            if statuses.get(model.provider) in {"unavailable", "rate_limited"}:
                rejected.append("provider_unavailable")
            if not set(task.capabilities) <= set(model.capabilities):
                rejected.append("capabilities")
            if task.min_input_tokens > int(
                model.practical_input_tokens * policy.context.max_fraction_of_context
            ) or max(task.expected_output_tokens, policy.context.reserve_output_tokens) > (
                model.output_tokens
            ):
                rejected.append("context")
            if model.family in task.excluded_families:
                rejected.append("reviewer_independence")
        quote = prices.get(model_id)
        over_budget = budget is not None and (
            quote is None or quote.currency != budget.currency or quote.amount > budget.maximum
        )
        if budget is not None and budget.hard and over_budget:
            rejected.append("budget")
        candidates.append(
            Candidate(
                model_id=model_id,
                rejected_by=tuple(rejected),
                over_soft_budget=bool(over_budget and budget and not budget.hard),
            )
        )
    eligible = [item for item in candidates if not item.rejected_by]
    within_budget = [item for item in eligible if not item.over_soft_budget]
    preferred = within_budget or eligible
    chosen = models[preferred[0].model_id] if preferred else None
    reasons = ("model_override" if model_override is not None else "policy_order",)
    if chosen is None:
        reasons += ("no_eligible_model",)
    elif budget is not None and eligible and preferred[0] != eligible[0]:
        reasons += ("soft_budget_preference",)
    return RoutingDecision(
        id=str(uuid4()),
        created_at=datetime.now(UTC),
        requirements=task,
        inventory=config.inventory.identity,
        policy=policy.identity,
        policy_source=source,
        selected=chosen,
        reasons=reasons,
        candidates=tuple(candidates),
        context=policy.context,
        max_input_tokens=(
            int(chosen.practical_input_tokens * policy.context.max_fraction_of_context)
            if chosen
            else 0
        ),
        escalation_from=escalation_from,
        model_override=model_override,
        health=health,
        budget=budget,
        quotes=quotes,
        project_local_only=config.local_only,
    )
