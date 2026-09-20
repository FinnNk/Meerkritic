# VS1 operational validation batch

Material: persistence and evidence-integrity hard triggers. User explicitly
authorised autonomous completion and a second PR stacked on annotation.
Base 843ff161d49e096d1da2a55cacf75acac03e97f3 (PR #7); same diary/semantic base.
External canonical store: extras/der-evidence/vs1-validation/r1.
One integrator; App author; diary branch change/vs1-validation-diary.

Audit of handover/backlog identified explicit outstanding artefact metadata,
structured job logs and lightweight DER readiness references. No new VS2 workflow.
P1: immutable artefact catalogue plus structured per-job event-log snapshots.
P2: externally verified DER reference index and read-only harness display.
P3: full-path integration verification and VS1 operational documentation.
Final detailed slice review and VS2 plan are a separate committed branch, no PR.

Design clarity before implementation: artefact storage hides atomic file publication
and checksum/metadata consistency; callers continue to publish/read by digest.
The optional SQLite catalogue contains only small references, not bodies. Job log
snapshots derive from committed operational events and are immutable filesystem
JSON, with the latest snapshot pointer in SQLite. A failed log export cannot undo
a committed job transition; explicit inspection can regenerate it. This is simpler
than adding a logging service or competing event history. No source/prompt bodies
or credentials are logged.

DER indexing owns validation of bounded local references and exact evidence hashes.
It never changes canonical evidence, infers readiness from a branch, or treats an
index entry as approval. The external record must identify exact pair/round,
diary/semantic heads, readiness and authoritative manifest/event; SQLite stores
references and checked digests. No remote fetching or shell execution from records.

Required checks: unchanged canonical command in each checkpoint's own Windows
Python3.12 locked environment; full live public dataset/llama.cpp/MAF/worker/human
decision path, restart/failure, usage Parquet/DuckDB export and architecture delta.
Routine functional/compatibility evidence is not an EDR-based model quality claim.
