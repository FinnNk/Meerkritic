# R4 authorised revision

Owner feedback: https://github.com/FinnNk/Meerkritic/pull/3#issuecomment-5744986964
The owner accepted concise exposed-method docstrings and explanations of non-obvious
internal intent/implementation in the Codex conversation. The harness meant Codex,
not a new Meerkritic UI feature. Eyes, thumbs up and the intent reply already exist.

Latest instruction: application to PR code belongs with that code in semantic
history; backfilling existing code must be separate. Guidance and its ADR must
be a separate semantic commit. Actual diary chronology remains untouched.

This is a documentation-only revision of an existing material DER pair. There
is no new runtime contract, abstraction, dependency or empirical decision.
The existing material classification remains appropriate for the overall PR;
no new pair is justified for these routine edits in isolation.

Plan: apply comments to PR code diary-first, backfill the existing quality runner,
verify, then document the convention and ADR lifecycle review. Freeze that result.
Reconstruct P1 registration, P2 browsing and P3 architecture with their comments;
P4 backfills the baseline quality runner; P5 records guidance and ADR-0003 with
actual confirmation. This order keeps implemented status downstream of application.
Retain ADR-0001 accepted (first empirical use outstanding), ADR-0002 proposed
(owner decision outstanding). Do not treat code presence or PR merge as acceptance.

Run every reconstructed checkpoint in its own fresh locked environment. Preserve
r3, all discussion accessible through the App, and the r4 frozen pair before
updating PR #3 with an exact expected-head lease. Owner acceptance/merge remain separate.
