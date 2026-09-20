"""Own embedding runtime messages without queue, selection or provider dependencies."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from semantic_reviewer.application.normalisation import FrameworkObservation
from semantic_reviewer.routing.selection import RoutingDecision
from semantic_reviewer.routing.usage import Measurement


@dataclass(frozen=True)
class EmbeddingInput:
    """Carry ordered model-independent texts and the persisted route into the runtime."""

    texts: tuple[str, ...]
    decision: RoutingDecision
    queued_at: datetime


@dataclass(frozen=True)
class EmbeddingOutcome:
    """Retain classified failures and available raw metadata without inventing vectors."""

    vectors: tuple[tuple[float, ...], ...]
    measurement: Measurement
    provenance: dict
    error: str | None = None
    framework: FrameworkObservation | None = None


class EmbeddingRuntime(Protocol):
    """Execute a bounded embedding workflow and report provider/framework failures as data."""

    def run(self, value: EmbeddingInput) -> EmbeddingOutcome:
        """Execute at most 100 texts; retain measurement, provenance and safe failure details."""
        ...
