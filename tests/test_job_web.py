"""Verify browser submission is local, queues only and escapes model/source output."""

import unittest

import test_jobs
from fastapi.testclient import TestClient

from semantic_reviewer.application.artefacts import Publication
from semantic_reviewer.web.app import create_app


class JobWebTest(unittest.TestCase):
    def setUp(self):
        test_jobs.JobsTest.setUp(self)
        self.client = TestClient(create_app(self.service, self.queue), base_url="http://127.0.0.1")
        self.url = f"/datasets/{self.source.id}/observations/0/normalise"

    def test_submit_returns_queue_redirect_and_never_invokes_model(self):
        response = self.client.post(
            self.url, headers={"Origin": "http://127.0.0.1"}, follow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(len(self.jobs.recent()), 1)
        self.assertEqual(self.jobs.recent()[0].status, "queued")
        page = self.client.get(response.headers["location"])
        self.assertIn("Waiting for the local worker", page.text)
        self.assertIn('http-equiv="refresh"', page.text)
        self.assertIn(self.source.id, self.client.get("/jobs").text)

    def test_cross_origin_missing_origin_and_rebound_host_cannot_submit(self):
        for headers in (
            {},
            {"Origin": "https://evil.example"},
        ):
            with self.subTest(headers=headers):
                self.assertEqual(self.client.post(self.url, headers=headers).status_code, 403)
        self.assertEqual(self.jobs.recent(), ())

    def test_host_rebinding_cannot_read_sources_jobs_or_results(self):
        for url in ("/", "/jobs", "/jobs/some-id", "/api/datasets"):
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url, headers={"Host": "evil.example"}).status_code, 400
                )
        self.assertEqual(
            self.client.post(
                self.url, headers={"Host": "evil.example", "Origin": "http://evil.example"}
            ).status_code,
            400,
        )

    def test_failed_result_is_inspectable_and_source_text_is_escaped(self):
        job = self.queue.enqueue(self.source.id, 0)
        claimed = self.jobs.claim("test")
        digest = self.results.publish(
            {"telemetry": "local", "interpretation": None, "response": "<script>bad()</script>"},
            Publication(job.id, "normalisation"),
        )
        self.jobs.finish(claimed, digest, "Output failed evidence validation.")
        response = self.client.get(f"/jobs/{job.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Output failed evidence validation", response.text)
        self.assertNotIn("<script>bad()", response.text)
        self.assertNotIn('http-equiv="refresh"', response.text)
        (self.results.root / (digest + ".json")).write_text("{}")
        self.assertEqual(self.client.get(f"/jobs/{job.id}").status_code, 409)
        self.assertEqual(self.client.get("/jobs/missing").status_code, 404)
