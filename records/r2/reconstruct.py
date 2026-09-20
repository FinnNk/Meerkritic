import json,subprocess,os
from pathlib import Path
root=Path('WORKSPACE');e=root/'extras/der-evidence/vs2-comparison/r2';old=root/'extras/der-evidence/vs2-comparison/r1';repo=root/'extras/der-checkouts/vs2-comparison';work=root/'extras/der-checkouts/vs2-comparison-semantic-r2';common=root/'working';identity=json.loads((old/'semantic-commits.json').read_bytes());check=json.loads((e/'diary-checks.json').read_bytes());assert check['status']=='passed' and check['clean'];frozen=check['revision'];base=identity['base'];parent=identity['commits'][3]
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(common),GIT_CONFIG_KEY_1='safe.directory',GIT_CONFIG_VALUE_1=str(repo),GIT_CONFIG_KEY_2='safe.directory',GIT_CONFIG_VALUE_2=str(work))
def git(r,*args,binary=False):
 p=subprocess.run(['git','-C',str(r),*map(str,args)],env=env,capture_output=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout if binary else p.stdout.decode('utf-8').strip()
notes='''# Documentation completion: round r2

Round r1 established the unchanged software. Its P1-P4 exact SHAs passed their own clean, locked checks. Before publishing, completion of the independent input-preparation work established 33 valid drafts from 55 qualified inputs, below the agreed target of 40. The last documentation proposition now records that finding, the frozen normalisation configuration and the owner amendment gate. No grouping comparison or human labels were supplied.

Only the final documentation proposition changes. Preserve r1's bundle and its unverified earlier P5; do not claim that P5 passed. Retain P1-P4 verbatim with their exact verification records. Verify the new diary and new P5/final tip separately. No code, tests, locks, contracts or criteria changed between rounds. This is completion of current documentation, not a fabricated implementation chronology.

P1 shared text/lexical baseline; P2 assessment criteria; P3 stored evidence binding; P4 registered commands/operator guide; P5 existing-document backfill plus actual input-preparation finding and small permitted evidence summary. The five-unit boundary rationale and contract challenges in r1/propositions.md still apply. Owner response to the preparation proposal remains pending.
'''
(e/'revision-notes.md').write_text(notes,encoding='utf-8');(e/'propositions.md').write_text((old/'propositions.md').read_text(encoding='utf-8')+'\n\n'+notes,encoding='utf-8')
git(common,'worktree','add','-b','feat/vs2-comparison-r2',work,parent)
paths=git(repo,'diff','--name-only',parent,frozen).splitlines();assert all(p.startswith('docs/') or p in ('IMPLEMENTATION_BACKLOG.yaml','tests/README.md') for p in paths)
for path in paths:
 target=work/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(git(repo,'show',f'{frozen}:{path}',binary=True))
git(work,'add','--',*paths);git(work,'commit','-m','docs: backfill comparison workflow and preparation findings','-m','Review-Unit: P5');tip=git(work,'rev-parse','HEAD');assert git(work,'rev-parse','HEAD^{tree}')==check['tree']
identity.update(diary=frozen,commits=[*identity['commits'][:4],tip],tree=check['tree']);(e/'semantic-commits.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
py=repo/'.venv/Scripts/python.exe';helper=work/'.agents/skills/double-entry-review/scripts/der.py'
for label,args in [('equivalence',['equivalence','--repo',work,'--diary',frozen,'--semantic',tip,'--diary-base',base,'--semantic-base',base]),('snapshot',['snapshot','--repo',work,'--store',root/'extras/der-evidence','--pair','vs2-comparison','--round','r2','--diary-base',base,'--semantic-base',base,'--diary',frozen,'--semantic',tip])]:
 p=subprocess.run([str(py),str(helper),*map(str,args)],env=env,capture_output=True,text=True,encoding='utf-8');(e/(label+'.json')).write_text(p.stdout,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
print(json.dumps(identity))
