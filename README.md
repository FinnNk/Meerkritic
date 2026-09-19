# Routing provenance — DER round r1

Evidence-only branch. Never merge this branch into main. Application branch: feat/routing-provenance.

Start with finalisation.md, plan.md, review.md, boundary-review.md and final-commits.json. The full review is self-review; a fresh-context reviewer assessed semantic boundaries separately. All four final checkpoints pass the canonical gates in separate locked Windows/Python 3.12 environments (26/33/40/43 tests), and the frozen diary passes 43. Exact source/package identities, command logs and lock hashes are included. Final tracked trees are identical. No hosted CI, live provider invocation, owner approval or integration is claimed. VS1 remains incomplete.

The first semantic reconstruction had a P3 import-formatting failure. Its bundle and logs remain available. It is not the submitted revision. The corrected final series has fresh exact checkpoint evidence; final tree equality is not substituted for checkpoint tests. Earlier environment, fixture and formatting failures remain in the record.

Reproduce: clone rounds/r1/history.bundle, check out each final-commits.json SHA, use Python 3.12 and uv sync --locked, then run uv run --locked python tools/check.py from that checkpoint. Each checkpoint must use its own source and environment. Architecture: python tools/architecture.py snapshot --root CHECKOUT, then python tools/architecture.py delta BEFORE AFTER. CLI examples are in docs/development/routing-operations.md at the semantic tip. All fixtures are synthetic; no credentials, raw datasets or model weights are included.

The manifest, bundles and ledger events are byte-preserved replicas of canonical external evidence. Text logs/records normalise line endings and replace local workspace/user-home paths; export-provenance.json records source/export hashes. SHA256SUMS.json covers the archive. Publication and later review events remain in the canonical external ledger; this immutable payload does not claim future actions.
