"""Retain immutable routing provenance and completion metadata in SQLite."""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

import duckdb

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

    def export_usage(self, target: Path) -> int:
        """Publish a new Parquet history snapshot with typed metrics and full record JSON.

        Use a fresh output path; existing files are never overwritten. Read completed
        usage from one SQLite snapshot in bounded batches. Publication occurs only
        after DuckDB closes the complete file; a failed export leaves the target
        absent. Runtime path policy is enforced by composition/CLI callers.

        Returns:
            Number of completed invocations exported, including failed invocations.
        """
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
            staged = Path(temporary) / "history.parquet"
            with self.state.connect() as sqlite, duckdb.connect() as analytical:
                analytical.execute(
                    "CREATE TABLE history (usage_id VARCHAR, decision_id VARCHAR, task_id VARCHAR, "
                    "task_class VARCHAR, provider VARCHAR, model VARCHAR, outcome VARCHAR, "
                    "input_tokens BIGINT, output_tokens BIGINT, cached_input_tokens BIGINT, "
                    "reasoning_tokens BIGINT, total_turnaround_ms DOUBLE, estimated_cost VARCHAR, "
                    "currency VARCHAR, decision_json VARCHAR, usage_json VARCHAR, "
                    "inventory_json VARCHAR, policy_json VARCHAR, price_catalogue_json VARCHAR)"
                )
                cursor = sqlite.execute(
                    "SELECT d.payload_json, u.payload_json, i.payload_json, p.payload_json, "
                    "c.payload_json FROM model_usage u "
                    "JOIN routing_decision d ON d.id=u.decision_id "
                    "JOIN routing_version i ON i.kind='inventory' "
                    "AND i.id=json_extract(d.payload_json,'$.inventory.id') "
                    "AND i.version=json_extract(d.payload_json,'$.inventory.version') "
                    "JOIN routing_version p ON p.kind='policy' "
                    "AND p.id=json_extract(d.payload_json,'$.policy.id') "
                    "AND p.version=json_extract(d.payload_json,'$.policy.version') "
                    "LEFT JOIN routing_version c ON c.kind='prices' "
                    "AND c.id=json_extract(u.payload_json,'$.price_catalogue.id') "
                    "AND c.version=json_extract(u.payload_json,'$.price_catalogue.version') "
                    "ORDER BY u.id"
                )
                count = 0
                while batch := cursor.fetchmany(500):
                    rows = []
                    for row in batch:
                        decision = RoutingDecision.model_validate_json(row[0])
                        usage = ModelUsage.model_validate_json(row[1])
                        tokens = usage.measurement.tokens
                        rows.append(
                            (
                                usage.id,
                                decision.id,
                                decision.requirements.task_id,
                                decision.requirements.task_class,
                                decision.selected.provider,
                                decision.selected.id,
                                usage.measurement.outcome,
                                tokens.input_tokens,
                                tokens.output_tokens,
                                tokens.cached_input_tokens,
                                tokens.reasoning_tokens,
                                usage.measurement.total_turnaround_ms,
                                str(usage.estimated_cost)
                                if usage.estimated_cost is not None
                                else None,
                                usage.currency,
                                row[0],
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                            )
                        )
                    analytical.executemany(
                        "INSERT INTO history VALUES (" + ",".join(["?"] * 19) + ")", rows
                    )
                    count += len(rows)
                analytical.execute("COPY history TO ? (FORMAT PARQUET)", [str(staged)])
            os.link(staged, target)
        return count
