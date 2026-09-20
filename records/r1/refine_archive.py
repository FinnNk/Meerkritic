from pathlib import Path
p=Path('WORKSPACE/extras/der-evidence/assessment-clarity/r1/export_packet.py');t=p.read_text(encoding='utf-8-sig');start=t.index('(PUB/\'README.md\').write_text("""');end=t.index('""",encoding=\'utf-8\')',start)
body='''# Assessment clarity: review evidence

This separate archive preserves true implementation chronology and three semantic
review propositions. It is not application ancestry and must not be merged.

- `canonical/rounds/r1` contains the immutable equivalent-pair manifest and bundle.
- `records/r1/verification-summary.json` derives standard-check status and test
  totals from each exact checkpoint's own locked Windows/Python environment.
- `records/r1/review-notes.md` records contract challenges and author self-review.
- `records/r1/discoveries.md` retains the prompt-version expectation failure and
  rejected screenshot attempts, with their dispositions.
- `records/r1/schema-compatibility.json` and `live-after.json` verify unchanged
  original model outputs and zero saved research judgements.
- `records/r1/architecture-*.json`, `docs-check.json` and `browser-check.json` cover
  typed architecture, current documentation and synthetic interface inspection.

Verify SHA256SUMS before importing the bundle into a separate repository. Canonical
files retain their bytes; export-index.json maps sanitised auxiliary files to the
original local hashes. Use the pinned DER helper to check the manifest. Check out
each semantic commit separately, install Python 3.12, run `uv sync --locked`, then
`uv run --locked python tools/check.py`. Adapt local paths in the retained scripts
to reproduce on another host. Verification here used Windows and the normal OS
temporary directory, following the predecessor's observed workspace cleanup locks.

No raw research dataset, source comments, model outputs, private walkthrough notes,
weights or credentials are included. Original model outputs remain in external
research storage. No research annotation, grouping comparison or EDR registration
is claimed. Author self-review is not independent review or owner approval.
'''
t=t[:start]+'(PUB/\'README.md\').write_text("""'+body+t[end:];p.write_text(t,encoding='utf-8')
