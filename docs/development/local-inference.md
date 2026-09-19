# Local inference

`LlamaClient` implements the project-owned `ModelClient` contract. It accepts a persisted local routing decision and a versioned prompt/schema; it does not select a model or write routing history. Literal loopback HTTP endpoints are required. Hostnames, credentials in URLs, redirects and environment proxies are rejected or disabled. Operate a trusted local llama.cpp process: loopback alone cannot prove what a separately configured proxy does internally.

Before generation, the adapter verifies the served model identity, renders its chat template and tokenises that exact prompt. It checks the selected input budget and the server's reported context capacity, including requested output. Oversized prompts fail instead of silently dropping evidence. Native streaming completion captures first-token time, input/output/cached tokens and generation duration where available. Cached-input counts come from `timings.cache_n`, not the server's post-generation cache size. Unknown reasoning tokens remain unknown. Input/output and raw request/response provenance return to the caller for immutable filesystem storage; bodies do not belong in SQLite.

Provider HTTP failures, malformed streams and identity mismatches remain infrastructure failures. Context overflow/truncation is a context failure. The consumer must validate schema and evidence grounding before treating content as an interpretation. Grammar-constrained JSON alone cannot establish semantic correctness.

Operational preflight used official llama.cpp v0.4.1's b10964 Windows CUDA 12.4 binaries and Qwen/Qwen3-4B-GGUF Q4_K_M at revision `bc640142c66e1fdd12af0bd68f40445458f3869b`. Published digests were checked before execution. These are compatibility fixtures, not evidence of preferred model quality. Local runtime configuration, weights and detailed preflight logs stay outside source control under `extras/preflight/vs1-inference`.

## Start the compatibility fixture

Download the official `llama-b10964-bin-win-cuda-12.4-x64.zip` and matching CUDA runtime
archive from the b10964 release. Verify their published SHA-256 digests before
extracting to the same directory. Obtain `Qwen3-4B-Q4_K_M.gguf` from the pinned model
revision above; its SHA-256 is
`7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`.
Keep binaries and weights outside the repository. This fixture needs about 3.1 GB
of downloads; other hardware/builds need their own compatibility verification.

Run the extracted server with the downloaded model path:

```sh
llama-server.exe --model PATH/TO/Qwen3-4B-Q4_K_M.gguf --alias qwen3-4b-local --host 127.0.0.1 --port 8081 --ctx-size 4096 --parallel 1 --n-gpu-layers 99 --threads 8 --jinja --cors-origins http://127.0.0.1:8081 --no-cors-credentials --no-webui
```

The adapter checks one elapsed-time budget across preparation, arriving chunks and
completion EOF; a late completion is never accepted as success. Pending network I/O
uses the remaining budget at request start, so an individual blocked read may return
after the elapsed deadline. This is bounded transport waiting, not hard real-time
cancellation. Raw chunks are bounded before line parsing, so unterminated lines cannot
bypass the 2 MiB limit. Failures may leave unknown usage; no retry is automatic.

Sources: [llama.cpp stable release](https://github.com/ggml-org/llama.cpp/releases/tag/v0.4.1), [binary release](https://github.com/ggml-org/llama.cpp/releases/tag/b10964), [pinned Qwen model card](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/bc640142c66e1fdd12af0bd68f40445458f3869b), and [server API](https://github.com/ggml-org/llama.cpp/blob/b10964/tools/server/README.md). Accessed 19 September 2026.
