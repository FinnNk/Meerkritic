# Reproducible discovery

Start with **Frozen inputs** in the harness. A selection names exact annotation
versions, preserves edits and labels exclusions. **Queue embeddings** submits work;
it never calls a model in the HTTP request. Inspect the run, then choose a cosine
threshold and minimum group size to **Queue clustering**. The result shows every
member, representative and outlier, linked to its original source and annotation.

The current cosine connected-component algorithm is an exploratory prototype,
version `cosine-components-v1`. Edges include equality at the chosen threshold;
transitive chains may join examples that are not pairwise similar. Small components
are outliers (`-1`). Representatives maximise within-component cosine sum, with
ties resolved by frozen input order. No seed is used. These are reproducibility
rules, not a claim of semantic coherence or superiority. EDR-0001 (Choose an initial
discovery grouping method) remains draft; human evaluation and adoption are pending.

## Local worker

Use an external runtime directory and the existing locked environment. Start the
pinned llama.cpp embedding server separately, bound to `127.0.0.1:8082`, using
`--embedding --pooling mean --ctx-size 2048 --batch-size 2048 --ubatch-size 2048`.
The compatibility fixture uses CPU execution (`--n-gpu-layers 0`). Keep the existing
normalisation server on port 8081. Use the model file named in the profile:

```powershell
uv run --locked python tools/run.py --data-root ../extras/runtime worker `
  --routing config/routing/discovery-local.json `
  --embedding-endpoint http://127.0.0.1:8082 `
  --embedding-profile config/models/nomic-embedding-fixture.json `
  --embedding-model ../extras/preflight/vs2-embedding/nomic-embed-text-v1.5.f16.gguf
```

Stop the old worker before starting this one. Both queues use the same exclusive
process lock and alternate to avoid starvation. A second worker cannot recover or
claim work while the first owns the lock. On restart, unfinished calls fail with
unknown external completion; nothing automatically replays. Normalisation-only
worker invocations remain supported and leave discovery jobs queued.

Equivalent explicit submission/inspection commands:

```text
python tools/run.py --data-root <external-runtime> embed <selection-sha256>
python tools/run.py --data-root <external-runtime> cluster <embedding-run-id> --threshold 0.85
python tools/run.py --data-root <external-runtime> discovery <run-id>
```

The threshold above is an example, not an adopted default. Changing the selection,
model profile, preprocessing or parameters creates a separate invocation. Results
do not overwrite earlier runs. A rerun may have different model vectors; only the
deterministic grouping of the same pinned vectors/parameters has a replay claim.

## Evidence and limits

Each run retains its exact request, selection, inventory/policy versions, model
profile, preprocessing, usage, framework observation and result hashes. Texts and
vectors are ordered Parquet rows; memberships are another immutable Parquet file.
SQLite holds small queue metadata and append-only events. JSON manifests, raw
invalid embedding responses and analytical bodies remain outside source control.
Files publish completely before terminal state; interrupted registration can leave
a complete orphan file, which is not a successful run.

The selected model file is SHA-256 checked. The server API verifies alias,
dimensions and context; it cannot prove the hash of the server's loaded bytes.
The operator must launch the verified file. No source goes to a hostname, remote
address, proxy or redirect through the supplied adapter. Inputs are bounded at
100 eligible records, 12,000 characters per text and the actual token budget; no
silent truncation occurs. Request preparation combines issue, invariant and coarse
categories. The model-specific clustering prefix belongs to the deployment profile.

Unknown provider token counts remain null. Embeddings generate zero output tokens;
known input tokens accumulate over completed calls. Live API spend is local, with
no electricity/hardware estimate. Provider failure, invalid vectors and routing
refusal are distinct; a failed run cannot supply a clustering input.

Compatibility on 20 September 2026 used llama.cpp `b10964-b29c606e2`, the pinned
Nomic F16 model and the project's locked MAF runtime. Real MAF execution produced
768-dimensional vectors and a cluster from synthetic interpretations. Automated
fixture decisions are not human research labels. Canonical method/log/result
references are in external DER `vs2-grouping/r1`; this is not an empirical EDR run.

## Sources

- [Pinned llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/blob/b10964/tools/server/README.md)
  defines the embedding endpoint and pooling requirement.
- [Nomic's model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
  specifies task prefixes; the compatibility profile retains full dimensionality.
- [Pinned GGUF distribution](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/tree/0188c9bf409793f810680a5a431e7b899c46104c)
  supplies the Apache-2.0 F16 file. Its exact digest and revision are in the profile.
