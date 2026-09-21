"""Publish the authorised source-reading stack through the configured App only."""
import json
import subprocess
from pathlib import Path

ROOT=Path('WORKSPACE'); E=ROOT/'extras/der-evidence/source-reading/r1'
PUB=ROOT/'extras/der-publication/source-reading-r1'; W=ROOT/'working'
R=ROOT/'extras/der-checkouts/source-reading-semantic'
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
parent=json.loads(run([PY,HELPER,'gh','pr','view','21','--json','state,headRefName,headRefOid']))
assert parent['state']=='OPEN' and parent['headRefOid']==i['base'],'Parent changed; reassess stack.'
base=parent['headRefName']
assert run(git+['ls-remote','origin','refs/heads/'+base]).split()[0]==i['base']
for branch in ('evidence/source-reading-r1','feat/source-reading'):
    assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected remote branch.'
run(git+['fetch',PUB,'refs/heads/evidence/source-reading-r1:refs/heads/evidence/source-reading-r1'],'archive-import')
run(git+['push','origin','refs/heads/evidence/source-reading-r1'],'publish-archive')
assert run(git+['ls-remote','origin','refs/heads/evidence/source-reading-r1']).split()[0]==archive['archive_commit']
run(git+['push','-u','origin','refs/heads/feat/source-reading'],'publish-branch')
assert run(git+['ls-remote','origin','refs/heads/feat/source-reading']).split()[0]==i['commits'][-1]
c=i['commits']; u='https://github.com/FinnNk/Meerkritic/tree/'+archive['archive_commit']
body=f'''Flattened dataset diffs make unrelated lines appear connected during assessment. This change shows **Preserved GitHub source**, with its retained line breaks, above **Dataset text supplied to the model**. Difference labels distinguish whitespace changes from other changes; the original model input and outputs remain untouched.

New decisions record which additional source was presented. Old tabs cannot silently save against newly attached context, and missing or damaged attachments block review. Exact evidence quotes still come from the dataset text. [ADR-0015](https://github.com/FinnNk/Meerkritic/blob/{c[-1]}/docs/adr/ADR-0015-separate-review-context-from-model-input.md) records the decision and limits.

**Stacked on #21. Merge order: #17, #18, #20, #21, then this PR.**

![Synthetic source panel showing preserved line breaks and the separate dataset view.](https://raw.githubusercontent.com/FinnNk/Meerkritic/{c[-1]}/docs/images/preserved-source.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/{c[-1]}/docs/images/README.md). No research judgement is shown.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `{c[0][:7]}` | Assessment policy, accepted ADR and prospective study-preparation amendment. |
| `{c[1][:7]}` | Complete import, two-view assessment, immutable source identity, stale-form protection and selection provenance, with tests and operating instructions. |
| `{c[2][:7]}` | Backfill current guides, backup instructions and the synthetic screenshot. |

## Validation

**Standard checks: passed** at `{c[-1][:7]}` - [evidence]({u}/records/r1/verification-summary.json). **253 tests; 0 skipped.** All three semantic checkpoints and the frozen diary passed in their own locked Windows/Python 3.12 environments.

| Test changes from #21 | Added | Altered | Removed |
| --- | ---: | ---: | ---: |
| Source identity, retention, redirects, standalone import, escaping, stale forms, races, exact quotes and selection integrity | 12 | 0 | 0 |
| Existing thread-boundary spy forwards the new keyword argument; its assertion is unchanged | 0 | 1 | 0 |

- [Live migration/import]({u}/records/r1/live-runtime.json): 54 attachments; the existing annotation, 58 dataset/result files and 332 earlier events preserved. No new research decisions or model calls.
- [Browser verification]({u}/records/r1/browser-check.json): synthetic save retains context and notes; [live read-only check]({u}/records/r1/live-browser-check.json) confirms the new source views and matching form identity.
- [Documentation]({u}/records/r1/docs-check.json): 385 local links and 59 imported source hashes checked. Screenshot inspected directly; local-file rendered-guide preview was blocked and is not claimed as verified.
- [Architecture]({u}/records/r1/architecture-delta.json): two modules isolate source-reading contracts and storage; no architecture contracts, ignores or dependencies changed.
- [Double-Entry Review evidence]({u}): exact diary/semantic tracked-tree equivalence, checkpoint checks and author self-review. Failed diagnostics and corrections are retained.

## Limits

The recorded source was presented, not necessarily read. Retained receipts establish local consistency, not independent GitHub authentication. Existing annotations are not backfilled. This change makes no claim that formatting improves model quality; that would require a separately pre-registered comparison. An earlier cross-tab assessment discrepancy remains a separate research reconciliation task.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8')
url=run([PY,HELPER,'gh','pr','create','--base',base,'--head','feat/source-reading','--title','feat: show preserved source alongside model input','--body-file',E/'pr-body.md'],'publish-pr')
(E/'pr-url.txt').write_text(url+'\n',encoding='utf-8')
print(json.dumps({'pr':url,'head':c[-1],'base':i['base'],'archive':archive['archive_commit']}))
