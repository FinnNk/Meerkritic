"""Reserve explicit continuity records without enabling mid-task switching in VS1."""

from typing import Literal

from pydantic import AwareDatetime, model_validator

from semantic_reviewer.routing.selection import Name, Record, Version


class RoutingPolicyTransition(Record):
    """Describe a future policy change without replacing the original routing decision."""

    id: Name
    agent_run_id: Name
    from_policy: Version
    to_policy: Version
    reason: Name
    requested_by: Literal["human", "router", "system"]
    created_at: AwareDatetime

    @model_validator(mode="after")
    def changed_policy(self) -> "RoutingPolicyTransition":
        """Reject a purported transition that does not change the versioned policy."""
        if self.from_policy == self.to_policy:
            raise ValueError("A policy transition must change the policy or its version.")
        return self


class AgentHandoff(Record):
    """Reserve structured task continuity; reference evidence rather than raw transcripts."""

    task_objective: Name
    acceptance_criteria: tuple[Name, ...]
    current_plan: tuple[Name, ...]
    completed_actions: tuple[Name, ...]
    changed_files: tuple[Name, ...]
    tool_results: tuple[Name, ...]
    failing_checks: tuple[Name, ...]
    unresolved_questions: tuple[Name, ...]
    relevant_context: tuple[Name, ...]
    previous_model_summary: Name
    provenance_refs: tuple[Name, ...]
