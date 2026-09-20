# VS1 milestone architecture review — DER r2

Evidence only; never merge this branch into main. Application PR: #9.

Round r2 adds the owner's requested six-finding discovery/resolution/earlier-review
record and the template/guidance required to produce equivalent future reviews.
Only five Markdown files change. Read r2/changes.md, r2/review-notes.md and
r2/verification-summary.json. Earlier round evidence remains under r1 and rounds/r1;
README-r1.md describes its runtime verification and reproduction.

Frozen diary: cdb5c2200a433d6588cf528fce2a54f0e9f845b2.
Semantic head: f353cfed1299608234f21e7159c6b0331e5b0660.
Exact tracked-tree equivalence, archive checks and review validation pass. The nine
published semantic commits retain their original SHA-bound checks/review; each of
the two new checkpoints and the frozen diary passes canonical checks and 102 tests
in its own clean locked Windows/Python 3.12 environment. Forty-two local Markdown
links resolve. The six narratives were checked against implementation and tests.
No new runtime change or live-model experiment occurred in this documentation round.

Reproduce the new checkpoints using rounds/r2/history.bundle, r2/series.json,
Python 3.12, uv sync --locked and uv run --locked python tools/check.py. Preserve
checkpoint-specific source and environments. Follow r1's live reproduction method
for the unchanged implementation; do not call that historical run a new r2 run.
Review remains author self-review. Owner approval and merge are pending.

Manifests, bundles and events are byte-preserved. Text paths are normalised to
$WORKSPACE/$USER_HOME; export-provenance.json records original/export hashes.
SHA256SUMS.json covers every payload file. No credentials, raw runtime bodies or
model weights are included. The immutable archive records prepared facts; later
publication/readiness events remain in the canonical external ledger.
