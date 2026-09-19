# vs1-annotation — DER r1

Evidence-only branch; never merge into the application. Canonical evidence remains
outside application worktrees. This is an immutable review replica.

Read records/review-notes.md, records/series.json and verification-summary.json.
The frozen diary and semantic tip have exactly equal tracked trees. All listed
checkpoints ran their own source, tests and lock in isolated Windows/Python 3.12
environments. Exact commands, package identity, timestamps and output are retained.
Self-review is not owner approval. Publication/integration occur after this archive.

Reproduce: clone round/history.bundle, check out a SHA from records/series.json,
run uv sync --locked and uv run --locked python tools/check.py in its own checkout.
Live runtime instructions are in the application documentation. Public dataset and
model identities are recorded there; GPU output/timings need not be identical.

Manifests, bundles and events are byte-preserved. Text paths and line endings are
normalised with paired hashes in export-provenance.json. SHA256SUMS.json covers
payload bytes. Runtime bodies, credentials, weights and hidden reasoning are absent.
