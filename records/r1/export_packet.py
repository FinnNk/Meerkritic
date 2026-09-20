import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';PAIR=ROOT/'extras/der-evidence/pairs/vs2-draft-repair';PUB=ROOT/'extras/der-publication/vs2-draft-repair-r1'
assert not PUB.exists();PUB.mkdir(parents=True)
shutil.copytree(PAIR/'rounds',PUB/'canonical/rounds');shutil.copytree(PAIR/'events',PUB/'canonical/events')
index=[]
for round_id in ('r1',):
 target=PUB/'records'/round_id;target.mkdir(parents=True)
 for path in sorted((ROOT/'extras/der-evidence/vs2-draft-repair'/round_id).iterdir()):
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
(PUB/'README.md').write_text("""# Failed-draft correction: review evidence

This separate archive preserves true implementation chronology and the four
semantic propositions. It is not application ancestry and must not be merged.

- `canonical/rounds/r1` contains the immutable equivalent-pair manifest and bundle.
- `records/r1/verification-summary.json` derives each standard-check result and
  test total from the exact checkpoint's own locked Windows/Python environment.
- `records/r1/review-notes.md` records contract challenges and author self-review.
- `records/r1/backend-discovery.md` preserves the migration and legacy-compatibility
  findings, including original failing verification attempts and their remedies.
- `records/r1/architecture-*.json`, `docs-check.json`, `browser-check.json` and
  `upgrade-rehearsal.json` record typed architecture, documentation, synthetic
  interaction and a copy-only rehearsal over the actual study database.
- `records/r1/pr16-integration.json` records the approved predecessor's ordered trees.

Verify SHA256SUMS before importing the bundle into a separate repository. Canonical
files retain their bytes; export-index.json maps sanitised auxiliary files to the
original local hashes. Use the pinned DER helper to check the manifest. Check out
each semantic commit separately, install Python 3.12 and run `uv sync --locked`
then `uv run --locked python tools/check.py`. Verification scripts record the
operational context and retained failures; local paths need adapting on another host.

No raw research dataset, source comments, model outputs, weights or credentials are
included. The original 33 successes and 22 failures remain in external research
storage; this software permits human corrections without changing model outcomes.
No research annotation, grouping comparison or EDR registration is claimed.
Author self-review is not independent review or owner approval.
""",encoding='utf-8')

files=sorted(p for p in PUB.rglob('*') if p.is_file())
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
def run(args):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
run(['git','init','-b','evidence/vs2-draft-repair-r1',PUB])
for k,v in [('user.name','meerkritic-agent[bot]'),('user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')]:run(['git','-C',PUB,'config',k,v])
run(['git','-C',PUB,'add','.']);run(['git','-C',PUB,'commit','-m','docs: archive failed-draft correction review evidence'])
for path in files:
 assert subprocess.check_output(['git','-C',str(PUB),'show','HEAD:'+path.relative_to(PUB).as_posix()])==path.read_bytes()
result={'archive_commit':run(['git','-C',PUB,'rev-parse','HEAD']),'archive_branch':'evidence/vs2-draft-repair-r1','files':len(files),'bytes':sum(p.stat().st_size for p in files)}
(E/'export-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
