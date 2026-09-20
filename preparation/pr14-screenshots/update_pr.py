"""Render the PR template's validation table from retained checks, then publish it."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path('WORKSPACE');E=ROOT/'extras/batch-evidence/pr14-screenshots'
R=ROOT/'extras/der-checkouts/vs2-study-preparation';W=ROOT/'working'
PUB=ROOT/'extras/der-publication/vs2-interaction-r2'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
APP=[PY,str(ROOT/'extras/tooling/meerkritic-agent/agent.py'),'gh']
GIT=['git','-c',f'safe.directory={W.as_posix()}','-C',str(W)]
HEAD='fb5745475e7dd7d0cf5a93e329b3cd0c34910c72'
PREVIOUS='8d456962f0bd410b4a548969cfb547f39ede9f18'
BASE='f7aa4e05411da9d804f3624abe57033544fb1073'
def run(args,record=None):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if record:(E/record).write_text(p.stdout+p.stderr,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout

quality=json.loads((E/'final-checks.json').read_text(encoding='utf-8'))
docs=json.loads((E/'docs-check.json').read_text(encoding='utf-8'))
images=json.loads((E/'images-check.json').read_text(encoding='utf-8'))
assert images['revision']==HEAD and images['status']=='passed'
mapping=json.loads((ROOT/'extras/integration/pr13/mapping.json').read_text(encoding='utf-8'))
assert quality['revision']==docs['revision']==HEAD
assert quality['status']==docs['status']=='passed' and quality['clean'] and not docs['errors']
assert all(c['exit_code']==0 for c in quality['commands'])
assert any(c['argv']==['uv','run','--locked','python','tools/check.py'] for c in quality['commands'])
counts=re.findall(r'^Ran (\d+) tests? in ',(E/'final-checks.log').read_text(encoding='utf-8'),flags=re.M)
assert len(counts)==1
template=(R/'.github/pull_request_template.md').read_text(encoding='utf-8')
assert '**Standard checks:** Not run' in template

# The canonical runner stops at the first failed gate. Require its zero exit and
# every expected invocation rather than trusting an overall success flag alone.
runner=ast.parse((R/'tools/check.py').read_text(encoding='utf-8'))
assignments=[node for node in ast.walk(runner) if isinstance(node,ast.Assign)
             and any(isinstance(target,ast.Name) and target.id=='commands' for target in node.targets)]
assert len(assignments)==1
expected=[]
for command in assignments[0].value.elts:
    parts=[]
    for part in command.elts:
        if isinstance(part,ast.Constant) and isinstance(part.value,str):
            parts.append(part.value)
        else:
            assert isinstance(part,ast.Attribute) and isinstance(part.value,ast.Name)
            assert part.value.id=='sys' and part.attr=='executable'
            parts.append(str(Path(quality['checkout'])/'.venv/Scripts/python.exe'))
    expected.append(' '.join(parts))
log=(E/'final-checks.log').read_text(encoding='utf-8')
observed=re.findall(r'^Running: (.+)$',log,flags=re.M)
normalise=lambda value:value.replace('\\','/').casefold()
assert list(map(normalise,observed))==list(map(normalise,expected))
assert len(expected)==5, 'Review required checks before changing the summary'
assert expected[:4]==['ruff format --check .','ruff check .','lint-imports --no-cache','tach check']
assert expected[4].endswith(' -m unittest discover -s tests -p test_*.py')
test_results=re.findall(r'^OK(?: \(skipped=(\d+)\))?$',log,flags=re.M)
assert len(test_results)==1, 'Require the suite outcome; do not infer passes from tests run'
skipped=int(test_results[0] or 0)
passed=int(counts[0])-skipped
assert passed>=0
(E/'summary-inputs.json').write_text(json.dumps({
    'revision':HEAD,'status':'passed','expected_commands':expected,'observed_commands':observed,
    'canonical_runner_exit_code':0,'tests':{'run':int(counts[0]),'passed':passed,'skipped':skipped},
    'runner_sha256':hashlib.sha256((R/'tools/check.py').read_bytes()).hexdigest(),
    'documentation_links':docs['local_links'],'imported_hashes':docs['imported_files_verified']
},indent=2),encoding='utf-8')
fields='url,state,headRefOid,baseRefOid,body,comments,reviews'
before=json.loads(run(APP+['pr','view','14','--json',fields],'pr-before.json'))
assert before['state']=='OPEN' and before['headRefOid']==PREVIOUS and before['baseRefOid']==BASE
assert run(GIT+['ls-remote','origin','refs/heads/docs/vs2-study-preparation']).split()[0]==PREVIOUS
assert not run(['git','-c',f'safe.directory={R.as_posix()}','-C',str(R),'status','--porcelain']).strip()

# This is a presentation-only routine change. Original evidence is retained;
# export only a sanitised copy, with hashes linking it to the source records.
dest=PUB/'preparation/pr14-screenshots';dest.mkdir(parents=True)
index=[]
for name in ('final-checks.json','final-checks.log','docs-check.json','summary-inputs.json','verify.py','docs_check.py','update_pr.py','images-check.json','verify_images.py','rendered-checks.json','scope.md'):
    raw=(E/name).read_bytes();s=raw.decode('utf-8-sig')
    for left,right in ((str(ROOT),'WORKSPACE'),(ROOT.as_posix(),'WORKSPACE'),('HOST_USER','HOST_USER'),('HOST_USER','HOST_USER')):
        s=s.replace(left.replace('\\','\\\\'),right).replace(left,right)
    data=s.encode('utf-8');(dest/name).write_bytes(data)
    index.append({'name':name,'source_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(data).hexdigest(),'transformation':'Local paths replaced; UTF-8 BOM removed where present'})
(dest/'export-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
files=sorted(p for p in PUB.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS')
(PUB/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUB).as_posix()+'\n' for p in files),encoding='utf-8')
run(['git','-C',str(PUB),'add','.']);run(['git','-C',str(PUB),'commit','-m','docs: retain screenshot documentation verification'])
archive=run(['git','-C',str(PUB),'rev-parse','HEAD']).strip()
assert run(GIT+['ls-remote','origin','refs/heads/evidence/vs2-interaction-r2']).split()[0]=='394a089962df813130890366a11ae336b7ec0cfc'
run(GIT+['fetch',str(PUB),'refs/heads/evidence/vs2-interaction-r2:refs/heads/evidence/vs2-interaction-r2'])
run(GIT+['push','origin','refs/heads/evidence/vs2-interaction-r2'],'archive-push.log')

url=f'https://github.com/FinnNk/Meerkritic/blob/{archive}/preparation/pr14-screenshots/'
integration='https://github.com/FinnNk/Meerkritic/blob/3a4f952818ee429f64f406fc7db3df369a087dca/integration/pr13/mapping.json'
summary='## Validation\n\n'
summary+=f'**Standard checks:** Passed · revision `{HEAD[:7]}` · [Evidence]({url}summary-inputs.json)\n\n'
summary+='Windows / Python 3.12 / locked environment.\n\n'
summary+=f'Tests: **{passed} passed, {skipped} skipped**; no test changes. [Results]({url}final-checks.log).\n\n'
summary+=f"- Documentation: {docs['local_links']} local links checked; {docs['imported_files_verified']} imported-source hashes unchanged. [Evidence]({url}docs-check.json).\n"
summary+=f"- Screenshots: {images['images_verified']} image hashes/dimensions and {len(images['route_statuses'])} fixture routes checked; fresh setup and overwrite refusal verified. [Evidence]({url}images-check.json).\n"
summary+=f"- Earlier PR #13 integration (`{mapping['integrated_tip'][:7]}`): {len(mapping['ordered_tree_mapping'])} commit trees match. [Evidence]({integration}).\n\n"
(E/'validation.md').write_text(summary,encoding='utf-8')
body=before['body'];assert body.count('## Validation\n')==body.count('## Decisions and remaining work\n')==1
start=body.index('## Validation\n');end=body.index('## Decisions and remaining work\n',start)
body=body[:start]+summary+body[end:]
new_row='| `da3e48c` | Define screenshot capture, accessibility and maintenance guidance before applying it. |\n| `'+HEAD[:7]+'` | Illustrate the README and user guides with shared, reproducible synthetic screenshots. |\n'
body=body.replace('\n\n## Validation\n','\n'+new_row+'\n## Validation\n',1)
image_url=f'https://github.com/FinnNk/Meerkritic/blob/{HEAD}/docs/images/annotation-assessment.png?raw=true'
notes_url=f'https://github.com/FinnNk/Meerkritic/blob/{HEAD}/docs/images/README.md'
assert body.count('## Review sequence\n')==1
illustration=('The documentation now explains when to use screenshots and how to maintain them. '
              'The README and interaction guides share cropped views from a reproducible synthetic fixture.\n\n'
              f'![Human assessment controls with optional notes, an expandable editor, and Accept, Edit and Reject buttons.]({image_url})\n\n'
              f'Existing input-review controls, illustrated with [synthetic data and capture notes]({notes_url}). '
              'This is not the proposed study-rating interface.\n\n')
body=body.replace('## Review sequence\n',illustration+'## Review sequence\n',1)
(E/'pr-body.md').write_text(body,encoding='utf-8',newline='\n')
fresh=json.loads(run(APP+['pr','view','14','--json',fields]))
assert fresh==before
run(GIT+['push','origin','refs/heads/docs/vs2-study-preparation'],'branch-push.log')
run(APP+['pr','edit','14','--body-file',str(E/'pr-body.md')],'pr-edit.log')
after=json.loads(run(APP+['pr','view','14','--json',fields],'pr-after.json'))
assert after['headRefOid']==HEAD and after['body'].replace('\r\n','\n')==body
(E/'publication.json').write_text(json.dumps({'url':after['url'],'head':HEAD,'archive':archive,'source_records':['final-checks.json','final-checks.log','docs-check.json','summary-inputs.json']},indent=2),encoding='utf-8')
print(json.dumps({'url':after['url'],'head':HEAD,'archive':archive}))
