"""Orchestrate bounded rule context, local generation and reference validation through MAF."""

import asyncio
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from importlib.metadata import version

from agent_framework import WorkflowBuilder, WorkflowContext, executor

from semantic_reviewer.application.model import ModelClient, ModelFailure, ModelReply, ModelRequest
from semantic_reviewer.application.normalisation import FrameworkObservation
from semantic_reviewer.application.synthesis import (
    SynthesisInput,
    SynthesisOutcome,
    synthesis_request,
)
from semantic_reviewer.domain.rules import RuleProposal
from semantic_reviewer.routing.usage import Measurement


@dataclass(frozen=True)
class Prepared:
    """Carry the bounded request and exact supplied reference set between private graph steps."""

    source: SynthesisInput
    request: ModelRequest


@dataclass(frozen=True)
class Inferred:
    """Carry replies or failure data; framework messages must not contain exception instances."""

    prepared: Prepared
    reply: ModelReply | None
    failure: Measurement | None
    error: str | None


class MafSynthesisRuntime:
    """Keep concrete framework types and execution details out of research/domain logic."""

    def __init__(self, model: ModelClient) -> None:
        """Bind transport without invoking models or creating durable framework entities."""
        self.model = model

    def run(self, value: SynthesisInput) -> SynthesisOutcome:
        """Run the graph and retain invalid output, safe failures and framework observations."""

        @executor(id="prepare-rule-context")
        async def prepare(source: SynthesisInput, ctx: WorkflowContext[Prepared, SynthesisOutcome]):
            try:
                request = synthesis_request(source)
            except ValueError:
                await ctx.yield_output(
                    SynthesisOutcome(
                        None,
                        None,
                        Measurement(
                            started_at=source.queued_at,
                            completed_at=datetime.now(UTC),
                            outcome="context_failure",
                        ),
                        "Synthesis inputs exceed the bounded context contract.",
                    )
                )
                return
            await ctx.send_message(Prepared(source, request))

        @executor(id="propose-rule")
        async def infer(prepared: Prepared, ctx: WorkflowContext[Inferred]):
            try:
                reply = await asyncio.to_thread(
                    self.model.generate,
                    prepared.source.decision,
                    prepared.request,
                    prepared.source.queued_at,
                )
                result = Inferred(prepared, reply, None, None)
            except ModelFailure as failure:
                result = Inferred(prepared, None, failure.measurement, str(failure))
            await ctx.send_message(result)

        @executor(id="validate-rule-references")
        async def validate(inferred: Inferred, ctx: WorkflowContext[None, SynthesisOutcome]):
            prepared = inferred.prepared
            if inferred.failure:
                outcome = SynthesisOutcome(
                    None, None, inferred.failure, inferred.error, prepared.request
                )
            else:
                reply = inferred.reply
                try:
                    proposal = RuleProposal.model_validate_json(reply.content)
                    proposal.validate_support(
                        tuple(record.annotation.id for record in prepared.source.records)
                    )
                    outcome = SynthesisOutcome(
                        proposal, reply, reply.measurement, None, prepared.request
                    )
                except ValueError:
                    outcome = SynthesisOutcome(
                        None,
                        reply,
                        Measurement(
                            **{**reply.measurement.model_dump(), "outcome": "semantic_failure"}
                        ),
                        "Rule output failed schema or supplied-reference validation.",
                        prepared.request,
                    )
            await ctx.yield_output(outcome)

        async def execute():
            graph = (
                WorkflowBuilder(start_executor=prepare)
                .add_edge(prepare, infer)
                .add_edge(infer, validate)
                .build()
            )
            results = (await graph.run(value)).get_outputs()
            if len(results) != 1 or not isinstance(results[0], SynthesisOutcome):
                raise RuntimeError("Unexpected synthesis workflow output.")
            return results[0]

        state = "completed"
        try:
            outcome = asyncio.run(execute())
        except Exception as error:
            state = "failed"
            outcome = SynthesisOutcome(
                None,
                None,
                Measurement(
                    started_at=value.queued_at,
                    completed_at=datetime.now(UTC),
                    outcome="deterministic_failure",
                ),
                f"Synthesis workflow runtime failed ({type(error).__name__}).",
            )
        observation = FrameworkObservation(
            "Microsoft Agent Framework",
            version("agent-framework-core"),
            "WorkflowBuilder/executors",
            "prepare cluster -> inference -> reference validation",
            state,
            "info" if state == "completed" else "error",
            "Typed candidate or failure retained.",
            "none",
            "Use the frozen examples, request/schema, model profile and runtime lock.",
        )
        return replace(outcome, framework=observation)
