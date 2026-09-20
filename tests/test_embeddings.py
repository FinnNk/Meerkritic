"""Challenge pinned local embedding transport, context bounds and MAF outcomes."""

import hashlib
import json
import unittest
from datetime import UTC, datetime
from pathlib import Path

import httpx

from semantic_reviewer.adapters.embedding import EmbeddingProfile, LlamaEmbeddingClient
from semantic_reviewer.adapters.maf_embedding import MafEmbeddingRuntime
from semantic_reviewer.application.embeddings import EmbeddingInput
from semantic_reviewer.routing.selection import RoutingConfig, TaskRequirements

ROOT = Path(__file__).resolve().parents[1]


class EmbeddingAdapterTest(unittest.TestCase):
    def setUp(self):
        import tempfile

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.model = Path(self.temp.name) / "model"
        self.model.write_bytes(b"fixture")
        self.profile = EmbeddingProfile(
            model_id="nomic-embed-v1.5-local",
            repository="fixture",
            revision="1",
            sha256=hashlib.sha256(b"fixture").hexdigest(),
            licence="fixture",
            runtime="fixture",
            prefix="clustering: ",
            dimensions=2,
            context_tokens=2048,
        )
        from semantic_reviewer.routing.selection import select_route

        self.route = select_route(
            RoutingConfig.model_validate_json(
                (ROOT / "config/routing/discovery-local.json").read_bytes()
            ),
            TaskRequirements(task_id="test", task_class="embedding", capabilities=("embeddings",)),
        )
        self.calls = []
        self.token_count = 10
        self.vector = [1.0, 0.0]

    def response(self, request):
        self.calls.append(request.url.path)
        if request.url.path == "/v1/models":
            body = {"data": [{"id": self.profile.model_id, "meta": {"n_embd": 2, "n_ctx": 2048}}]}
        elif request.url.path == "/tokenize":
            body = {"tokens": list(range(self.token_count))}
        else:
            self.assertTrue(json.loads(request.content)["input"][0].startswith("clustering: "))
            body = {
                "data": [{"index": 0, "embedding": self.vector}],
                "usage": {"prompt_tokens": 10},
            }
        return httpx.Response(200, json=body)

    def run_model(self):
        client = LlamaEmbeddingClient(
            "http://127.0.0.1:8082",
            self.profile,
            self.model,
            transport=httpx.MockTransport(self.response),
        )
        return client.run(EmbeddingInput(("Close files.",), self.route, datetime.now(UTC)))

    def test_local_pinned_model_and_actual_token_bound_before_embeddings(self):
        result = self.run_model()
        self.assertIsNone(result.error)
        self.assertEqual(result.measurement.tokens.input_tokens, 10)
        self.token_count = 2049
        self.calls = []
        self.assertEqual(self.run_model().measurement.outcome, "context_failure")
        self.assertNotIn("/v1/embeddings", self.calls)
        for endpoint in ("http://localhost:8082", "http://example.org", "http://127.0.0.1/evil"):
            with self.assertRaises(ValueError):
                LlamaEmbeddingClient(endpoint, self.profile, self.model)
        self.model.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.run_model()

    def test_invalid_vectors_do_not_become_provider_success(self):
        self.vector = [0.0, 0.0]
        result = self.run_model()
        self.assertEqual(result.measurement.outcome, "semantic_failure")
        self.assertIn("invalid_response_json", result.provenance)

    def test_real_maf_retains_model_outcome_and_framework_observation(self):
        client = LlamaEmbeddingClient(
            "http://127.0.0.1:8082",
            self.profile,
            self.model,
            transport=httpx.MockTransport(self.response),
        )
        result = MafEmbeddingRuntime(client).run(
            EmbeddingInput(("Close files.",), self.route, datetime.now(UTC))
        )
        self.assertIsNone(result.error)
        self.assertEqual(result.framework.outcome, "completed")
        self.assertEqual(result.framework.framework, "Microsoft Agent Framework")
