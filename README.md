# Grouping comparison tooling: review evidence

This separate archive preserves implementation chronology, reconstructed semantic
histories and verification. It is not application ancestry and must not be merged.
Round r1 established the software; r2 completes the last documentation proposition
with actual preparation findings. P1-P4 retain their exact SHAs and passing checks.
The earlier r1 P5 was not verified or published; it is retained without a pass claim.
Two r2 P5 runs hit a Windows temporary-Git cleanup lock. Both failures, isolated
checks, the diagnostic full run and final canonical run are retained separately.
The intermittent lock cause remains uncertain; no cleanup error was suppressed.

| Record | Purpose |
| --- | --- |
| records/r1/design.md and records/r2/propositions.md | Materiality, design and semantic boundaries |
| records/r2/verification-summary.json | Checks and test totals derived from exact checkpoint records |
| records/r2/review-notes.md | Full author self-review and concrete contract challenges |
| records/r2/revision-notes.md | Precisely what changed between rounds |
| records/r2/architecture-*.json | Typed before/after/delta |
| records/r2/docs-check.json | Documentation, source hashes and actual command help |
| records/r1/pr15-integration.json | Predecessor review/merge mapping |
| canonical/rounds/r2 | Equivalent pair manifest and self-contained Git bundle |

To inspect or reproduce:

1. Verify SHA256SUMS. Canonical manifests/bundles/events retain original bytes;
   export-index.json maps original to sanitised auxiliary evidence hashes.
2. Import the bundle into a separate repository and run the pinned DER helper's
   check-round on the manifest. Local paths in auxiliary records use placeholders.
3. Check out each semantic commit separately. With Python 3.12 run uv sync --locked
   then uv run --locked python tools/check.py. Required recorded context: Windows.
4. Adapt records/r2/verify.py for isolated checkpoint-owned environments. P1-P4 use
   their exact r1 records; the r2 diary and final P5 were checked independently.
5. Follow the application's study guides for preparation and comparison. No raw
   dataset, source comment, model output, weights or credentials are included here.

The 80-candidate preparation pool produced 55 qualified origins and 33 valid drafts
from one initial local model pass. All 22 failures remain in external research
storage. Forty usable human-reviewed inputs are unattainable under current rules;
owner amendment is pending. No human annotations, research grouping run, registered
EDR or comparative result is claimed. Author self-review is not owner approval.
