# Dataset browser - DER round r4

Evidence-only branch: never merge this branch into main. Application PR: #3.
Read plan.md, review.md, commits.json and rounds/r4/manifest.json. The r3 and r4
self-contained bundles preserve the prior published and current paired histories.

R4 folds concise docstrings/comments into the three introducing capability commits,
backfills the existing quality runner separately, records commenting guidance and
ADR-0003 separately, then records the owner's ADR-0002 choice. ADR-0002 and ADR-0003
are implemented in the candidate branch; ADR-0001 awaits first empirical use.

All six checkpoint-local quality runs passed on Windows/Python 3.12 with their own
locked environments: 11/14/15/15/15/15 tests. Use pN-checks.log and pN-environment.json.
Earlier failed/incomplete attempts are retained and explained in verification-correction.md.
The final diary and semantic trees are exactly equal. Executable Python structure
and typed architecture are unchanged from r3; docstrings add documentation metadata.
No hosted CI is configured. This is self-review, not independent or owner approval.

Reproduce by cloning rounds/r4/history.bundle and checking out each commits.json
SHA in a fresh worktree/environment. Use Python 3.12, uv sync --locked, then
uv run --locked python tools/check.py. Do not reuse later editable packages or
surplus dependencies. Use the source paths and version identities in each record.
Architecture checks: python tools/architecture.py snapshot --root CHECKOUT, then
python tools/architecture.py delta BEFORE.json AFTER.json. No model inference or
human annotation is implemented in this batch; VS1 remains incomplete.

Bundles/manifests/events are byte-preserved replicas of the canonical external
evidence store. Other text normalises line endings and redacts machine paths;
export-provenance.json records both hashes. SHA256SUMS.json covers the payload.
Discussion export includes accessible PR comments, inline comments, reviews and
timeline at preparation time. Deleted/edited history and private drafts are not
recoverable. No credentials, private datasets, raw dataset bodies or model weights
are included. Publication/readiness events appended later remain in the canonical
store and do not mutate this archive.
