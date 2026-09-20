"""Verify the committed capture recipe and its assets without a model or research data."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient
from semantic_reviewer.asgi import build_app

ROOT = Path('WORKSPACE')
R = ROOT/'extras/der-checkouts/pr14-screenshots-final'
E = ROOT/'extras/batch-evidence/pr14-screenshots'
DATA = ROOT/'extras/runtime/documentation-screenshot-verification'
env = os.environ.copy()
env.update(PYTHONPATH=str(R/'src'), TEMP=str(ROOT/'extras/der-tmp'), TMP=str(ROOT/'extras/der-tmp'))
command = [sys.executable, str(R/'docs/images/create_demo.py'), '--data-root', str(DATA)]
result = subprocess.run(command, cwd=R, env=env, capture_output=True, text=True, encoding='utf-8')
(E/'fixture.log').write_text(result.stdout+result.stderr, encoding='utf-8')
assert result.returncode == 0
routes = json.loads(result.stdout)
with TestClient(build_app(DATA), base_url='http://127.0.0.1') as client:
    pages = {name:client.get(route) for name,route in routes.items()}
    assert all(page.status_code == 200 for page in pages.values())
    assert 'Documentation demo (synthetic)' in pages['observations'].text
    assert 'Each action saves immediately' in pages['annotation'].text
    assert 'Software fixture' in pages['selection'].text
    assert 'No model call' in pages['discovery'].text
    assert 'saved target revision 1' in pages['workspace'].text
    assert 'current revision 1' in pages['workspace'].text
    assert 'Apply this saved batch' in pages['workspace'].text
    assert 'No submitted guidance' in pages['guidance'].text
before = {str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.rglob('*') if p.is_file()}
repeat = subprocess.run(command,cwd=R,env=env,capture_output=True,text=True,encoding='utf-8')
assert repeat.returncode != 0 and 'FileExistsError' in repeat.stderr
assert before == {str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.rglob('*') if p.is_file()}
unsafe = subprocess.run(command[:-1]+[str(R/'forbidden-demo')],cwd=R,env=env,capture_output=True,text=True,encoding='utf-8')
assert unsafe.returncode != 0 and not (R/'forbidden-demo').exists()
manifest = json.loads((R/'docs/images/captures.json').read_text())
assert manifest['fixture_sha256'] == hashlib.sha256((R/'docs/images/create_demo.py').read_bytes()).hexdigest()
for item in manifest['images']:
    raw = (R/'docs/images'/item['file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    assert [int.from_bytes(raw[16:20]),int.from_bytes(raw[20:24])] == item['size']
assert {i['size'][0] for i in manifest['images']} == {960,1232}
record={'revision':'fb5745475e7dd7d0cf5a93e329b3cd0c34910c72','status':'passed',
        'images_verified':len(manifest['images']),'route_statuses':{name:p.status_code for name,p in pages.items()},
        'fresh_fixture_succeeded':True,'existing_runtime_refused_without_changes':True,
        'worktree_destination_refused':True,'model_calls':0,
        'visual_review':'All native captures inspected; README and annotation crop inspected in rendered guides; every illustrated guide checked for loaded images and alt text.'}
(E/'images-check.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
