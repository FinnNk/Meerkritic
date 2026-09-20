# Research interaction: documentation revision evidence

This standalone archive preserves round r2 of PR13. It is not application history.
The canonical manifest, Git bundle and captured local ledger retain original bytes.
The records directory contains sanitised methods, logs, identities, architecture
records, review scope and original/export hashes. No runtime datasets, keys,
installation tokens, model weights or private research data are included.

1. Verify SHA256SUMS and read records/review-notes.md and carry-forward.json.
2. Use the Git bundle with a separate repository; run the pinned DER helper's
   check-round against canonical/manifest.json.
3. Check out each semantic commit independently, install its locked environment
   using uv sync --locked, then run uv run --locked python tools/check.py.
4. Adapt WORKSPACE/HOST_USER placeholders in records/verify.py and docs_check.py
   to reproduce the Windows/Python 3.12 and read-only documentation checks.

The original five commit identities, reviews and checks remain in the [r1 archive]
(https://github.com/FinnNk/Meerkritic/tree/2894cbdbe22b5a84ba387e7c710115b591698388).
Their exact mapping is in carry-forward.json. All four appended commits and the
new frozen diary were checked afresh. No new live model call or hosted CI run is
claimed. Author changes review is not independent review or owner approval.
