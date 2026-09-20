# Start a local model server

The application sends model requests to a separate llama.cpp server on this
computer. This guide starts the tested Qwen generation model used to interpret
comments, propose rules and answer guidance. [Discovery](discovery.md) also needs
an embedding server to turn text into numerical representations for comparison.

## Prepare the generation model

The tested setup uses Windows, an NVIDIA GPU and CUDA 12.4. It needs about 3.1 GB
of downloads. Other hardware or builds need their own compatibility check.

1. From the [llama.cpp b10964 release](https://github.com/ggml-org/llama.cpp/releases/tag/b10964),
   download `llama-b10964-bin-win-cuda-12.4-x64.zip` and its matching CUDA runtime archive.
2. Compare each archive's SHA-256 checksum with the published release checksum.
   In PowerShell, use `Get-FileHash <downloaded-file> -Algorithm SHA256`.
3. Extract both archives into the same directory outside the repository, for example
   `../extras/llama`. Keep their existing licences and notices.
4. Download `Qwen3-4B-Q4_K_M.gguf` from the
   [pinned model revision](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/bc640142c66e1fdd12af0bd68f40445458f3869b)
   into `../extras/models`.
5. Check its SHA-256 against:

   ```text
   7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5
   ```

## Start the server

Run this from the repository root in PowerShell. Substitute your actual executable
and model paths if you used different directories:

```powershell
& ../extras/llama/llama-server.exe `
  --model ../extras/models/Qwen3-4B-Q4_K_M.gguf `
  --alias qwen3-4b-local --host 127.0.0.1 --port 8081 `
  --ctx-size 4096 --parallel 1 --n-gpu-layers 99 --threads 8 `
  --jinja --cors-origins http://127.0.0.1:8081 --no-cors-credentials --no-webui
```

- Keep the server terminal running. Wait for the model to finish loading.
- Check readiness with `Invoke-RestMethod http://127.0.0.1:8081/health`; expect an
  OK status once loading completes.
- Start the [normalisation worker](normalisation.md) or [discovery worker](discovery.md).
  Starting the server alone does not process application jobs.

The model alias and context size must match the supplied routing configuration.
This is a tested configuration, not evidence that Qwen is the best model for research.

## Diagnose connection and request failures

| Problem | Check or next action |
| --- | --- |
| Server cannot load | Inspect its terminal, downloaded files, CUDA runtime and available GPU memory. |
| Port already in use | Inspect the existing process. Reuse a verified server or stop it deliberately before starting another. |
| Identity/context mismatch | Check model alias, served model and context size against the routing configuration. |
| Prompt exceeds capacity | Reduce the selected input or deliberately configure a compatible larger context. The adapter does not silently drop evidence. |
| Call times out or stream is malformed | Inspect the retained job error and server log before a new submission. Usage may be unknown; retries are not automatic. |

The adapter accepts literal loopback addresses only; hostnames, URL credentials,
redirects and environment proxies are refused or disabled. Operate a trusted local
server: an address alone cannot prove which model bytes a separate process loaded.

## Adapter reference

| Responsibility | Behaviour |
| --- | --- |
| Model selection | Supplied by a saved routing decision; `LlamaClient` does not choose the model. |
| Context checks | Render the actual chat template, count tokens and reserve output space before generation. |
| Model controls | Adapter request `llama-native-v2` owns Qwen3's `/no_think` and `enable_thinking=False`; other families receive neither. |
| Timing and tokens | Streaming captures first-token time, input/output/cache counts and generation time when exposed. Cached input uses `timings.cache_n`; unknown reasoning counts stay unknown. |
| Retained evidence | Return the prompt/schema version, actual provider request/response and usage to the caller for file storage. |
| Validation | The caller validates the interpretation and its evidence; grammatical JSON alone is insufficient. |

One elapsed-time budget covers preparation and completion. A blocked read can
return after the deadline, but a late completion is refused. Raw chunks are bounded
before parsing, including unterminated lines, to enforce the 2 MiB response limit.
HTTP/identity/stream failures are infrastructure failures; context overflow is a
context failure. See the [interpretation contract](normalisation-contract.md).

The [pinned server API](https://github.com/ggml-org/llama.cpp/blob/b10964/tools/server/README.md)
and model revision above identify the tested interface. Earlier stored request
versions remain readable; do not rewrite historical evidence during an upgrade.
