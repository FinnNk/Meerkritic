"""Publish the authorised append-only revision through the project App identity."""
import json
from pathlib import Path
import subprocess
ROOT=Path('WORKSPACE')
W=ROOT/'working';R=ROOT/'extras/der-checkouts/vs2-interaction'
E=ROOT/'extras/der-evidence/vs2-interaction/r2'
PUB=ROOT/'extras/der-publication/vs2-interaction-r2'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
APP=[PY,str(ROOT/'extras/tooling/meerkritic-agent/agent.py'),'gh']
GIT=['git','-c',f'safe.directory={W.as_posix()}','-c',f'safe.directory={R.as_posix()}',
     '-c',f'safe.directory={(R/".git").as_posix()}','-C',str(W)]
B='ff9af2e68d989590ebe030002e2e3789c35efef0'
OLD='eaeecaafd37883f2cb6da09d2845886413a9a530'
S='a2580a0785ab109c6014e404a949f60722282844'
A='347a6788f00bc46852dae36dba0c0d49c2580c12'
FIELDS='number,url,title,body,headRefOid,baseRefOid,headRefName,baseRefName,state,author,reviewDecision,mergeStateStatus,statusCheckRollup,comments,reviews'
def run(args,record=None):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if record:(E/record).write_text(p.stdout+p.stderr,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout
assert not run(GIT+['status','--porcelain']).strip()
pr=json.loads(run(APP+['pr','view','13','--json',FIELDS],'pr-at-publication.json'))
previous=json.loads((E/'pr-prepublish.json').read_text(encoding='utf-8-sig'))
assert pr['headRefOid']==OLD and pr['baseRefOid']==B and pr['state']=='OPEN'
assert pr['body']==previous['body'] and pr['comments']==previous['comments'] and pr['reviews']==previous['reviews']
refs=run(GIT+['ls-remote','origin','refs/heads/main','refs/heads/feat/vs2-interaction','refs/heads/evidence/vs2-interaction-r2'])
assert set(refs.splitlines())=={B+'\trefs/heads/main',OLD+'\trefs/heads/feat/vs2-interaction'}
run(GIT+['fetch',str(PUB),'refs/heads/evidence/vs2-interaction-r2:refs/heads/evidence/vs2-interaction-r2'])
assert run(GIT+['rev-parse','evidence/vs2-interaction-r2']).strip()==A
run(GIT+['push','origin','refs/heads/evidence/vs2-interaction-r2'],'publication-archive.log')
run(GIT+['fetch',str(R),'refs/heads/feat/vs2-interaction-docs:refs/heads/feat/vs2-interaction'])
assert run(GIT+['rev-parse','feat/vs2-interaction']).strip()==S
run(GIT+['merge-base','--is-ancestor',OLD,S])
run(GIT+['push','origin','refs/heads/feat/vs2-interaction'],'publication-branch.log')
run(APP+['pr','edit','13','--body-file',str(E/'pr-body.md')],'publication-pr.log')
fresh=json.loads(run(APP+['pr','view','13','--json',FIELDS],'published-pr.json'))
assert fresh['headRefOid']==S and fresh['baseRefOid']==B
assert fresh['body'].replace('\r\n','\n')==(E/'pr-body.md').read_text()
refs=run(GIT+['ls-remote','origin','refs/heads/feat/vs2-interaction','refs/heads/evidence/vs2-interaction-r2'],'published-refs.txt')
assert S in refs and A in refs
run(APP+['api','repos/FinnNk/Meerkritic/rules/branches/main'],'host-rules.json')
licence=json.loads(run(APP+['api','repos/FinnNk/Meerkritic/license?ref='+S],'github-licence.json'))
assert licence['path']=='LICENSE.md' and licence['license']['spdx_id']=='MIT'
print(json.dumps({'pr':fresh['url'],'head':S,'archive':A,'licence':licence['license']['spdx_id']}))
