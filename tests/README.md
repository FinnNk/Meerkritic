# Run and understand the checks

From the repository root, with Python 3.12:

```text
uv sync --locked
uv run --locked python tools/check.py
```

Expect Ruff, Import Linter, Tach and all `test_*.py` unittest tests to pass.
The runner selects this checkout's source and environment.

| Area | Examples of coverage |
| --- | --- |
| Data and annotations | Integrity, real SQLite/DuckDB/Parquet, immutable edits, progress and restart |
| Routing and models | Version retention, privacy/context rules, usage and actual MAF graphs with deterministic model responses |
| Worker and evidence | Process exclusion, recovery without automatic replay, publication and atomic events |
| Discovery and rules | Fixed selections, embeddings/grouping, synthesis, inherited evidence and concurrent decisions |
| Research interaction | Saved/apply distinction, whole-batch rollback, discussion, advice-only responses and unknown completion |
| Web and architecture | Escaping, bounded input, source freshness, corrupt projections and forbidden imports |

`test_vs1_path.py` retains its historical filename and joins the input-to-annotation
path, restart and usage export. Other tests cover later workflows. Live-model
compatibility is checked separately using [workflow verification](../docs/development/verification.md);
a deterministic test response does not establish model quality.

## Add or review tests

- Test the promised behaviour and meaningful failure boundaries, not a copy of the implementation.
- Keep tests near related behaviour; introduce subdirectories only when they improve navigation.
- Architecture negative controls must fail for the intended forbidden dependency.
  A setup failure or arbitrary nonzero exit is not evidence of that boundary.
- Use small synthetic or explicitly permitted fixtures. Full datasets, secrets and
  live outputs remain in external runtime/evidence storage.
- Label automated decisions as test data, not human research labels.
- For editorial changes, check links, commands and rendering without introducing
  brittle tests that merely match prose. Follow the [documentation checklist](../docs/development/documentation-style.md#author-and-reviewer-checks).
