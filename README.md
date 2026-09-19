# Dataset browser — DER round r3

Evidence-only branch: never merge this branch into main. The application PR is #3.
The owner requested smaller capability-led review units; r3 accepts that feedback:

1. `cc0bca41402601028826865539c819375e23f0b9` — pinned dataset registration (11 tests).
2. `16a2b9daf89544df4550f53dda41f48f2c921b31` — observation browsing (14 tests).
3. `8e5e77f406639c88655c88c20341083f655e7013` — architecture snapshots/deltas (15 tests).

Every checkpoint passed the canonical quality command in its own fresh locked
Windows/Python 3.12 environment. Use the `*-isolated-*` records; earlier in-place
runs retained surplus packages and are explicitly superseded for environment
qualification. Source, tests and lock identities are recorded per checkpoint.

The final tree is exactly unchanged from the prior PR head and frozen diary.
Start with `plan.md`, `review.md` and `rounds/r3/manifest.json`. Both r2 and r3 bundles
are retained, along with the exported public PR discussion. Self-review does not
constitute independent review or owner approval. No hosted CI checks are configured.

To inspect independently: clone `rounds/r3/history.bundle` and check out each semantic
commit in order. For each, use a fresh environment, `uv sync --locked`, then
`uv run --locked python tools/check.py`. Each checkpoint README documents the
capability available at that point. Normalisation/llama.cpp and annotation remain
outstanding VS1 work. Application progress docs retain their original r2 reference;
this external record and the PR own current round/readiness information.

This is a replica of the canonical external DER store. Bundles/manifests/events are
byte-preserved. Other text exports normalise line endings and redact machine paths
as `$WORKSPACE`/`$USER_HOME`; original/export hashes are listed. No credentials,
private datasets, model weights or raw dataset bodies are included. Edited/deleted
comments and private review drafts cannot be recovered by this discussion export.
