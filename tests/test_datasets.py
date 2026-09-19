"""Dataset boundaries tested with synthetic source bytes and real SQLite/DuckDB."""

import hashlib
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from semantic_reviewer.adapters.observations import ParquetObservations
from semantic_reviewer.adapters.registry import SQLiteRegistry
from semantic_reviewer.application.datasets import DatasetService, PublicDataset
from semantic_reviewer.bootstrap import build_datasets
from semantic_reviewer.domain.datasets import DatasetError
from semantic_reviewer.web.app import create_app


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = ParquetObservations(self.root / "datasets")
        self.database = self.root / "state.sqlite3"
        self.registry = SQLiteRegistry(self.database)
        self.rows = [
            {
                "owner": "example",
                "repo": "synthetic",
                "pr_number": 3,
                "comment_id": index + 10,
                "file_path": "sample.py",
                "comment": "<script>x()</script>",
                "code": "x < 2",
                "category": "discussion",
                "subcategory": "question",
                "comment_created_at": "2026-01-02T00:00:00Z",
                "enriched": "context",
                "line_number": None,
            }
            for index in range(3)
        ]
        body = json.dumps(self.rows).encode()
        self.source = PublicDataset(
            "synthetic-v1",
            "Synthetic sample",
            "a" * 40,
            "https://raw.githubusercontent.com/example/synthetic/" + "a" * 40 + "/data.json",
            hashlib.sha256(body).hexdigest(),
            3,
        )
        self.raw = self.store.root / (self.source.source_sha256 + ".json")
        self.raw.write_bytes(body)
        self.service = DatasetService((self.source,), self.registry, self.store)

    def test_round_trip_idempotence_restart_and_pagination(self):
        first = self.service.register(self.source.id)
        self.assertEqual(first, self.service.register(self.source.id))
        service = DatasetService((self.source,), SQLiteRegistry(self.database), self.store)
        page = service.browse(first.id, page=2, page_size=2)
        self.assertEqual([item.source_index for item in page.items], [2])
        self.assertEqual(page.items[0].id, f"{self.source.source_sha256}:2")
        self.assertEqual(page.items[0].comment, self.rows[2]["comment"])
        self.assertEqual(page.total, 3)
        self.assertEqual(service.browse(first.id, page=4).items, ())
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            self.assertEqual(db.execute("SELECT count(*) FROM event").fetchone()[0], 1)
            self.assertEqual(
                db.execute("SELECT kind FROM event").fetchone()[0], "dataset_registered"
            )

    def test_checksum_failure_leaves_registry_empty(self):
        self.raw.write_text("[]")
        with self.assertRaisesRegex(DatasetError, "checksum"):
            self.service.register(self.source.id)
        self.assertEqual(self.service.datasets(), ())

    def test_download_checksum_failure_does_not_publish(self):
        self.raw.unlink()
        with patch("semantic_reviewer.adapters.observations.urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = b"wrong"
            with self.assertRaisesRegex(DatasetError, "checksum"):
                self.service.register(self.source.id)
        self.assertFalse(self.raw.exists())
        self.assertEqual(list(self.store.root.iterdir()), [])

    def test_schema_validation_preserves_repeated_source_comments(self):
        self.rows[1]["comment_id"] = self.rows[0]["comment_id"]
        self.rows[0]["enriched"] = None
        del self.rows[1]["enriched"]
        records = self.store._canonical_rows(self.rows, self.source)
        self.assertNotEqual(records[0]["id"], records[1]["id"])
        self.assertEqual(records[0]["comment_id"], records[1]["comment_id"])
        self.assertIsNone(records[0]["line_number"])
        self.assertIsNone(records[0]["enriched"])
        self.assertIsNone(records[1]["enriched"])
        self.rows[1]["comment_id"] = True
        with self.assertRaisesRegex(DatasetError, "identifiers"):
            self.store._canonical_rows(self.rows, self.source)

    def test_conflicting_identity_is_rejected(self):
        dataset = self.service.register(self.source.id)
        with self.assertRaisesRegex(DatasetError, "different content"):
            self.registry.register(replace(dataset, source_sha256="f" * 64))
        self.assertEqual(self.registry.get(dataset.id), dataset)

    def test_registration_and_event_are_one_transaction(self):
        dataset = self.store.prepare(self.source)
        with closing(sqlite3.connect(self.database)) as db:
            db.execute(
                "CREATE TRIGGER fail_event BEFORE INSERT ON event "
                "BEGIN SELECT RAISE(ABORT, 'injected failure'); END"
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected failure"):
            self.registry.register(dataset)
        self.assertEqual(self.registry.list(), ())

    def test_events_cannot_be_changed_or_deleted(self):
        self.service.register(self.source.id)
        with closing(sqlite3.connect(self.database)) as db:
            for sql in ("DELETE FROM event", "UPDATE event SET kind='other'"):
                with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
                    db.execute(sql)

    def test_concurrent_registration_appends_one_event(self):
        dataset = self.store.prepare(self.source)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.registry.register, [dataset, dataset]))
        self.assertEqual(results[0], results[1])
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM event").fetchone()[0], 1)

    def test_corrupt_parquet_fails_closed(self):
        dataset = self.service.register(self.source.id)
        (self.store.root / (dataset.parquet_sha256 + ".parquet")).write_bytes(b"changed")
        with self.assertRaisesRegex(DatasetError, "has changed"):
            self.service.browse(dataset.id)

    def test_web_escapes_source_text_and_bounds_queries(self):
        self.service.register(self.source.id)
        with TestClient(create_app(self.service)) as client:
            self.assertEqual(client.get("/").status_code, 200)
            html = client.get(f"/datasets/{self.source.id}")
            self.assertEqual(html.status_code, 200)
            self.assertIn("&lt;script&gt;", html.text)
            self.assertNotIn("<script>x()", html.text)
            url = f"/api/datasets/{self.source.id}/observations"
            response = client.get(url + "?page=2&page_size=2")
            self.assertEqual(response.json()["items"][0]["source_index"], 2)
            self.assertEqual(client.get(url + "?page_size=101").status_code, 422)
            self.assertEqual(client.get(url + "?page=0").status_code, 422)
            self.assertEqual(client.get("/datasets/unknown").status_code, 404)
            self.assertEqual(client.get("/datasets/x' OR '1'='1").status_code, 404)

    def test_runtime_data_must_stay_outside_worktrees(self):
        repository = Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError, "outside"):
            build_datasets(repository / "runtime")
        other = self.root / "other"
        other.mkdir()
        (other / ".git").write_text("gitdir: somewhere")
        with self.assertRaisesRegex(ValueError, "outside"):
            build_datasets(other / "runtime")


if __name__ == "__main__":
    unittest.main()
