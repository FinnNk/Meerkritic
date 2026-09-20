# Verify a local workflow

Use a disposable data directory to check that an installation works from source
input to reviewed output. Keep its commands, source revision, configuration and
results outside the repository. Never run failure experiments on live research data.

## Prepare

1. Check out the exact commit to verify in an isolated checkout.
2. Install with `uv sync --locked` and run `uv run --locked python tools/check.py`.
3. Choose a fresh external data directory and use it for every command and process.
4. Follow [local inference setup](local-inference.md) to verify/start the generation server.
5. [Register the public sample and serve it](../../README.md#browse-the-sample).
   Confirm that you can browse comments and code.

## Exercise the workflows

| Step | Action | Expected observation |
| --- | --- | --- |
| 1 | Submit normalisation while the worker is stopped, then run a worker with `--once`. | HTTP queues promptly; the worker later records output or an inspectable failure. |
| 2 | Inspect a successful result. | Source, structured interpretation, quotes, model usage and framework observation are available. |
| 3 | Accept, Edit and Reject separate successful results. Label automated decisions as test decisions. | Original output stays unchanged; edits and decisions remain after restart. |
| 4 | Freeze explicit test annotations using the [selection guide](selections.md). | Included/excluded records and exact chosen versions are inspectable. |
| 5 | Start the embedding server and [discovery worker](discovery.md), then embed and group. | Ordered vectors, groups, representatives and outliers retain source references. |
| 6 | [Request a candidate rule](rules.md). | A proposed rule or a valid insufficient-evidence result is retained with the model trace. |
| 7 | [Save and apply a decision draft](research-interaction.md). | Saving changes no rule decision; applying records the batch and history. |
| 8 | Send explicitly selected discussion as guidance. | The response is advisory and leaves rule definitions/decisions unchanged. |
| 9 | [Publish an architecture view](../architecture/README.md). | It identifies saved source and warns when that source changes. |

Model output varies. Retain failed attempts; do not bypass validation merely to
obtain a successful example. If no valid rule is proposed, record that outcome and
which dependent checks could not run.

## Challenge failure and recovery

Perform these only in the disposable runtime:

- Use an unavailable loopback model endpoint for one request. Expect a provider
  failure, not automatic selection of a stronger model.
- Interrupt a worker after it claims a job. Restart after the process exits and
  confirm interruption/unknown completion, retained history and no automatic replay.
- Save a rule draft, change one target through another explicit operation, then
  apply the old draft. Expect no partial decisions and a retained conflict draft.
- Restart the web application and worker. Inspect decisions, events and progress.
- [Export usage](routing-operations.md#export-completed-usage) and query it with DuckDB.
  Unavailable counts must remain null.
- Inspect `job-log`, and run `index-artefacts` after an upgrade as described in
  [operational evidence](operational-evidence.md).

## Record the result

- Identify the exact code commit, lockfile, Python/platform and local model/server versions.
- Retain commands, configuration, source/model hashes, run/result IDs and actual outcomes.
- Record unrun steps and their reasons, partial failures and reproduction limits.
- Keep software-test decisions separate from human labels. Compatibility does not
  establish the quality of a model, prompt or grouping method.
- Use the [EDR process](../edr/README.md) before a significant comparative decision.

Windows/Python 3.12 is the tested platform. Synthetic hosted-price tests are not
billed hosted calls. A model file hash cannot attest which bytes another running
process loaded. No independent reproduction or hosted CI execution follows from
these instructions alone; report only what was actually checked.
