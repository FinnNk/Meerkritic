import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';PAIR=ROOT/'extras/der-evidence/pairs/vs2-draft-repair';PUB=ROOT/'extras/der-publication/vs2-draft-repair-r1';R=ROOT/'extras/der-checkouts/vs2-draft-repair-semantic';W=ROOT/'working'
PY=ROOT/'extras/der-checkouts/vs2-draft-repair/.venv/Scripts/python.exe';SKILL=R/'.agents/skills/double-entry-review/scripts/der.py'
def run(args):
 p=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
pr=json.loads((E/'published-pr.json').read_text(encoding='utf-8-sig'));rules=json.loads((E/'host-rules.json').read_text(encoding='utf-8-sig'));summary=json.loads((E/'verification-summary.json').read_text());archive=json.loads((E/'export-result.json').read_text())
assert pr['headRefOid']==summary['head'] and pr['baseRefOid']==summary['base'] and pr['state']=='OPEN' and pr['mergeable']=='MERGEABLE'
assert pr['author']['login']=='app/meerkritic-agent' and not pr['statusCheckRollup']
assert not any(rule['type']=='required_status_checks' for rule in rules)
event={'kind':'publication','round_id':'r1','actor':{'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'/root'},'payload':{'stage':'owner_review_ready','pr':pr['url'],'head':pr['headRefOid'],'base':pr['baseRefOid'],'archive_commit':archive['archive_commit'],'hosted_qualification':{'required_contexts':[],'observed_rollup':[],'note':'Repository rules require owner review/resolution, not hosted CI. No hosted CI run claimed.'},'owner_approval':False,'integrated':False,'evidence':['published-pr.json','host-rules.json','published-refs.txt','host-rules.json','verification-summary.json','review.json','equivalence.json']}}
(E/'ready-event.json').write_text(json.dumps(event,indent=2),encoding='utf-8')
last=json.loads(run([PY,SKILL,'ledger','--store',ROOT/'extras/der-evidence','--pair','vs2-draft-repair']))['last_hash']
# record does not read credentials; repository Git ownership is explicitly scoped.
import os
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
result=subprocess.run([str(x) for x in [PY,SKILL,'record','--repo',R,'--store',ROOT/'extras/der-evidence','--pair','vs2-draft-repair','--event',E/'ready-event.json','--expected-last',last]],env=env,capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stdout+result.stderr
(E/'ready-ledger.json').write_text(result.stdout,encoding='utf-8')
for path in (PAIR/'events').glob('*.json'):
 target=PUB/'canonical/events'/path.name
 if target.exists():assert target.read_bytes()==path.read_bytes()
 else:target.write_bytes(path.read_bytes())
index=[]
for name in ('export-result.json','publish.py','archive-import.log','publish-archive.log','publish-branch.log','publish-pr.log','pr-url.txt','pr-body.md','published-pr.json','host-rules.json','published-refs.txt','ready-event.json','ready-ledger.json','qualify.py'):
 raw=(E/name).read_bytes();text=raw.decode('utf-8-sig')
 for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):text=text.replace(left.replace('\\','\\\\'),right).replace(left,right)
 output=text.encode('utf-8');(PUB/'records/r1'/name).write_bytes(output)
 index.append({'source':'r2/'+name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(output).hexdigest(),'transformation':'Local paths replaced; UTF-8 BOM removed if present'})
(PUB/'publication-export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS')
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
run(['git','-C',PUB,'add','.']);run(['git','-C',PUB,'commit','-m','docs: record verified failed-draft correction publication'])
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
assert run(git+['ls-remote','origin','refs/heads/evidence/vs2-draft-repair-r1']).split()[0]==archive['archive_commit']
run(git+['fetch',PUB,'refs/heads/evidence/vs2-draft-repair-r1:refs/heads/evidence/vs2-draft-repair-r1']);run(git+['push','origin','refs/heads/evidence/vs2-draft-repair-r1'])
sha=run(['git','-C',PUB,'rev-parse','HEAD']);refs=run(git+['ls-remote','origin','refs/heads/main','refs/heads/evidence/vs2-draft-repair-r1','refs/heads/feat/vs2-draft-repair'])
assert sha in refs and pr['headRefOid'] in refs and pr['baseRefOid'] in refs
result={'pr':pr['url'],'stage':'owner_review_ready','head':pr['headRefOid'],'base':pr['baseRefOid'],'archive_commit':sha,'owner_approval':False,'integrated':False,'verified_refs':refs}
(E/'publication-complete.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
