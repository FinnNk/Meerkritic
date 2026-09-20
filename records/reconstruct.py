"""Append four complete documentation propositions to the retained r1 series."""
import json
import os
from pathlib import Path
import subprocess
ROOT=Path('WORKSPACE')
R=ROOT/'extras/der-checkouts/vs2-interaction'
W=ROOT/'extras/der-checkouts/vs2-interaction-docs-semantic'
E=ROOT/'extras/der-evidence/vs2-interaction/r2'
D='4e26b9e7bc4b762425586eab80a3aa9011d094f9'
OLD='eaeecaafd37883f2cb6da09d2845886413a9a530'
env=os.environ.copy()
env.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=R.as_posix(),GIT_CONFIG_KEY_1='safe.directory',GIT_CONFIG_VALUE_1=W.as_posix())
def git(repo,*args,input=None):
    return subprocess.check_output(['git','-C',str(repo),*args],input=input,env=env)
assert json.loads((E/'diary-final-checks.json').read_text())['status']=='passed'
assert not git(R,'status','--porcelain').strip()
git(R,'worktree','add','-b','feat/vs2-interaction-docs',str(W),OLD)
def restore(revision,paths):
    git(W,'restore','--source',revision,'--staged','--worktree','--',*paths)
def commit(label,message):
    git(W,'diff','--check')
    git(W,'commit','-m',message)
    record={'proposition':label,'revision':git(W,'rev-parse','HEAD').decode().strip(),
            'tree':git(W,'rev-parse','HEAD^{tree}').decode().strip(),'message':message}
    (E/(label+'-identity.json')).write_text(json.dumps(record,indent=2))
    print(json.dumps(record),flush=True)
restore(D,['LICENSE.md','pyproject.toml','docs/sources.md'])
restore('3c37c6e6161abc9e0a768081e0243ec59314e63e',['README.md'])
commit('p6','docs: license Meerkritic under MIT')
for label,left,right,message in [
    ('p7','3c37c6e6161abc9e0a768081e0243ec59314e63e','2f03b050ad68f6120e304f8575edb21d33432762','docs: define reader-focused writing and review guidance'),
    ('p8','7c91a032bcb37fe5eb8f3a8cb13c4b2c24c234a6','6cecefa1b495009a5342b5fe5645250b04c81a9a','docs: organise task guides around steps and recovery'),
    ('p9','6cecefa1b495009a5342b5fe5645250b04c81a9a',D,'docs: clarify developer references and documentation navigation')]:
    patch=git(R,'diff','--binary',left,right)
    git(W,'apply','--index','-',input=patch)
    commit(label,message)
assert git(W,'rev-parse','HEAD^{tree}')==git(R,'rev-parse',D+'^{tree}')
assert not git(W,'status','--porcelain').strip()
