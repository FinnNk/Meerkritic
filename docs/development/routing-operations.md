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
