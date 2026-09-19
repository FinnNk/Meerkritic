# Round r2 proposition plan

This round supersedes unpublished r1. Initial materiality/design assessment and boundary
alternatives are retained at ../r1/setup.md and ../r1/plan.md. Scope is unchanged.
Frozen diary: 3da9af4a2c04fecb1bd18fee309af0411c8a9894.
Base: f1478217d43414da6e55599a5bf390c7f957dadb. Exact commits: commits.json.

P0 confirms accepted ADR0005 implementation. P1 establishes bounded local transport
and telemetry. P2 establishes evidence/schema validation through real MAF. P3 establishes
the durable queue, process lock, immutable artefacts, recovery and CLI with ADR0006.
P4 establishes browser submission/read protection, results and live telemetry.
Each includes its tests/docs; P3 uses P1/P2 contracts, P4 uses P3. The worker unit is
larger because process ownership, queue transitions and crash publication must be
reviewed together to establish the recovery guarantee; its tests are part of that claim.

The alternative combining transport and MAF was rejected because each has an independent
testable owned contract. No layer-only or tests-later commits. One PR balances related
capabilities against owner review overhead. Comment/docstrings accompany their code.
There is no separate governance change or unrelated comment backfill in this batch.
