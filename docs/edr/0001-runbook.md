# Run the registered EDR-0001 comparison

This runbook fixes the commands for the [study plan](0001-discovery-grouping-method.md).
Run only after its two registration commits exist. The local paths below identify
the retained evidence; another researcher needs permitted access to that bundle.
Changing paths is harmless; changing inputs, implementation or parameters requires
a recorded prospective amendment.

## Prepare the environment

- Check out the registration branch/commit and run `uv sync --locked`.
- Verify the selection and model hashes against
  [the registration inventory](evidence/0001-registration.json).
- Keep the original evidence read-only when reproducing. Use a separate copy of
  the runtime and a fresh comparison directory; do not overwrite original runs.
- Start the pinned server with the settings below. Loading is measured separately
  from method execution. The original run retains its startup log.

```powershell
$study = 'D:/codex/semantic-reviewer/extras/research/edr-0001'
$data = "$study/runtime"
$evidence = "$study/comparison"
$python = '.venv/Scripts/python.exe'
$model = 'D:/codex/semantic-reviewer/extras/preflight/vs2-embedding/nomic-embed-text-v1.5.f16.gguf'
$server = 'D:/codex/semantic-reviewer/extras/preflight/vs1-inference/llama-b10964-cuda12/llama-server.exe'
$selection = 'f5bc84b772da601d3a068e42cdbb77799e887628773084aa9fe9b32ca1fabdd7'
# Set to the full SHA of the second registration commit, not the completed-plan SHA.
$registration = '<registration commit SHA>'
& $server --model $model --alias nomic-embed-v1.5-local --host 127.0.0.1 --port 8082 --embedding --pooling mean --ctx-size 2048 --batch-size 2048 --ubatch-size 2048 --n-gpu-layers 0 --threads 8 --no-webui
```

Run the server in a separate terminal or hidden background process; retain stdout,
stderr and the launch command. Use the exact profile and routing configuration in
the registered checkout. No normalisation model call is needed for this comparison.

## Execute once per method

| Step | Command/action | Record |
| --- | --- | --- |
| Baseline | Run the first command below | Baseline digest and log |
| Embeddings | Queue the selection and run one worker | Returned embedding ID and worker log |
| Groups | Queue clustering for that ID and run one worker | Returned clustering ID and worker log |
| Attempts | Write the attempt file | Every attempt, including failures; do not omit them |
| Pack | Run the pack command | Returned comparison, pack, template and private mapping digests |

```powershell
& $python tools/study_compare.py --data-root $data --evidence $evidence --registration-commit $registration baseline $selection
& $python tools/run.py --data-root $data embed $selection
& $python tools/run.py --data-root $data worker --routing config/routing/discovery-local.json --endpoint http://127.0.0.1:8081 --embedding-endpoint http://127.0.0.1:8082 --embedding-profile config/models/nomic-embedding-fixture.json --embedding-model $model --once
# Substitute the ID returned by embed, without rerunning embed.
& $python tools/run.py --data-root $data cluster '<embedding run ID>' --threshold 0.85 --minimum-size 2
& $python tools/run.py --data-root $data worker --routing config/routing/discovery-local.json --endpoint http://127.0.0.1:8081 --embedding-endpoint http://127.0.0.1:8082 --embedding-profile config/models/nomic-embedding-fixture.json --embedding-model $model --once
```

Set `candidate-attempts.json` to an array containing the actual `embedding_run` and
`cluster_run` IDs. Failed embeddings have no invented clustering ID. The
[comparison guide](../development/study-comparison.md) specifies the one permitted
technical retry and its diagnosis. Stop execution at the registered 30-minute
cap per method; the CLI checks timings but does not supervise that cap itself.

```powershell
& $python tools/study_compare.py --data-root $data --evidence $evidence --registration-commit $registration pack '<baseline digest>' --attempts "$study/candidate-attempts.json" --profile config/models/nomic-embedding-fixture.json
```

## Hand off human ratings

- Check the pack's status before requesting ratings. If fewer than eight groups
  per method are available, record primary insufficiency and stop for the owner's
  decision; do not change thresholds or manufacture ratings.
- Otherwise give Finn Newick only the masked pack and a copy of its blank rating
  template. Keep method identities and comparative outputs separate until all
  ratings are complete. The rubric is included in the pack and study plan.
- Retain the submitted human ratings, then run `analyse` as documented in the
  [comparison guide](../development/study-comparison.md#give-the-human-reviewer-only-the-masked-pack).
- Record results, deviations and limitations in the EDR. A recommendation does
  not authorise adoption; record the owner's decision separately.

## Verification and reproduction limits

The original preflight ran `.venv/Scripts/python.exe tools/check.py`: Ruff format,
Ruff lint, Import Linter, Tach and 259 tests passed. The environment was already
installed from the repository lock. Synthetic MAF embedding compatibility also
passed; detailed versions, identities and evidence hashes are in the inventory.

The selection, public-source receipts and human-edited interpretation bodies are
retained locally. The committed inventory contains identities and hashes, not
their text. Replaying the exact comparison requires permitted access to those
artefacts; re-labelling the public records would be a separate replication.
