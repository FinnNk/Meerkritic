import json,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-study-tools/r2';PUB=ROOT/'extras/der-publication/vs2-study-tools-r2';W=ROOT/'working';R=ROOT/'extras/der-checkouts/vs2-study-tools-semantic-r2'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';HELPER=ROOT/'extras/tooling/meerkritic-agent/agent.py'
identity=json.loads((E/'semantic-commits.json').read_text());archive=json.loads((E/'export-result.json').read_text());summary=json.loads((E/'verification-summary.json').read_text());assert summary['status']=='passed'
def run(args,label=None):
 p=subprocess.run([str(x) for x in args],cwd=R,capture_output=True,text=True,encoding='utf-8')
 if label:(E/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
assert run(git+['ls-remote','origin','refs/heads/main']).split()[0]==identity['base']
for branch in ('evidence/vs2-study-tools-r2','feat/vs2-study-tools'):
 assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected remote branch exists; preserve it.'
run(git+['fetch',PUB,'refs/heads/evidence/vs2-study-tools-r2:refs/heads/evidence/vs2-study-tools-r2'],'archive-import')
run(git+['push','origin','refs/heads/evidence/vs2-study-tools-r2'],'publish-archive')
assert run(git+['ls-remote','origin','refs/heads/evidence/vs2-study-tools-r2']).split()[0]==archive['archive_commit']
run(git+['push','-u','origin','refs/heads/feat/vs2-study-tools'],'publish-branch')
assert run(git+['ls-remote','origin','refs/heads/feat/vs2-study-tools']).split()[0]==identity['commits'][-1]
base_url='https://github.com/FinnNk/Meerkritic/tree/'+archive['archive_commit']
commits=identity['commits'];tests=summary['checkpoints'][-1]['tests'];changes=summary['test_changes']
body=f'''Preparing study inputs by hand leaves room to change the sample accidentally or lose failed and rejected records. This adds a command-line workflow that fixes the candidate order, retains exclusions and records each source check and human review without overwriting earlier evidence.

It records Finn's agreement to **EDR-0001 (Choose an initial discovery grouping method)** while keeping the study unregistered. The prepared pool contains 80 candidates across 45 development repositories, with 12 repositories held out. These are candidates for source verification, not approved research inputs.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `{commits[0][:7]}` | Record the explicit protocol agreement and freeze this bounded implementation scope. |
| `{commits[1][:7]}` | Reproduce candidate order, holdouts and complete exclusions from pinned source bytes. |
| `{commits[2][:7]}` | Record ordered review attempts, enforce limits and preserve immutable evidence; includes the operator guide. |
| `{commits[3][:7]}` | Backfill preparation identities, integration history and remaining study gates. |

## Validation

**Standard checks:** Passed · revision `{commits[-1][:7]}` · [Evidence]({base_url}/records/r2/verification-summary.json)

{tests} tests passed; 0 skipped. Every semantic checkpoint passed in its own locked Windows/Python 3.12 environment.

| Behaviour | Added tests |
| --- | ---: |
| Candidate ordering, exclusions and source validation | {changes['source_sampling_added']} |
| Review evidence, quotas, shortfall and immutable command-line records | {changes['attempt_and_publication_added']} |

No existing tests removed or altered. [Same-host replay]({base_url}/records/r2/sample-replay-summary.json) reproduced the original plan's exact byte hash. [Documentation checks]({base_url}/records/r2/docs-check.json) verified 316 local links and 59 imported-source hashes. [Architecture delta]({base_url}/records/r2/architecture-delta.json): one domain module added; existing boundaries/contracts unchanged.

[DER review packet]({base_url}): final diary/semantic trees match exactly. A reconstruction-only import-format error was caught at an intermediate checkpoint, retained and corrected before publication. Review is author self-review, not independent approval.

## Remaining work

- Qualify original sources, freeze normalisation configuration and collect the agreed human-reviewed inputs. The log records assertions; it does not authenticate people or prove source validity.
- Implement the lexical baseline, method-masked rating pack and analysis in the next material batch, stacked if this PR remains unmerged.
- Complete and commit registration before collecting grouping results or ratings. No comparison, human labels, method adoption or full slice closure is claimed here.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8')
url=run([PY,HELPER,'gh','pr','create','--base','main','--head','feat/vs2-study-tools','--title','feat: prepare reproducible study inputs','--body-file',E/'pr-body.md'],'publish-pr')
(E/'pr-url.txt').write_text(url+'\n',encoding='utf-8')
print(json.dumps({'pr':url,'head':commits[-1],'archive':archive['archive_commit']}))
