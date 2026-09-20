"""Read-only documentation checks and representative Markdown renders."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib
from urllib.parse import unquote, urlsplit
from markdown_it import MarkdownIt

ROOT = Path('WORKSPACE')
R = ROOT/'extras/der-checkouts/vs2-interaction'
E = ROOT/'extras/der-evidence/vs2-interaction/r2'
OLD = 'eaeecaafd37883f2cb6da09d2845886413a9a530'
md = MarkdownIt('commonmark').enable('table')
files = [R/p for p in subprocess.check_output(['git','-C',str(R),'ls-files','*.md'], text=True).splitlines()
         if not p.startswith(('.agents/', 'docs/research/research-pack/'))]
errors = []
links = 0
tables = 0
def slugs(path):
    found = set()
    for token in md.parse(path.read_text(encoding='utf-8-sig')):
        if token.type == 'inline' and token.map:
            line = path.read_text(encoding='utf-8-sig').splitlines()[token.map[0]]
            if line.startswith('#'):
                slug = re.sub(r'[^\w\- ]', '', token.content.lower()).replace(' ', '-')
                found.add(slug)
    return found
for path in files:
    tokens = md.parse(path.read_text(encoding='utf-8-sig'))
    tables += sum(t.type == 'table_open' for t in tokens)
    for token in tokens:
        for item in token.children or []:
            if item.type not in ('link_open','image'):
                continue
            url = item.attrGet('href' if item.type == 'link_open' else 'src')
            target = urlsplit(url)
            if target.scheme or target.netloc or url.startswith('/'):
                continue
            links += 1
            dest = (path.parent/unquote(target.path)).resolve() if target.path else path
            if not dest.exists():
                errors.append(f'{path.relative_to(R)}: missing {url}')
            elif target.fragment and dest.suffix == '.md' and unquote(target.fragment) not in slugs(dest):
                errors.append(f'{path.relative_to(R)}: missing anchor {url}')
manifest = json.loads((R/'docs/source-manifest.json').read_text())
for item in manifest['files']:
    if hashlib.sha256((R/item['path']).read_bytes()).hexdigest() != item['sha256']:
        errors.append('Changed imported original: '+item['path'])
changed = subprocess.check_output(['git','-C',str(R),'diff','--name-only',OLD,'HEAD'],text=True).splitlines()
assert not any(p.startswith(('src/','tools/','tests/')) and p != 'tests/README.md' for p in changed)
assert 'uv.lock' not in changed
project = tomllib.loads((R/'pyproject.toml').read_text())['project']
assert project['license'] == 'MIT' and project['license-files'] == ['LICENSE.md']
assert not (R/'LICENSE').exists()
assert 'Copyright (c) 2026 Finn Newick' in (R/'LICENSE.md').read_text()
commands = [('tools/run.py','--help'), ('tools/run.py','annotate','--help'),
            ('tools/run.py','worker','--help'), ('tools/route.py','preview','--help'),
            ('tools/route.py','preview','--config','config/routing/example.json','--task','config/routing/task-example.json'), ('tools/architecture.py','--help')]
command_results = []
for args in commands:
    result = subprocess.run([str(R/'.venv/Scripts/python.exe'), *args], cwd=R,
                            capture_output=True,text=True,encoding='utf-8')
    command_results.append({'argv':list(args),'exit_code':result.returncode,'output':result.stdout+result.stderr})
    if result.returncode:
        errors.append('CLI check failed: '+' '.join(args))
samples = ['README.md','docs/development/normalisation.md','docs/development/research-interaction.md',
           'docs/development/documentation-style.md','docs/edr/README.md']
render = E/'rendered';render.mkdir(exist_ok=True)
for name in samples:
    content = md.render((R/name).read_text())
    (render/(name.replace('/','-')+'.html')).write_text(
        '<!doctype html><meta charset="utf-8"><style>body{font:16px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:0 25px}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:8px;text-align:left}pre{background:#eee;padding:16px;overflow:auto}h1,h2{line-height:1.25}</style>'+content,encoding='utf-8')
result = {'status':'failed' if errors else 'passed','markdown_files':len(files),'local_links':links,
          'tables':tables,'imported_files_verified':len(manifest['files']), 'errors':errors,
          'commands':command_results,'rendered_samples':samples,
          'application_source_tests_lock_unchanged':True,'sole_licence_file':'LICENSE.md'}
(E/'docs-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='commands'},indent=2))
raise SystemExit(bool(errors))

