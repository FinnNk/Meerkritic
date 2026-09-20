"""Check real queue transactions, crash recovery, artefact integrity and routed execution."""

import json
import sqlite3
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import test_datasets
import test_normalisation
from test_routing_selection import EXAMPLE

from semantic_reviewer.adapters.jobs import SQLiteJobs
from semantic_reviewer.adapters.maf import MafWorkflowRunner
from semantic_reviewer.adapters.results import JsonResults
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal
from semantic_reviewer.adapters.worker_lock import worker_lock
from semantic_reviewer.application.artefacts import Publication
from semantic_reviewer.application.jobs import JobService
from semantic_reviewer.application.routing import RoutingService
from semantic_reviewer.routing.selection import RoutingConfig


class JobsTest(unittest.TestCase):
    def setUp(self):
        test_datasets.DatasetTest.setUp(self)
        self.service.register(self.source.id)
        self.jobs = SQLiteJobs(self.database)
        self.results = JsonResults(self.root / "results", self.database)
        self.queue = JobService(self.service, self.jobs, self.results)

    def test_invalid_completion_cannot_create_success_or_event(self):
        job = self.queue.enqueue(self.source.id, 0)
        claimed = self.jobs.claim("worker")
        with self.jobs.state.connect() as db:
            before = db.execute("SELECT count(*) FROM event").fetchone()[0]
        for digest, error in ((None, ""), (None, " \t"), (None, None), ("", None)):
            with self.subTest(digest=digest, error=error), self.assertRaises(ValueError):
                self.jobs.finish(claimed, digest, error)
        with self.jobs.state.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM event").fetchone()[0], before)
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE job SET status='succeeded', error='' WHERE id=?", (job.id,))
            for status, digest, error in (
                ("succeeded", "g" * 64, None),
                ("failed", None, "\t\r\n"),
            ):
                with self.subTest(status=status), self.assertRaises(sqlite3.IntegrityError):
                    db.execute(
                        "UPDATE job SET status=?, artefact_sha256=?, error=? WHERE id=?",
                        (status, digest, error, job.id),
                    )
        self.assertEqual(self.jobs.get(job.id).status, "running")
        self.jobs.finish(claimed, None, "Provider unavailable")
        self.assertEqual(self.jobs.get(job.id).status, "failed")

    def test_concurrent_claim_restart_and_old_worker_fencing(self):
        first = self.queue.enqueue(self.source.id, 0)
        second = self.queue.enqueue(self.source.id, 1)
        with ThreadPoolExecutor(2) as pool:
            claims = list(pool.map(self.jobs.claim, ("worker-a", "worker-b")))
        claimed = next(job for job in claims if job)
        self.assertEqual(sum(job is not None for job in claims), 1)
        self.assertEqual(claimed.id, first.id)
        with worker_lock(self.root):
            restarted = SQLiteJobs(self.database)
            self.assertEqual(restarted.recover_interrupted(), 1)
            self.assertEqual(restarted.recover_interrupted(), 0)
        with self.assertRaises(ValueError):
            self.jobs.finish(claimed, "a" * 64, None)
        self.assertEqual(self.jobs.get(first.id).status, "failed")
        self.assertEqual(self.jobs.claim("new-worker").id, second.id)
        with self.jobs.state.connect() as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM event WHERE kind='job_interrupted'").fetchone()[0],
                1,
            )

    def test_os_lock_blocks_second_process_and_releases_after_exit(self):
        program = (
            "from pathlib import Path; from semantic_reviewer.adapters.worker_lock "
            "import worker_lock; import sys; "
            "lock=worker_lock(Path(sys.argv[1])); lock.__enter__(); lock.__exit__(None,None,None)"
        )
        with worker_lock(self.root):
            result = subprocess.run(
                [sys.executable, "-c", program, str(self.root)], capture_output=True, text=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Another worker", result.stderr)
        result = subprocess.run(
            [sys.executable, "-c", program, str(self.root)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_staleness_is_inspection_only_and_never_retries(self):
        job = self.queue.enqueue(self.source.id, 0)
        claimed = self.jobs.claim("worker")
        old = (datetime.now(UTC) - timedelta(minutes=2)).isoformat()
        with self.jobs.state.connect() as db:
            db.execute("UPDATE job SET heartbeat_at=? WHERE id=?", (old, job.id))
        self.assertTrue(self.jobs.get(job.id).stale)
        self.assertIsNone(self.jobs.claim("other"))
        self.jobs.heartbeat(claimed)
        self.assertFalse(self.jobs.get(job.id).stale)

    def test_result_publication_is_immutable_and_detects_tampering(self):
        value = {"source": "public synthetic", "interpretation": "<script>bad</script>"}
        job = self.queue.enqueue(self.source.id, 0)
        publication = Publication(job.id, "normalisation")
        with self.assertRaises(ValueError):
            self.results.publish([value], publication)
        self.assertEqual(list(self.results.root.iterdir()), [])
        digest = self.results.publish(value, publication)
        self.assertEqual(self.results.publish(value, publication), digest)
        self.assertEqual(self.results.read(digest), value)
        (self.results.root / (digest + ".json")).write_text("{}")
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.results.read(digest)
        with self.assertRaises(ValueError):
            self.results.read("../state.sqlite3")

    def test_maf_job_persists_provenance_usage_framework_and_events_across_restart(self):
        fixture = test_normalisation.WorkflowTest()
        fixture.setUp()
        fixture.payload["evidence_quotes"] = [{"source": "code", "quote": "x < 2"}]

        class Model:
            def generate(inner, decision, request, queued_at):
                from semantic_reviewer.application.model import ModelReply
                from semantic_reviewer.routing.usage import Measurement

                return ModelReply(
                    json.dumps(fixture.payload),
                    Measurement(
                        started_at=queued_at, completed_at=datetime.now(UTC), outcome="success"
                    ),
                    json.dumps({"prompt_version": request.prompt_version}),
                    "raw-response",
                )

        routing = RoutingService(
            RoutingConfig.model_validate_json(EXAMPLE.read_bytes()),
            SQLiteRoutingJournal(self.database),
        )
        queued = self.queue.enqueue(self.source.id, 0)
        self.assertTrue(self.queue.run_once(routing, MafWorkflowRunner(Model()), "worker"))
        restarted = JobService(self.service, SQLiteJobs(self.database), self.results)
        job, bundle = restarted.inspect(queued.id)
        self.assertEqual(job.status, "succeeded")
        self.assertEqual(bundle["source"]["id"], queued.observation_id)
        self.assertEqual(bundle["framework"]["version"], "1.19.0")
        self.assertEqual(bundle["usage"]["decision_id"], job.decision_id)
        self.assertEqual(bundle["dataset"]["source_sha256"], self.source.source_sha256)
        self.assertEqual(bundle["evidence_spans"][0]["quote"], "x < 2")
        with self.jobs.state.connect() as db:
            events = [
                row[0]
                for row in db.execute(
                    "SELECT kind FROM event WHERE subject_id=? ORDER BY sequence", (job.id,)
                )
            ]
            self.assertEqual(events, ["job_queued", "job_started", "job_routed", "job_succeeded"])
        self.assertFalse(self.queue.run_once(routing, MafWorkflowRunner(Model()), "worker"))

    def test_refused_route_fails_job_without_calling_model(self):
        config = RoutingConfig.model_validate_json(EXAMPLE.read_bytes())
        config = config.model_copy(
            update={
                "inventory": config.inventory.model_copy(
                    update={
                        "models": tuple(
                            model.model_copy(update={"status": "unavailable"})
                            for model in config.inventory.models
                        )
                    }
                )
            }
        )
        routing = RoutingService(config, SQLiteRoutingJournal(self.database))
        job = self.queue.enqueue(self.source.id, 0)
        self.queue.run_once(routing, None, "worker")
        failed = self.jobs.get(job.id)
        self.assertEqual(failed.status, "failed")
        self.assertIsNotNone(failed.decision_id)
        self.assertIn("no_eligible_model", failed.error)

    def test_queue_rejects_unknown_source_without_partial_job(self):
        with self.assertRaises(LookupError):
            self.queue.enqueue(self.source.id, 100)
        self.assertEqual(self.jobs.recent(), ())

    def test_process_death_releases_lock_and_recovery_does_not_requeue(self):
        job = self.queue.enqueue(self.source.id, 0)
        program = (
            "from pathlib import Path; import sys,time; "
            "from semantic_reviewer.adapters.worker_lock import worker_lock; "
            "from semantic_reviewer.adapters.jobs import SQLiteJobs; "
            "root=Path(sys.argv[1]); lock=worker_lock(root); lock.__enter__(); "
            "SQLiteJobs(root/'state.sqlite3').claim('child'); print('ready',flush=True); "
            "time.sleep(30)"
        )
        process = subprocess.Popen(
            [sys.executable, "-c", program, str(self.root)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            self.assertEqual(process.stdout.readline().strip(), "ready")
            with self.assertRaises(RuntimeError), worker_lock(self.root):
                pass
        finally:
            process.terminate()
            process.communicate(timeout=5)
        with worker_lock(self.root):
            self.assertEqual(self.jobs.recover_interrupted(), 1)
        self.assertEqual(self.jobs.get(job.id).status, "failed")
        self.assertIsNone(self.jobs.claim("replacement"))

    def test_failures_retain_prompt_usage_and_framework_observation(self):
        from semantic_reviewer.application.model import ModelFailure, ModelReply
        from semantic_reviewer.routing.usage import Measurement

        routing = RoutingService(
            RoutingConfig.model_validate_json(EXAMPLE.read_bytes()),
            SQLiteRoutingJournal(self.database),
        )
        for failure in ("provider_failure", "semantic_failure"):

            class Model:
                def generate(inner, decision, request, queued_at, failure=failure):
                    measured = Measurement(
                        started_at=queued_at,
                        completed_at=datetime.now(UTC),
                        outcome=failure if failure == "provider_failure" else "success",
                    )
                    if failure == "provider_failure":
                        raise ModelFailure("Unavailable", measured)
                    return ModelReply("{}", measured, "request", "response")

            job = self.queue.enqueue(self.source.id, 0)
            self.queue.run_once(routing, MafWorkflowRunner(Model()), "worker")
            state, bundle = self.queue.inspect(job.id)
            self.assertEqual(state.status, "failed")
            self.assertEqual(bundle["usage"]["measurement"]["outcome"], failure)
            self.assertEqual(bundle["request"]["prompt_version"], "normalisation-v1")
            self.assertEqual(bundle["source"]["id"], job.observation_id)
            self.assertEqual(bundle["framework"]["outcome"], "completed")
            if failure == "semantic_failure":
                self.assertEqual(bundle["model_output"], "{}")

    def test_publication_and_final_write_failure_preserve_uncertain_work_without_replay(self):
        from semantic_reviewer.application.model import ModelFailure
        from semantic_reviewer.routing.usage import Measurement

        class Model:
            calls = 0

            def generate(inner, decision, request, queued_at):
                inner.calls += 1
                raise ModelFailure(
                    "Unavailable",
                    Measurement(
                        started_at=queued_at,
                        completed_at=datetime.now(UTC),
                        outcome="provider_failure",
                    ),
                )

        routing = RoutingService(
            RoutingConfig.model_validate_json(EXAMPLE.read_bytes()),
            SQLiteRoutingJournal(self.database),
        )
        model = Model()
        for target, method in ((self.results, "publish"), (self.jobs, "finish")):
            job = self.queue.enqueue(self.source.id, 0)
            before_files = set(self.results.root.glob("*.json"))
            with patch.object(target, method, side_effect=OSError("injected storage failure")):
                with self.assertRaises(OSError):
                    self.queue.run_once(routing, MafWorkflowRunner(model), "worker")
            state = self.jobs.get(job.id)
            self.assertEqual(state.status, "running")
            self.assertIsNotNone(routing.journal.get(state.decision_id)[1])
            self.assertIsNone(state.artefact_sha256)
            if method == "finish":
                orphans = set(self.results.root.glob("*.json")) - before_files
                self.assertEqual(len(orphans), 1)
                self.assertEqual(self.results.read(next(iter(orphans)).stem)["job_id"], job.id)
            with worker_lock(self.root):
                self.jobs.recover_interrupted()
            self.assertFalse(self.queue.run_once(routing, MafWorkflowRunner(model), "replacement"))
        self.assertEqual(model.calls, 2)
