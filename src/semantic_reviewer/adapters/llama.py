"""Use a literal-loopback llama.cpp endpoint with bounded context and streamed telemetry."""

import ipaddress
import json
import math
import time
from datetime import UTC, datetime
from urllib.parse import urlsplit

import httpx

from semantic_reviewer.application.model import ModelFailure, ModelReply, ModelRequest
from semantic_reviewer.routing.selection import RoutingDecision
from semantic_reviewer.routing.usage import Measurement, TokenUsage


class LlamaClient:
    """Keep local-only routes on loopback, with proxies and redirects disabled.

    The endpoint must run a trusted local llama.cpp process. Loopback restriction
    prevents this adapter from sending source material to a remote address; it
    cannot prove what an independently configured local proxy does internally.
    """

    def __init__(self, endpoint: str, timeout: float = 120) -> None:
        """Validate the endpoint before accepting prompts; never resolve hostnames."""
        parsed = urlsplit(endpoint)
        try:
            local = ipaddress.ip_address(parsed.hostname or "").is_loopback
        except ValueError:
            local = False
        if (
            not local
            or parsed.scheme != "http"
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            raise ValueError(
                "llama.cpp requires an HTTP literal-loopback endpoint without credentials."
            )
        if not math.isfinite(timeout) or timeout <= 0 or timeout > 600:
            raise ValueError("Model timeout must be between zero and 600 seconds.")
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def generate(
        self, decision: RoutingDecision, request: ModelRequest, queued_at: datetime
    ) -> ModelReply:
        """Check identity/context, stream native completion and return raw provenance.

        The caller must have persisted the decision before invocation. Template
        rendering and tokenisation occur before generation. Refused/non-local
        decisions never send a prompt. Truncated, unfinished or malformed responses
        are failures, not successful interpretations. This method does not judge
        whether the returned content is semantically grounded.
        """
        started = datetime.now(UTC)
        clock = time.monotonic()
        tokens = TokenUsage()
        first_token_ms = None
        generation_ms = None

        def measurement(outcome: str) -> Measurement:
            return Measurement(
                started_at=queued_at,
                completed_at=datetime.now(UTC),
                outcome=outcome,
                tokens=tokens,
                queue_ms=max(0.0, (started - queued_at).total_seconds() * 1000),
                time_to_first_token_ms=first_token_ms,
                generation_ms=generation_ms,
            )

        def fail(message: str, outcome: str = "provider_failure") -> ModelFailure:
            return ModelFailure(message, measurement(outcome))

        def remaining() -> float:
            available = self.timeout - (time.monotonic() - clock)
            if available <= 0:
                raise fail("Model invocation exceeded its time limit.")
            return available

        def lines(response):
            # Bound raw chunks before line parsing: an unterminated SSE line must
            # not bypass the deadline or grow an unbounded line buffer.
            pending = b""
            size = 0
            for chunk in response.iter_bytes():
                remaining()
                size += len(chunk)
                if size > 2 * 1024 * 1024:
                    raise fail("Model response exceeded its size limit.")
                pending += chunk
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    yield line.decode("utf-8").rstrip("\r")

        model = decision.selected
        if model is None or model.locality != "local":
            raise fail("A selected local route is required.", "policy_failure")
        if not 1 <= request.max_output_tokens <= model.output_tokens:
            raise fail("Requested output exceeds the selected route.", "context_failure")
        try:
            with httpx.Client(
                base_url=self.endpoint,
                timeout=self.timeout,
                trust_env=False,
                follow_redirects=False,
            ) as client:

                def post(path: str, data: dict) -> dict:
                    return read_json("POST", path, data)

                def read_json(method: str, path: str, data: dict | None = None) -> dict:
                    # Preflight also consumes the shared deadline while bytes arrive.
                    # A trickling template response must not bypass the stream guard.
                    body = bytearray()
                    with client.stream(method, path, json=data, timeout=remaining()) as response:
                        response.raise_for_status()
                        for chunk in response.iter_bytes():
                            remaining()
                            body.extend(chunk)
                            if len(body) > 2 * 1024 * 1024:
                                raise fail("Provider preflight response exceeded its size limit.")
                    remaining()
                    return json.loads(body)

                available = read_json("GET", "/v1/models")
                entry = next((item for item in available["data"] if item["id"] == model.id), None)
                if entry is None:
                    raise fail("Selected model is not served by this endpoint.")
                messages = [
                    {"role": "system", "content": request.system},
                    {"role": "user", "content": request.user},
                ]
                rendered = post(
                    "/apply-template",
                    {
                        "messages": messages,
                        "add_generation_prompt": True,
                        "chat_template_kwargs": {"enable_thinking": False},
                    },
                )["prompt"]
                token_count = len(
                    post("/tokenize", {"content": rendered, "add_special": True})["tokens"]
                )
                actual_context = entry["meta"]["n_ctx"]
                if token_count > decision.max_input_tokens or (
                    token_count + request.max_output_tokens > actual_context
                ):
                    raise fail("Rendered prompt does not fit the model context.", "context_failure")
                payload = {
                    "prompt": rendered,
                    "n_predict": request.max_output_tokens,
                    "temperature": 0,
                    "seed": 0,
                    "json_schema": request.schema,
                    "stream": True,
                    "cache_prompt": False,
                }
                fragments = []
                final = None
                with client.stream(
                    "POST", "/completion", json=payload, timeout=remaining()
                ) as response:
                    response.raise_for_status()
                    for line in lines(response):
                        if not line.startswith("data: "):
                            continue
                        item = json.loads(line[6:])
                        content = item.get("content", "")
                        if not isinstance(content, str):
                            raise fail("Model response content is malformed.")
                        if content and first_token_ms is None:
                            first_token_ms = (time.monotonic() - clock) * 1000
                        fragments.append(content)
                        if item.get("stop") is True:
                            final = item
                remaining()
                if final is None or final.get("model") != model.id:
                    raise fail("Model stream ended without a matching completion record.")
                timings = final.get("timings", {})
                tokens = TokenUsage(
                    input_tokens=final.get("tokens_evaluated"),
                    output_tokens=final.get("tokens_predicted"),
                    cached_input_tokens=timings.get("cache_n"),
                )
                generation_ms = timings.get("predicted_ms")
                if final.get("truncated") or final.get("stop_type") == "limit":
                    raise fail("Model response was truncated.", "context_failure")
                if final.get("stop_type") not in ("eos", "word"):
                    raise fail("Model response has no recognised completion reason.")
                return ModelReply(
                    "".join(fragments),
                    measurement("success"),
                    json.dumps({"prompt_version": request.prompt_version, "request": payload}),
                    json.dumps(final),
                )
        except ModelFailure:
            raise
        except httpx.HTTPStatusError as error:
            raise fail(f"Local provider returned HTTP {error.response.status_code}.") from None
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, StopIteration):
            generation_ms = None
            raise fail("Local provider failed or returned an invalid response.") from None
