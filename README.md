# VS2 frozen annotation inputs — DER r1

Evidence-only branch. Never merge into main. Application branch: feat/vs2-input-selections.
Start with r1/setup.md, r1/freeze-and-plan.md, r1/review-notes.md and r1/verification-summary.json.
Base fa6856bff52efecba55700572cb10e67f9a8f3c0; diary f669491ca9890796fa4d8723f733506669c9b96a;
semantic 4abbcdd20f0dfe339e53f8332d3b509b07753341; shared tree 914e149eb3cb593ef314816e7964e8c8999c4d2c.

Three clean checkpoint-owned Windows/Python3.12/locked environments pass canonical gates,
with 102, 113 and 115 tests respectively. Frozen diary passes115. Evidence retains initial
JSON tuple-boundary and import-order failures and the subsequent fixes. No test/ignore weakened.
No hosted CI, independent review or reproduction, human labels or empirical comparison claimed.

To reproduce, clone rounds/r1/history.bundle, check out each full SHA in r1/semantic-commits.json,
install Python3.12 and uv, run uv sync --locked then uv run --locked python tools/check.py.
Use each checkout's own environment/source. r1/verify.py shows the Windows method; replace
$WORKSPACE/$USER_HOME with local paths and use a writable external TEMP directory. Tests need
no model server, credentials, public dataset download or private research state. Generate typed
architecture data with the pinned generator and source revisions in architecture-identities.json.
The recorded tests prove software integrity, not interpretation quality or sampling validity.

Canonical manifests, bundles and ledger events retain exact bytes. Other text paths/line endings
are normalised; export-provenance.json retains source/export hashes. SHA256SUMS.json covers all
payload files. Bundles contain tracked public application history, not runtime datasets or keys.
Later publication/readiness records live in the canonical external ledger; this archive records
locally prepared evidence and does not claim future owner approval or integration.
