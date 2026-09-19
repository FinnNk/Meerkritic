import json, subprocess
from pathlib import Path
R=Path('$WORKSPACE/extras/der-checkouts/vs1-annotation')
E=Path('$WORKSPACE/extras/der-evidence/vs1-annotation/r1')
S=R.with_name('vs1-annotation-semantic')
base='b9ffa2ee49b60758dba6832f08b988f797b439af'
diary='9d5124098a79a97d3b88a064e979a0b04451f410'
assert json.loads((E/'r1-diary-checks.json').read_text(encoding='utf-8'))['status']=='passed'
def git(path,*args):
    return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
git(R,'worktree','add','-b','feat/annotation-review',str(S),base)
groups=[('docs: confirm process-lock recovery is implemented',['docs/adr/README.md','docs/adr/ADR-0006-recover-jobs-under-process-lock.md']),
('feat: persist grounded human decisions and review queries',['src/semantic_reviewer/application/annotations.py','src/semantic_reviewer/adapters/annotations.py','src/semantic_reviewer/adapters/migrations/004_annotations.sql','src/semantic_reviewer/bootstrap.py','tools/run.py','tests/test_annotations.py','docs/development/annotations.md'])]
commits=[]
for index,(message,paths) in enumerate(groups):
    git(S,'checkout',diary,'--',*paths)
    if index==1:
        git(S,'checkout','1df3e0b','--','docs/development/annotations.md')
    git(S,'commit','-m',message)
    commits.append(git(S,'rev-parse','HEAD'))
remaining=git(S,'diff','--name-only','HEAD',diary).splitlines()
git(S,'checkout',diary,'--',*remaining)
git(S,'commit','-m','feat(web): review interpretations and track annotation progress')
commits.append(git(S,'rev-parse','HEAD'))
assert git(S,'rev-parse','HEAD^{tree}')==git(R,'rev-parse',diary+'^{tree}')
(E/'series.json').write_text(json.dumps({'base':base,'diary':diary,'semantic':commits[-1],'commits':commits},indent=2),encoding='utf-8')
print(json.dumps(commits))
