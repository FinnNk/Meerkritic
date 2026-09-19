"""Exercise real migrations, atomic events, concurrency and CLI/Parquet boundaries."""

import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from test_routing_selection import EXAMPLE
from yoyo import get_backend, read_migrations

from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.application.routing import RoutingService
from semantic_reviewer.routing.selection import RoutingConfig, TaskRequirements, Version
from semantic_reviewer.routing.usage import Measurement, Price, PriceCatalogue, TokenUsage

ROOT = Path(__file__).resolve().parents[1]


class JournalTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / "state.sqlite3"
        self.config = RoutingConfig.model_validate_json(EXAMPLE.read_bytes())
        self.journal = SQLiteRoutingJournal(self.database)
        self.service = RoutingService(self.config, self.journal)
        self.task = TaskRequirements(task_id="1", task_class="normalisation")
        start = datetime.now(UTC)
        self.measurement = Measurement(
            started_at=start,
            completed_at=start + timedelta(seconds=1),
            outcome="success",
            tokens=TokenUsage(input_tokens=20, output_tokens=4),
        )

    def test_restart_idempotence_and_append_only_events(self):
        decision = self.service.route(self.task)
        self.journal.record(self.config, decision)
        first = self.service.complete(decision.id, self.measurement)
        service = RoutingService(self.config, SQLiteRoutingJournal(self.database))
        self.assertEqual(service.complete(decision.id, self.measurement), first)
        self.assertEqual(service.journal.get(decision.id), (decision, first))
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            self.assertEqual(db.execute("SELECT count(*) FROM event").fetchone()[0], 2)
            for table in ("event", "routing_version", "routing_decision", "model_usage"):
                with self.subTest(table=table), self.assertRaises(sqlite3.IntegrityError):
                    db.execute(f"DELETE FROM {table}")
                db.rollback()

    def test_conflicting_versions_and_completions_leave_existing_records_intact(self):
        decision = self.service.route(self.task)
        raw = self.config.model_dump(mode="json")
        raw["inventory"]["models"][1]["evidence"] = "changed content under same version"
        changed = RoutingConfig.model_validate_json(json.dumps(raw))
        with self.assertRaisesRegex(ValueError, "different content"):
            RoutingService(changed, self.journal).route(self.task)
        first = self.service.complete(decision.id, self.measurement)
        changed_measurement = Measurement(
            **{**self.measurement.model_dump(), "outcome": "provider_failure"}
        )
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.service.complete(decision.id, changed_measurement)
        self.assertEqual(self.journal.get(decision.id)[1], first)
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM routing_decision").fetchone()[0], 1)

    def test_event_failure_rolls_back_decision_and_versions(self):
        with closing(sqlite3.connect(self.database)) as db:
            db.execute(
                "CREATE TRIGGER fail_event BEFORE INSERT ON event "
                "BEGIN SELECT RAISE(ABORT, 'injected event failure'); END;"
            )
            db.commit()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected event failure"):
            self.service.route(self.task)
        with closing(sqlite3.connect(self.database)) as db:
            for table in ("routing_version", "routing_decision", "event"):
                self.assertEqual(db.execute(f"SELECT count(*) FROM {table}").fetchone()[0], 0)

    def test_concurrent_completion_retries_return_one_identity_and_event(self):
        decision = self.service.route(self.task)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(
                pool.map(lambda _: self.service.complete(decision.id, self.measurement), range(8))
            )
        self.assertEqual(len({usage.id for usage in results}), 1)
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM model_usage").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM event").fetchone()[0], 2)

    def test_refusal_is_recorded_but_cannot_acquire_usage(self):
        decision = self.service.route(self.task, model_override="example-remote")
        self.assertIsNone(self.journal.get(decision.id)[0].selected)
        with self.assertRaisesRegex(ValueError, "refused"):
            self.service.complete(decision.id, self.measurement)

    def test_historical_price_identity_reuse_is_rejected(self):
        decision = self.service.route(
            TaskRequirements(task_id="remote", task_class="normalisation", privacy="public")
        )
        catalogue = PriceCatalogue(
            identity=Version(id="prices", version="1"),
            currency="USD",
            effective_from=self.measurement.started_at,
            source="Synthetic test price",
            prices=(
                Price(
                    model_id="example-remote",
                    provider="example-host",
                    input_per_million=Decimal("2"),
                    output_per_million=Decimal("4"),
                ),
            ),
        )
        first = self.service.complete(decision.id, self.measurement, catalogue)
        changed = PriceCatalogue(
            **{**catalogue.model_dump(), "source": "Changed under same version"}
        )
        with self.assertRaisesRegex(ValueError, "different content"):
            self.service.complete(decision.id, self.measurement, changed)
        self.assertEqual(self.journal.get(decision.id)[1], first)

    def test_upgrade_preserves_dataset_events_and_subject_integrity(self):
        old = self.root / "old.sqlite3"
        backend = get_backend("sqlite:///" + old.as_posix())
        try:
            old_migrations = self.root / "old-migrations"
            old_migrations.mkdir()
            source = ROOT / "src/semantic_reviewer/adapters/migrations/001_registry.sql"
            (old_migrations / source.name).write_bytes(source.read_bytes())
            migrations = read_migrations(str(old_migrations))
            with backend.lock():
                backend.apply_migrations(backend.to_apply(migrations))
        finally:
            backend.connection.close()
        with closing(sqlite3.connect(old)) as db:
            db.execute(
                "INSERT INTO dataset VALUES "
                "('source', 'title', 'rev', 'url', 'sha', 'sha', 1, 'now', 1)"
            )
            db.execute("INSERT INTO event VALUES (7, 'dataset_registered', 'source', 'now', '{}')")
            db.commit()
        upgraded = SQLiteRoutingJournal(old)
        RoutingService(self.config, upgraded).route(self.task)
        with closing(sqlite3.connect(old)) as db:
            self.assertEqual(
                db.execute("SELECT * FROM event WHERE sequence=7").fetchone(),
                (7, "dataset_registered", "source", "now", "{}"),
            )
            self.assertGreater(db.execute("SELECT max(sequence) FROM event").fetchone()[0], 7)
            with self.assertRaisesRegex(sqlite3.IntegrityError, "subject does not exist"):
                db.execute(
                    "INSERT INTO event(kind,subject_id,occurred_at,details_json) "
                    "VALUES ('dataset_registered','missing','now','{}')"
                )
            db.rollback()
            for sql in ("DELETE FROM dataset", "UPDATE dataset SET id='renamed'"):
                with (
                    self.subTest(sql=sql),
                    self.assertRaisesRegex(sqlite3.IntegrityError, "history"),
                ):
                    db.execute(sql)
                db.rollback()
