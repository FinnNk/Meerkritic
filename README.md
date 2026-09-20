# Reproducible study input preparation: review evidence

This separate archive retains the actual implementation diary, reconstructed review
histories and their evidence. It is not application ancestry and must not be merged.
Round r1 contains an unpublished checkpoint with a Ruff import-format failure.
Round r2 corrects reconstruction only, preserving the verified diary's final tree.

| Record | Purpose |
| --- | --- |
| records/r1/design.md and r1/propositions.md | Materiality, design and complete review boundaries |
| records/r2/verification-summary.json | Evidence-derived status and test totals for every exact checkpoint |
| records/r2/review-notes.md | Full author self-review, contract challenges and limitations |
| records/r2/revision-notes.md | Retained failed reconstruction and its correction |
| records/r2/architecture-*.json | Typed before/after/delta |
| records/r1/sample-plan-summary.json | Original metadata-only preparation identity; no human labels |
| records/r2/sample-replay-summary.json | Same-host exact replay, not independent research replication |
| canonical/rounds/r2 | Verified equivalent pair manifest and self-contained Git bundle |

To inspect or reproduce:

1. Verify SHA256SUMS. Canonical bundle/manifest/event bytes are preserved; the export
   index maps original to sanitised log/method hashes. Local paths use placeholders.
2. Use a bundle in a separate repository and run its pinned DER helper's check-round.
3. Check out each semantic commit separately, run uv sync --locked with Python 3.12,
   then uv run --locked python tools/check.py. The recorded required context is Windows.
4. Adapt paths in records/r2/verify.py to repeat checkpoint-owned checks. P1 is unchanged
   from r1 and uses that exact passing record; changed r2 identities were checked afresh.
5. Follow the application's study-preparation guide to reproduce the metadata plan
   from the pinned public source bytes. No raw source text, dataset, model weights,
   credentials or human research labels are included in this archive.

Author review is not independent review or owner approval. Study preparation does not
register the EDR, qualify original sources, authenticate people or adopt a grouping
method. The owner agreed the workload/criteria; empirical work has not begun.
