exec(compile(open('WORKSPACE/extras/der-evidence/vs2-interaction/r2/write_tasks.py',encoding='utf-8-sig').read().split("write('README.md'")[0],'<helpers>','exec'))
write('docs/development/local-inference.md',r'''
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
''')
write('docs/development/discovery.md',r'''
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
''')
write('docs/development/rules.md',r'''
# Inspect and challenge candidate rules

A rule candidate describes a concern that might become a reusable code check.
Its evidence is inspectable, but proposing or promoting it does not prove that
it generalises or deploy a detector.

## Propose a candidate

You need a successful [clustering run and discovery-enabled worker](discovery.md).

1. Open a group and choose **Queue rule synthesis for this group**.
2. Wait for the worker, then inspect the result. It may propose a rule or explain
   that the supplied examples are insufficient; both are legitimate outcomes.
3. Open the candidate in **Rule registry**. Read its statement, scope, applicability,
   violation definition and exclusions.
4. Follow evidence links back to the original observations and interpretations.
   The model sees the representative and up to five other included examples, not
   necessarily the whole group. Its trace identifies exactly what was supplied.

The synthesis trace retains the prompt, schema, model selection, usage, framework
observation and raw output. Invalid JSON or invented support is refused and retained
for inspection. A provider failure is reported separately from invalid model output.

## Challenge and decide

| Action | Effect and responsibility |
| --- | --- |
| Add evidence | Choose positive, counterexample, false-positive, false-negative or unresolved evidence from the same saved selection. |
| Mark evidence verified | Attest that classification for this exact rule version with your name and rationale. A source match alone does not establish validity. |
| Promote | Retain a reviewed research candidate. This does not validate, enforce or deploy it. |
| Reject | Record why the current candidate should not be retained. |
| Revise | Create a new definition version; keep the original and its decisions. |
| Stage several actions | Use the [review workspace](research-interaction.md) to save a draft and apply it explicitly. |

Repository holdouts remain excluded. Rejected interpretations can supply weak
(unverified) evidence; rejection does not establish a verified negative example.
A false positive is a reported violation judged incorrect; a false negative is a
missed violation. State why the classification applies to this rule.

When revising:

- Evidence classifications carry forward with parent links and **weak** status.
  Reassess verification against the changed definition.
- Counterexamples cannot be silently discarded. Each version has a 1,000-link limit;
  a revision exceeding it is refused without changing the current version.
- Changes made after you prepared a decision cause a conflict. Submitted values
  remain available for correction; identical decision retries return the original.
- Reopen an answered or deferred rule review before another decision.

## Inspect failures and usage

| Condition | Next action |
| --- | --- |
| Insufficient evidence | Inspect the explanation; a successful run may produce no candidate. |
| Context too large | Reduce selected material. Synthesis permits six examples and 12,000 characters; the model's actual token budget is checked too. |
| Invalid output or references | Inspect the retained raw output and supplied IDs; no candidate is accepted from invalid support. |
| Interrupted job | Check the registry and original trace before submitting again: a complete candidate may exist even if final job registration failed. |
| Unknown token count | Treat it as unavailable, not zero. Running telemetry refreshes every five seconds. |

Recovery never automatically repeats the call or selects a stronger model. Current
routing configuration is `config/routing/discovery-local.json`; older policy versions
remain available to interpret stored runs. Model controls stay outside rule logic.

## Command-line equivalents

Run from the repository root using the same data directory as the web application.
Copy a cluster run ID/group number from discovery, or a version ID from the rule page.

```text
uv run --locked python tools/run.py --data-root ../extras/runtime synthesise <cluster-run-id> <group-number>
uv run --locked python tools/run.py --data-root ../extras/runtime discovery <run-id>
uv run --locked python tools/run.py --data-root ../extras/runtime rules
uv run --locked python tools/run.py --data-root ../extras/runtime rule <version-id>
```

The first command queues work. The others inspect runs, the registry or a specific
version. Test selections and automated decisions remain test data; significant
method choices follow the [empirical decision process](../edr/README.md).
''')
write('docs/development/datasets.md',r'''
# Register and browse the public sample

The supplied dataset pairs review comments with code context. Registration downloads
its pinned source, checks the bytes and creates a Parquet copy for browsing.

## Register and inspect

Run from the repository root after `uv sync --locked`. Use a local-disk data directory
outside every Git worktree; the same directory must be used by the server and worker.

1. List available dataset manifests:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime catalogue
   ```

2. Register the public sample:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime register crc-py-manual-4176ac0
   ```

3. [Start the web application](../../README.md#browse-the-sample) and select the dataset.
   Expect 1,030 records. Repeating registration returns its existing record without
   adding another registration event.
4. For read API details, open `/docs` on the running server. Observation pages use
   `/api/datasets/{id}/observations?page=1&page_size=20`, with page sizes capped at 100.

Importing runs in the command-line process, outside web requests. Browsing queries
Parquet through DuckDB and verifies its checksum first.

## Understand the sample

| Property | Value or interpretation |
| --- | --- |
| Source | [CRC-Py](https://github.com/busraicoz/crc-py-dataset), revision `4176ac0013136ae3c8283fcdaf087d27159050cf` |
| File | `data/manual/manual_labeled_data.json`, 2,517,473 bytes |
| Licence | [Upstream MIT notice](https://github.com/busraicoz/crc-py-dataset/blob/4176ac0013136ae3c8283fcdaf087d27159050cf/LICENSE); inspect source terms before redistribution |
| Record identity | Source SHA-256 plus zero-based record index; repeated comment IDs remain distinct records |
| Missing information | Thirty records lack enriched context; it becomes null in Parquet. Commit SHAs are unavailable and remain null. |
| Duplicate comment identities | Six repeat; all supplied records are retained. |
| Labels | Upstream categories, not verified ground truth |

The upstream pipeline preprocesses comments and code. Meerkritic preserves those
supplied values; it does not claim they are verbatim original GitHub comments.
The repository's language does not establish the language of every excerpt.
No upstream code is executed during registration.

The manifest retains source URL, revision and checksum. SQLite also records the
derived Parquet hash and schema version. Changes to import/schema logic or pinned
DuckDB can change derived bytes and require explicit versioning.

## Storage and recovery

| Situation | Action |
| --- | --- |
| Registration interrupted before metadata was saved | Retry registration. A complete unreferenced file may remain; keep it for diagnosis. |
| Derived Parquet file missing | Run registration again to rebuild it from verified source. |
| A checksummed file changed | Preserve it elsewhere for inspection before restoring verified bytes. Registration will not overwrite conflicting content. |
| Backup needed | Stop application/worker processes and back up the whole runtime, including SQLite WAL files if present. |
| Network-share runtime | Use a local filesystem with hard-link support, such as NTFS; network shares are not validated. |

Source and derived files live at `datasets/<sha256>.json` and `.parquet` under the
data directory. Small metadata and events live in `state.sqlite3`, using WAL mode
and short transactions. Files are published completely before registration metadata
and its event are saved together. Do not remove unreferenced files without an explicit
retention decision.

This small sample supports integration work; it is not an empirically selected
research population. Record prior data exposure and register decision-bearing
analysis through the [EDR process](../edr/README.md). Full-file checksum checks on
each browse request would need reassessment for a much larger dataset.
''')
write('docs/development/routing-operations.md',r'''
# Inspect model selection and export usage

Routing chooses an eligible model from a versioned configuration. These commands
let you inspect that choice without calling a model. Run from the repository root
after `uv sync --locked`; the supplied example uses synthetic model entries.

## Preview or record a choice

1. Preview the example:

   ```text
   uv run --locked python tools/route.py preview --config config/routing/example.json --task config/routing/task-example.json
   ```

   Expect the remote first choice to be rejected for local-only input and a local
   alternative to be selected. JSON explains the choice, rejected alternatives and limits.
2. To save the decision without executing it, use:

   ```text
   uv run --locked python tools/route.py record --config config/routing/example.json --task config/routing/task-example.json --data-root ../extras/routing-example
   ```

3. Copy its returned ID and inspect it:

   ```text
   uv run --locked python tools/route.py inspect --data-root ../extras/routing-example <decision-id>
   ```

   `usage: null` is expected until an application records completion. Recording a
   routing choice does not call the provider or create usage measurements.

| Option or result | Meaning |
| --- | --- |
| `--model` | Override the model for this invocation while retaining all constraints. |
| `--policy-id` and `--policy-version` | Supply together to select a policy version. |
| Exit 0 | A model was selected. |
| Exit 2 | Selection was refused; inspect the reasons. |
| Exit 1 | Configuration or storage input was invalid. |

The example does not configure a live endpoint or credentials. Verify availability
and privacy claims before running a model with a real configuration.

## Export completed usage

1. Choose the data directory used by actual completed jobs, and a **new** output filename:

   ```text
   uv run --locked python tools/route.py export-usage --data-root ../extras/runtime --output ../extras/runtime/history-001.parquet
   ```

2. Query the resulting Parquet file with DuckDB or another compatible tool.
3. Retain the file as a snapshot; use another filename for the next export.

| Export property | Behaviour |
| --- | --- |
| No completed history | Produce a typed, empty Parquet file. |
| Existing output | Refuse to overwrite it. |
| Outcomes | Include successful and failed invocations. |
| Missing measurements | Preserve null token/timing fields, not invented zeroes. |
| Spend | Exact decimal text; cast to the precision your analysis requires. |
| Reproduction | Retain full decision/usage JSON and inventory, policy and price snapshots. |
| SQLite history | Copy without deleting it; there is no automatic retention cleanup. |

Keep runtime paths outside Git worktrees. See the [routing reference](routing.md)
for selection/accounting contracts and [normalisation](normalisation.md) for model execution.
''')
write('docs/development/operational-evidence.md',r'''
# Inspect stored outputs and logs

The runtime retains outputs and history outside Git. Use these records to understand
what happened, investigate a failure or reproduce a result. A file's presence alone
does not prove that the corresponding operation completed successfully.

## Find the right record

| Record | Contains | Authority or limit |
| --- | --- | --- |
| Result/edit JSON | Immutable normalisation output or human edit, identified by checksum | Read through the application to verify its bytes. |
| Artefact catalogue | Job, kind, hash, path, size and publication time | Small SQLite metadata; not the body itself. |
| Operational events | Committed state changes | Append-only database history. |
| Job log snapshot | Event sequence, timestamps, job, level and small details | Derived from committed events; not a second history. |
| Discovery/guidance files | Saved input, model trace and result bodies | Their own manifests/registrations identify successful results. |
| Change-review reference | Path/hash and last indexed Double-Entry Review status | A reference to external review evidence, not approval. |

## Inspect a job log

Run from the repository root after `uv sync --locked`, using the application's data directory.
Copy the job ID from its page or the `jobs` command.

```text
uv run --locked python tools/run.py --data-root ../extras/runtime job-log <job-id>
```

The command generates or inspects the current structured log and returns its verified
path and checksum. Logs omit source/prompt bodies; detailed model requests and
responses remain in result bundles. Older snapshots under `logs/` remain immutable.

## Index existing results after an upgrade

1. Back up the runtime before maintenance.
2. Verify and index referenced normalisation results and edits:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime index-artefacts
   ```

3. Inspect any reported corruption or conflicting metadata before continuing.
   Do not rewrite stored JSON or rename checksummed files to make the command pass.

The catalogue uses relational job/kind ownership, not arbitrary JSON keys, to index
older results. Original bytes and hashes remain unchanged. Its absolute paths bind
a populated runtime to its location; moving it requires a deliberate migration.

## Show an external change-review status

Double-Entry Review (DER) retains a material change's implementation history,
review history and verification in a separate evidence store. The web application
can display a reference to a status explicitly recorded there.

1. Use the pinned DER helper/process to verify the canonical round and readiness event.
2. Choose its manifest and event JSON files outside application worktrees.
3. Index those exact files:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime index-review <manifest.json> <event.json>
   ```

4. Open **Change review references**. It rechecks the indexed file hashes and flags
   missing or changed evidence.
5. Re-index when a later external event should be shown. This is not a live subscription.

The event must match the manifest's pair, round and exact Git identities, and contain
a recognised status and positive sequence. Identical retries do not duplicate the
record; changed evidence cannot replace an old identity. Later events retain earlier
references. The index does not verify the ledger chain/bundle or grant approval.

## Handle partial failures

| Situation | Action or meaning |
| --- | --- |
| Complete output exists without a saved result reference | Retain it for diagnosis; file publication can precede a failed database write. |
| Log export fails after a job transition | Read the warning and regenerate the log. The committed job transition remains valid. |
| Referenced file is corrupt | Preserve it for inspection and restore trusted bytes; do not change its contents in place. |
| Catalogue path conflicts after moving data | Plan a runtime migration instead of forcing a new path into immutable metadata. |
| Review evidence is missing/stale | Restore the canonical files or explicitly index the later verified event. Do not infer readiness from a branch name. |

Files are published before references; operational metadata and its event are saved
together in short SQLite transactions. Logging happens afterwards and cannot undo
that committed transition. See [ADR-0008: Make artefact publication metadata explicit](../adr/ADR-0008-own-artefact-publication-metadata.md)
for the design rationale.
''')
