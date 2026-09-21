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
prior=json.loads(gh('pr','view','22','--json',fields))
assert prior['state']=='OPEN' and prior['headRefOid']==i['previous_tip'] and prior['baseRefOid']==i['base']
(E/'prior-pr.json').write_text(json.dumps(prior,indent=2),encoding='utf-8')
body=prior['body'].replace('\r\n','\n')
oldarchive='https://github.com/FinnNk/Meerkritic/tree/d16c2882815b9f11c298eec98c7cb34cb63baac7'
archive='https://github.com/FinnNk/Meerkritic/tree/'+a['archive_commit']
head=i['commits'][-1]
intro='\n\n**Stacked on #21.'
assert body.count(intro)==1
body=body.replace(intro,'\n\nThe shared header also groups links under **Research**, **Review** and **Project**, with separate links for the current assessment. Groups share a compact desktop row and wrap on smaller screens.\n\n**Stacked on #21.',1)
row='| `4e63077` | Backfill current guides, backup instructions and the synthetic screenshot. |'
assert row in body
body=body.replace(row,row+f'\n| `{i["commits"][3][:7]}` | Group shared navigation, retain conditional destinations and separate assessment links. |\n| `{head[:7]}` | Explain navigation in the task-guide index with a synthetic header capture. |')
oldvalidation=f'**Standard checks: passed** at `4e63077` - [evidence]({oldarchive}/records/r1/verification-summary.json). **253 tests; 0 skipped.** All three semantic checkpoints and the frozen diary passed in their own locked Windows/Python 3.12 environments.'
assert oldvalidation in body
body=body.replace(oldvalidation,f'**Standard checks: passed** at `{head[:7]}` - [evidence]({archive}/records/r2/verification-summary.json). **253 tests; 0 skipped.** Each checkpoint passed in its own locked Windows/Python 3.12 environment; the first three commits retain their unchanged exact-SHA results. The navigation refinement changes no tests.')
body=body.replace(f'- [Documentation]({oldarchive}/records/r1/docs-check.json): 385 local links',f'- [Documentation]({archive}/records/r2/docs-check.json): 389 local links')
body=body.replace(f'- [Double-Entry Review evidence]({oldarchive})',f'- [Double-Entry Review evidence]({archive})')
needle='\n## Validation\n'
assert body.count(needle)==1
body=body.replace(needle,f'\n![Grouped navigation with assessment-specific links below.](https://raw.githubusercontent.com/FinnNk/Meerkritic/{head}/docs/images/harness-navigation.png)\n\n[Navigation browser checks]({archive}/records/r2/browser-check.json): 1280px and 375px layouts, link visibility and keyboard focus.\n'+needle)
(E/'pr-body.md').write_text(body,encoding='utf-8')
git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
assert run(git+['ls-remote','origin','refs/heads/feat/source-reading']).split()[0]==i['previous_tip']
assert not run(git+['ls-remote','origin','refs/heads/evidence/source-reading-r2'])
run(git+['fetch',PUB,'refs/heads/evidence/source-reading-r2:refs/heads/evidence/source-reading-r2'],'archive-import')
run(git+['push','origin','refs/heads/evidence/source-reading-r2'],'publish-archive')
assert run(git+['ls-remote','origin','refs/heads/evidence/source-reading-r2']).split()[0]==a['archive_commit']
run(git+['push','origin','refs/heads/feat/source-reading'],'publish-branch')
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
