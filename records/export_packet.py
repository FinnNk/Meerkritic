"""Export an explicit sanitised review packet; preserve canonical DER bytes unchanged."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path('WORKSPACE')
E=ROOT/'extras/der-evidence/vs2-grouping/r1'
PAIR=ROOT/'extras/der-evidence/pairs/vs2-grouping'
M=PAIR/'rounds/r1/manifest.json'
A=ROOT/'extras/der-checkouts/vs2-grouping-archive'
R=ROOT/'extras/der-checkouts/vs2-grouping'
PUB=ROOT/'extras/der-publication/vs2-grouping-r1'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
SKILL=R/'.agents/skills/double-entry-review/scripts/der.py'
actor={'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'vs2-grouping-2026-09-20'}
commits=[json.loads((E/(p+'-identity.json')).read_text())['revision'] for p in ('p1','p2','p3','p4')]

def run(args):
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout

review={'schema_version':1,'pair_id':'vs2-grouping','round_id':'r1',
    'manifest_sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'semantic_tip':commits[-1],
    'actor':actor,'independence':'self-review','mode':'full','status':'complete',
    'orientation_done':True,'reviewed_commits':commits,'aggregate_done':True,'findings':[],
    'check_records':['verification-summary.json','review-notes.md','live-embedding-final.json'],
    'limitations':['Author self-review, not independent review','Windows/Python 3.12 only',
                   'Synthetic compatibility only; empirical adoption pending'],
    'carry_forward_record':None, 'platform_approval':False}
(E/'review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
(E/'review-validation.json').write_text(run([PY,str(SKILL),'validate-review','--manifest',str(M),
                                           '--report',str(E/'review.json')]),encoding='utf-8')
event={'kind':'verification','round_id':'r1','actor':actor,'payload':{
    'stage':'locally_prepared','base':'c9ef38f48b10d7876fe26babee36f2f15f258bf3',
    'diary':'0c1f39f31ba6ecba36d4568eaa66ebc54056079b','semantic':commits[-1],
    'records':['verification-summary.json','review.json','equivalence.json'],
    'summary':'Checkpoint-owned checks, live synthetic compatibility, full self-review, exact final tree equality and canonical local snapshot complete. Remote replication and owner acceptance pending.'}}
(E/'prepared-event.json').write_text(json.dumps(event,indent=2),encoding='utf-8')
if not (E/'prepared-ledger.json').exists():
    (E/'prepared-ledger.json').write_text(run([PY,str(SKILL),'record','--repo',str(A),
        '--store',str(ROOT/'extras/der-evidence'),'--pair','vs2-grouping',
        '--event',str(E/'prepared-event.json'),'--expected-last','none']),encoding='utf-8')
if PUB.exists(): raise RuntimeError('Archive already exists; preserve it, do not overwrite')
PUB.mkdir(parents=True)
canonical=PUB/'canonical';canonical.mkdir()
for path in (PAIR/'rounds/r1').iterdir():
    if path.is_file():shutil.copyfile(path,canonical/path.name)
for path in PAIR.glob('*.jsonl'):shutil.copyfile(path,canonical/path.name)

def sanitise(text):
    for source,target in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),
        ('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
        text=text.replace(source.replace('\\','\\\\'),target).replace(source,target)
    return text

records=PUB/'records';records.mkdir()
index=[]
for path in sorted(E.iterdir()):
    if path.suffix not in ('.md','.json','.log','.py') or path.name in ('export-result.json',):continue
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
(PUB/'README.md').write_text('''# VS2 grouping review evidence

This is a standalone evidence archive, not application history. The canonical
manifest, Git bundle and captured local ledger retain their original bytes.
`records/` contains sanitised methods, logs, identities, architecture data and
author self-review; export-index.json records both source and exported hashes.
Local paths use WORKSPACE and HOST_USER placeholders. No keys, tokens, runtime
databases, model weights or research datasets are included.

Verify SHA256SUMS, then use the bundled DER helper from the Git bundle to run
check-round against canonical/manifest.json. Fetch its semantic/diary objects into
a separate repository and run each recorded checkpoint with Python 3.12, uv and
its own locked environment: `uv sync --locked`, `uv run --locked python tools/check.py`.
The verification script shows the exact Windows method; adjust placeholder paths.
The live compatibility script uses synthetic fixtures and the publicly pinned
Nomic model/profile, a local llama.cpp server and actual MAF. Its retained runtime
is local, not part of this archive. Model weights can be independently downloaded
at the pinned revision and verified by digest. Results are compatibility evidence,
not research labels, a registered EDR study or a method-quality claim.

Read propositions.md and review-notes.md in records before reviewing the series.
Author self-review is not independent review or owner approval. No hosted CI run
is claimed. The owner controls acceptance and merge.
''',encoding='utf-8',newline='\n')
files=sorted(p for p in PUB.rglob('*') if p.is_file())
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
run(['git','init','-b','evidence/vs2-grouping-r1',str(PUB)])
for key,value in [('user.name','meerkritic-agent[bot]'),('user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')]:
    run(['git','-C',str(PUB),'config',key,value])
run(['git','-C',str(PUB),'add','.'])
run(['git','-C',str(PUB),'commit','-m','docs: archive VS2 grouping review evidence'])
for path in files:
    staged=subprocess.check_output(['git','-C',str(PUB),'show','HEAD:'+path.relative_to(PUB).as_posix()])
    if staged != path.read_bytes():raise RuntimeError('Committed archive bytes changed')
identity={'archive':str(PUB),'commit':run(['git','-C',str(PUB),'rev-parse','HEAD']).strip(),
          'verified_files':len(files)}
(E/'export-result.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
print(json.dumps(identity))
