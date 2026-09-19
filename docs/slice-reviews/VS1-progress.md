# VS1 progress

Status: in progress. This is a batch reference, not a completed slice review.

The first material batch covers launch → pinned registration → DuckDB/Parquet
browsing, including metadata/events, provenance and restart/failure behaviour.
Routing/telemetry, the worker, MAF application execution, Accept/Edit/Reject and
annotation progress are outstanding. VS2 remains DRAFT.

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

DER pair `vs1-dataset-browser`, round `r2`, has one history integrator. Canonical
evidence lives in `../extras/der-evidence` relative to this repository, outside all
application worktrees. It owns assessment/design notes, the diary, verification,
architecture before/after/delta, propositions and review/readiness records. This
document is only a reference; see the batch PR for archive publication. DER readiness,
owner acceptance and slice state remain separate.

Before completing VS1, finish its remaining contracts, complete the full slice review
template, record architecture changes and explicitly revise the subsequent slices.
Do not promote VS2 merely because this batch merges.
