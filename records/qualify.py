"""Record exact publication/readiness and replicate the appended evidence without changing code."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-interaction/r2';PUB=ROOT/'extras/der-publication/vs2-interaction-r2';PAIR=ROOT/'extras/der-evidence/pairs/vs2-interaction'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';SKILL=ROOT/'extras/der-checkouts/vs2-interaction/.agents/skills/double-entry-review/scripts/der.py'
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr;return p.stdout
pr=json.loads((E/'published-pr.json').read_text(encoding='utf-8-sig'));rules=json.loads((E/'host-rules.json').read_text(encoding='utf-8-sig'))
assert pr['headRefOid']=='a2580a0785ab109c6014e404a949f60722282844' and pr['baseRefOid']=='ff9af2e68d989590ebe030002e2e3789c35efef0'
assert pr['author']['login']=='app/meerkritic-agent' and pr['state']=='OPEN'
assert not any(rule['type']=='required_status_checks' for rule in rules)
assert not pr['statusCheckRollup']
last=json.loads((E/'prepared-ledger.json').read_text())['event_hash']
event={'kind':'publication','round_id':'r2','actor':{'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'vs2-interaction-2026-09-20'},'payload':{'stage':'owner_review_ready','pr':pr['url'],'head':pr['headRefOid'],'base':pr['baseRefOid'],'archive_commit':'347a6788f00bc46852dae36dba0c0d49c2580c12','archive_branch':'evidence/vs2-interaction-r2','hosted_qualification':{'required_status_contexts':[],'observed_rollup':[],'note':'Current repository rules require owner review/resolution, not hosted CI; no hosted CI execution is claimed.'},'owner_approval':False,'integrated':False,'licence_detection':'unconfirmed; published bytes verified; see licence-verification.json','records':['published-pr.json','published-refs.txt','host-rules.json','published-pr.json','verification-summary.json','review.json','equivalence.json']}}
(E/'ready-event.json').write_text(json.dumps(event,indent=2),encoding='utf-8')
(E/'ready-ledger.json').write_text(run([PY,str(SKILL),'record','--repo',str(ROOT/'extras/der-checkouts/vs2-interaction-docs-archive'),'--store',str(ROOT/'extras/der-evidence'),'--pair','vs2-interaction','--event',str(E/'ready-event.json'),'--expected-last',last]),encoding='utf-8')
for path in (PAIR/'events').glob('*.json'):
 target=PUB/'canonical/events'/path.name
 if target.exists():assert target.read_bytes()==path.read_bytes()
 else:target.write_bytes(path.read_bytes())
# Supplement only: the original commit and export index retain original observations.
index=[]
for name in ('ready-event.json','ready-ledger.json','published-pr.json','host-rules.json','published-refs.txt','pr-body.md','publication-pr.log','publication-archive.log','publication-branch.log','github-licence.json','github-licence-branch.json','github-licence-content.json','licence-verification.json','publication-observation.md','publish.py','qualify.py'):
 source=E/name;raw=source.read_bytes();s=raw.decode('utf-8-sig')
 for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):s=s.replace(left.replace('\\','\\\\'),right).replace(left,right)
 output=s.encode('utf-8');(PUB/'records'/name).write_bytes(output)
 index.append({'source':name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(output).hexdigest(),'transformation':'Local paths replaced; UTF-8 BOM removed if present'})
(PUB/'publication-export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS')
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
run(['git','-C',str(PUB),'add','.']);run(['git','-C',str(PUB),'commit','-m','docs: record verified documentation review publication'])
W=ROOT/'working';git=['git','-c',f'safe.directory={W.as_posix()}','-C',str(W)]
remote=run(git+['ls-remote','origin','refs/heads/evidence/vs2-interaction-r2']).split()[0];assert remote=='347a6788f00bc46852dae36dba0c0d49c2580c12'
run(git+['fetch',str(PUB),'refs/heads/evidence/vs2-interaction-r2:refs/heads/evidence/vs2-interaction-r2'])
run(git+['push','origin','refs/heads/evidence/vs2-interaction-r2'])
sha=run(['git','-C',str(PUB),'rev-parse','HEAD']).strip()
refs=run(git+['ls-remote','origin','refs/heads/evidence/vs2-interaction-r2','refs/heads/feat/vs2-interaction'])
assert sha in refs and pr['headRefOid'] in refs
(E/'publication-complete.json').write_text(json.dumps({'pr':pr['url'],'head':pr['headRefOid'],'base':pr['baseRefOid'],'archive_commit':sha,'ready_ledger':json.loads((E/'ready-ledger.json').read_text()),'verified_refs':refs},indent=2))
print(json.dumps({'pr':pr['url'],'archive':sha,'stage':'owner_review_ready','owner_approval':False}))
