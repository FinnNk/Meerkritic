# Tests

Run `uv run --locked python tools/check.py` from the repository root. It runs
Ruff, Import Linter, Tach and all `test_*.py` files with Python's unittest runner.

The suite covers dataset integrity, real SQLite/DuckDB/Parquet storage, routing
and retained versions, the actual MAF graph with deterministic model responses,
worker exclusion/recovery, artefact publication, HTTP interaction and immediate
annotation. `test_vs1_path.py` joins the complete path and checks restart and
usage export. Separate live-model evidence is required for provider compatibility;
unit tests do not establish model quality or replace that operational check.

Three negative architecture controls require the intended Import Linter/Tach
failure for forbidden domain-to-adapter, web-to-composition and web-to-SQLite
access. A nonzero command alone does not satisfy those controls.

Keep tests near the behaviour they verify; introduce subdirectories only when
that improves navigation. Fixtures must be small, synthetic or explicitly permitted
for redistribution. Full datasets, private examples, live model outputs and
credentials stay in external runtime/evidence storage.

`test_selections.py` checks exact annotation versions, effective edits, explicit
research claims, exclusions, corrupted evidence, concurrent idempotence, interrupted
publication, restart and the CLI with synthetic source records. These are software
checks, not human-labelled discovery data or a registered empirical comparison.

`test_selection_web.py` opens a composed application after freezing and checks
source/decision display, escaping, pagination and missing/corrupt snapshot failures.
