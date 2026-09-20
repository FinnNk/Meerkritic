"""Own immutable rule provenance, evidence eligibility and explicit research decisions."""

from dataclasses import dataclass
from typing import Literal, Protocol
from uuid import uuid4

from semantic_reviewer.application.discovery import DiscoveryFiles, DiscoveryRun, DiscoveryService
from semantic_reviewer.application.selections import SelectedAnnotation, SelectionSnapshot
from semantic_reviewer.domain.rules import (
    RuleDecisionRequest,
    RuleDefinition,
    RuleEvidence,
    RuleOrigin,
    RuleVersionBody,
)


@dataclass(frozen=True)
class RuleHead:
    """Expose current version and optimistic revision separately from immutable history."""

    rule_id: str
    version_id: str
    revision: int
    status: Literal["candidate", "promoted", "rejected"]
    created_at: str


class RuleStore(Protocol):
    """Own atomic version publication, inherited evidence and fenced decisions/events."""

    def publish(self, body: RuleVersionBody, expected_revision: int | None) -> str:
        """Publish immutable content and initialise/carry evidence in one registry transaction.

        A new rule uses expected_revision=None; revision requires the current parent
        version and expected counter. Identical content returns its original digest;
        conflicts raise ValueError. A complete orphan body may remain after rollback.
        """
        ...

    def read(
        self, version_id: str
    ) -> tuple[RuleHead, RuleVersionBody, tuple[RuleEvidence, ...], tuple[dict, ...]]:
        """Verify body/metadata and return current head, selected version, evidence and decisions.

        Historical versions remain inspectable. Unknown identities raise LookupError,
        corrupt/mismatched bodies ValueError; filesystem/database errors propagate.
        """
        ...

    def recent(self) -> tuple[RuleHead, ...]:
        """List at most 100 current heads without claiming body verification."""
        ...

    def add_evidence(self, evidence: RuleEvidence, expected_revision: int) -> None:
        """Append evidence/event to a current version; identical IDs are replay-safe.

        Conflicting IDs or stale version/revision raise ValueError without a write.
        Verification is the named actor's claim, not an inferred property.
        """
        ...

    def decide(self, request: RuleDecisionRequest) -> dict:
        """Apply promotion/rejection atomically with its event; identical request IDs replay once.

        A stale version/revision, conflicting ID or already decided version raises
        ValueError. Return the immutable decision, even on a later identical retry.
        """
        ...


class RuleService:
    """Hide cluster/source resolution and evidence policy from UI and synthesis callers."""

    def __init__(
        self, discovery: DiscoveryService, store: RuleStore, files: DiscoveryFiles
    ) -> None:
        """Bind ports for the same runtime; no model execution or state change occurs."""
        self.discovery, self.store, self.files = discovery, store, files

    def cluster_inputs(
        self, run_id: str, cluster: int
    ) -> tuple[DiscoveryRun, dict, SelectionSnapshot, tuple[SelectedAnnotation, ...]]:
        """Return verified run, manifest, snapshot and members, with the representative first."""
        run, body = self.discovery.inspect(run_id)
        if run.status != "succeeded" or run.request.kind != "clustering" or cluster < 0:
            raise ValueError("Rules require a successful non-outlier cluster.")
        _, snapshot = self.discovery.selections.read(run.request.selection_id)
        membership = self.files.read_members(body["members_digest"])
        ids = {item["annotation_id"] for item in membership if item["cluster"] == cluster}
        records = tuple(
            item
            for item in snapshot.records
            if item.annotation.id in ids and item.exclusion is None
        )
        if not records or len(records) != len(ids):
            raise ValueError("Cluster membership disagrees with the eligible frozen selection.")
        representatives = {
            item["annotation_id"]
            for item in membership
            if item["cluster"] == cluster and item["representative"]
        }
        records = tuple(sorted(records, key=lambda item: item.annotation.id not in representatives))
        return run, body, snapshot, records

    def propose(
        self, cluster_run: str, cluster: int, definition: RuleDefinition, origin: RuleOrigin
    ) -> str:
        """Publish a distinct candidate with exact cluster members and weak initial support.

        Source links prove provenance, not engineering validity. Invented references,
        unavailable source artefacts or mismatched model traces fail before registration.
        """
        run, _, snapshot, records = self.cluster_inputs(cluster_run, cluster)
        self._validate_support(definition, records)
        if origin.trace_digest:
            trace = self.files.read_json(origin.trace_digest)
            if (
                trace.get("cluster_run") != run.id
                or trace.get("cluster_digest") != run.result_digest
                or trace.get("cluster") != cluster
                or trace.get("selection_id") != run.request.selection_id
            ):
                raise ValueError("Synthesis trace does not identify this exact cluster input.")
            proposal = trace.get("proposal")
            if (
                trace.get("error") is not None
                or not isinstance(proposal, dict)
                or proposal.get("candidate") != definition.model_dump(mode="json")
            ):
                raise ValueError("Synthesis trace does not contain this successful candidate.")
        return self.store.publish(
            RuleVersionBody(
                rule_id=str(uuid4()),
                parent_version=None,
                selection_id=run.request.selection_id,
                cluster_run=run.id,
                cluster_digest=run.result_digest,
                cluster=cluster,
                purpose=snapshot.request.purpose,
                definition=definition,
                origin=origin,
            ),
            None,
        )

    @staticmethod
    def _validate_support(definition, records):
        definition = RuleDefinition.model_validate_json(definition.model_dump_json())
        ids = {item.annotation.id for item in records}
        if not set(definition.supporting_annotations) <= ids:
            raise ValueError("Rule support must identify supplied eligible cluster annotations.")

    def revise(
        self,
        version_id: str,
        definition: RuleDefinition,
        actor: str,
        rationale: str,
        expected_revision: int,
    ) -> str:
        """Create a new immutable candidate version, preserving parent lineage and all evidence.

        Never overwrite a decision or counterexample. Concurrent changes fail the
        revision check, leaving any complete body unreferenced and prior state intact.
        """
        _, parent, _, _ = self.store.read(version_id)
        _, _, _, records = self.cluster_inputs(parent.cluster_run, parent.cluster)
        self._validate_support(definition, records)
        body = RuleVersionBody(
            **{
                **parent.model_dump(),
                "parent_version": version_id,
                "definition": definition,
                "origin": RuleOrigin(kind="human", actor=actor, rationale=rationale),
            }
        )
        return self.store.publish(body, expected_revision)

    def add_evidence(self, evidence: RuleEvidence, expected_revision: int) -> None:
        """Validate an explicit source link; holdouts cannot be reintroduced as counterexamples.

        Rejected interpretations may supply inspectable weak examples, but are never
        automatically verified negatives. Verification requires an explicit actor claim.
        """
        _, body, _, _ = self.store.read(evidence.version_id)
        _, snapshot = self.discovery.selections.read(body.selection_id)
        chosen = next(
            (item for item in snapshot.records if item.annotation.id == evidence.annotation_id),
            None,
        )
        if (
            chosen is None
            or chosen.exclusion == "holdout_repository"
            or evidence.inherited_from is not None
        ):
            raise ValueError(
                "Evidence must name an available, non-holdout annotation in this selection."
            )
        self.store.add_evidence(evidence, expected_revision)
