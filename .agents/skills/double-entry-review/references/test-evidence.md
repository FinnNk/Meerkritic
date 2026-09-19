# Tests serve supported contracts

Design coherent abstractions; tests support and challenge those designs. Selective
test-first investigation is useful, especially for reproducing a defect, but neither
a writing order nor a permanent test for every development episode is prescribed.

Distinguish the faulty candidate, its reproduction/fix commits, and the behavioural
obligation. The first two may disappear from the semantic narrative while useful
contract evidence remains with the corrected proposition.

| Evidence situation | Disposition |
|---|---|
| Still-relevant contract, boundary or failure mode | Retain or express the obligation in a suitable current test |
| Better test subsumes it | Consolidate with mapping of inputs, assertions and failure paths |
| Abandoned implementation-only diagnostic | Retire after checking that no continuing obligation is lost |
| Incorrect expected behaviour | Correct against the authoritative requirement, not just to get green |
| Deliberate transitional contract | Keep evidence at that checkpoint; retire when the contract ends |

All test edits, replacements and retirements happen on the diary before freezing,
with reasons and replacement evidence where relevant. Reconstruction cannot silently
change tests. Tree equality includes them. Earlier diary snapshots retain historical
experiments; their old passing results are not coverage of the current tree.

Bind each result to the exact checkpoint SHA/tree, its own checked-out source and tests,
dependency lock, installed-package identity, command, environment and required context.
Evidence produced with later editable code, shared build output or an unrecorded ambient
dependency is not checkpoint-local. A required result that is failed, missing, stale,
skipped or partial is not complete, even when the final tip is green or trees are equal.

For a negative control, record the intended failing assertion and preserve stderr. A
checkout, fixture, import or infrastructure failure before that assertion does not prove
the control. Exercise Git modes and symlinks in a context that preserves them when relevant.

A within-PR bug does not automatically make its test obsolete. Internal tests are not
automatically worthless. Equal counts, line coverage or a green remaining suite do
not establish redundancy. Conversely, existing tests may suffice for a proposition;
never add duplicates just to improve a production/test co-change metric.

Record material decisions with original/retirement diary SHAs, the continuing
obligation, replacement evidence, relevant input/assertion details and any limitation.
Expose reductions in current evidence during review, including between rounds.

Carry results forward only when repository policy permits and the tested identity,
environmental assumptions and assertion remain unchanged. Reordering or regrouping a
semantic series changes checkpoint identities and requires fresh checkpoint evidence,
even if the final tracked tree is equal. Never combine selected green jobs from different
hosted run attempts to conceal a failed complete attempt.
