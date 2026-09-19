# State, handoff and evidence

## Identity

Use an explicit evidence store outside the application worktrees. Each pair has stable
`pair_id`; each publication attempt/review has a distinct `round_id`, immutable bases
and tips, tree IDs and proposition map. Record method/skill versions and the client,
model, CLI version and session that produced each observation. Never infer an active
pair from a mutable branch alone. Local “latest” summaries are caches, not evidence.

The snapshot manifest is a mechanical snapshot, not proof that tests/review/publication
occurred. Its `stage` is deliberately `archived_candidate`. Publication, approval and
integration are separate events. See schemas and helper-usage.md.

## Records

Record facts when observed: scope, requirements, what-matters map, diary milestones,
boundary alternatives, test dispositions, command/check outputs, review findings,
revision comparisons and final integration. Reference raw artefacts by path/hash.
Records are append-only. A later correction is a new event, not a retroactive edit.

The helper `record` serialises writes with a local exclusive lock and requires the
expected previous event hash. It provides integrity/concurrency checks for cooperating
writers, not signatures or a tamper-proof audit system. Protect and back up the store.
Its lock is not a Git lock: one designated history integrator must still control branch
reconstruction across clients. Do not automatically remove a stale lock after a crash;
inspect active processes, check the last durable event and recover with human authority.
Use local filesystems with reliable locking, not an assumed atomic network share.

## Resume and handoff

Create a concise packet using assets/handoff.md. Include exact round/manifest digest,
current stage, completed checks and evidence, current findings, cursor keyed to commit
SHAs, next operation, blockers and authority still required. Do not export hidden
reasoning, chat transcripts, tokens or credentials merely to transfer progress.

On receipt, verify manifests/objects, compare current refs with recorded identities,
validate review scope and re-read only the active workflow. A new round requires an
explicit review-scope decision; do not carry approval or a numeric cursor forward
silently. Same client/model in a new session is a new observation source.

## Collect and export

`evidence collect` gathers available evidence; it does not fabricate missing baseline
runs or chronology. `evidence export` copies only authorised material with checksums,
source identifiers and a limitations statement. A locally generated Git bundle is not
yet a replicated durable archive and may contain sensitive ancestral history.

For a later case study, distinguish final diff size from per-commit churn; static
fragmentation from observed navigation; current tests from archive-only tests; method
hypotheses from demonstrated outcomes. Retain adverse and null findings. Preparation
and re-review effort count, not only reviewer execution.
