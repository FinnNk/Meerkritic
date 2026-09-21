"""Publish this authorised candidate and its separate evidence using only App Git auth."""
import json
import subprocess
from pathlib import Path

ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/assessment-form/r1'
PUB=ROOT/'extras/der-publication/assessment-form-r1';W=ROOT/'working'
R=ROOT/'extras/der-checkouts/assessment-form-semantic'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
HELPER=ROOT/'extras/tooling/meerkritic-agent/agent.py'
i=json.loads((E/'semantic-commits.json').read_text())
archive=json.loads((E/'export-result.json').read_text())
summary=json.loads((E/'verification-summary.json').read_text())
assert summary['status']=='passed'

def run(args,label=None):
    p=subprocess.run([str(x) for x in args],cwd=R,capture_output=True,text=True,encoding='utf-8')
    if label:(E/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
    assert p.returncode==0,p.stdout+p.stderr
    return p.stdout.strip()

git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
parent=json.loads(run([PY,HELPER,'gh','pr','view','18','--json','state,headRefName,headRefOid']))
assert parent['state']=='OPEN' and parent['headRefOid']==i['base'],'Parent changed; reassess the stack.'
base=parent['headRefName']
assert run(git+['ls-remote','origin','refs/heads/'+base]).split()[0]==i['base']
for branch in ('evidence/assessment-form-r1','feat/assessment-form'):
    assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected remote branch.'
run(git+['fetch',PUB,'refs/heads/evidence/assessment-form-r1:refs/heads/evidence/assessment-form-r1'],'archive-import')
run(git+['push','origin','refs/heads/evidence/assessment-form-r1'],'publish-archive')
assert run(git+['ls-remote','origin','refs/heads/evidence/assessment-form-r1']).split()[0]==archive['archive_commit']
run(git+['push','-u','origin','refs/heads/feat/assessment-form'],'publish-branch')
assert run(git+['ls-remote','origin','refs/heads/feat/assessment-form']).split()[0]==i['commits'][-1]
c=i['commits'];u='https://github.com/FinnNk/Meerkritic/tree/'+archive['archive_commit']
body=f'''Correcting an interpretation currently requires editing raw JSON, and the **Edit** button does not explain that it saves immediately. This change provides labelled text fields, judgement dropdowns and add/remove controls for categories, quotes and applicability limits.

**Save edited assessment** saves the corrected fields and notes. **Accept original** explicitly keeps the model interpretation. List controls only update the unsaved form; validation errors retain its contents. Saved interpretations are readable without opening JSON. Existing open JSON forms remain compatible.

**Stacked on #18. Merge order: #17 → #18 → this PR.**

![Synthetic assessment editor with labelled issue text and judgement dropdowns.](https://raw.githubusercontent.com/FinnNk/Meerkritic/{c[-1]}/docs/images/annotation-assessment.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/{c[-1]}/docs/images/README.md). No research judgement is shown.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `{c[0][:7]}` | Complete field editing, unsaved list operations, recoverable validation, compatible old submissions and readable saved results, with tests and editing instructions. |
| `{c[1][:7]}` | Backfill the current guides and synthetic screenshots. |

## Validation

**Standard checks: passed** at `{c[-1][:7]}` — [evidence]({u}/records/r1/verification-summary.json). Both semantic checkpoints and the frozen diary use their own locked Windows/Python 3.12 environments. **241 tests; 0 skipped.**

| Test changes from #18 | Added | Altered | Removed |
| --- | ---: | ---: | ---: |
| Field submission, row operations, validation recovery, failed drafts, input bounds, exact source line endings and stale-tab protection | 8 | 0 | 0 |
| Existing decision-button expectations | 0 | 1 | 0 |

- [Browser checks]({u}/records/r1/browser-check.json): synthetic editing through save, retained invalid input, visible errors and a 600px layout.
- [Documentation]({u}/records/r1/docs-check.json): 367 local links and 59 imported source hashes checked; three synthetic captures inspected, including in the rendered guide.
- [Architecture]({u}/records/r1/architecture-delta.json): one web form adapter; no domain, persistence, dependency or architecture-contract changes.
- [DER evidence]({u}): exact diary/semantic tracked-tree equivalence, checkpoint checks and author self-review. Earlier failures and their corrections are retained. No independent approval or hosted CI run is claimed.

## Limits

Edits remain tab-local until submitted; this is not a durable draft workspace. Saved source assessments cannot be reopened or overwritten. The UI now makes these limits explicit and retains attempted values on a stale-tab conflict. A real cross-tab save discrepancy was recorded separately for research reconciliation; this change does not rewrite that judgement, rerun models or alter study criteria.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8')
url=run([PY,HELPER,'gh','pr','create','--base',base,'--head','feat/assessment-form','--title','feat: edit assessments with labelled form fields','--body-file',E/'pr-body.md'],'publish-pr')
(E/'pr-url.txt').write_text(url+'\n',encoding='utf-8')
print(json.dumps({'pr':url,'head':c[-1],'base':i['base'],'archive':archive['archive_commit']}))
