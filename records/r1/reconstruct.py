"""Reconstruct two complete propositions from the verified diary, without edits."""
import json
import os
import subprocess
from pathlib import Path

ROOT=Path('WORKSPACE')
W=ROOT/'working'; R=ROOT/'extras/der-checkouts/assessment-form-semantic'
E=ROOT/'extras/der-evidence/assessment-form/r1'
B='796db0edc2032ed7ff0c518eecadd718b91c3e22'
D='97af70e1ad642c2e830d3eb68f9948af9b46e6ec'
check=json.loads((E/'diary-final-checks.json').read_text())
assert check['revision']==D and check['status']=='passed' and check['clean']
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(W),GIT_CONFIG_KEY_1='safe.directory',GIT_CONFIG_VALUE_1=str(R))
def git(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],env=env,capture_output=True,text=True,encoding='utf-8')
    assert p.returncode==0,p.stdout+p.stderr
    return p.stdout.strip()
assert not R.exists()
git(W,'worktree','add','-b','feat/assessment-form',str(R),B)
git(R,'restore','--source='+D,'--staged','--worktree','--','src','tests','docs/development/assessment-form.md')
git(R,'commit','-m','feat: edit assessments using labelled form fields')
p1=git(R,'rev-parse','HEAD')
git(R,'restore','--source='+D,'--staged','--worktree','--','.')
git(R,'commit','-m','docs: backfill assessment guides and screenshots')
p2=git(R,'rev-parse','HEAD')
assert git(R,'rev-parse','HEAD^{tree}')==git(R,'rev-parse',D+'^{tree}')
assert not git(R,'status','--porcelain')
result={'base':B,'diary':D,'commits':[p1,p2]}
(E/'semantic-commits.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
