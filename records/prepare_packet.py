"""Retain r1 identities and bind documentation revision evidence to r2."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path('WORKSPACE')
R=ROOT/'extras/der-checkouts/vs2-interaction'
A=ROOT/'extras/der-checkouts/vs2-interaction-docs-archive'
E=ROOT/'extras/der-evidence/vs2-interaction/r2'
OLD=ROOT/'extras/der-evidence/vs2-interaction/r1'
B='ff9af2e68d989590ebe030002e2e3789c35efef0'
DB='dc6ba77119b2cf148cf014c54a7748953bd9735d'
D='4e26b9e7bc4b762425586eab80a3aa9011d094f9'
PREV='eaeecaafd37883f2cb6da09d2845886413a9a530'
S=json.loads((E/'p9-identity.json').read_text())['revision']
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
skill=R/'.agents/skills/double-entry-review/scripts/der.py'
def run(args,path=None):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if path:(E/path).write_text(p.stdout+p.stderr,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout
def write(name,value):
    (E/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
checks=[json.loads((E/(label+'-checks.json')).read_text()) for label in ('diary-final','p6','p7','p8','p9')]
assert all(c['status']=='passed' and c['clean'] for c in checks)
assert json.loads((E/'docs-check.json').read_text())['status']=='passed'
if not A.exists():
    run(['git','-c',f'safe.directory={R.as_posix()}','-c',f'safe.directory={(R/".git").as_posix()}',
         'clone','--no-hardlinks',str(R),str(A)])
commits=run(['git','-C',str(A),'rev-list','--reverse',B+'..'+S]).splitlines()
old_commits=run(['git','-C',str(A),'rev-list','--reverse',B+'..'+PREV]).splitlines()
assert commits[:5]==old_commits and len(commits)==9
records=[]
for index,label in enumerate(('p1','p2','p3-release','p4-release','p5-release')):
    path=OLD/(label+'-checks.json')
    record=json.loads(path.read_text())
    assert record['revision']==old_commits[index] and record['status']=='passed'
    records.append({'revision':old_commits[index],'record':'../r1/'+path.name,
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'passed'})
write('carry-forward.json',{'from_round':'r1','to_round':'r2','unchanged_commits':old_commits,
      'check_records':records,'review_record':'../r1/review.json',
      'review_sha256':hashlib.sha256((OLD/'review.json').read_bytes()).hexdigest(),
      'archive_commit':'2894cbdbe22b5a84ba387e7c710115b591698388',
      'scope':'Original five commit identities and their parent relationships are unchanged. Source, tests, lock and architecture contracts are unchanged by the four appends. Carry forward only r1 review/checks for those exact identities, including runtime evidence on eaeecaafd37883f2cb6da09d2845886413a9a530. No new runtime model call is claimed.'})
M=ROOT/'extras/der-evidence/pairs/vs2-interaction/rounds/r2/manifest.json'
if not M.exists():
    run([PY,str(skill),'snapshot','--repo',str(A),'--store',str(ROOT/'extras/der-evidence'),
        '--pair','vs2-interaction','--round','r2','--diary-base',DB,'--semantic-base',B,'--diary',D,'--semantic',S],'snapshot.json')
run([PY,str(skill),'equivalence','--repo',str(A),'--diary',D,'--semantic',S,'--diary-base',DB,'--semantic-base',B],'equivalence.json')
run([PY,str(skill),'check-round','--manifest',str(M),'--repo',str(A)],'check-round.json')
run([PY,str(skill),'inventory','--repo',str(A),'--base',B,'--tip',S],'inventory.json')
run(['git','-C',str(A),'range-diff',B+'..'+PREV,B+'..'+S],'range-diff.txt')
run(['git','--version'],'git-version.txt')
after=ROOT/'extras/der-checkouts/vs2-interaction-docs-p9'
before=ROOT/'extras/der-checkouts/vs2-interaction-integrated-base'
for name,repo in [('before',before),('after',after)]:
    run([str(after/'.venv/Scripts/python.exe'),str(after/'tools/architecture.py'),'snapshot','--root',str(repo)],f'architecture-{name}.json')
run([str(after/'.venv/Scripts/python.exe'),str(after/'tools/architecture.py'),'delta',str(E/'architecture-before.json'),str(E/'architecture-after.json')],'architecture-delta.json')
write('architecture-identities.json',{'before':B,'after':S,'generator':S,'schema':3,
      'note':'Same generator for both sides. r2 documentation changes no modules or contracts; MIT package metadata changes the source fingerprint.',
      'hashes':{n:hashlib.sha256((E/n).read_bytes()).hexdigest() for n in ('architecture-before.json','architecture-after.json','architecture-delta.json')}})
write('verification-summary.json',{'new_checks':checks,'unchanged_checkpoint_checks':'carry-forward.json',
      'documentation_checks':'docs-check.json','scope':'Windows/Python 3.12, checkpoint-owned locked environments; no hosted CI or new live model call claimed'})
print(json.dumps({'manifest':str(M),'sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'head':S}))
