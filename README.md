# VS1 milestone architecture review — DER r1

Evidence-only branch: never merge into main. Application branch:
`refactor/vs1-milestone-review`. Start with `r1/plan.md`, `r1/review-notes.md`,
`r1/verification-summary.json` and `r1/reconstruction-attempts.md`.

Base: 0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9.
Frozen diary: 45c29fcfea43c99026a9ae54051df61d905e30fc.
Semantic tip: 036ff45827370f62d798b92ce10c9a52b6ed6330.
Exact shared tree: c98dffccb65429bae5fc217ead6462ccf49da8e7.

Nine checkpoint-owned clean Windows/Python 3.12/locked environments pass all
canonical gates (94, 96, 97, 100, 101, 102, 102, 102, 102 tests). Frozen diary
passes 102. Each record binds SHA, tree, lock, source/package identity, environment,
commands, status and clean state. The first reconstruction's failed import-order
checkpoint and its history are retained; all corrected descendants were reverified.
An early AST whitespace expectation and environmental access/line-ending failures
are recorded. No tests, architecture contracts or ignores were weakened.

The exact semantic tip also ran a separate worker through real MAF and the pinned
llama.cpp/Qwen fixture in a fresh public-data runtime. It confirmed prompt/provider
version provenance, an edit/reopen and unchanged original result reference. A
backup of prior functional-test data migrated with all rows preserved. This is
compatibility evidence, not a model-quality experiment or human research judgement.
See r1/semantic-live/live.py and live.json; private/runtime bodies are omitted.

Reproduction: clone rounds/r1/history.bundle and create a clean checkout/environment
for each SHA in r1/series.json. Install Python 3.12 and uv, then `uv sync --locked`
and `uv run --locked python tools/check.py`. Compare snapshots with the same tip
version of tools/architecture.py on base and tip; r1/architecture-identities.json
pins the generator and input revisions. Live reproduction requires the fixture in
verified-downloads.json and the application's local-inference/normalisation guides,
a fresh external runtime, and the pinned public source. Scripts show the actual
method; replace $WORKSPACE/$USER_HOME and choose local paths. Recorded model output
and timing can vary. No independent reproduction or hosted CI run is claimed.

Canonical manifests, bundles and ledger events are byte-preserved. Text paths and
line endings are normalised; export-provenance.json retains original/export hashes.
SHA256SUMS.json covers every payload file. Check-round initially inspected an
unpopulated archive clone; check-round-populated.json records its clean populated
state. Actual verification always used the separately identified clean checkouts.
Public-history bundles contain no credentials, private data or model weights.
No chat transcripts or hidden reasoning are exported. Later publication/readiness
observations stay in the external canonical ledger; this immutable archive records
locally prepared facts, not future owner approval or integration.
