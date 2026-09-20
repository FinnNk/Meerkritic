# Semantic proposition plan

Pair vs2-study-tools/r1. Frozen diary 9e47863265c21f27ac07b4b3613d0b1aec2fe3c1.
Base cd0a4d8c9a254e3027513274b39ce3f65cf227d2. Diary quality checks: passed, 181 tests.
What matters: the owner's protocol agreement is explicit but not registration;
selection is reproducible from exact source bytes; human/source claims are explicit;
input order, quotas and shortfall cannot be silently changed; evidence is external.

1. docs: record study agreement and freeze input preparation
   Complete owner disposition and bounded work plan. Source: ce7bb20, 69abf53.
   Existing baseline tests suffice. No new functionality or study registration claim.
2. feat: freeze reproducible study candidates and exclusions
   Pure deterministic sampling contract: exact source hash, case-folded identities,
   prior exposure/holdouts, lowest-position duplicate precedence and bounded seeded
   round-robin. Include the three synthetic source/sampling contract tests.
   Source: sampling portions of b90fd12 and f027a95. No CLI/log contract claimed yet.
3. feat: retain bounded human input-review attempts
   Apply the frozen candidate contract: explicit outcomes/attribution, progress and
   stopping, immutable external publication, CLI and operator guide. Include all six
   attempt/persistence/CLI tests. Source: remaining b90fd12 and f027a95.
   No source authentication, model execution, labels, registration or comparison.
4. docs: record preparation evidence and remaining study gates
   Source: 9e47863. Current documentation backfill, actual metadata-only plan identities
   and PR14 integration. No earlier-commit test result relabelled as current execution.

Alternative: combine sampling and the attempt ledger into one feature commit. Both
share an input-preparation goal but not all correctness obligations: the deterministic
source pool can be checked before the stateful human-review log. Prefer two complete
contracts, with CLI/docs and error paths retained together in the latter. No PR split
needed; one related batch avoids separate tiny review requests. Do not split by layer.
Challenge: if the sampling checkpoint requires later log/CLI code to pass or describe
its own contract, recombine or correct the diary first. Final tree must match exactly.

Every checkpoint runs all declared checks in its own Windows/Python3.12 locked
checkout. New tests are retained; no baseline test deleted or weakened. Review unchanged
selection validation as the later authenticity/version gate. No ADR status change is
needed for this implementation of the agreed EDR preparation protocol.
