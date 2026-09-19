# VS1 dataset browser — DER archive

This evidence-only branch must never be merged into main. The application candidate
is `feat/dataset-browser`, semantic commit `6556aa4e784d0713f3029b3140ae87c5c1b55767`.
It reconstructs diary `951a28fc3da35160a01c61ba1e310f44b0d6d299` at the same tracked tree.
Round r1 is retained; r2 fixes its self-review finding. Owner approval is outstanding.

Start with `r2-self-review.md`, `freeze-and-propositions.md` and `rounds/r2/manifest.json`.
The bundle retains both histories and their baseline, independently of remote branches.
For example: `git clone rounds/r2/history.bundle candidate`, then check out the semantic
SHA, install Python 3.12/uv and run `uv sync --locked` and
`uv run --locked python tools/check.py`. The candidate README reproduces public ingestion.

Local checks passed in Windows/Python 3.12.14 at both exact tips, including 15 tests.
The same locked isolated environment supplied the r2 source/tests; no editable package
from another checkout was loaded. `checkpoint-environment.json` records dependency
and lock identity. No hosted CI checks are configured. Self-review is not independent
review or owner acceptance. No model invocation or annotation capability is claimed.

This is a replica of the canonical external DER store, not harness-owned evidence.
Bundles, manifests and events are byte-preserved. Other text copies replace machine
paths with `$WORKSPACE`/`$USER_HOME`; `export-provenance.json` records original/export
hashes. This redaction is not a claim of byte equality for logs. No credentials,
private datasets, model weights or raw dataset bodies are included. Historical failed
checks remain visible; final passing evidence is named `r2-...`.
