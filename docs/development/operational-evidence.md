# Inspect stored outputs and logs

The runtime retains outputs and history outside Git. Use these records to understand
what happened, investigate a failure or reproduce a result. A file's presence alone
does not prove that the corresponding operation completed successfully.

## Find the right record

| Record | Contains | Authority or limit |
| --- | --- | --- |
| Result/edit JSON | Immutable normalisation output or human edit, identified by checksum | Read through the application to verify its bytes. |
| Preserved source context | Exact retrieved response and receipt, bound to a job | Stored under `source-context/`; new annotations record which digest was presented. Back up these files with the database. See [source views](preserved-source.md). |
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
