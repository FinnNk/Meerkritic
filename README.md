# Preserved source reading: review evidence

This separate archive preserves implementation chronology and five semantic review
propositions. It is not application ancestry and must not be merged.

- `canonical/rounds/r2` contains the equivalent frozen pair, manifest and Git bundle.
- `records/r2/verification-summary.json` derives every expected standard check and
  test total from exact-checkpoint, locked Windows/Python3.12 environments.
- `records/r2/review-notes.md` and `propositions.md` record author self-review and
  the review boundaries, including source identity and assessment provenance.
- `records/r1/discoveries.md` and `targeted-first.log` retain adverse observations.
- Architecture snapshots, documentation checks and synthetic browser/screenshot
  records retain reproduction details and limits.

Verify SHA256SUMS before importing the bundle into a separate repository. Canonical
files retain their bytes; export-index.json identifies sanitised auxiliary records.
Use the pinned DER helper to check the manifest. Check out each semantic commit,
install Python3.12, run `uv sync --locked`, then `uv run --locked python tools/check.py`.
Adapt local paths in scripts to your host. Browser fixtures are reproduced using
`docs/images/create_demo.py` in a new external runtime, without a model or worker.

No research source comments, raw model outputs, private walkthrough records,
credentials or weights are included. Research-runtime records, if present, contain
only counts and hashes. No agent-submitted research judgement is claimed.
Author self-review is not independent review, owner acceptance or merge authority.
