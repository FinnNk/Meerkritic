import json,os,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/source-reading/r2'
R=ROOT/'extras/der-checkouts/source-reading-semantic'
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
def git(*args):
 p=subprocess.run(['git','-C',str(R),*args],env=env,capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
 return p.stdout.strip()
old=json.loads((E.parent/'r1/semantic-commits.json').read_text())
check=json.loads((E/'diary-checks.json').read_text())
assert check['status']=='passed' and check['clean']
assert git('rev-parse','HEAD')==old['commits'][-1] and not git('status','--porcelain')
new=[]
for sha in ('cb3957a','8985f91'):
 git('cherry-pick',sha);new.append(git('rev-parse','HEAD'))
assert git('rev-parse','HEAD^{tree}')==check['tree']
record=dict(base=old['base'],diary=check['revision'],previous_tip=old['commits'][-1],commits=old['commits']+new)
(E/'semantic-commits.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
(E/'range-diff.txt').write_text(git('range-diff',old['base']+'..'+old['commits'][-1],old['base']+'..'+new[-1]),encoding='utf-8')
print(json.dumps(record))
