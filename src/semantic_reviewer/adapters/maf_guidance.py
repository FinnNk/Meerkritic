"""Keep concrete MAF orchestration behind the advisory guidance runtime port."""

import asyncio
from datetime import UTC, datetime
from importlib.metadata import version

from agent_framework import WorkflowBuilder, WorkflowContext, executor

from semantic_reviewer.application.guidance import GuidanceOutcome
from semantic_reviewer.application.model import ModelClient, ModelFailure, ModelRequest
from semantic_reviewer.application.normalisation import FrameworkObservation
from semantic_reviewer.domain.guidance import GuidanceResponse
from semantic_reviewer.routing.selection import RoutingDecision
from semantic_reviewer.routing.usage import Measurement


class MafGuidanceRuntime:
    """Run inference and exact-target validation without applying agent advice to rule state."""

    def __init__(self, model: ModelClient) -> None:
        """Bind the provider port; no model calls or durable framework sessions are created."""
        self.model = model

    def run(
        self,
        decision: RoutingDecision,
        request: ModelRequest,
        targets: tuple[str, ...],
        queued_at: datetime,
    ) -> GuidanceOutcome:
        """Return raw output and typed advice/failure with a framework observation."""
        framework = FrameworkObservation(
            "Microsoft Agent Framework",
            version("agent-framework-core"),
            "WorkflowBuilder/executors",
            "submitted context -> advisory response -> coverage validation",
            "completed",
            "info",
            "Advice never applies decisions or edits.",
            "none",
            "Retain submitted snapshot, prompt/schema, model profile and lock.",
        )

        @executor(id="respond-to-guidance")
        async def respond(value: ModelRequest, ctx: WorkflowContext[None, GuidanceOutcome]):
            try:
                reply = await asyncio.to_thread(self.model.generate, decision, value, queued_at)
            except ModelFailure as failure:
                await ctx.yield_output(
                    GuidanceOutcome(None, None, failure.measurement, str(failure), framework)
                )
                return
            try:
                response = GuidanceResponse.model_validate_json(reply.content)
                response.validate_targets(targets)
                result = GuidanceOutcome(response, reply, reply.measurement, None, framework)
            except ValueError:
                result = GuidanceOutcome(
                    None,
                    reply,
                    Measurement(
                        **{**reply.measurement.model_dump(), "outcome": "semantic_failure"}
                    ),
                    "Guidance output failed schema or exact-target validation.",
                    framework,
                )
            await ctx.yield_output(result)

        async def execute():
            outputs = (
                await WorkflowBuilder(start_executor=respond).build().run(request)
            ).get_outputs()
            if len(outputs) != 1 or not isinstance(outputs[0], GuidanceOutcome):
                raise RuntimeError("Unexpected guidance workflow output.")
            return outputs[0]

        try:
            return asyncio.run(execute())
        except Exception as error:
            from dataclasses import replace

            return GuidanceOutcome(
                None,
                None,
                Measurement(
                    started_at=queued_at,
                    completed_at=datetime.now(UTC),
                    outcome="deterministic_failure",
                ),
                f"Guidance workflow runtime failed ({type(error).__name__}).",
                replace(framework, outcome="failed", severity="error"),
            )
