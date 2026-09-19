"""Project-owned model transport contracts; no provider SDK or workflow framework types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from semantic_reviewer.routing.selection import RoutingDecision
from semantic_reviewer.routing.usage import Measurement


@dataclass(frozen=True)
class ModelRequest:
    """Supply a versioned prompt and JSON schema, without choosing a model."""

    system: str
    user: str
    schema: dict[str, object]
    prompt_version: str
    max_output_tokens: int


@dataclass(frozen=True)
class ModelReply:
    """Return content and observed telemetry; retain raw provenance outside SQLite."""

    content: str
    measurement: Measurement
    request_json: str
    response_json: str


class ModelFailure(Exception):
    """Carry a safe failure summary and any observed usage for a failed invocation."""

    def __init__(self, message: str, measurement: Measurement) -> None:
        """Retain telemetry without embedding prompts or raw provider errors in logs."""
        super().__init__(message)
        self.measurement = measurement


class ModelClient(Protocol):
    """Execute an already recorded route and retain failures as infrastructure observations."""

    def generate(
        self, decision: RoutingDecision, request: ModelRequest, queued_at: datetime
    ) -> ModelReply:
        """Return untrusted content and telemetry, or raise ModelFailure with a safe summary."""
        ...
