# Frozen result and semantic plan

Frozen diary f669491ca9890796fa4d8723f733506669c9b96a after its own clean locked
Windows verification: 115 tests, Ruff, Import Linter and Tach. diary-checks.json
records the supplied abbreviated ref f669491; its worktree HEAD resolves to the full
SHA above. Earlier failures remain in selection-first-tests.log and browser-checks.log.
No tests removed. The edit test was strengthened because the first fixture made
original and edited text identical; changed fixtures now discriminate body choice.

P1 reconciles integrated VS1 and activates A1 with later gates; no runtime claims.
P2 establishes the complete freeze use case: request/eligibility/effective edits,
publication/migration/transactions, CLI, failure tests and operational guide/ADR.
P3 adds browser inspection/escaping/failure statuses and visible annotation IDs,
with its own tests and user guide; depends on P2's verified read contract.

Alternative: one feature commit plus planning is plausible but conflates independently
assessable publication and inspection claims. Splitting P2 by schemas/store/service
would expose unusable intermediate contracts and forward correctness obligations.
One PR with three propositions balances review overhead; do not create one PR per layer.
Source map: P1 from e34f044 and f669491 documentation reconciliation; P2 from c224e32,
87a1f0c and f669491 tests, plus strict attestation from 6f11398; P3 from 6f11398.
Intermediate docs omit later browser behaviour, final tracked result stays exact.
