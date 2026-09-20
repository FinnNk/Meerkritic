import json, subprocess
from pathlib import Path
R=Path('$WORKSPACE/extras/der-checkouts/vs1-validation')
E=Path('$WORKSPACE/extras/der-evidence/vs1-validation/r1')
S=R.with_name('vs1-validation-semantic')
base='843ff161d49e096d1da2a55cacf75acac03e97f3'
diary='0ea4edeae12029bcbbd1db11843fe41824651220'
assert json.loads((E/'r1-diary-checks.json').read_text(encoding='utf-8'))['status']=='passed'
def git(path,*args):
    return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
git(R,'worktree','add','-b','feat/vs1-validation',str(S),base)
groups=[('feat: catalogue immutable artefacts and structured job logs',[
    'src/semantic_reviewer/adapters/migrations/005_artefacts.sql','src/semantic_reviewer/adapters/results.py',
    'src/semantic_reviewer/adapters/jobs.py','src/semantic_reviewer/application/jobs.py',
    'src/semantic_reviewer/bootstrap.py','tools/run.py','tests/test_artefacts.py','docs/development/operational-evidence.md']),
('feat: index external DER readiness references',[
    'src/semantic_reviewer/adapters/migrations/006_review_references.sql','src/semantic_reviewer/adapters/reviews.py',
    'src/semantic_reviewer/application/reviews.py','src/semantic_reviewer/bootstrap.py','src/semantic_reviewer/asgi.py',
    'src/semantic_reviewer/web/app.py','src/semantic_reviewer/web/templates/base.html','src/semantic_reviewer/web/templates/reviews.html',
    'tools/run.py','tests/test_review_references.py','docs/development/operational-evidence.md']),
('feat(routing): reserve explicit policy continuity records',[
    'src/semantic_reviewer/routing/continuity.py','tests/test_routing_continuity.py','docs/development/routing.md'])]
commits=[]
for index,(message,paths) in enumerate(groups):
    git(S,'checkout',diary,'--',*paths)
    if index==0:
        git(S,'checkout','400b734','--','src/semantic_reviewer/bootstrap.py','tools/run.py')
        p=S/'docs/development/operational-evidence.md'
        p.write_text(p.read_text(encoding='utf-8').split('## DER references')[0].rstrip()+'\n',encoding='utf-8')
        git(S,'add','docs/development/operational-evidence.md')
    git(S,'commit','-m',message)
    commits.append(git(S,'rev-parse','HEAD'))
remaining=git(S,'diff','--name-only','HEAD',diary).splitlines()
git(S,'checkout',diary,'--',*remaining)
git(S,'commit','-m','test: verify the complete VS1 data-to-annotation path')
commits.append(git(S,'rev-parse','HEAD'))
assert git(S,'rev-parse','HEAD^{tree}')==git(R,'rev-parse',diary+'^{tree}')
(E/'series.json').write_text(json.dumps({'base':base,'diary':diary,'semantic':commits[-1],'commits':commits},indent=2),encoding='utf-8')
print(json.dumps(commits))
