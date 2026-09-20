import json,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-comparison/r2';PUB=ROOT/'extras/der-publication/vs2-comparison-r2';W=ROOT/'working';R=ROOT/'extras/der-checkouts/vs2-comparison-semantic-r2'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';HELPER=ROOT/'extras/tooling/meerkritic-agent/agent.py'
identity=json.loads((E/'semantic-commits.json').read_text());archive=json.loads((E/'export-result.json').read_text());summary=json.loads((E/'verification-summary.json').read_text());assert summary['status']=='passed'
def run(args,label=None):
 p=subprocess.run([str(x) for x in args],cwd=R,capture_output=True,text=True,encoding='utf-8')
 if label:(E/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
assert run(git+['ls-remote','origin','refs/heads/main']).split()[0]==identity['base']
for branch in ('evidence/vs2-comparison-r2','feat/vs2-comparison-r2'):
 assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected remote branch exists; preserve it.'
run(git+['fetch',PUB,'refs/heads/evidence/vs2-comparison-r2:refs/heads/evidence/vs2-comparison-r2'],'archive-import')
run(git+['push','origin','refs/heads/evidence/vs2-comparison-r2'],'publish-archive')
assert run(git+['ls-remote','origin','refs/heads/evidence/vs2-comparison-r2']).split()[0]==archive['archive_commit']
run(git+['push','-u','origin','refs/heads/feat/vs2-comparison-r2'],'publish-branch')
assert run(git+['ls-remote','origin','refs/heads/feat/vs2-comparison-r2']).split()[0]==identity['commits'][-1]
base_url='https://github.com/FinnNk/Meerkritic/tree/'+archive['archive_commit']
commits=identity['commits'];tests=summary['checkpoints'][-1]['tests'];changes=summary['test_changes']
body=f'''This adds a reproducible command-line comparison of the fixed lexical baseline and embedding-based grouping method. It binds both methods to the same saved inputs, prepares a rating pack with method names hidden, and reports the agreed criteria from completed human ratings.

It also records the completed input-preparation pass: **33 valid drafts from 55 qualified sources**, below the agreed target of 40. All 22 failed outputs and 25 unresolved source checks are retained. EDR-0001 remains unregistered; no human labels, research grouping runs or adoption decision are claimed.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `{commits[0][:7]}` | Shared input text and the deterministic lexical baseline. |
| `{commits[1][:7]}` | Equal assessment budgets, masked groups and exact decision criteria. |
| `{commits[2][:7]}` | Exact stored-input/run binding, replay checks and failed-attempt accounting. |
| `{commits[3][:7]}` | Registration checks, immutable rating/report files and the operator guide. |
| `{commits[4][:7]}` | Current-document backfills and the measured input-preparation shortfall. |

## Validation

**Standard checks: passed** at `{commits[-1][:7]}`. [Evidence]({base_url}/records/r2/verification-summary.json)

{tests} tests passed; 0 skipped. All five semantic checkpoints passed separately with locked dependencies on Windows/Python 3.12.

| Behaviour | Tests added |
| --- | ---: |
| Lexical grouping and shared text | {changes['lexical_shared_text_added']} |
| Masking, completeness and criterion boundaries | {changes['masked_assessment_added']} |
| Stored evidence, failures and retry timing | {changes['evidence_binding_added']} |
| Registration and command-line publication | {changes['registration_publication_added']} |

Two earlier full runs hit an intermittent Windows temporary-Git cleanup lock. Isolated checks and the diagnostic full suite passed unchanged; the lock cause remains uncertain. [All attempts are retained]({base_url}/records/r2/verification-summary.json). Compared with base `{identity['base'][:7]}`, no existing tests were removed or altered. [Documentation checks]({base_url}/records/r2/docs-check.json): 326 local links, 77 tables, 59 imported-source hashes and actual command help. [Architecture delta]({base_url}/records/r2/architecture-delta.json): two modules added and shared grouping logic updated; contracts unchanged.

[DER review packet]({base_url}): exact diary/semantic tree equivalence and full author self-review. The earlier final documentation commit was superseded before verification/publication; both rounds are retained. This is local verification, not a hosted CI or independent approval claim.

## Decision needed before the study

The fixed candidate pool and single model pass cannot yield 40 usable inputs. Human repair of failed drafts is proposed, preserving the original failures and avoiding another model pass; it needs owner agreement and a separate workflow change. The current harness cannot edit failed jobs. No preparation rule or validation check has been relaxed.

After that decision: finish human input review, freeze and register the study, collect masked group ratings, record the outcome/owner decision, then complete the milestone review. This PR delivers the comparison tooling; it does not close VS2.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8')
url=run([PY,HELPER,'gh','pr','create','--base','main','--head','feat/vs2-comparison-r2','--title','feat: add reproducible grouping comparison tools','--body-file',E/'pr-body.md'],'publish-pr')
(E/'pr-url.txt').write_text(url+'\n',encoding='utf-8')
print(json.dumps({'pr':url,'head':commits[-1],'archive':archive['archive_commit']}))
