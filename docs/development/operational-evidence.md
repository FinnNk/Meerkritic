# Operational evidence

Runtime evidence stays outside Git. SQLite's `artefact` catalogue stores job,
kind, content hash, absolute path, byte size and publication time; bodies remain
immutable filesystem JSON. Normalisation and human edits are registered before
their references are committed. Files can be orphaned by a partial failure;
retain them for diagnosis rather than assuming they were accepted results.

Publication supplies a separate `Publication(job_id, kind)` contract; JSON keys
never select catalogue behaviour. The catalogue is always present in the runtime
store. An explicit `ArtefactIndex` maintenance interface indexes old result/edit
references using their relational owners and kinds, preserving original bytes and
hashes. Existing schema-version-1 bundles remain readable; no payload rewrite or
type inference is needed. Conflicting metadata still fails rather than overwriting
evidence. See [ADR-0008](../adr/ADR-0008-own-artefact-publication-metadata.md).

Each committed queue/start/route/completion/recovery transition produces a new
structured job-log snapshot under `logs/`. It includes event sequence, timestamp,
job identity, level, event and small operational details. Logs omit source/prompt
bodies and derive from committed events, so they do not compete with event history.
The `job_log` table points at the latest snapshot and event; older snapshots remain
immutable. Filesystem work happens after the short state transaction. A log disk
failure emits a warning and cannot roll back or disguise a committed transition.

After upgrading a runtime, run `uv run --locked python tools/run.py --data-root
<external-directory> index-artefacts` to verify and index existing referenced
results and edits. A corrupted file fails verification. Regenerate or inspect a
job's current structured log with `job-log <job-id>` using the same command prefix.
This reports its verified artefact path and checksum. These are basic lifecycle
logs; detailed model request/response evidence remains in the result bundle.
Catalogue paths bind this runtime to its configured location. Moving a populated
runtime requires a deliberate migration; conflicting paths for an existing hash
are rejected rather than silently recorded as successful indexing.

## DER references

Run `index-review <manifest.json> <event.json>` with the same CLI prefix to index
an explicit canonical DER readiness event. Both files must live outside Git
worktrees. The event must identify the same pair, round and exact diary/semantic
heads as the manifest, with a positive sequence and recognised readiness stage.
The index stores only paths, identities, stage and hashes. Re-indexing the same
record is idempotent; changed evidence cannot replace its old identity. A later
event advances the displayed reference without deleting earlier records.

Open **Change review references** in the harness. It rechecks file hashes and flags
changed or unavailable evidence. Status is an assertion from the last explicitly
indexed event, not a live subscription: later external events require re-indexing.
The index does not verify the DER ledger chain or Git bundle, approve a change,
infer readiness from branch names, or claim slice completion. Use the pinned DER
helpers and review process for qualification before indexing its result. Canonical
evidence remains authoritative; no file paths supplied over HTTP are opened.
