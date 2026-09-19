"""Coordinate route selection and durable provenance before any provider execution."""

from typing import Protocol

from semantic_reviewer.routing.selection import (
    RoutingConfig,
    RoutingDecision,
    TaskRequirements,
    Version,
    select_route,
)
from semantic_reviewer.routing.usage import Measurement, ModelUsage, PriceCatalogue, account_usage


class RoutingJournal(Protocol):
    """Persist immutable decisions and completion records with atomic operational events."""

    def record(self, config: RoutingConfig, decision: RoutingDecision) -> None:
        """Retain config versions and decision, or reject an identity conflict atomically."""
        ...

    def get(self, decision_id: str) -> tuple[RoutingDecision, ModelUsage | None] | None:
        """Return a decision and optional completion, or None if unknown."""
        ...

    def complete(self, usage: ModelUsage, catalogue: PriceCatalogue | None) -> ModelUsage:
        """Retain a single completion per decision, rejecting conflicting repeats."""
        ...


class RoutingService:
    """Keep version conflicts from allowing an unrecorded model invocation."""

    def __init__(self, config: RoutingConfig, journal: RoutingJournal) -> None:
        """Use explicit configuration and a journal; do not invoke providers."""
        self.config = config
        self.journal = journal

    def route(
        self,
        task: TaskRequirements,
        *,
        invocation_policy: Version | None = None,
        model_override: str | None = None,
    ) -> RoutingDecision:
        """Select and persist a decision before returning permission to a future executor.

        Each call is a distinct invocation decision. Persist even an explained
        refusal. A journal failure propagates, so callers must not execute a model
        unless this operation returns a selected decision successfully.
        """
        decision = select_route(
            self.config, task, invocation_policy=invocation_policy, model_override=model_override
        )
        self.journal.record(self.config, decision)
        return decision

    def complete(
        self, decision_id: str, measurement: Measurement, catalogue: PriceCatalogue | None = None
    ) -> ModelUsage:
        """Persist accounting once; identical completion retries return the original record.

        Raises:
            ValueError: Decision is unknown/refused, observations conflict, or price
                configuration has an invalid or reused identity.
        """
        record = self.journal.get(decision_id)
        if record is None:
            raise ValueError("Routing decision is unknown.")
        decision, previous = record
        usage = account_usage(decision, measurement, catalogue)
        if previous is not None:
            usage = ModelUsage(**{**usage.model_dump(), "id": previous.id})
        return self.journal.complete(usage, catalogue)
