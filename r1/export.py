"""Export only the authorised public review packet; preserve canonical bytes/hashes."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path('$WORKSPACE')
STORE=ROOT/'extras/der-evidence'
E=STORE/'vs1-architecture-review/r1'
OUT=ROOT/'extras/der-publication/vs1-architecture-review-r1-v2'
OUT.mkdir(parents=True,exist_ok=False)
(OUT/'.gitattributes').write_bytes(b'* -text\n')
shutil.copytree(STORE/'pairs/vs1-architecture-review/rounds',OUT/'rounds')
shutil.copytree(STORE/'pairs/vs1-architecture-review/events',OUT/'events')
shutil.copyfile(E/'reconstruction-attempt-1.bundle',OUT/'reconstruction-attempt-1.bundle')
shutil.copyfile(ROOT/'extras/preflight/vs1-inference/verified-downloads.json',OUT/'verified-downloads.json')
records=[]
for p in sorted(E.rglob('*')):
 if not p.is_file() or p.suffix not in ('.md','.json','.log','.py'): continue
 raw=p.read_bytes()
 text=raw.decode('utf-8-sig').replace('\r\n','\n')
 for old,new in [('D:\\\\codex\\\\semantic-reviewer','$WORKSPACE'),('$WORKSPACE','$WORKSPACE'),('$WORKSPACE','$WORKSPACE'),('C:\\\\Users\\\\finnn','$USER_HOME'),('$USER_HOME','$USER_HOME'),('$USER_HOME','$USER_HOME')]: text=text.replace(old,new)
 if p.name != 'export.py':
  assert '-----BEGIN PRIVATE KEY-----' not in text and 'ghs_' not in text and 'github_pat_' not in text,p
 target=OUT/'r1'/p.relative_to(E)
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(text,encoding='utf-8',newline='\n')
 records.append({'file':target.relative_to(OUT).as_posix(),'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(OUT/'export-provenance.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(OUT/'README.md').write_text('''# VS1 milestone architecture review — DER r1

Evidence-only branch: never merge into main. Application branch:
`refactor/vs1-milestone-review`. Start with `r1/plan.md`, `r1/review-notes.md`,
`r1/verification-summary.json` and `r1/reconstruction-attempts.md`.

Base: 0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9.
Frozen diary: 45c29fcfea43c99026a9ae54051df61d905e30fc.
Semantic tip: 036ff45827370f62d798b92ce10c9a52b6ed6330.
Exact shared tree: c98dffccb65429bae5fc217ead6462ccf49da8e7.

Nine checkpoint-owned clean Windows/Python 3.12/locked environments pass all
canonical gates (94, 96, 97, 100, 101, 102, 102, 102, 102 tests). Frozen diary
passes 102. Each record binds SHA, tree, lock, source/package identity, environment,
commands, status and clean state. The first reconstruction's failed import-order
checkpoint and its history are retained; all corrected descendants were reverified.
An early AST whitespace expectation and environmental access/line-ending failures
are recorded. No tests, architecture contracts or ignores were weakened.

The exact semantic tip also ran a separate worker through real MAF and the pinned
llama.cpp/Qwen fixture in a fresh public-data runtime. It confirmed prompt/provider
version provenance, an edit/reopen and unchanged original result reference. A
backup of prior functional-test data migrated with all rows preserved. This is
compatibility evidence, not a model-quality experiment or human research judgement.
See r1/semantic-live/live.py and live.json; private/runtime bodies are omitted.

Reproduction: clone rounds/r1/history.bundle and create a clean checkout/environment
for each SHA in r1/series.json. Install Python 3.12 and uv, then `uv sync --locked`
and `uv run --locked python tools/check.py`. Compare snapshots with the same tip
version of tools/architecture.py on base and tip; r1/architecture-identities.json
pins the generator and input revisions. Live reproduction requires the fixture in
verified-downloads.json and the application's local-inference/normalisation guides,
a fresh external runtime, and the pinned public source. Scripts show the actual
method; replace $WORKSPACE/$USER_HOME and choose local paths. Recorded model output
and timing can vary. No independent reproduction or hosted CI run is claimed.

Canonical manifests, bundles and ledger events are byte-preserved. Text paths and
line endings are normalised; export-provenance.json retains original/export hashes.
SHA256SUMS.json covers every payload file. Check-round initially inspected an
unpopulated archive clone; check-round-populated.json records its clean populated
state. Actual verification always used the separately identified clean checkouts.
Public-history bundles contain no credentials, private data or model weights.
No chat transcripts or hidden reasoning are exported. Later publication/readiness
observations stay in the external canonical ledger; this immutable archive records
locally prepared facts, not future owner approval or integration.
''',encoding='utf-8')
checksums={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'SHA256SUMS.json').write_text(json.dumps(checksums,indent=2,sort_keys=True),encoding='utf-8')
def git(*args): return subprocess.check_output(['git','-C',str(OUT),*args])
subprocess.run(['git','init','-b','evidence/vs1-architecture-review-r1',str(OUT)],check=True,capture_output=True)
git('config','user.name','meerkritic-agent[bot]')
git('config','user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')
git('add','.')
for path,digest in checksums.items(): assert hashlib.sha256(git('show',':'+path)).hexdigest()==digest,path
git('commit','-m','docs: archive VS1 milestone architecture review evidence')
commit=git('rev-parse','HEAD').decode().strip()
(E/'export-result.json').write_text(json.dumps({'archive':str(OUT),'commit':commit,'files_verified':len(checksums)},indent=2),encoding='utf-8')
print(json.dumps({'archive_commit':commit,'files_verified':len(checksums)}))
