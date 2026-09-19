# Verify without conflating assurances

`verify` defaults to `all`. Modes: `equivalence`, `checkpoints`, `tip`, `all`.

## Equivalence

Resolve each supplied ref to a full commit SHA and record it. The two snapshots must
belong to the same round. Run the helper's `equivalence` with both bases when available.
Its tree check and direct diff cover all tracked content. A successful result does
not verify tests, chronology, external state, approval or integration.

A diary ahead of the current published semantic round is normal pending work. Compare
the frozen pair, not moving tips. In a stack verify every predecessor and every pair.
LFS payloads, submodule contents beyond gitlinks, generated untracked files, services,
configuration and dependencies need separate checks when material.

## Checkpoints

Before execution, derive the required-context matrix from repository policy and the
change's risks. Include relevant operating systems, language/runtime versions, locked
dependencies, build modes, synthetic pull-request merges and other platform contexts.
Do not invent a universal matrix, but do not omit a declared required context.

Use clean isolated checkouts of every semantic commit. Each checkout must supply that
checkpoint's source, tests and dependency lock. Verify the package or executable loaded
by the command came from that checkout; a controller checkout, later editable install,
shared build output or ambient dependency state must not supply newer code. Record
actual argv, environment and installed-package identity, commit/tree, clean status,
timestamps, exit status, required context and evidence paths. Tests execute repository
code: require execution authority and an appropriate sandbox/container without
publication credentials. Record an attempt that loads source/package material from the
wrong checkpoint as `failed` for identity contamination; the intended exact checkpoint
context remains `not_run` until a clean rerun completes it.

The helper intentionally does not execute profile-supplied tests. An approved runner
or agent follows this procedure; profile command strings are not implicit permission.
Record unsupported environments, pre-existing failures and unrun checks explicitly.
Diagnose flakes; do not rerun until green and discard failures.

A negative control passes only when it reaches and fails at the intended assertion.
A fixture, checkout, dependency or infrastructure failure is a failed control, not
proof of the property. Preserve stderr and the diagnostic path needed to tell them
apart. POSIX mode checks require a context that preserves and exercises Git modes.

Checkpoint evidence is complete only when every required context has a passing result
for that exact checkpoint identity. Failed, missing, stale, skipped and partial results
remain incomplete. Later tip evidence, tree equality or a result for another SHA/run
attempt cannot be carried backwards. After a defect, preserve the failed round, repair
through the diary, freeze/reconstruct and rerun the affected checkpoint-context matrix.

## Tip

Run the full risk-proportionate suite on the exact final semantic and diary results
as agreed. Equal trees do not prove equal external environment. Inspect the aggregate
diff, incoming commit list and ancestry for diary/archival contamination.
`git diff --check` is useful but not a behavioural validator.

## Result

Report equivalence, checkpoint checks, final-tip checks, and external-state checks
separately as passed/failed/not_run/blocked/partial. Identify the exact head, base,
context and hosted run attempt for each result. A partial rerun does not replace a
complete failed attempt. Link raw logs instead of dumping all output into the model
context. Do not certify final approval or integration here. When a check exposes a
defect, report it and return changes through the diary.
