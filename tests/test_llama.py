"""Verify local transport, context refusals and provider failures without a model dependency."""

import json
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import httpx
from test_routing_selection import EXAMPLE

from semantic_reviewer.adapters.llama import LlamaClient
from semantic_reviewer.application.model import ModelFailure, ModelRequest
from semantic_reviewer.routing.selection import RoutingConfig, TaskRequirements, select_route


class LlamaTest(unittest.TestCase):
    def setUp(self):
        self.config = RoutingConfig.model_validate_json(EXAMPLE.read_bytes())
        self.decision = select_route(
            self.config, TaskRequirements(task_id="1", task_class="normalisation")
        )
        self.request = ModelRequest("system", "source", {"type": "object"}, "test-v1", 100)
        self.queued = datetime.now(UTC) - timedelta(seconds=1)
        self.calls = []
        self.status = 200
        self.context = 4096
        self.stream = None
        self.preflight_hook = lambda: None
        self.preflight_stream = None
        self.final = {
            "content": "",
            "stop": True,
            "model": "example-local",
            "tokens_evaluated": 4,
            "tokens_predicted": 3,
            "stop_type": "eos",
            "truncated": False,
            "timings": {"cache_n": 0, "predicted_ms": 1.0},
        }

    def generate(self):
        def handler(request):
            self.calls.append(request.url.path)
            if request.url.path == "/v1/models":
                self.preflight_hook()
                if self.preflight_stream is not None:
                    return httpx.Response(200, stream=self.preflight_stream)
                return httpx.Response(
                    self.status,
                    json={"data": [{"id": "example-local", "meta": {"n_ctx": self.context}}]},
                )
            if request.url.path == "/apply-template":
                return httpx.Response(200, json={"prompt": "rendered prompt"})
            if request.url.path == "/tokenize":
                return httpx.Response(200, json={"tokens": [1, 2, 3, 4]})
            data = json.loads(request.content)
            self.assertEqual(data["prompt"], "rendered prompt")
            self.assertFalse(data["cache_prompt"])
            if self.stream is not None:
                return httpx.Response(200, stream=self.stream)
            return httpx.Response(
                200,
                text='data: {"content":"{}","stop":false}\n\n'
                + "data: "
                + json.dumps(self.final)
                + "\n\n",
            )

        original = httpx.Client

        def factory(**kwargs):
            self.assertFalse(kwargs["trust_env"])
            self.assertFalse(kwargs["follow_redirects"])
            return original(**kwargs, transport=httpx.MockTransport(handler))

        with patch("semantic_reviewer.adapters.llama.httpx.Client", side_effect=factory):
            return LlamaClient("http://127.0.0.1:8081").generate(
                self.decision, self.request, self.queued
            )

    def test_only_literal_loopback_without_credentials_or_redirects(self):
        for url in (
            "https://example.com",
            "http://localhost:8081",
            "http://127.0.0.1@evil.test",
            "http://127.0.0.1/private",
            "http://192.168.1.2:8081",
            "http://127.0.0.1?x=1",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                LlamaClient(url)
        LlamaClient("http://[::1]:8081")
        with self.assertRaises(ValueError):
            LlamaClient("http://127.0.0.1", timeout=float("nan"))

    def test_stream_retains_usage_prompt_version_and_observed_first_token(self):
        reply = self.generate()
        self.assertEqual(reply.content, "{}")
        self.assertEqual(reply.measurement.tokens.input_tokens, 4)
        self.assertEqual(reply.measurement.tokens.output_tokens, 3)
        self.assertEqual(reply.measurement.tokens.cached_input_tokens, 0)
        self.assertIsNotNone(reply.measurement.time_to_first_token_ms)
        self.assertEqual(json.loads(reply.request_json)["prompt_version"], "test-v1")

    def test_context_refusal_happens_before_generation(self):
        self.context = 50
        with self.assertRaises(ModelFailure) as raised:
            self.generate()
        self.assertEqual(raised.exception.measurement.outcome, "context_failure")
        self.assertNotIn("/completion", self.calls)

    def test_rate_limit_and_redirect_are_provider_failures_without_escalation(self):
        for status in (429, 503, 302):
            self.status = status
            with self.subTest(status=status), self.assertRaises(ModelFailure) as raised:
                self.generate()
            self.assertEqual(raised.exception.measurement.outcome, "provider_failure")
            self.assertNotIn("/completion", self.calls)

    def test_wrong_model_truncation_and_invalid_telemetry_are_not_success(self):
        for field, value, outcome in (
            ("model", "wrong", "provider_failure"),
            ("truncated", True, "context_failure"),
            ("timings", {"predicted_ms": -1}, "provider_failure"),
        ):
            original = self.final[field]
            self.final[field] = value
            with self.subTest(field=field), self.assertRaises(ModelFailure) as raised:
                self.generate()
            self.assertEqual(raised.exception.measurement.outcome, outcome)
            self.final[field] = original

    def test_remote_decision_never_contacts_provider(self):
        self.decision = select_route(
            self.config,
            TaskRequirements(task_id="public", task_class="normalisation", privacy="public"),
        )
        with self.assertRaises(ModelFailure) as raised:
            self.generate()
        self.assertEqual(raised.exception.measurement.outcome, "policy_failure")
        self.assertEqual(self.calls, [])

    def test_unterminated_stream_is_bounded_before_line_parsing(self):
        consumed = []

        class Stream(httpx.SyncByteStream):
            def __iter__(inner):
                for index in range(4):
                    consumed.append(index)
                    yield b"x" * (1024 * 1024)

        self.stream = Stream()
        with self.assertRaisesRegex(ModelFailure, "size limit"):
            self.generate()
        self.assertEqual(len(consumed), 3)

    def test_continuous_trickle_and_exhausted_preflight_share_deadline(self):
        clock = [0.0]

        class Stream(httpx.SyncByteStream):
            def __iter__(inner):
                for _ in range(10):
                    clock[0] += 61
                    yield b"x"

        self.stream = Stream()
        with patch("semantic_reviewer.adapters.llama.time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaisesRegex(ModelFailure, "time limit"):
                self.generate()
            clock[0] = 0
            self.calls.clear()
            self.preflight_hook = lambda: clock.__setitem__(0, 121)
            with self.assertRaisesRegex(ModelFailure, "time limit"):
                self.generate()
        self.assertEqual(self.calls, ["/v1/models"])

    def test_trickling_preflight_cannot_hold_worker_past_deadline(self):
        clock = [0.0]
        consumed = []

        class Stream(httpx.SyncByteStream):
            def __iter__(inner):
                for index in range(10):
                    consumed.append(index)
                    clock[0] += 61
                    yield b" "

        self.preflight_stream = Stream()
        with patch("semantic_reviewer.adapters.llama.time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaisesRegex(ModelFailure, "time limit"):
                self.generate()
        self.assertEqual(len(consumed), 2)
        self.assertNotIn("/completion", self.calls)

    def test_eof_after_deadline_cannot_turn_a_final_record_into_success(self):
        clock = [0.0]
        final = self.final

        class Stream(httpx.SyncByteStream):
            def __iter__(inner):
                yield b'data: {"content":"{}","stop":false}\n\n'
                clock[0] = 119
                yield ("data: " + json.dumps(final) + "\n\n").encode()
                clock[0] = 121

        self.stream = Stream()
        with patch("semantic_reviewer.adapters.llama.time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaisesRegex(ModelFailure, "time limit"):
                self.generate()
