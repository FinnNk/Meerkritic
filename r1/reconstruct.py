"""Reassemble verified diary propositions without editing their frozen content."""
import json,subprocess
from pathlib import Path
R=Path('$WORKSPACE/extras/der-checkouts/vs1-architecture-review')
E=Path('$WORKSPACE/extras/der-evidence/vs1-architecture-review/r1')
S=R.with_name('vs1-architecture-review-semantic')
base='0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9'
diary='45c29fcfea43c99026a9ae54051df61d905e30fc'
check=json.loads((E/'r1-diary-checks.json').read_text())
assert check['revision']==diary and check['status']=='passed'
def git(root,*args):
 return subprocess.check_output(['git','-c','safe.directory='+str(root),'-C',str(root),*args],text=True).strip()
assert not git(R,'status','--porcelain')
git(R,'worktree','add','-b','refactor/vs1-milestone-architecture-review',str(S),base)
groups=[
 ('docs: define milestone architecture and contract reviews',['ef5b8b2']),
 ('fix: reject contradictory normalisation completions',['1d01b07','e54439b']),
 ('refactor: make artefact metadata and maintenance explicit',['05e8d4a','9d881a9']),
 ('refactor: own source lookup and exclusive worker execution',['287967d']),
 ('refactor: isolate model controls from task context',['e84fc76']),
 ('feat: expose public contracts in architecture snapshots',['24844da','3cb5891']),
 ('docs: complete existing public operation contracts',['394af60']),
 ('docs: reconcile maintained guidance with delivered VS1',['1780f77']),
 ('docs: record VS1 milestone findings and confirmations',['45c29fc'])]
commits=[]
for index,(title,diaries) in enumerate(groups,1):
 for revision in diaries: git(S,'cherry-pick','--no-commit',revision)
 git(S,'commit','-m',title,'-m',f'Review-Unit: P{index}')
 commits.append(git(S,'rev-parse','HEAD'))
 (E/'series-progress.json').write_text(json.dumps(commits,indent=2))
assert git(S,'rev-parse','HEAD^{tree}')==git(R,'rev-parse',diary+'^{tree}')
(E/'series.json').write_text(json.dumps({'base':base,'diary':diary,'semantic':commits[-1],'commits':commits,'titles':[t for t,_ in groups]},indent=2))
print(json.dumps({'commits':commits,'equivalent':True}))
