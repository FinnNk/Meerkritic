"""Retain immutable routing provenance and completion metadata in SQLite."""

import json
import sqlite3
from pathlib import Path

from semantic_reviewer.adapters.state import SQLiteState
from semantic_reviewer.routing.selection import Record, RoutingConfig, RoutingDecision, Version
from semantic_reviewer.routing.usage import ModelUsage, PriceCatalogue


def _payload(record: Record) -> str:
    """Serialise an immutable record canonically for identity conflict checks."""
    return json.dumps(record.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))


class SQLiteRoutingJournal:
    """Keep metadata, version snapshots and events atomic across process restarts."""

    def __init__(self, database: Path) -> None:
        """Migrate the shared operational database before accepting writes."""
        self.state = SQLiteState(database)

    @staticmethod
    def _version(
        connection: sqlite3.Connection, kind: str, identity: Version, value: Record
    ) -> None:
        payload = _payload(value)
        row = connection.execute(
            "SELECT payload_json FROM routing_version WHERE kind=? AND id=? AND version=?",
            (kind, identity.id, identity.version),
        ).fetchone()
        if row:
            if row[0] != payload:
                raise ValueError("Configuration version already identifies different content.")
        else:
            connection.execute(
                "INSERT INTO routing_version VALUES (?, ?, ?, ?)",
                (kind, identity.id, identity.version, payload),
            )

    def record(self, config: RoutingConfig, decision: RoutingDecision) -> None:
        """Persist the decision and exact versions atomically; identical repeats are no-ops."""
        policy = next((item for item in config.policies if item.identity == decision.policy), None)
        if decision.inventory != config.inventory.identity or policy is None:
            raise ValueError("Decision does not reference the supplied configuration.")
        with self.state.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._version(connection, "inventory", config.inventory.identity, config.inventory)
            self._version(connection, "policy", policy.identity, policy)
            row = connection.execute(
                "SELECT payload_json FROM routing_decision WHERE id=?", (decision.id,)
            ).fetchone()
            payload = _payload(decision)
            if row:
                if row[0] != payload:
                    raise ValueError("Routing decision identity conflict.")
                return
            connection.execute("INSERT INTO routing_decision VALUES (?, ?)", (decision.id, payload))
            connection.execute(
                "INSERT INTO event(kind, subject_id, occurred_at, details_json) "
                "VALUES (?, ?, ?, ?)",
                (
                    "routing_decision_recorded",
                    decision.id,
                    decision.created_at.isoformat(),
                    json.dumps({"schema_version": 1, "selected": decision.selected is not None}),
                ),
            )

    def get(self, decision_id: str) -> tuple[RoutingDecision, ModelUsage | None] | None:
        """Read a decision and its completion in one database snapshot."""
        with self.state.connect() as connection:
            row = connection.execute(
                "SELECT d.payload_json, u.payload_json FROM routing_decision d "
                "LEFT JOIN model_usage u ON u.decision_id=d.id WHERE d.id=?",
                (decision_id,),
            ).fetchone()
            if row is None:
                return None
            return (
                RoutingDecision.model_validate_json(row[0]),
                ModelUsage.model_validate_json(row[1]) if row[1] else None,
            )

    def complete(self, usage: ModelUsage, catalogue: PriceCatalogue | None) -> ModelUsage:
        """Commit one usage record and event; reject changed retries without partial writes."""
        with self.state.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if usage.price_catalogue is not None:
                if catalogue is None or catalogue.identity != usage.price_catalogue:
                    raise ValueError("Usage price version does not match the supplied catalogue.")
                self._version(connection, "prices", catalogue.identity, catalogue)
            existing = connection.execute(
                "SELECT payload_json FROM model_usage WHERE decision_id=?", (usage.decision_id,)
            ).fetchone()
            if existing:
                # Retries can race after reading an incomplete decision. Preserve the first ID.
                prior = ModelUsage.model_validate_json(existing[0])
                if prior.model_dump(exclude={"id"}) != usage.model_dump(exclude={"id"}):
                    raise ValueError("Completion conflicts with the recorded invocation.")
                return prior
            decision = connection.execute(
                "SELECT payload_json FROM routing_decision WHERE id=?", (usage.decision_id,)
            ).fetchone()
            if (
                decision is None
                or RoutingDecision.model_validate_json(decision[0]).selected is None
            ):
                raise ValueError("Usage requires a recorded selected decision.")
            connection.execute(
                "INSERT INTO model_usage VALUES (?, ?, ?)",
                (usage.id, usage.decision_id, _payload(usage)),
            )
            connection.execute(
                "INSERT INTO event(kind, subject_id, occurred_at, details_json) "
                "VALUES (?, ?, ?, ?)",
                (
                    "model_usage_recorded",
                    usage.id,
                    usage.measurement.completed_at.isoformat(),
                    json.dumps({"schema_version": 1, "decision_id": usage.decision_id}),
                ),
            )
            return usage
