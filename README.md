# Dataset browser - DER round r5

Evidence-only branch; never merge this branch into main. Application PR: #3.
R5 expands caller contracts and class meaning, refines ADR-0003, and adopts a
selective Python style policy in ADR-0004. Both ADRs contain IEEE references and
explicitly state that Google's guide has not been adopted in its entirety.

Start with plan.md, review.md, commits.json and rounds/r5/manifest.json. The r4
and r5 bundles preserve both published histories. The initial unpublished r5
candidate passed, then review corrected publication/size wording; initial/ retains
those results, which do not substitute for the final checkpoint evidence.

All seven final checkpoints passed their canonical commands in separate locked
Windows/Python 3.12 environments: 11/14/15/15/15/15/15 tests. Source and package
identities appear in pN-environment.json. Final diary and semantic tracked trees
are equal. Executable structure and architecture are unchanged; documentation
metadata, including API descriptions, is updated. This is self-review. There is
no hosted CI; owner approval and merge remain outstanding. VS1 is incomplete.

Reproduce by cloning rounds/r5/history.bundle, checking out each commits.json SHA,
and creating a fresh environment with Python 3.12 and uv sync --locked. Run
uv run --locked python tools/check.py from that checkpoint. Architecture commands
are python tools/architecture.py snapshot --root CHECKOUT and delta BEFORE AFTER.
Do not use another worktree's source or reuse surplus dependencies.

google-reference.json identifies the pinned upstream source and its verified blob
and SHA-256 hashes. The raw upstream guide is not republished here. No credentials,
private datasets, raw dataset bodies or model weights are included. Accessible PR
comments, reviews, inline comments and timeline are retained; deleted/edited
history and private drafts cannot be recovered by the export.

Bundles, manifests and ledger events are byte-preserved replicas of the canonical
external store. Other text normalises line endings and redacts machine paths;
export-provenance.json records original/export hashes, and SHA256SUMS.json covers
the payload. Later publication events stay in the canonical store; this archive
does not claim the future publication or owner-acceptance result.
