"""Render the PR template's validation table from retained checks, then publish it."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path('WORKSPACE');E=ROOT/'extras/batch-evidence/pr14-validation'
R=ROOT/'extras/der-checkouts/vs2-study-preparation';W=ROOT/'working'
PUB=ROOT/'extras/der-publication/vs2-interaction-r2'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
APP=[PY,str(ROOT/'extras/tooling/meerkritic-agent/agent.py'),'gh']
GIT=['git','-c',f'safe.directory={W.as_posix()}','-C',str(W)]
HEAD='6b9540afff64c28e65ee3b55aaf70c1b6ce94a21'
PREVIOUS='1a8ec0a3ddb56569dce26c13745f34feef1dc83c'
BASE='f7aa4e05411da9d804f3624abe57033544fb1073'
def run(args,record=None):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if record:(E/record).write_text(p.stdout+p.stderr,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout

quality=json.loads((E/'final-checks.json').read_text(encoding='utf-8'))
docs=json.loads((E/'docs-check.json').read_text(encoding='utf-8'))
mapping=json.loads((ROOT/'extras/integration/pr13/mapping.json').read_text(encoding='utf-8'))
assert quality['revision']==docs['revision']==HEAD
assert quality['status']==docs['status']=='passed' and quality['clean'] and not docs['errors']
assert all(c['exit_code']==0 for c in quality['commands'])
assert any(c['argv']==['uv','run','--locked','python','tools/check.py'] for c in quality['commands'])
counts=re.findall(r'^Ran (\d+) tests? in ',(E/'final-checks.log').read_text(encoding='utf-8'),flags=re.M)
assert len(counts)==1
template=(R/'.github/pull_request_template.md').read_text(encoding='utf-8')
assert '| Check | Result | Evidence |\n| --- | --- | --- |' in template
fields='url,state,headRefOid,baseRefOid,body,comments,reviews'
before=json.loads(run(APP+['pr','view','14','--json',fields],'pr-before.json'))
assert before['state']=='OPEN' and before['headRefOid']==PREVIOUS and before['baseRefOid']==BASE
assert run(GIT+['ls-remote','origin','refs/heads/docs/vs2-study-preparation']).split()[0]==PREVIOUS
assert not run(['git','-c',f'safe.directory={R.as_posix()}','-C',str(R),'status','--porcelain']).strip()

# This is a presentation-only routine change. Original evidence is retained;
# export only a sanitised copy, with hashes linking it to the source records.
dest=PUB/'preparation/pr14-validation';dest.mkdir(parents=True)
index=[]
for name in ('final-checks.json','final-checks.log','docs-check.json','verify.py','docs_check.py','update_pr.py'):
    raw=(E/name).read_bytes();s=raw.decode('utf-8-sig')
    for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
        s=s.replace(left.replace('\\','\\\\'),right).replace(left,right)
    data=s.encode('utf-8');(dest/name).write_bytes(data)
    index.append({'name':name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(data).hexdigest(),'transformation':'Local paths replaced; UTF-8 BOM removed where present'})
(dest/'export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS')
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
run(['git','-C',str(PUB),'add','.']);run(['git','-C',str(PUB),'commit','-m','docs: retain evidence for the compact PR validation summary'])
archive=run(['git','-C',str(PUB),'rev-parse','HEAD']).strip()
assert run(GIT+['ls-remote','origin','refs/heads/evidence/vs2-interaction-r2']).split()[0]=='5d297bb9e3dd4f0204d3b9e369be9f2677975630'
run(GIT+['fetch',str(PUB),'refs/heads/evidence/vs2-interaction-r2:refs/heads/evidence/vs2-interaction-r2'])
run(GIT+['push','origin','refs/heads/evidence/vs2-interaction-r2'],'archive-push.log')

url=f'https://github.com/FinnNk/Meerkritic/blob/{archive}/preparation/pr14-validation/'
integration='https://github.com/FinnNk/Meerkritic/blob/3a4f952818ee429f64f406fc7db3df369a087dca/integration/pr13/mapping.json'
rows=[
    ('Ruff · Import Linter · Tach','Passed',url+'final-checks.json'),
    ('Tests',counts[0]+' passed',url+'final-checks.log'),
    ('Documentation',str(docs['local_links'])+' local links checked',url+'docs-check.json'),
    ('Imported sources',str(docs['imported_files_verified'])+' hashes unchanged',url+'docs-check.json'),
    ('PR #13 integration (`'+mapping['integrated_tip'][:7]+'`)',str(len(mapping['ordered_tree_mapping']))+' commit trees match',integration)]
summary='## Validation\n\nLocal checks: `'+HEAD[:7]+'` · Windows / Python 3.12 · locked environment.\n\n'
summary+='| Check | Result | Evidence |\n| --- | --- | --- |\n'
summary+=''.join(f'| {name} | {result} | [Record]({link}) |\n' for name,result,link in rows)+'\n'
(E/'validation.md').write_text(summary,encoding='utf-8')
body=before['body'];assert body.count('## Validation\n')==body.count('## Decisions and remaining work\n')==1
start=body.index('## Validation\n');end=body.index('## Decisions and remaining work\n',start)
body=body[:start]+summary+body[end:]
new_row='| `'+HEAD[:7]+'` | Use evidence-linked validation tables in the PR template and author/reviewer guidance. |\n'
body=body.replace('\n\n## Validation\n','\n'+new_row+'\n## Validation\n',1)
(E/'pr-body.md').write_text(body,encoding='utf-8',newline='\n')
fresh=json.loads(run(APP+['pr','view','14','--json',fields]))
assert fresh==before
run(GIT+['push','origin','refs/heads/docs/vs2-study-preparation'],'branch-push.log')
run(APP+['pr','edit','14','--body-file',str(E/'pr-body.md')],'pr-edit.log')
after=json.loads(run(APP+['pr','view','14','--json',fields],'pr-after.json'))
assert after['headRefOid']==HEAD and after['body'].replace('\r\n','\n')==body
(E/'publication.json').write_text(json.dumps({'url':after['url'],'head':HEAD,'archive':archive,'source_records':['final-checks.json','final-checks.log','docs-check.json'],'rows':rows},indent=2),encoding='utf-8')
print(json.dumps({'url':after['url'],'head':HEAD,'archive':archive,'rows':len(rows)}))
