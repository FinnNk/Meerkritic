"""Orchestrate context, inference and grounding with Microsoft Agent Framework."""

import asyncio
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from importlib.metadata import version

from agent_framework import WorkflowBuilder, WorkflowContext, executor

from semantic_reviewer.application.model import ModelClient, ModelFailure, ModelReply, ModelRequest
from semantic_reviewer.application.normalisation import (
    ContextBuilder,
    FrameworkObservation,
    NormalisationInput,
    NormalisationOutcome,
    SourceContext,
)
from semantic_reviewer.domain.normalisation import IssueInterpretation, ground
from semantic_reviewer.routing.usage import Measurement


@dataclass(frozen=True)
class Prepared:
    """Carry source identity and prepared model input between private workflow steps."""

    source: NormalisationInput
    request: ModelRequest


@dataclass(frozen=True)
class Inferred:
    """Carry inference or its typed failure to the grounding step."""

    source: NormalisationInput
    reply: ModelReply | None
    failure: Measurement | None
    error: str | None
    request: ModelRequest


class MafWorkflowRunner:
    """Keep the default orchestration substrate behind a project-owned runtime boundary."""

    def __init__(self, model: ModelClient, context: ContextBuilder | None = None) -> None:
        """Bind transport and context dependencies without invoking the framework or model."""
        self.model = model
        self.context = context or SourceContext()

    def run(self, value: NormalisationInput) -> NormalisationOutcome:
        """Execute the real three-step MAF graph and attach an observation, including failures."""

        @executor(id="prepare-source")
        async def prepare(source: NormalisationInput, ctx: WorkflowContext[Prepared]) -> None:
            await ctx.send_message(Prepared(source, self.context.build(source)))

        @executor(id="infer")
        async def infer(prepared: Prepared, ctx: WorkflowContext[Inferred]) -> None:
            try:
                reply = await asyncio.to_thread(
                    self.model.generate,
                    prepared.source.decision,
                    prepared.request,
                    prepared.source.queued_at,
                )
                message = Inferred(prepared.source, reply, None, None, prepared.request)
            except ModelFailure as error:
                # Workflow messages are data: exception instances cannot be copied reliably.
                message = Inferred(
                    prepared.source, None, error.measurement, str(error), prepared.request
                )
            await ctx.send_message(message)

        @executor(id="validate-evidence")
        async def validate(
            inferred: Inferred, ctx: WorkflowContext[None, NormalisationOutcome]
        ) -> None:
            if inferred.failure is not None:
                outcome = NormalisationOutcome(None, (), None, inferred.failure, inferred.error)
            else:
                reply = inferred.reply
                try:
                    issue = IssueInterpretation.model_validate_json(reply.content)
                    spans = ground(issue, inferred.source.observation)
                    outcome = NormalisationOutcome(issue, spans, reply, reply.measurement, None)
                except ValueError:
                    measurement = Measurement(
                        **{**reply.measurement.model_dump(), "outcome": "semantic_failure"}
                    )
                    outcome = NormalisationOutcome(
                        None, (), reply, measurement, "Output failed schema or evidence validation."
                    )
            await ctx.yield_output(replace(outcome, request=inferred.request))

        async def execute() -> NormalisationOutcome:
            workflow = (
                WorkflowBuilder(start_executor=prepare)
                .add_edge(prepare, infer)
                .add_edge(infer, validate)
                .build()
            )
            results = (await workflow.run(value)).get_outputs()
            if len(results) != 1 or not isinstance(results[0], NormalisationOutcome):
                raise RuntimeError("Unexpected framework output contract.")
            return results[0]

        framework_outcome = "completed"
        try:
            outcome = asyncio.run(execute())
        except Exception as error:
            # This is a runtime boundary: retain a safe failure instead of losing the job.
            framework_outcome = "failed"
            outcome = NormalisationOutcome(
                None,
                (),
                None,
                Measurement(
                    started_at=value.queued_at,
                    completed_at=datetime.now(UTC),
                    outcome="deterministic_failure",
                ),
                f"Workflow runtime failed ({type(error).__name__}).",
            )
        observation = FrameworkObservation(
            "Microsoft Agent Framework",
            version("agent-framework-core"),
            "WorkflowBuilder/executors",
            "source preparation -> inference -> evidence validation",
            framework_outcome,
            "info" if framework_outcome == "completed" else "error",
            "Three-step graph returned a typed outcome."
            if framework_outcome == "completed"
            else outcome.error,
            "none",
            "Repeat with the retained prompt, source and runtime versions.",
        )
        return replace(outcome, framework=observation)
