import json,subprocess,os
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';D=ROOT/'extras/der-checkouts/vs2-draft-repair';S=ROOT/'extras/der-checkouts/vs2-draft-repair-semantic';W=ROOT/'working';base='e7726500930e79f0ba69becae5d12b77edbb5dea'
def git(repo,*args):
 p=subprocess.run(['git','-c','safe.directory='+repo.as_posix(),'-C',str(repo),*map(str,args)],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
check=json.loads((E/'diary-complete-checks.json').read_text());assert check['status']=='passed' and check['clean'];diary=check['revision'];assert git(D,'rev-parse','HEAD')==diary
p1=git(D,'rev-parse','9e8e91d');git(W,'worktree','add','-b','feat/vs2-draft-repair',S,p1)
paths=git(D,'diff-tree','--no-commit-id','--name-only','-r','5ec8d39').splitlines();git(S,'restore','--source='+diary,'--staged','--worktree','--',*paths);git(S,'commit','-m','feat: retain failed drafts through human decisions and selections');p2=git(S,'rev-parse','HEAD')
paths=git(D,'diff-tree','--no-commit-id','--name-only','-r','71fa5c5').splitlines()+['docs/images/failed-draft-assessment.png','docs/images/captures-draft-repair.json','docs/images/annotation-result.png','docs/images/annotation-assessment.png']
git(S,'restore','--source='+diary,'--staged','--worktree','--',*paths);git(S,'commit','-m','feat: expose grounded correction of failed drafts in the harness');p3=git(S,'rev-parse','HEAD')
git(S,'restore','--source='+diary,'--staged','--worktree','.');git(S,'commit','-m','docs: backfill correction guides and implementation records');p4=git(S,'rev-parse','HEAD');assert git(S,'rev-parse','HEAD^{tree}')==check['tree'];assert not git(S,'status','--porcelain')
record={'base':base,'diary':diary,'semantic_tree':check['tree'],'commits':[p1,p2,p3,p4],'mapping':{'P1':'9e8e91d policy retained exactly','P2':'5ec8d39 backend plus diary 3545567 legacy compatibility fix','P3':'71fa5c5 UI/new guide plus 1899ea3 screenshot updates','P4':'d816b7f maintained-document backfill'}}
(E/'semantic-commits.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
