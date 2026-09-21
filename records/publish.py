"""Publish this routine documentation extraction through the project App."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=Path(__file__).parent;W=ROOT/'working';R=ROOT/'extras/der-checkouts/documentation-skill'
PUB=ROOT/'extras/review-publication/documentation-skill-r1'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';H=ROOT/'extras/tooling/meerkritic-agent/agent.py'
BASE='13b635a221fa9178f922e2ef1b946c0d45081077';HEAD='f574faddfcc10aa774995094a998b2b2ce3db57a'
def run(args):
 p=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
 return p.stdout.strip()
def gh(*args):return run([PY,H,'gh',*args])
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
check=json.loads((E/'final-checks.json').read_text());assert check['revision']==HEAD and check['status']=='passed' and check['clean']
log=(E/'final-checks.log').read_text(encoding='utf-8')
tree=ast.parse(run(git+['show',HEAD+':tools/check.py']))
node=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='commands' for t in n.targets))
expected=[[n.value if isinstance(n,ast.Constant) else '<python>' for n in row.elts] for row in node.elts]
observed=[line.removeprefix('Running: ') for line in log.splitlines() if line.startswith('Running: ')]
assert len(expected)==len(observed)
for wanted,actual in zip(expected,observed,strict=True):
 assert actual==' '.join(wanted) if wanted[0]!='<python>' else actual.endswith(' '+' '.join(wanted[1:])) and '.venv' in actual
assert re.search(r'^OK\s*$',log,re.M) and not re.search(r'skipped=|^SKIP',log,re.M)
tests=int(re.search(r'Ran (\d+) tests? in',log)[1])
assert tests==253
summary={'status':'passed','revision':HEAD,'base':BASE,'tests':tests,'skipped':0,'expected_checks':expected,'observed_checks':observed,'test_changes':'None; documentation and skill instructions only','classification':'routine','skill_validation':'Passed with Python UTF-8 mode','docs':json.loads((E/'docs-check.json').read_text())}
(E/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
assert not PUB.exists();(PUB/'records').mkdir(parents=True)
index=[]
for path in sorted(E.iterdir()):
 if path.suffix not in ('.json','.log','.md','.py'):continue
 raw=path.read_bytes();text=raw.decode('utf-8-sig')
 for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
  text=text.replace(left.replace('\\','\\\\'),right).replace(left,right)
 data=text.encode('utf-8')
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghs_[A-Za-z0-9]{30,}',data)
 (PUB/'records'/path.name).write_bytes(data)
 index.append({'source':path.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(data).hexdigest(),'transformation':'Host/workspace paths replaced; UTF-8 BOM removed if present'})
(PUB/'export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
(PUB/'.gitattributes').write_text('* -text\n',encoding='utf-8')
(PUB/'README.md').write_text('# Documentation skill extraction evidence\n\nRoutine documentation change at '+HEAD+'. No DER pair is claimed. The canonical check log, exact revision/environment, link/source checks and skill installation hashes are retained under records/. Self-review is not independent approval. No application behaviour or research data changed.\n\nReproduce software checks from the stated commit using Python 3.12 and `uv sync --locked`, then `uv run --locked python tools/check.py`. Validate the skill with the host skill-creator quick_validate helper using Python UTF-8 mode. Paths in auxiliary records are sanitised as listed in export-index.json.\n',encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file())
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
run(['git','init','-b','evidence/documentation-skill-r1',PUB])
for key,value in [('user.name','meerkritic-agent[bot]'),('user.email','331366570+meerkritic-agent[bot]@users.noreply.github.com')]:run(['git','-C',PUB,'config',key,value])
run(['git','-C',PUB,'add','.']);run(['git','-C',PUB,'commit','-m','docs: retain documentation skill validation evidence'])
archive=run(['git','-C',PUB,'rev-parse','HEAD'])
parent=json.loads(gh('pr','view','22','--json','state,headRefOid'));assert parent['state']=='OPEN' and parent['headRefOid']==BASE
for branch in ('evidence/documentation-skill-r1','docs/reusable-documentation-skill'):
 assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected remote branch.'
run(git+['fetch',PUB,'refs/heads/evidence/documentation-skill-r1:refs/heads/evidence/documentation-skill-r1'])
run(git+['push','origin','refs/heads/evidence/documentation-skill-r1'])
(E/'archive-publication.json').write_text(json.dumps({'archive_commit':archive,'branch':'evidence/documentation-skill-r1'}),encoding='utf-8')
run(git+['push','-u','origin','refs/heads/docs/reusable-documentation-skill'])
assert run(git+['ls-remote','origin','refs/heads/docs/reusable-documentation-skill']).split()[0]==HEAD
url='https://github.com/FinnNk/Meerkritic/tree/'+archive
body=f'''Documentation advice is now available as the reusable `technical-documentation` skill. It covers plain-English technical writing, structured instructions, current-behaviour guides, screenshots and evidence-based PR summaries. The skill has no Meerkritic, language-stack or hosting-service dependency.

Meerkritic's writing guide retains British English, exact quality commands, research safeguards, screenshot storage/fixtures and semantic-review conventions. Agent instructions and the PR template point to both the reusable method and local requirements. Existing guide anchors and imported originals are preserved.

The repository copy is versioned; an identical personal copy was installed for use across projects. The skill keeps screenshot and PR details in optional references, so ordinary writing tasks need only its core guide.

**Stacked on #22. Merge #22 before this PR.**

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `87f8488` | Reusable skill, personal-discovery metadata and Meerkritic-specific guidance/instruction integration. |
| `f574fad` | Backfill the documentation index and repository-structure guide. |

## Validation

**Standard checks: passed** at `{HEAD[:7]}` - [evidence]({url}/records/verification-summary.json). **253 tests; 0 skipped**, using a clean locked Windows/Python 3.12 environment. No tests or application code changed.

- Skill frontmatter/metadata validate; all four installed files match the repository copy by SHA-256.
- [Documentation checks]({url}/records/docs-check.json): 403 local links, including the skill references; all 59 imported-source hashes preserved.
- [Extraction review]({url}/records/review.md): general/local guidance mapping and scope checks. Author self-review; no independent behavioural evaluation claimed.

This is a routine documentation extraction. It changes no application behaviour, research decisions, model calls or repository permissions.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8')
pr=gh('pr','create','--base','feat/source-reading','--head','docs/reusable-documentation-skill','--title','docs: extract reusable technical documentation skill','--body-file',E/'pr-body.md')
(E/'pr-url.txt').write_text(pr+'\n',encoding='utf-8')
print(json.dumps({'pr':pr,'head':HEAD,'archive':archive,'tests':tests}))
