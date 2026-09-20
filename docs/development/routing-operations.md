# Inspect routing without invoking a model

Run from the repository root after `uv sync --locked`. The supplied inventory and task are synthetic. Preview performs no provider calls or database writes:

```text
uv run --locked python tools/route.py preview --config config/routing/example.json --task config/routing/task-example.json
```

The example rejects the remote primary for local-only input and selects the local candidate. JSON includes policy/inventory versions, rejected alternatives and context limits. Exit codes are 0 for selection, 2 for an explained refusal and 1 for invalid configuration/storage input. `--model` chooses once without bypassing constraints; `--policy-id` and `--policy-version` must be supplied together.

Record a decision in external runtime storage, then inspect its returned ID:

```text
uv run --locked python tools/route.py record --config config/routing/example.json --task config/routing/task-example.json --data-root ../extras/data/routing-example
uv run --locked python tools/route.py inspect --data-root ../extras/data/routing-example DECISION_ID
```

`record` commits provenance without model execution or fabricated usage. `inspect` returns `usage: null` until an application caller records completion through `RoutingService.complete`. Keep real configuration, observations and runtime data outside source control. Locality and availability claims require operational preflight before execution.

Export completed history to a new immutable Parquet file:

```text
uv run --locked python tools/route.py export-usage --data-root ../extras/data/routing-example --output ../extras/data/routing-example/history-001.parquet
```

Empty history produces typed, empty Parquet. Existing files are never overwritten. Snapshots include successful and failed invocations, nullable tokens, elapsed time, exact decimal spend as text, full decision/usage JSON and retained inventory/policy/price snapshots. DuckDB can query these independently; cast spend to the analysis's required decimal precision. Export copies records without deleting SQLite history; automatic retention is deferred. Runtime paths must be outside Git worktrees.

See the [routing contracts](routing.md), [live normalisation](normalisation.md) and
[annotation guide](annotations.md). The inspection commands remain useful independently
of the delivered VS1 worker and UI.
