# Operational evidence

Runtime evidence stays outside Git. SQLite's `artefact` catalogue stores job,
kind, content hash, absolute path, byte size and publication time; bodies remain
immutable filesystem JSON. Normalisation and human edits are registered before
their references are committed. Files can be orphaned by a partial failure;
retain them for diagnosis rather than assuming they were accepted results.

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
