# Normalisation workflow

See the [interpretation contract](normalisation-contract.md) for schema, evidence and MAF boundaries.

## Run locally

First follow [local inference](local-inference.md) to start the verified llama.cpp
fixture with alias `qwen3-4b-local` and a 4,096-token context. From the repository:

```sh
uv run --locked python tools/run.py --data-root ../extras/runtime worker --routing config/routing/llama-local.json
```

The supplied routing file is an explicitly identified compatibility fixture, not a
claim that this model is best. Use a new inventory/policy version for changed content.
The worker enforces local-only input and literal-loopback inference. A hosted-only
route fails closed. 

For a one-job CLI invocation:

```sh
uv run --locked python tools/run.py --data-root ../extras/runtime normalise crc-py-manual-4176ac0 0
uv run --locked python tools/run.py --data-root ../extras/runtime worker --routing config/routing/llama-local.json --once
uv run --locked python tools/run.py --data-root ../extras/runtime jobs
```

`source_index` is zero-based. Each explicit submission creates a new invocation;
refreshing a redirected result page does not resubmit it. A repeated button press can.

## Persistence and recovery

Use the same **local-disk** data root for server and worker. The worker owns an OS
process lock for its lifetime; a second process refuses to start. Queue claims use
short SQLite WAL transactions and a single-running-job constraint. A background
heartbeat refreshes every five seconds; overdue means inspect, not retry.

On restart, obtaining the OS lock establishes that the previous cooperating worker
no longer owns this root. Previously running jobs become failed with an interruption
event. They are never automatically retried. Inspect any recorded route, usage and
artefacts before submitting again: the provider may have finished before the crash.
A hung live worker retains its lock and must be stopped by the operator before recovery.
See [ADR-0006](../adr/ADR-0006-recover-jobs-under-process-lock.md).

Complete result bundles live at `results/<sha256>.json`, published atomically before
SQLite references them. SQLite contains job metadata and references, not prompt or
result bodies. Files can be orphaned if a later database write fails. They are retained
for inspection. Checksums are verified on read; a damaged result returns an explicit
error. SQLite events accompany queue/start/route/completion/interruption transitions;
heartbeats do not flood the event stream. This remains operational history, not event sourcing.

Completed usage can use the existing [routing export](routing-operations.md) for Parquet/DuckDB.
No network queue, distributed worker or full MAF durable runtime is introduced.
