"""Bound local llama.cpp embedding calls and keep model controls behind the adapter."""

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field

from semantic_reviewer.adapters.local_http import local_endpoint
from semantic_reviewer.application.embeddings import (
    EmbeddingInput,
    EmbeddingOutcome,
)
from semantic_reviewer.domain.grouping import validate_vectors
from semantic_reviewer.routing.usage import Measurement, TokenUsage


class EmbeddingProfile(BaseModel):
    """Pin local deployment claims independently of research preprocessing and routing."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    model_id: str
    repository: str
    revision: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    licence: str
    runtime: str
    prefix: str = Field(max_length=100)
    dimensions: int = Field(ge=1, le=4096)
    context_tokens: int = Field(ge=1, le=8192)


class LlamaEmbeddingClient:
    """Use trusted literal-loopback HTTP with no proxy, redirects, truncation or automatic retry.

    The supplied model file is hashed before use. The API confirms alias/dimensions/
    context, not a cryptographic identity of the server's loaded bytes; that remaining
    operator claim is explicit in provenance. A local proxy cannot be attested here.
    """

    def __init__(
        self,
        endpoint: str,
        profile: EmbeddingProfile,
        model_file: Path,
        timeout: float = 120,
        transport=None,
    ) -> None:
        """Validate endpoint and model bytes before accepting any selected text."""
        endpoint = local_endpoint(endpoint, timeout)
        with model_file.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != profile.sha256:
            raise ValueError("Embedding model file differs from its pinned digest.")
        self.endpoint, self.profile, self.timeout, self.transport = (
            endpoint.rstrip("/"),
            profile,
            timeout,
            transport,
        )

    def run(self, value: EmbeddingInput) -> EmbeddingOutcome:
        """Check all token budgets before embedding; retain partial accounting on failure."""
        started, clock = datetime.now(UTC), time.monotonic()
        tokens = 0
        provenance = {
            "profile": self.profile.model_dump(),
            "model_file_digest_verified": True,
            "server_identity": "API alias/dimensions/context; loaded bytes are an operator claim",
            "adapter": "llama-embeddings-v1",
            "request_text_sha256": [],
            "responses": [],
        }

        def result(outcome, error=None, vectors=()):
            return EmbeddingOutcome(
                vectors,
                Measurement(
                    started_at=value.queued_at,
                    completed_at=datetime.now(UTC),
                    outcome=outcome,
                    tokens=TokenUsage(input_tokens=tokens, output_tokens=0),
                    queue_ms=max(0, (started - value.queued_at).total_seconds() * 1000),
                ),
                provenance,
                error,
            )

        model = value.decision.selected
        if (
            model is None
            or model.locality != "local"
            or model.provider != "llama.cpp"
            or model.id != self.profile.model_id
            or "embeddings" not in model.capabilities
        ):
            return result(
                "policy_failure", "Embedding route does not match the pinned local deployment."
            )
        if not 1 <= len(value.texts) <= 100 or any(not t or len(t) > 12000 for t in value.texts):
            return result("context_failure", "Embedding input count or text bound exceeded.")
        try:
            with httpx.Client(
                trust_env=False, follow_redirects=False, transport=self.transport
            ) as client:

                def request(method, path, payload=None):
                    remaining = self.timeout - (time.monotonic() - clock)
                    if remaining <= 0:
                        raise TimeoutError("Embedding deadline exceeded.")
                    with client.stream(
                        method, self.endpoint + path, json=payload, timeout=remaining
                    ) as response:
                        response.raise_for_status()
                        raw = bytearray()
                        for chunk in response.iter_bytes():
                            raw.extend(chunk)
                            if len(raw) > 2_000_000 or time.monotonic() - clock > self.timeout:
                                raise TimeoutError("Embedding response bound exceeded.")
                        return json.loads(raw)

                models = request("GET", "/v1/models")
                entry = next(item for item in models["data"] if item["id"] == model.id)
                meta = entry["meta"]
                if (
                    meta["n_embd"] != self.profile.dimensions
                    or meta["n_ctx"] < self.profile.context_tokens
                ):
                    return result(
                        "policy_failure", "Embedding server metadata differs from the profile."
                    )
                provenance["server_metadata"] = meta
                texts = tuple(self.profile.prefix + t for t in value.texts)
                for text in texts:
                    count = len(
                        request("POST", "/tokenize", {"content": text, "add_special": True})[
                            "tokens"
                        ]
                    )
                    if count > min(value.decision.max_input_tokens, self.profile.context_tokens):
                        return result(
                            "context_failure",
                            "Embedding text exceeds the token budget; no truncation applied.",
                        )
                vectors = []
                for text in texts:
                    payload = {"model": model.id, "input": [text], "encoding_format": "float"}
                    response = request("POST", "/v1/embeddings", payload)
                    provenance["request_text_sha256"].append(
                        hashlib.sha256(text.encode()).hexdigest()
                    )
                    provenance["responses"].append(
                        {k: v for k, v in response.items() if k != "data"}
                    )
                    usage = response.get("usage", {})
                    observed = usage.get("prompt_tokens")
                    tokens = (
                        tokens + observed
                        if tokens is not None and type(observed) is int and observed >= 0
                        else None
                    )
                    data = response["data"]
                    if (
                        len(data) != 1
                        or data[0]["index"] != 0
                        or len(data[0]["embedding"]) != self.profile.dimensions
                    ):
                        provenance["invalid_response_json"] = json.dumps(response)
                        return result(
                            "semantic_failure",
                            "Embedding response has invalid row identity or dimensions.",
                        )
                    try:
                        vector = validate_vectors((tuple(data[0]["embedding"]),), 1)[0]
                    except (ValueError, TypeError):
                        provenance["invalid_response_json"] = json.dumps(response)
                        return result(
                            "semantic_failure", "Embedding response contains invalid vectors."
                        )
                    vectors.append(vector)
                try:
                    validated = validate_vectors(tuple(vectors), len(texts))
                except ValueError:
                    return result(
                        "semantic_failure", "Embedding response contains invalid vectors."
                    )
                return result("success", vectors=validated)
        except (httpx.HTTPError, TimeoutError, OSError):
            return result(
                "provider_failure", "Local embedding provider failed; no automatic retry."
            )
        except (ValueError, KeyError, TypeError, StopIteration):
            return result(
                "provider_failure",
                "Local embedding provider returned an invalid protocol response.",
            )
