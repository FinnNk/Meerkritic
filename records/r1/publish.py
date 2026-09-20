import json,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';PUB=ROOT/'extras/der-publication/vs2-draft-repair-r1';W=ROOT/'working';R=ROOT/'extras/der-checkouts/vs2-draft-repair-semantic'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';HELPER=ROOT/'extras/tooling/meerkritic-agent/agent.py'
i=json.loads((E/'semantic-commits.json').read_text());archive=json.loads((E/'export-result.json').read_text());summary=json.loads((E/'verification-summary.json').read_text());assert summary['status']=='passed'
def run(args,label=None):
 p=subprocess.run([str(x) for x in args],cwd=R,capture_output=True,text=True,encoding='utf-8')
 if label:(E/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
 assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
assert run(git+['ls-remote','origin','refs/heads/main']).split()[0]==i['base']
for branch in ('evidence/vs2-draft-repair-r1','feat/vs2-draft-repair'):
 assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected existing branch; preserve it'
run(git+['fetch',PUB,'refs/heads/evidence/vs2-draft-repair-r1:refs/heads/evidence/vs2-draft-repair-r1'],'archive-import')
run(git+['push','origin','refs/heads/evidence/vs2-draft-repair-r1'],'publish-archive');assert run(git+['ls-remote','origin','refs/heads/evidence/vs2-draft-repair-r1']).split()[0]==archive['archive_commit']
run(git+['push','-u','origin','refs/heads/feat/vs2-draft-repair'],'publish-branch');assert run(git+['ls-remote','origin','refs/heads/feat/vs2-draft-repair']).split()[0]==i['commits'][-1]
u='https://github.com/FinnNk/Meerkritic/tree/'+archive['archive_commit'];c=i['commits'];checks=json.loads((E/'docs-check.json').read_text());image='https://raw.githubusercontent.com/FinnNk/Meerkritic/'+c[-1]+'/docs/images/failed-draft-assessment.png'
body=f'''A retained draft that fails schema or source-evidence validation can now be corrected or rejected in the harness. The page shows the original source, preserves an invalid edit for correction, and saves a valid human interpretation separately. **The original job stays failed and its output remains unchanged.** No additional model pass is introduced.

This implements the agreed EDR-0001 preparation amendment. Successful drafts still offer Accept/Edit/Reject; failed drafts offer Edit/Reject only. Provider or missing-output failures remain for inspection. Corrected drafts can enter saved selections; rejected failures remain explicit exclusions. Existing selection files stay readable.

![Synthetic failed-draft assessment with its original draft and Edit/Reject controls.]({image})

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/{c[-1]}/docs/images/README.md). The image illustrates the controls, not a research judgement.

## Review sequence

| Commit | Review proposition |
| --- | --- |
| `{c[0][:7]}` | Record the agreed preparation amendment and preservation decision. |
| `{c[1][:7]}` | Preserve failed outputs through decisions, progress and versioned selections, including legacy compatibility. |
| `{c[2][:7]}` | Add the source-backed correction screen, focused guide and browser coverage. |
| `{c[3][:7]}` | Backfill current guides, screenshots and implementation records; mark ADR-0013 implemented. |

## Validation

**Standard checks: passed** at `{c[-1][:7]}`. [Evidence]({u}/records/r1/verification-summary.json). All four semantic checkpoints passed separately with locked dependencies on Windows/Python 3.12; final total **229 tests, 0 skipped**.

| Coverage added | Tests |
| --- | ---: |
| Decision eligibility, immutable provenance, atomic events, restart, progress and selection compatibility | 10 |
| Browser controls, escaped text, retained edits and infrastructure failures | 4 |

No existing test was removed or altered. A full run caught a legacy-result compatibility regression; it was fixed before reconstruction. Earlier runs also hit an intermittent Windows temporary-Git cleanup lock. A 40-run isolated check passed using the normal OS temporary directory, which subsequent verification uses; the lock owner remains unidentified. [Failures and dispositions]({u}/records/r1/backend-discovery.md) are retained, with no ignored errors or weakened checks.

- [Upgrade rehearsal]({u}/records/r1/upgrade-rehearsal.json): every application table unchanged on a study-database copy; all 33 successful and 22 failed outputs retain their hashes and correct actions.
- [Live upgrade]({u}/records/r1/live-after.json): all 55 original result files unchanged; zero research annotations or grouping runs.
- [Synthetic browser exercise]({u}/records/r1/browser-check.json): invalid correction retained, valid correction saved, original failure still visible.
- [Documentation]({u}/records/r1/docs-check.json): links, tables, imported-source hashes and screenshots checked. [Typed architecture delta]({u}/records/r1/architecture-delta.json): existing interfaces extended; no new modules or boundary exceptions.
- [DER packet]({u}): exact diary/semantic tracked-tree equivalence and full author self-review. This is local verification, not independent approval or a hosted CI claim.

## Study handoff

The database is backed up before upgrade. No research annotation or additional model call was made. Human **input reviews** can now proceed in the fixed candidate order, stopping at 40 usable inputs or the agreed shortfall limit, with at most five per repository. Forty is possible, not guaranteed. Group-coherence ratings wait for the reviewed selection to be frozen and EDR-0001 registered; VS2 remains active.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8');url=run([PY,HELPER,'gh','pr','create','--base','main','--head','feat/vs2-draft-repair','--title','feat: correct failed drafts without replacing model evidence','--body-file',E/'pr-body.md'],'publish-pr');(E/'pr-url.txt').write_text(url+'\n',encoding='utf-8');print(json.dumps({'pr':url,'head':c[-1],'archive':archive['archive_commit']}))
