import json
import os
from pathlib import Path
import subprocess

root = Path('WORKSPACE')
repo = root/'working'
target = root/'extras/der-checkouts/source-reading-semantic'
evidence = root/'extras/der-evidence/source-reading/r1'
base = 'a39b989d8fbb6842c73703ff320eee81e45a1a52'
diary = '070d547bf0154b12282738ea499c4cb46244fb26'
env = os.environ.copy()
env.update(GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(repo), GIT_CONFIG_KEY_1='safe.directory', GIT_CONFIG_VALUE_1=str(target))
def git(path, *args):
    result = subprocess.run(['git','-C',str(path),*args],env=env,capture_output=True,text=True,encoding='utf-8')
    assert result.returncode == 0, result.stdout+result.stderr
    return result.stdout.strip()
assert json.loads((evidence/'diary-complete-checks.json').read_text())['status'] == 'passed'
git(repo,'worktree','add','-b','feat/source-reading',str(target),base)
commits=[]
git(target,'cherry-pick','bc33734')
commits.append(git(target,'rev-parse','HEAD'))
git(target,'cherry-pick','--no-commit','af811ee','f00e4f8','dde8b35')
git(target,'commit','-m','feat: preserve source reading context with human assessments')
commits.append(git(target,'rev-parse','HEAD'))
git(target,'cherry-pick','--no-commit','f425a62','070d547')
git(target,'commit','-m','docs: backfill preserved source guides and screenshot')
commits.append(git(target,'rev-parse','HEAD'))
assert not git(target,'status','--porcelain')
assert git(target,'rev-parse',diary+'^{tree}') == git(target,'rev-parse','HEAD^{tree}')
record=dict(base=base,diary=diary,commits=commits)
(evidence/'semantic-commits.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
