"""Bind the C packet to exact checked identities and the owner's integrated prerequisite."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('WORKSPACE'); R=ROOT/'extras/der-checkouts/vs2-interaction'
A=ROOT/'extras/der-checkouts/vs2-interaction-archive'; E=ROOT/'extras/der-evidence/vs2-interaction/r1'
B='ff9af2e68d989590ebe030002e2e3789c35efef0'; DB='dc6ba77119b2cf148cf014c54a7748953bd9735d'
D='6bf1544b1fa1f70f188ae19fd08f55df78574787'; S=json.loads((E/'p5-identity.json').read_text())['revision']
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
skill=R/'.agents/skills/double-entry-review/scripts/der.py'
def run(args,path=None):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if path:(E/path).write_text(p.stdout+p.stderr,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout
checks=[json.loads((E/(label+'-checks.json')).read_text()) for label in ('integrated-base','diary-final2','p1','p2','p3-release','p4-release','p5-release')]
assert all(item['status']=='passed' for item in checks)
if not A.exists():run(['git','-c',f'safe.directory={R.as_posix()}', '-c',f'safe.directory={(R/".git").as_posix()}',
    'clone','--no-hardlinks',str(R),str(A)])
manifest=ROOT/'extras/der-evidence/pairs/vs2-interaction/rounds/r1/manifest.json'
if not manifest.exists():run([PY,str(skill),'snapshot','--repo',str(A),'--store',str(ROOT/'extras/der-evidence'),
    '--pair','vs2-interaction','--round','r1','--diary-base',DB,'--semantic-base',B,'--diary',D,'--semantic',S],'snapshot.json')
run([PY,str(skill),'equivalence','--repo',str(A),'--diary',D,'--semantic',S,'--diary-base',DB,'--semantic-base',B],'equivalence.json')
run([PY,str(skill),'check-round','--manifest',str(manifest),'--repo',str(A)],'check-round.json')
run([PY,str(skill),'inventory','--repo',str(A),'--base',B,'--tip',S],'inventory.json')
before=ROOT/'extras/der-checkouts/vs2-interaction-integrated-base'; after=ROOT/'extras/der-checkouts/vs2-interaction-p5-release'
for name,repo in [('before',before),('after',after)]:
    run([str(after/'.venv/Scripts/python.exe'),str(after/'tools/architecture.py'),'snapshot','--root',str(repo)],f'architecture-{name}.json')
run([str(after/'.venv/Scripts/python.exe'),str(after/'tools/architecture.py'),'delta',str(E/'architecture-before.json'),str(E/'architecture-after.json')],'architecture-delta.json')
(E/'architecture-identities.json').write_text(json.dumps({'before':B,'after':S,'generator':S,'schema':3,'note':'Both sides generated with final schema-3 generator; earlier archives unchanged','hashes':{
    n:hashlib.sha256((E/n).read_bytes()).hexdigest() for n in ('architecture-before.json','architecture-after.json','architecture-delta.json')}},indent=2))
(E/'verification-summary.json').write_text(json.dumps({'checks':checks,'scope':'Windows/Python 3.12; no other platform claim'},indent=2))
# Verify the ordered rebase mapping without transferring old checks to new SHAs.
old=run(['git','-C',str(A),'rev-list','--reverse','e81c2e867e714f2fed72d235eb44ba035b4bf302..'+DB]).splitlines()
new=run(['git','-C',str(A),'rev-list','--reverse','e81c2e867e714f2fed72d235eb44ba035b4bf302..'+B]).splitlines()
assert len(old)==len(new)==3
mapping=[]
for left,right in zip(old,new):
    lt=run(['git','-C',str(A),'rev-parse',left+'^{tree}']).strip()
    rt=run(['git','-C',str(A),'rev-parse',right+'^{tree}']).strip()
    assert lt==rt
    mapping.append({'reviewed':left,'integrated':right,'tree':lt})
(E/'pr12-integration.json').write_text(json.dumps({'pr':12,'integrated':B,'ordered_tree_mapping':mapping,
    'owner_statement':'Accepted and merged PR12; continue autonomously',
    'post_merge_checks':'integrated-base-checks.json','old_checks_remain_bound_to_reviewed_shas':True},indent=2))
print(json.dumps({'manifest':str(manifest),'sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}))
