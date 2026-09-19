# Reconstruct a frozen result

## Preconditions

A recorded verified diary tip, exact base(s), plan and authority for local history
work. For a single pair use the same base commit. For a stack verify predecessor
base-tree equality; record the distinct predecessor SHAs. Preserve published heads
before any replacement. Use an isolated worktree and one history integrator.

## Procedure

1. Pin the frozen diary SHA and tree; do not work from a moving ref thereafter.
2. Create a separate semantic branch/worktree from its correct base. Rebase a copy
   of the diary or reassemble the frozen base-to-tip patch in coherent units. Never
   rewrite the evidence branch itself into the submission series.
3. Stage according to the proposition plan. Explain necessity and constraints rather
   than enumerate files. Use stable `Review-Unit` IDs where round mapping needs them.
4. Preserve the frozen content exactly at the final tip. That includes tracked tests,
   documentation, executable bits, symlinks, generated content and submodule pointers.
5. If the plan requires content correction, test retirement, renaming, consolidation
   or a missing test: stop. Record the proposal, change the diary under authority,
   verify/freeze it again, then reconstruct. Do not “compensate” on both branches.
6. Keep evidence available at meaningful intermediate contracts. Temporary tests
   introduced and retired within diary development need not appear in the semantic
   history if no semantic checkpoint needs them. A base-existing deletion remains
   a visible delivered change. Do not equate test co-change with adequacy.
7. Verify every clean intermediate checkout in every repository-required context and
   verify the final tip separately. Bind source, tests, locks and installed packages to
   each checkpoint. Compare the frozen pair using the equivalence helper. Inspect the
   incoming ancestry as well as the final diff.

## Completion

Return semantic base/tip/tree, ordered propositions and source diary mappings,
checkpoint verification, final equivalence and any limitations. This creates a
candidate, not a published/approved round. `round prepare` handles its evidence packet.

## Divergence / interruption

Preserve work. Identify missing/extra content with the direct diff; treat the verified
diary as canonical. Resume only against the same pinned manifest or explicitly create
a new revision. A failed checkpoint returns the correction to the diary; preserve the
failed round, repair, freeze, reconstruct and reverify the affected identities and
contexts. Do not carry a later green tip backwards.

Reordering or regrouping the same final tree creates a new semantic series. Its changed
checkpoint identities require fresh evidence; no earlier status is transferred merely
because an ordered sequence ends at equal content. Never let auto-compaction invent progress.
