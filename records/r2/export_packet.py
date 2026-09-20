import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-study-tools/r2';PAIR=ROOT/'extras/der-evidence/pairs/vs2-study-tools';PUB=ROOT/'extras/der-publication/vs2-study-tools-r2'
assert not PUB.exists();PUB.mkdir(parents=True)
shutil.copytree(PAIR/'rounds',PUB/'canonical/rounds');shutil.copytree(PAIR/'events',PUB/'canonical/events')
index=[]
for round_id in ('r1','r2'):
 target=PUB/'records'/round_id;target.mkdir(parents=True)
 for path in sorted((ROOT/'extras/der-evidence/vs2-study-tools'/round_id).iterdir()):
  if path.suffix not in ('.md','.json','.log','.py','.txt') or path.name=='sample-replay.json':continue
  raw=path.read_bytes(); text=raw.decode('utf-8-sig')
  for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
   text=text.replace(left.replace('\\','\\\\'),right).replace(left,right)
  output=text.encode('utf-8')
  if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghs_[A-Za-z0-9]{30,}',output):raise RuntimeError('Potential secret in '+path.name)
  (target/path.name).write_bytes(output)
  index.append({'source':round_id+'/'+path.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(output).hexdigest(),'transformation':'Local workspace/user paths replaced; UTF-8 BOM removed if present'})
(PUB/'export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
(PUB/'.gitattributes').write_text('* -text\n',encoding='utf-8')
(PUB/'README.md').write_text('''# Reproducible study input preparation: review evidence

This separate archive retains the actual implementation diary, reconstructed review
histories and their evidence. It is not application ancestry and must not be merged.
Round r1 contains an unpublished checkpoint with a Ruff import-format failure.
Round r2 corrects reconstruction only, preserving the verified diary's final tree.

| Record | Purpose |
| --- | --- |
| records/r1/design.md and r1/propositions.md | Materiality, design and complete review boundaries |
| records/r2/verification-summary.json | Evidence-derived status and test totals for every exact checkpoint |
| records/r2/review-notes.md | Full author self-review, contract challenges and limitations |
| records/r2/revision-notes.md | Retained failed reconstruction and its correction |
| records/r2/architecture-*.json | Typed before/after/delta |
| records/r1/sample-plan-summary.json | Original metadata-only preparation identity; no human labels |
| records/r2/sample-replay-summary.json | Same-host exact replay, not independent research replication |
| canonical/rounds/r2 | Verified equivalent pair manifest and self-contained Git bundle |

To inspect or reproduce:

1. Verify SHA256SUMS. Canonical bundle/manifest/event bytes are preserved; the export
   index maps original to sanitised log/method hashes. Local paths use placeholders.
2. Use a bundle in a separate repository and run its pinned DER helper's check-round.
3. Check out each semantic commit separately, run uv sync --locked with Python 3.12,
   then uv run --locked python tools/check.py. The recorded required context is Windows.
4. Adapt paths in records/r2/verify.py to repeat checkpoint-owned checks. P1 is unchanged
   from r1 and uses that exact passing record; changed r2 identities were checked afresh.
5. Follow the application's study-preparation guide to reproduce the metadata plan
   from the pinned public source bytes. No raw source text, dataset, model weights,
   credentials or human research labels are included in this archive.

Author review is not independent review or owner approval. Study preparation does not
register the EDR, qualify original sources, authenticate people or adopt a grouping
method. The owner agreed the workload/criteria; empirical work has not begun.
''',encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file())
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
def run(args):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
run(['git','init','-b','evidence/vs2-study-tools-r2',PUB])
for k,v in [('user.name','meerkritic-agent[bot]'),('user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')]:run(['git','-C',PUB,'config',k,v])
run(['git','-C',PUB,'add','.']);run(['git','-C',PUB,'commit','-m','docs: archive study preparation review evidence'])
for path in files:
 assert subprocess.check_output(['git','-C',str(PUB),'show','HEAD:'+path.relative_to(PUB).as_posix()])==path.read_bytes()
result={'archive_commit':run(['git','-C',PUB,'rev-parse','HEAD']),'archive_branch':'evidence/vs2-study-tools-r2','files':len(files),'bytes':sum(p.stat().st_size for p in files)}
(E/'export-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
