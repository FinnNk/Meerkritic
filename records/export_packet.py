"""Export an explicit sanitised review packet; preserve canonical DER bytes unchanged."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path('WORKSPACE')
E=ROOT/'extras/der-evidence/vs2-interaction/r2'
PAIR=ROOT/'extras/der-evidence/pairs/vs2-interaction'
M=PAIR/'rounds/r2/manifest.json'
A=ROOT/'extras/der-checkouts/vs2-interaction-docs-archive'
R=ROOT/'extras/der-checkouts/vs2-interaction'
PUB=ROOT/'extras/der-publication/vs2-interaction-r2'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
SKILL=R/'.agents/skills/double-entry-review/scripts/der.py'
actor={'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'vs2-interaction-2026-09-20'}
commits=[json.loads((E/(p+'-identity.json')).read_text())['revision'] for p in ('p6','p7','p8','p9')]

def run(args):
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout

review={'schema_version':1,'pair_id':'vs2-interaction','round_id':'r2',
    'manifest_sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'semantic_tip':commits[-1],
    'actor':actor,'independence':'self-review','mode':'changes','status':'complete',
    'orientation_done':True,'reviewed_commits':commits,'aggregate_done':True,'findings':[],
    'check_records':['verification-summary.json','review-notes.md','docs-check.json','carry-forward.json'],
    'limitations':['Author self-review, not independent review','Windows/Python 3.12 only',
                   'Synthetic compatibility only; empirical adoption pending'],
    'carry_forward_record':'carry-forward.json', 'platform_approval':False}
(E/'review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
(E/'review-validation.json').write_text(run([PY,str(SKILL),'validate-review','--manifest',str(M),
                                           '--report',str(E/'review.json')]),encoding='utf-8')
event={'kind':'verification','round_id':'r2','actor':actor,'payload':{
    'stage':'locally_prepared','base':'ff9af2e68d989590ebe030002e2e3789c35efef0',
    'diary':'4e26b9e7bc4b762425586eab80a3aa9011d094f9','semantic':commits[-1],
    'records':['verification-summary.json','review.json','equivalence.json'],
    'summary':'New checkpoint-owned checks, documentation verification, scoped changes self-review with exact r1 carry-forward, final tree equality and canonical snapshot complete. Remote replication and owner acceptance pending.'}}
(E/'prepared-event.json').write_text(json.dumps(event,indent=2),encoding='utf-8')
if not (E/'prepared-ledger.json').exists():
    (E/'prepared-ledger.json').write_text(run([PY,str(SKILL),'record','--repo',str(A),
        '--store',str(ROOT/'extras/der-evidence'),'--pair','vs2-interaction',
        '--event',str(E/'prepared-event.json'),'--expected-last',json.loads(run([PY,str(SKILL),'ledger','--store',str(ROOT/'extras/der-evidence'),'--pair','vs2-interaction']))['last_hash']]),encoding='utf-8')
if PUB.exists(): raise RuntimeError('Archive already exists; preserve it, do not overwrite')
PUB.mkdir(parents=True)
canonical=PUB/'canonical';canonical.mkdir()
for path in (PAIR/'rounds/r2').iterdir():
    if path.is_file():shutil.copyfile(path,canonical/path.name)
shutil.copytree(PAIR/'events',canonical/'events')

def sanitise(text):
    for source,target in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),
        ('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
        text=text.replace(source.replace('\\','\\\\'),target).replace(source,target)
    return text

records=PUB/'records';records.mkdir()
index=[]
for path in sorted(E.iterdir()):
    if path.suffix not in ('.md','.json','.log','.py','.txt') or path.name in ('export-result.json',):continue
    original=path.read_bytes()
    exported=sanitise(original.decode('utf-8-sig')).encode('utf-8')
    if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghs_[A-Za-z0-9]{30,}',exported):
        raise RuntimeError('Potential secret in '+path.name)
    (records/path.name).write_bytes(exported)
    index.append({'source':path.name,'source_sha256':hashlib.sha256(original).hexdigest(),
                  'export_sha256':hashlib.sha256(exported).hexdigest(),
                  'transformation':'Local workspace/user paths replaced with placeholders'})
(PUB/'export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8',newline='\n')
(PUB/'.gitattributes').write_text('* -text\n',encoding='utf-8',newline='\n')
(PUB/'README.md').write_text("""# Research interaction: documentation revision evidence

This standalone archive preserves round r2 of PR13. It is not application history.
The canonical manifest, Git bundle and captured local ledger retain original bytes.
The records directory contains sanitised methods, logs, identities, architecture
records, review scope and original/export hashes. No runtime datasets, keys,
installation tokens, model weights or private research data are included.

1. Verify SHA256SUMS and read records/review-notes.md and carry-forward.json.
2. Use the Git bundle with a separate repository; run the pinned DER helper's
   check-round against canonical/manifest.json.
3. Check out each semantic commit independently, install its locked environment
   using uv sync --locked, then run uv run --locked python tools/check.py.
4. Adapt WORKSPACE/HOST_USER placeholders in records/verify.py and docs_check.py
   to reproduce the Windows/Python 3.12 and read-only documentation checks.

The original five commit identities, reviews and checks remain in the [r1 archive]
(https://github.com/FinnNk/Meerkritic/tree/2894cbdbe22b5a84ba387e7c710115b591698388).
Their exact mapping is in carry-forward.json. All four appended commits and the
new frozen diary were checked afresh. No new live model call or hosted CI run is
claimed. Author changes review is not independent review or owner approval.
""",encoding='utf-8',newline='\n')
files=sorted(p for p in PUB.rglob('*') if p.is_file())
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
run(['git','init','-b','evidence/vs2-interaction-r2',str(PUB)])
for key,value in [('user.name','meerkritic-agent[bot]'),('user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')]:
    run(['git','-C',str(PUB),'config',key,value])
run(['git','-C',str(PUB),'add','.'])
run(['git','-C',str(PUB),'commit','-m','docs: archive documentation revision review evidence'])
for path in files:
    staged=subprocess.check_output(['git','-C',str(PUB),'show','HEAD:'+path.relative_to(PUB).as_posix()])
    if staged != path.read_bytes():raise RuntimeError('Committed archive bytes changed')
identity={'archive':str(PUB),'commit':run(['git','-C',str(PUB),'rev-parse','HEAD']).strip(),
          'verified_files':len(files)}
(E/'export-result.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
print(json.dumps(identity))


