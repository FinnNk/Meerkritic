# VS1 progress

Status: in progress. This is a batch reference, not a completed slice review.

The first material batch covers launch → pinned registration → DuckDB/Parquet
browsing, including metadata/events, provenance and restart/failure behaviour.
The next candidate batch adds routing selection, usage accounting, immutable SQLite provenance and CLI/Parquet inspection. Live model calls and telemetry capture, the worker, MAF application execution, Accept/Edit/Reject and annotation progress remain outstanding. VS2 remains DRAFT.

Preflight used Windows, Python 3.12.14 and SQLite 3.53.1. FastAPI 0.141.1, DuckDB
1.5.5, Yoyo 9.0.0 and Uvicorn 0.53.0 are locked for this batch. MAF core 1.19.0 ran
an executor graph in an external preflight environment, recording a FrameworkObservation
from first use. This does not validate model inference or an application workflow.

The owner selected llama.cpp. No model weights or provider compatibility are yet
validated. llama.cpp was not on PATH; the checked Ollama/LM Studio endpoints were
unavailable and no provider API keys were present in the session. The machine has
a 16 GB RTX 4090 Laptop GPU and about 96 GB RAM. Actual model setup remains part
of the next batch; available memory alone is not compatibility evidence.

No EDR was opened for these prescribed architecture and operational checks. Future
comparative model quality/cost decisions must follow the EDR process; incidental
compatibility measurements need not become experiments.

The dataset/browser batch landed from DER pair `vs1-dataset-browser`, round `r5`. The routing candidate uses pair `vs1-routing`, round `r1`, with one history integrator. Canonical
evidence lives in `../extras/der-evidence` relative to this repository, outside all
application worktrees. It owns assessment/design notes, the diary, verification,
architecture before/after/delta, propositions and review/readiness records. This
document is only a reference; see the batch PR for archive publication. DER readiness,
owner acceptance and slice state remain separate.

Routing validation uses synthetic inventories, quotes and measurements, plus real SQLite migrations, DuckDB/Parquet and CLI subprocesses. It checks privacy refusals, override precedence, missing telemetry, historical prices, atomic events, migration preservation, idempotence and concurrent completion. These checks do not establish provider availability, model quality or live token capture. Pydantic 2.13.5 is now an explicit locked dependency for immutable validated records; it was already present through FastAPI. No architecture contracts or ignores were weakened.

The proposed retention decision is [ADR-0005](../adr/ADR-0005-retain-immutable-routing-provenance.md); owner acceptance remains pending. Existing ADR statuses were reviewed without advancing the empirical-process ADR merely because ordinary tests produced data.

Remaining VS1 work is reviewed as a sequence of contracts: operational llama.cpp preflight and model invocation; MAF normalisation through a recoverable worker; annotation and progress; then live integration/failure checks and slice review. These are provisional semantic boundaries, not a requirement for one PR per capability. Group related work into reviewable PRs and normally stack dependent PRs when a split is useful. Later slices remain unchanged and DRAFT until the final VS1 review.

Before completing VS1, finish its remaining contracts, complete the full slice review
template, record architecture changes and explicitly revise the subsequent slices.
Do not promote VS2 merely because this batch merges.
