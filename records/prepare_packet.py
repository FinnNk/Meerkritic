"""Create mechanical DER evidence and typed architecture snapshots for explicit frozen identities."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('WORKSPACE')
R=ROOT/'extras/der-checkouts/vs2-grouping'
A=ROOT/'extras/der-checkouts/vs2-grouping-archive'
E=ROOT/'extras/der-evidence/vs2-grouping/r1'
BASE='c9ef38f48b10d7876fe26babee36f2f15f258bf3'
D='0c1f39f31ba6ecba36d4568eaa66ebc54056079b'
S='125fd8c055b9c110efa1c4dd31dcc661358b32bc'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
skill=R/'.agents/skills/double-entry-review/scripts/der.py'

def run(args,path=None):
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if path: (E/path).write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout

if not A.exists():
    run(['git','-c',f'safe.directory={R.as_posix()}', '-c',f'safe.directory={(R/".git").as_posix()}',
         'clone','--no-hardlinks',str(R),str(A)])
manifest=ROOT/'extras/der-evidence/pairs/vs2-grouping/rounds/r1/manifest.json'
if not manifest.exists():
    run([PY,str(skill),'snapshot','--repo',str(A),'--store',str(ROOT/'extras/der-evidence'),
        '--pair','vs2-grouping','--round','r1','--diary-base',BASE,'--semantic-base',BASE,
        '--diary',D,'--semantic',S],'snapshot.json')
run([PY,str(skill),'equivalence','--repo',str(A),'--diary',D,'--semantic',S,
     '--diary-base',BASE,'--semantic-base',BASE],'equivalence.json')
run([PY,str(skill),'check-round','--manifest',str(manifest),'--repo',str(A)],'check-round.json')
run([PY,str(skill),'inventory','--repo',str(A),'--base',BASE,'--tip',S],'inventory.json')
before=ROOT/'extras/der-checkouts/vs2-grouping-p1'
after=ROOT/'extras/der-checkouts/vs2-grouping-p4'
run([str(before/'.venv/Scripts/python.exe'),str(before/'tools/architecture.py'),'snapshot','--root',str(before)],'architecture-before.json')
run([str(after/'.venv/Scripts/python.exe'),str(after/'tools/architecture.py'),'snapshot','--root',str(after)],'architecture-after.json')
run([str(after/'.venv/Scripts/python.exe'),str(after/'tools/architecture.py'),'delta',
     str(E/'architecture-before.json'),str(E/'architecture-after.json')],'architecture-delta.json')
identity={'before':'ab010c451f98c41f22c95dc49e078d787aac6ce3','after':S,
          'before_note':'P1 changes guidance only; its source/dependency architecture equals the integrated base.',
          'generator':'Each snapshot uses its own checkpoint tools/architecture.py',
          'hashes':{name:hashlib.sha256((E/name).read_bytes()).hexdigest() for name in
                    ('architecture-before.json','architecture-after.json','architecture-delta.json')}}
(E/'architecture-identities.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
checks=[json.loads((E/(name+'-checks.json')).read_text()) for name in ('diary-final','p1','p2','p3','p4')]
if any(c['status']!='passed' for c in checks): raise RuntimeError('Incomplete checkpoint evidence')
(E/'verification-summary.json').write_text(json.dumps({'checks':checks,'scope':'Required Windows/Python 3.12 contexts; no other platform claim'},indent=2),encoding='utf-8')
print(json.dumps({'manifest':str(manifest),'sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}))
