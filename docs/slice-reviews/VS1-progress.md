# VS1 progress

Status: ACTIVE (milestone follow-up). The functional VS1 batches are integrated;
this is a progress index, not the separate final slice review or VS2 plan.

Dataset browsing and routing are integrated. PR #5 was approved and merged as
`f1478217d43414da6e55599a5bf390c7f957dadb`; all 43 tests passed on main and all four
integrated proposition trees match the reviewed series. ADR-0005 is implemented
following owner acceptance and confirmation.

The integrated material batch, DER pair `vs1-normalisation`, round `r2`, adds
local llama.cpp inference, real MAF normalisation, a durable single-worker queue
and browser launch, results and failed-job inspection. PR #6 was approved and
merged; ADR-0006 now records its confirmed process-lock recovery policy as implemented.

Preflight verified official llama.cpp v0.4.1/b10964 Windows CUDA 12.4 archives and
pinned Qwen3 4B Q4_K_M weights against published hashes. Template rendering,
tokenisation, structured streaming, token counts and timings worked on the 16 GB
RTX 4090 Laptop GPU. Public record 0 completed through MAF core 1.19.0 and a separate
worker with source spans, immutable provenance, usage and a FrameworkObservation.
This establishes fixture compatibility, not comparative model quality.

The 72-test candidate suite checks provider/context/semantic failures, source grounding,
route refusal, atomic claims/events, process exclusion and death, recovery without replay,
old-worker rejection, storage-failure artefacts, provenance and browser host/origin checks.
Architecture contracts remain unchanged. Exact checkpoint and live/browser results belong
to the external DER evidence store and the batch PR, not this progress index.

MAF failure-message copying initially failed. Passing plain failure data mitigated it;
the failed test is retained. No EDR is needed for prescribed architecture or incidental
compatibility checks. Comparative quality/cost choices must follow the EDR process.
ADR-0001 remains accepted pending its first applicable empirical decision; ADRs 0002-0004
remain implemented. Ordinary tests do not advance the empirical-process ADR.

The integrated `vs1-annotation/r1` batch (PR #7) adds immediate Accept/Edit/Reject, source-grounded
immutable edits, atomic decision/events, history and snapshot-consistent progress.
Concurrent identical submissions create one record; conflicting decisions cannot
overwrite it. The browser exposes only the three VS1 decision actions.

The integrated `vs1-validation/r1` batch (PR #8, merged through PR #7) adds artefact metadata, structured
committed-event log snapshots, reserved routing-continuity schemas and a read-only
DER reference page. Full-path tests and live isolated public-data verification
exercise all three annotation actions, restart, failed-provider inspection and
Parquet/DuckDB usage analysis. See the [verification guide](VS1-verification.md).

The final stack is integrated at `0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9`.
The milestone architecture review is now integrated via PR #9 at
`fa6856bff52efecba55700572cb10e67f9a8f3c0`. The [final slice review](VS1-review.md)
and [VS2 plan](../plans/VS2-plan.md) are reconciled with its findings. VS1 is
complete; VS2 A1 is active after the owner's instruction. Later batches retain
their model/corpus/empirical entry gates. Related semantic propositions may share
one PR; prefer stacked PRs when splitting dependent batches.

Canonical evidence lives outside application worktrees at `extras/der-evidence`.
Earlier pairs are `vs1-dataset-browser/r5` and `vs1-routing/r1`. This file only indexes
progress; evidence owns chronology, verification, propositions and review/readiness.

The [milestone architecture review](VS1-milestone-architecture-review.md) records
the all-guidance assessment, authorised fixes and verification limits. Its material
follow-up uses DER pair `vs1-architecture-review/r2` (retaining r1 runtime evidence)
in owner-approved and merged PR #9.
