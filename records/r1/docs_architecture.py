import ast, hashlib, json, os, re, subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit
from markdown_it import MarkdownIt
ROOT=Path('WORKSPACE'); R=ROOT/'extras/der-checkouts/vs2-comparison-semantic-r1'; E=ROOT/'extras/der-evidence/vs2-comparison/r1'; B=ROOT/'extras/der-checkouts/vs2-comparison-check-baseline'
PY=ROOT/'extras/der-checkouts/vs2-comparison/.venv/Scripts/python.exe'
env=os.environ.copy();env.update(PYTHONIOENCODING='utf-8', GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R),GIT_CONFIG_KEY_1='safe.directory',GIT_CONFIG_VALUE_1=str(B))
def run(args,cwd=R):
 p=subprocess.run([str(x) for x in args],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
for name,repo in [('before',B),('after',R)]:
 body=run([PY,repo/'tools/architecture.py','snapshot','--root',repo],repo)
 json.loads(body);(E/('architecture-'+name+'.json')).write_text(body,encoding='utf-8')
(E/'architecture-delta.json').write_text(run([PY,R/'tools/architecture.py','delta',E/'architecture-before.json',E/'architecture-after.json']),encoding='utf-8')
md=MarkdownIt('commonmark').enable('table');errors=[];links=0;tables=0
paths=[R/p for p in run(['git','ls-files','*.md']).splitlines() if not p.startswith(('.agents/','docs/research/research-pack/'))]
def slugs(path):
 text=path.read_text(encoding='utf-8-sig'); lines=text.splitlines(); found=set()
 for token in md.parse(text):
  if token.type=='inline' and token.map and lines[token.map[0]].startswith('#'):
   found.add(re.sub(r'[^\w\- ]','',token.content.lower()).replace(' ','-'))
 return found
for path in paths:
 tokens=md.parse(path.read_text(encoding='utf-8-sig'));tables+=sum(t.type=='table_open' for t in tokens)
 for token in tokens:
  for item in token.children or []:
   if item.type not in ('link_open','image'):continue
   url=item.attrGet('href' if item.type=='link_open' else 'src');target=urlsplit(url)
   if target.scheme or target.netloc or url.startswith('/'):continue
   links+=1; dest=(path.parent/unquote(target.path)).resolve() if target.path else path
   if not dest.exists():errors.append(f'{path.relative_to(R)}: missing {url}')
   elif target.fragment and dest.suffix=='.md' and unquote(target.fragment) not in slugs(dest):errors.append(f'{path.relative_to(R)}: missing anchor {url}')
manifest=json.loads((R/'docs/source-manifest.json').read_text())
for item in manifest['files']:
 if hashlib.sha256((R/item['path']).read_bytes()).hexdigest()!=item['sha256']:errors.append('Changed imported original: '+item['path'])
for relative in ('docs/development/study-comparison.md','docs/development/study-preparation.md','docs/edr/0001-discovery-grouping-method.md'):
 text=(R/relative).read_text(encoding='utf-8');(E/(Path(relative).stem+'.html')).write_text(md.render(text),encoding='utf-8')
commands=[]
for arguments in (['--help'],['--data-root','external','--evidence','evidence','baseline','--help'],['--data-root','external','--evidence','evidence','pack','--help'],['--data-root','external','--evidence','evidence','analyse','--help']):
 output=run([PY,R/'tools/study_compare.py',*arguments]);commands.append({'arguments':arguments,'output':output,'exit_code':0})
record={'status':'passed' if not errors else 'failed','revision':run(['git','rev-parse','HEAD']).strip(),'links':links,'tables':tables,'imported_files_verified':len(manifest['files']),'errors':errors,'cli_help':commands,'rendered':['study-comparison.html','study-preparation.html','0001-discovery-grouping-method.html']}
(E/'docs-check.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='cli_help'}));assert not errors


