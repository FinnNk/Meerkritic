from pathlib import Path
import sqlite3,json,hashlib
from datetime import datetime,timezone
root=Path('WORKSPACE');study=root/'extras/research/edr-0001';e=root/'extras/der-evidence/vs2-draft-repair/r1';backup=study/'backups/before-failed-draft-correction.sqlite3';backup.parent.mkdir(exist_ok=True);assert not backup.exists()
src=sqlite3.connect(study/'runtime/state.sqlite3');dst=sqlite3.connect(backup);src.backup(dst);dst.close();counts={name:src.execute('select count(*) from '+name).fetchone()[0] for name in ['job','annotation','event','discovery_run']};assert counts['annotation']==0 and counts['job']==55 and counts['discovery_run']==0
original={str(p.relative_to(study/'runtime')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (study/'runtime/results').glob('*.json')};src.close()
record={'recorded_at':datetime.now(timezone.utc).isoformat(),'backup':str(backup),'backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'counts':counts,'original_artefacts':original};(e/'live-before.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
p=study/'INPUT-REVIEW.md';old=p.read_text(encoding='utf-8');(study/'INPUT-REVIEW-before-correction.md').write_text(old,encoding='utf-8');table=old[old.index('| Rank |'):];new='''# Review the prepared study inputs

The owner agreed human correction of retained failed drafts on 20 September 2026.
The fixed pool has 55 verified sources: 33 successful drafts and 22 retained failures.
These are input-review judgements; group-coherence ratings come after selection
freeze and registration. Forty usable inputs are possible, not guaranteed.

- Work down the table in candidate-rank order. Missing ranks are retained unresolved
  source checks, not invitations to choose replacements. The first unresolved
  position is already recorded; later preparation records will be reconciled with
  the actual saved human decisions and source receipts before selection freeze.
- Open **Original** for provenance and **Open job** for the supplied source/draft.
  Expand **Source for your assessment**. Supplied text can differ from the original
  formatting; judge against the supplied evidence without inventing missing context.
- Successful drafts offer **Accept / Edit / Reject**. Failed drafts offer only
  **Edit / Reject**. An edit must retain the complete JSON structure and use exact,
  unique quotes from the supplied comment or code. Add a reason when rejecting.
- Each action saves immediately and cannot be overwritten through this screen.
  Stop and flag a mistaken saved decision; do not create a replacement model run.
- Stop at **40 usable Accept/Edit inputs**, with **at most five per repository**.
  Skip later candidates in a repository once it reaches five; keep their positions
  in the log. A Reject does not count as usable. Stop if the fixed pool is exhausted.
- Do not use the general completion-ordered queue for this study. Do not queue new
  normalisation or grouping runs. The existing outputs are sufficient for this stage.
- The agent will read the saved decisions, preserve their exact IDs and reconcile
  the ordered preparation ledger. It will not supply judgements on your behalf.

'''+table;p.write_text(new,encoding='utf-8');print(json.dumps({'backup':str(backup),'counts':counts,'artefacts':len(original),'handoff':str(p)}))
