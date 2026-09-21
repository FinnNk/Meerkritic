import hashlib,json,os,re,subprocess
from pathlib import Path
from urllib.parse import urlsplit,unquote
from markdown_it import MarkdownIt
import yaml
ROOT=Path('WORKSPACE'); R=ROOT/'extras/der-checkouts/documentation-skill'; E=Path(__file__).parent
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],env=env,text=True,encoding='utf-8').strip()
md=MarkdownIt('commonmark').enable('table'); errors=[];links=0;tables=0
paths=[R/p for p in git('ls-files','*.md').splitlines() if not p.startswith(('.agents/','docs/research/research-pack/')) or p.startswith('.agents/skills/technical-documentation/')]
def slugs(path):
 text=path.read_text(encoding='utf-8-sig');lines=text.splitlines();found=set()
 for token in md.parse(text):
  if token.type=='inline' and token.map and lines[token.map[0]].startswith('#'):
   found.add(re.sub(r'[^\w\- ]','',token.content.lower()).replace(' ','-'))
 return found
for path in paths:
 text=path.read_text(encoding='utf-8-sig');tokens=md.parse(text);tables+=sum(t.type=='table_open' for t in tokens)
 if '\ufffd' in text:errors.append(str(path)+': replacement character')
 for token in tokens:
  for item in token.children or []:
   if item.type not in ('link_open','image'):continue
   url=item.attrGet('href' if item.type=='link_open' else 'src');target=urlsplit(url)
   if target.scheme or target.netloc or url.startswith('/'):continue
   links+=1;dest=(path.parent/unquote(target.path)).resolve() if target.path else path
   if not dest.exists():errors.append(f'{path.relative_to(R)}: missing {url}')
   elif target.fragment and dest.suffix=='.md' and unquote(target.fragment) not in slugs(dest):errors.append(f'{path.relative_to(R)}: missing anchor {url}')
manifest=json.loads((R/'docs/source-manifest.json').read_text())
for item in manifest['files']:
 if hashlib.sha256((R/item['path']).read_bytes()).hexdigest()!=item['sha256']:errors.append('Imported original changed: '+item['path'])
skill=R/'.agents/skills/technical-documentation'
metadata=yaml.safe_load((skill/'agents/openai.yaml').read_text(encoding='utf-8'))
assert '$technical-documentation' in metadata['interface']['default_prompt']
assert 25<=len(metadata['interface']['short_description'])<=64
assert metadata.get('policy',{}).get('allow_implicit_invocation',True)
for path in [R/'docs/development/documentation-style.md',skill/'SKILL.md',*sorted((skill/'references').glob('*.md'))]:
 (E/(path.stem+'.html')).write_text(md.render(path.read_text(encoding='utf-8')),encoding='utf-8')
record={'status':'passed' if not errors else 'failed','revision':git('rev-parse','HEAD'),'documents':len(paths),'links':links,'tables':tables,'imported_files_verified':len(manifest['files']),'skill_metadata':'passed','errors':errors,'rendering':'Markdown parsed/rendered to HTML; no browser visual inspection claimed'}
(E/'docs-check.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record));assert not errors
