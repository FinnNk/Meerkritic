# Group similar review concerns

Discovery compares the interpretations in a [saved selection](selections.md).
It first converts their text into numerical representations called *embeddings*,
then groups sufficiently similar representations. Open any group to inspect its
members and original evidence; similarity alone does not establish a shared rule.

## Prepare the embedding server

You need the locked Python environment, a saved selection with included records,
and the llama.cpp executable from [local inference setup](local-inference.md).
Keep the generation server on port 8081 for normalisation, synthesis and guidance.

1. Download `nomic-embed-text-v1.5.f16.gguf` from the
   [pinned Nomic distribution](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/tree/0188c9bf409793f810680a5a431e7b899c46104c).
   Save it outside Git, for example `../extras/models/nomic-embed-text-v1.5.f16.gguf`.
2. In PowerShell, run `Get-FileHash <model-file> -Algorithm SHA256` and compare with
   `sha256` in `config/models/nomic-embedding-fixture.json`.
3. Start a separate server from the repository root. Adjust the executable/model paths:

   ```powershell
   & ../extras/llama/llama-server.exe `
     --model ../extras/models/nomic-embed-text-v1.5.f16.gguf `
     --alias nomic-embed-v1.5-local --host 127.0.0.1 --port 8082 `
     --embedding --pooling mean --ctx-size 2048 `
     --batch-size 2048 --ubatch-size 2048 --n-gpu-layers 0
   ```

4. Keep it running and check `Invoke-RestMethod http://127.0.0.1:8082/health`.
   This tested setup uses CPU execution and 768-dimensional vectors.

The worker checks the model file's digest and the server's alias, dimensions and
context. The server API cannot prove the hash of its loaded bytes; launch the
verified file yourself. The profile retains Nomic's `clustering: ` input prefix.

## Start the worker

Stop any previous worker using the same data directory. Run from the repository
root in PowerShell after `uv sync --locked`:

```powershell
uv run --locked python tools/run.py --data-root ../extras/runtime worker `
  --routing config/routing/discovery-local.json `
  --endpoint http://127.0.0.1:8081 `
  --embedding-endpoint http://127.0.0.1:8082 `
  --embedding-profile config/models/nomic-embedding-fixture.json `
  --embedding-model ../extras/models/nomic-embed-text-v1.5.f16.gguf
```

This one worker handles normalisation, discovery (including synthesis) and guidance.
It takes turns between available work types. A second worker cannot claim or recover
work while the first owns the data directory's process lock.

## Embed and group a selection

1. Open **Frozen annotation inputs** and choose the selection.
2. Choose **Queue embeddings**, then inspect the resulting run.
3. After embeddings succeed, enter a cosine threshold and minimum group size and
   choose **Queue clustering**. The threshold controls which vector pairs count as similar.
4. Inspect each group's members, representative and outliers. Follow source links
   before deciding whether a group expresses a useful shared concern.
5. To propose a reusable check, continue with [candidate rules](rules.md).

Equivalent commands print a run ID or a run's stored request/result:

```text
uv run --locked python tools/run.py --data-root ../extras/runtime embed <selection-id>
uv run --locked python tools/run.py --data-root ../extras/runtime cluster <embedding-run-id> --threshold 0.85 --minimum-size 2
uv run --locked python tools/run.py --data-root ../extras/runtime discovery <run-id>
```

The threshold `0.85` is an example, not an adopted research default.

## How grouping works

| Choice | Current behaviour |
| --- | --- |
| Algorithm | `cosine-components-v1`, an exploratory connected-component method |
| Pair connection | Cosine similarity meets or exceeds the supplied threshold |
| Group membership | Transitive connections join a group; not every pair need be similar |
| Outlier | A component smaller than the minimum group size, labelled `-1` |
| Representative | Member with the greatest summed within-group similarity; ties use saved input order |
| Reproduction | Same vectors and parameters give the same grouping; new model calls may produce different vectors |

No random seed is used by grouping. Method adoption still needs a registered
comparison under the [EDR process](../edr/README.md); this prototype does not establish
semantic coherence or superiority.

## Limits and troubleshooting

| Condition | Meaning and next action |
| --- | --- |
| Job remains queued | Check worker configuration and data directory. A normalisation-only worker leaves discovery jobs queued. |
| Embedding run fails | Read its error/retained response. Failed embeddings cannot feed clustering. |
| Input exceeds a limit | Reduce the selection: at most 100 included records, 12,000 characters per text and the actual token budget. Input is not truncated. |
| Worker interrupted | Completion may be unknown; inspect stored evidence before a new explicit request. Restart never automatically repeats the call. |
| File exists without a completed run | It may be an unreferenced file from interrupted registration, not a successful result. Preserve it for diagnosis. |

Each run retains its request, selection, model/profile, input preparation, routing
versions, usage and framework observation. Texts, vectors and memberships are
ordered Parquet files; JSON manifests and invalid raw responses remain external.
SQLite stores queue metadata and events. Unknown token counts remain unknown;
embeddings have zero generated output tokens. Local spend excludes hardware costs.

Sources: [pinned server API](https://github.com/ggml-org/llama.cpp/blob/b10964/tools/server/README.md)
and [Nomic model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5).
