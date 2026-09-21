"""Publish this routine documentation extraction through the project App."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=Path(__file__).parent;W=ROOT/'working';R=ROOT/'extras/der-checkouts/documentation-skill'
PUB=ROOT/'extras/review-publication/documentation-skill-r1'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';H=ROOT/'extras/tooling/meerkritic-agent/agent.py'
BASE='13b635a221fa9178f922e2ef1b946c0d45081077';HEAD='8d97bd67ddc09dbbbd9d140fb58199e6ec733ee0'
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
OLD='f574faddfcc10aa774995094a998b2b2ce3db57a'
fields='url,state,headRefOid,baseRefOid,author,body,statusCheckRollup,mergeable'
prior=json.loads(gh('pr','view','23','--json',fields))
assert prior['state']=='OPEN' and prior['headRefOid']==OLD and prior['baseRefOid']==BASE
(E/'prior-pr.json').write_text(json.dumps(prior,indent=2),encoding='utf-8')
assert run(git+['ls-remote','origin','refs/heads/docs/reusable-documentation-skill']).split()[0]==OLD
old_archive='23dc6bcf8d9b5c2fe5f455b0a2b85505ee0694c1'
assert run(['git','-C',PUB,'rev-parse','HEAD'])==old_archive
assert not run(['git','-C',PUB,'status','--porcelain'])
(PUB/'records/r2').mkdir()
index=[]
for path in sorted(E.iterdir()):
 if path.suffix not in ('.json','.md','.py','.log'):continue
 raw=path.read_bytes();text=raw.decode('utf-8-sig')
 for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
  text=text.replace(left.replace('\\','\\\\'),right).replace(left,right)
 data=text.encode('utf-8')
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghs_[A-Za-z0-9]{30,}',data)
 (PUB/'records/r2'/path.name).write_bytes(data)
 index.append({'source':path.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(data).hexdigest(),'transformation':'Host/workspace paths replaced'})
(PUB/'export-index-r2.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
with (PUB/'README.md').open('a',encoding='utf-8') as stream:
 stream.write('\nRefinement r2 at '+HEAD+' adds a tick-box checklist and conditional commit advice, and clarifies shared/local project guidance. Current verification is under records/r2; earlier evidence remains unchanged.\n')
files=sorted(p for p in PUB.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS')
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
run(['git','-C',PUB,'add','.']);run(['git','-C',PUB,'commit','-m','docs: retain documentation skill refinement checks'])
archive=run(['git','-C',PUB,'rev-parse','HEAD'])
assert run(git+['ls-remote','origin','refs/heads/evidence/documentation-skill-r1']).split()[0]==old_archive
run(git+['fetch',PUB,'refs/heads/evidence/documentation-skill-r1:refs/heads/evidence/documentation-skill-r1'])
run(git+['push','origin','refs/heads/evidence/documentation-skill-r1'])
(E/'archive-publication.json').write_text(json.dumps({'archive':archive,'previous':old_archive}),encoding='utf-8')
run(git+['push','origin','refs/heads/docs/reusable-documentation-skill'])
assert run(git+['ls-remote','origin','refs/heads/docs/reusable-documentation-skill']).split()[0]==HEAD
fresh=json.loads(gh('pr','view','23','--json',fields))
assert fresh['body']==prior['body'] and fresh['baseRefOid']==BASE,'Concurrent description/base edit; preserve and reconcile.'
body=prior['body'].replace('\r\n','\n')
body=body.replace('## Review sequence','The skill now includes a directly usable tick-box checklist and conditional advice for separating policy changes from backfills in semantic commits. The project guide explicitly distinguishes shared reminders from local choices. These additions do not impose Meerkritic\'s workflow on other projects.\n\n## Review sequence',1)
row='| `f574fad` | Backfill the documentation index and repository-structure guide. |'
assert row in body
body=body.replace(row,row+'\n| `d2c37fd` | Add conditional commit guidance and the reusable tick-box checklist (skill 0.1.1). |\n| `8d97bd6` | Clarify shared reminders and Meerkritic-specific choices in the project guide. |')
body=body.replace('at `f574fad`','at `8d97bd6`').replace('403 local links','404 local links')
body=body.replace('https://github.com/FinnNk/Meerkritic/tree/'+old_archive+'/records/','https://github.com/FinnNk/Meerkritic/tree/'+archive+'/records/r2/')
body=body.replace('general/local guidance mapping and scope checks','shared/local guidance and conditional-workflow scope checks')
(E/'pr-body.md').write_text(body,encoding='utf-8')
gh('pr','edit','23','--body-file',E/'pr-body.md')
published=json.loads(gh('pr','view','23','--json',fields))
assert published['headRefOid']==HEAD and published['baseRefOid']==BASE
assert published['body'].replace('\r\n','\n').strip()==body.strip()
assert published['author']['login']=='app/meerkritic-agent'
(E/'published-pr.json').write_text(json.dumps(published,indent=2),encoding='utf-8')
record={'status':'published and verified','pr':published['url'],'head':HEAD,'base':BASE,'archive':archive,'body_matches':True,'owner_approval':False,'merged':False}
(E/'publication-complete.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
