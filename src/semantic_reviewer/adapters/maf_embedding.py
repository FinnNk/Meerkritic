"""Orchestrate embeddings through the default MAF substrate without leaking its types."""

import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from importlib.metadata import version

from agent_framework import WorkflowBuilder, WorkflowContext, executor

from semantic_reviewer.application.embeddings import (
    EmbeddingInput,
    EmbeddingOutcome,
    EmbeddingRuntime,
)
from semantic_reviewer.application.normalisation import FrameworkObservation
from semantic_reviewer.routing.usage import Measurement


class MafEmbeddingRuntime:
    """Keep the framework lifecycle and observations around an owned embedding contract."""

    def __init__(self, model: EmbeddingRuntime) -> None:
        """Bind the transport without starting inference."""
        self.model = model

    def run(self, value: EmbeddingInput) -> EmbeddingOutcome:
        """Execute real MAF embedding work and preserve safe framework failures."""

        @executor(id="embed-selected-interpretations")
        async def embed(inputs: EmbeddingInput, ctx: WorkflowContext[None, EmbeddingOutcome]):
            await ctx.yield_output(await asyncio.to_thread(self.model.run, inputs))

        async def execute():
            outputs = (await WorkflowBuilder(start_executor=embed).build().run(value)).get_outputs()
            if len(outputs) != 1 or not isinstance(outputs[0], EmbeddingOutcome):
                raise RuntimeError("Invalid embedding framework output.")
            return outputs[0]

        state = "completed"
        try:
            outcome = asyncio.run(execute())
        except Exception as error:
            state = "failed"
            outcome = EmbeddingOutcome(
                (),
                Measurement(
                    started_at=value.queued_at,
                    completed_at=datetime.now(UTC),
                    outcome="deterministic_failure",
                ),
                {},
                f"Embedding workflow runtime failed ({type(error).__name__}).",
            )
        observation = FrameworkObservation(
            "Microsoft Agent Framework",
            version("agent-framework-core"),
            "WorkflowBuilder/executor",
            "embed selected interpretations",
            state,
            "info" if state == "completed" else "error",
            "Typed embedding outcome retained.",
            "none",
            "Use the frozen selection, deployment profile and dependency lock.",
        )
        return replace(outcome, framework=observation)
