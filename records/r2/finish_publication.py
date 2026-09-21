"""Append the authorised navigation refinement and preserve owner PR edits."""
import json,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE'); E=ROOT/'extras/der-evidence/source-reading/r2'
PUB=ROOT/'extras/der-publication/source-reading-r2'; W=ROOT/'working'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
H=ROOT/'extras/tooling/meerkritic-agent/agent.py'
def run(args,label=None):
 p=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8')
 if label:(E/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
 assert p.returncode==0,p.stdout+p.stderr
 return p.stdout.strip()
def gh(*args):return run([PY,H,'gh',*args])
i=json.loads((E/'semantic-commits.json').read_text()); a=json.loads((E/'export-result.json').read_text())
assert json.loads((E/'verification-summary.json').read_text())['status']=='passed'
fields='url,state,headRefName,headRefOid,baseRefName,baseRefOid,author,mergeable,statusCheckRollup,body'
prior=json.loads((E/'prior-pr.json').read_text())
body=(E/'pr-body.md').read_text()
head=i['commits'][-1]
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
assert run(git+['ls-remote','origin','refs/heads/feat/source-reading']).split()[0]==head
fresh=json.loads(gh('pr','view','22','--json',fields))
assert fresh['body']==prior['body'] and fresh['headRefOid']==head and fresh['baseRefOid']==i['base'],'Concurrent PR edit; preserve and reconcile.'
run([PY,H,'gh','pr','edit','22','--body-file',E/'pr-body.md'],'publish-pr')
published=json.loads(gh('pr','view','22','--json',fields))
assert published['body'].replace('\r\n','\n').strip()==body.strip()
(E/'published-pr.json').write_text(json.dumps(published,indent=2),encoding='utf-8')
(E/'description-readback.json').write_text(json.dumps({'status':'passed','head':head,'body_matches':True,'owner_edits_preserved':True}),encoding='utf-8')
(E/'pr-url.txt').write_text(published['url']+'\n',encoding='utf-8')
(E/'host-rules.json').write_text(gh('api','repos/FinnNk/Meerkritic/rules/branches/docs%2Frepair-text-encoding'),encoding='utf-8')
(E/'published-refs.txt').write_text(run(git+['ls-remote','origin','refs/heads/docs/repair-text-encoding','refs/heads/feat/source-reading','refs/heads/evidence/source-reading-r2']),encoding='utf-8')
print(json.dumps({'pr':published['url'],'head':head,'archive':a['archive_commit']}))
