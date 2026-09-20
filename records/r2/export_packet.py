import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-comparison/r2';PAIR=ROOT/'extras/der-evidence/pairs/vs2-comparison';PUB=ROOT/'extras/der-publication/vs2-comparison-r2'
assert not PUB.exists();PUB.mkdir(parents=True)
shutil.copytree(PAIR/'rounds',PUB/'canonical/rounds');shutil.copytree(PAIR/'events',PUB/'canonical/events')
index=[]
for round_id in ('r1','r2'):
 target=PUB/'records'/round_id;target.mkdir(parents=True)
 for path in sorted((ROOT/'extras/der-evidence/vs2-comparison'/round_id).iterdir()):
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
(PUB/'README.md').write_text("""# Grouping comparison tooling: review evidence

This separate archive preserves implementation chronology, reconstructed semantic
histories and verification. It is not application ancestry and must not be merged.
Round r1 established the software; r2 completes the last documentation proposition
with actual preparation findings. P1-P4 retain their exact SHAs and passing checks.
The earlier r1 P5 was not verified or published; it is retained without a pass claim.
Two r2 P5 runs hit a Windows temporary-Git cleanup lock. Both failures, isolated
checks, the diagnostic full run and final canonical run are retained separately.
The intermittent lock cause remains uncertain; no cleanup error was suppressed.

| Record | Purpose |
| --- | --- |
| records/r1/design.md and records/r2/propositions.md | Materiality, design and semantic boundaries |
| records/r2/verification-summary.json | Checks and test totals derived from exact checkpoint records |
| records/r2/review-notes.md | Full author self-review and concrete contract challenges |
| records/r2/revision-notes.md | Precisely what changed between rounds |
| records/r2/architecture-*.json | Typed before/after/delta |
| records/r2/docs-check.json | Documentation, source hashes and actual command help |
| records/r1/pr15-integration.json | Predecessor review/merge mapping |
| canonical/rounds/r2 | Equivalent pair manifest and self-contained Git bundle |

To inspect or reproduce:

1. Verify SHA256SUMS. Canonical manifests/bundles/events retain original bytes;
   export-index.json maps original to sanitised auxiliary evidence hashes.
2. Import the bundle into a separate repository and run the pinned DER helper's
   check-round on the manifest. Local paths in auxiliary records use placeholders.
3. Check out each semantic commit separately. With Python 3.12 run uv sync --locked
   then uv run --locked python tools/check.py. Required recorded context: Windows.
4. Adapt records/r2/verify.py for isolated checkpoint-owned environments. P1-P4 use
   their exact r1 records; the r2 diary and final P5 were checked independently.
5. Follow the application's study guides for preparation and comparison. No raw
   dataset, source comment, model output, weights or credentials are included here.

The 80-candidate preparation pool produced 55 qualified origins and 33 valid drafts
from one initial local model pass. All 22 failures remain in external research
storage. Forty usable human-reviewed inputs are unattainable under current rules;
owner amendment is pending. No human annotations, research grouping run, registered
EDR or comparative result is claimed. Author self-review is not owner approval.
""",encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file())
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
def run(args):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
run(['git','init','-b','evidence/vs2-comparison-r2',PUB])
for k,v in [('user.name','meerkritic-agent[bot]'),('user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')]:run(['git','-C',PUB,'config',k,v])
run(['git','-C',PUB,'add','.']);run(['git','-C',PUB,'commit','-m','docs: archive grouping comparison review evidence'])
for path in files:
 assert subprocess.check_output(['git','-C',str(PUB),'show','HEAD:'+path.relative_to(PUB).as_posix()])==path.read_bytes()
result={'archive_commit':run(['git','-C',PUB,'rev-parse','HEAD']),'archive_branch':'evidence/vs2-comparison-r2','files':len(files),'bytes':sum(p.stat().st_size for p in files)}
(E/'export-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
