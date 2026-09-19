# VS1 progress

Status: in progress. This is a batch reference, not a completed slice review.

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

The `vs1-annotation/r1` candidate adds immediate Accept/Edit/Reject, source-grounded
immutable edits, atomic decision/events, history and snapshot-consistent progress.
Concurrent identical submissions create one record; conflicting decisions cannot
overwrite it. The browser exposes only the three VS1 decision actions.

Remaining VS1 work: operational evidence indexing and structured logs, full
interaction/restart/failure integration, final slice review and explicit
review/revision of future slices. VS2 and later slices remain DRAFT. Related semantic
propositions may share a PR; prefer stacked PRs when splitting dependent batches.
Candidate readiness, owner acceptance and slice completion remain separate.

Canonical evidence lives outside application worktrees at `extras/der-evidence`.
Earlier pairs are `vs1-dataset-browser/r5` and `vs1-routing/r1`. This file only indexes
progress; evidence owns chronology, verification, propositions and review/readiness.
