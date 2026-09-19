# Setup, diary work and overall preparation

## Preconditions

Use an explicit repository and bounded objective. Preserve unrelated edits. Confirm
branch names, bases, required verification contexts, commands, evidence location,
routine-repair policy and remote authority. Record the source method revision and skill
version. Do not change repository policy. If a profile is missing, propose the smallest
profile needed; do not guess risky commands. Local evidence writing is separate from
application editing.

## Prepare

`prepare --until locally-prepared` orchestrates these existing operations, loading each
procedure only when reached: inspect/setup → authorised `work` if required → assess
test evidence → diary verification/freeze → `plan` → `reconstruct` → `verify all` →
`round prepare`. Stop before publication or hosted qualification. The deprecated
`review-ready` spelling is an alias for this same local boundary. A user can instead
invoke any stage directly. An existing verified result need not be reimplemented.
Do not repeatedly request permission already supplied for the same scope; do not broaden
that scope yourself.

If the user asks to adopt an existing PR without a diary, preserve the actual history
as imported provenance. Label missing chronological evidence and imported milestones.
Do not invent test-first events or claim the workflow governed earlier development.
Stop for an adoption decision before mutating shared branches.

## Work

1. Establish baseline commit/tree and representative verification; record known failures.
2. Work on the diary or a bounded contributor branch integrated into it. Use separate
   worktrees where another client/agent is active. One integrator owns paired history.
3. Record meaningful discoveries, implementations, corrections and decisions in actual
   order. Do not create a commit for every edit or force a particular test-writing order.
4. Develop coherent abstractions and relevant contracts. Use a failing reproducer when
   useful; record observations rather than manufacture them later.
5. Assess test purpose before freezing: retain useful obligations, consolidate superseded
   checks and retire obsolete diagnostics on the diary with reasons. See test-evidence.
   When an observed defect has a routine repair already covered by repository policy
   and current authority, retain the failure and apply that repair diary-first. Stop for
   a new contract, scope or authority decision, an independent defect, or work beyond
   agreed repair bounds. Routine repair permission does not authorise a remote action.
6. Verify the diary from an isolated clean state; record the exact SHA/tree, environment,
   commands and results. Do not count a green dirty worktree as a verified checkpoint.
7. Freeze the diary SHA for reconstruction. Do not freeze unresolved unexplained changes.

“Freeze” means a recorded immutable commit reference and retained objects, not a Git
lock on a moving branch. Further diary work is allowed but belongs to a later snapshot.

## Completion

Return objective, base(s), diary tip/tree, baseline/current verification, assumptions
and test dispositions, the locally prepared state and outstanding hosted contexts.
No push, PR creation, review request or merge occurs merely because local work is complete.
