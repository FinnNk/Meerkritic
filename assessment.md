# VS1 dataset browser — initial materiality assessment

Assessed 2026-09-19 before implementation or pair creation. Classification: material.
Hard triggers: persistent registry/event schema, provenance identity, public read API,
transaction and immutable analytical artefact guarantees. DER required under the
project policy (11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md). Reassess if scope changes.

Bounded objective: local harness launch, reproducible pinned CRC-Py manual subset
registration through a CLI outside web requests, DuckDB/Parquet observation browsing.
Routing, llama.cpp inference, MAF normalisation and annotation remain the next material
batch within VS1. Runtime preference: llama.cpp, explicitly selected by the owner.

Integrator: Codex desktop, GPT-6, current Meerkritic session; CLI version not exposed.
Pair: vs1-dataset-browser; round r1. Diary and semantic base:
3db848bd0992d0686bb5c45ddadd87ec6fbde8d2. Diary: change/vs1-dataset-browser-diary.
Semantic: feat/dataset-browser. Evidence: this directory, outside all worktrees.
Required context: Windows, Python 3.12, each checkpoint's own lock and source,
uv run --locked python tools/check.py. Live pinned dataset smoke at final tip.
Remote scope: App-authenticated topic branch and PR; owner approval and merge.
No permission to bypass main, use personal credentials or force-push.

Before implementation, software-design-clarity assessment:
- DatasetService applies allowed catalogue choices, stable registration and bounded
  browsing. Callers rely on typed records and idempotence, not paths or SQL. It owns
  use-case coordination across storage operations, rather than mirroring a DB API.
- Registry port hides short SQLite transactions and atomic registration/event append.
  Callers do not manage connections or migrations. Metadata only, never source bodies.
- ObservationStore port hides pinned source validation, immutable Parquet publication
  and analytical querying. Callers know dataset identity and page, not file layout or
  DuckDB. One adapter owns this lifecycle rather than one abstraction per file format.
- Composition chooses runtime locations and adapters. Web only reads through the
  application service; CLI import performs potentially slow preparation outside HTTP.
No EDR: implementing prescribed architecture and operational preflight are incidental
measurements, not decision-bearing empirical research. Dataset exposure is recorded;
this subset is an integration fixture, not a validated model evaluation sample.
