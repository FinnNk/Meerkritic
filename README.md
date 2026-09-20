# VS2 — Annotation-to-Rule Discovery: frozen inputs, review round 2

Evidence-only branch; never merge into main. Round 2 addresses owner feedback about
code/title references in PR descriptions and commit comments. Start with r2/changes.md,
r2/review-notes.md and r2/verification-summary.json. Round 1 records remain included.

Base: fa6856bff52efecba55700572cb10e67f9a8f3c0.
Diary: e0cd75f2f4c4bfd9128d4182fbd5809bbb7b85f0.
Semantic: 068376980510d4e32004583efb11c6e2d0c9b2be.
Both new tips pass115 tests and all canonical checks; final tracked trees equal.
Three unchanged semantic checkpoints retain exact-SHA r1 checks and review.

Reproduce using rounds/r2/history.bundle: check out each recorded SHA separately,
uv sync --locked, then uv run --locked python tools/check.py with Python3.12.
Windows own-source/locked-environment commands and source identities are in logs.
Other platforms and independent reproduction are not claimed. No empirical study.
Canonical manifests/bundles/ledger bytes retained; other paths/line endings normalised.
export-provenance.json and SHA256SUMS.json record hashes. Public feedback included;
private drafts/deleted history unavailable. No credentials or runtime datasets included.
Later publication/readiness observations remain in the canonical external ledger.
