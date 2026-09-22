import json
import os
from pathlib import Path
import subprocess

ROOT = Path('D:/codex/semantic-reviewer/extras/der-checkouts/codegraph-navigation')
OUT = Path(__file__).parent
NODE = 'C:/Program Files/nodejs/node.exe'
RUN = ROOT / 'tools/codegraph/run.cjs'
records = []


def run(*args):
    result = subprocess.run([NODE, str(RUN), *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    records.append({'args': list(args), 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    (OUT / 'commands.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


probe = ROOT / 'tools/codegraph_refresh_probe.py'
excluded = ROOT / '.agents/codegraph_excluded_probe.py'
assert not probe.exists() and not excluded.exists()
try:
    run('sync')
    known = json.loads(run('query', 'create_app', '--json', '--limit', '3'))
    assert known[0]['node']['filePath'] == 'src/semantic_reviewer/web/app.py'
    callers = json.loads(run('callers', 'create_app', '--json'))
    assert any(item['name'] == 'build_app' and item['filePath'] == 'src/semantic_reviewer/asgi.py' for item in callers['callers'])
    assert 'create_app(' in (ROOT / 'src/semantic_reviewer/asgi.py').read_text(encoding='utf-8')
    probe.write_text('def navigation_probe_before():\n    return 1\n', encoding='utf-8')
    excluded.write_text('def navigation_excluded_probe():\n    return 1\n', encoding='utf-8')
    run('sync')
    assert any(x['node']['name'] == 'navigation_probe_before' for x in json.loads(run('query', 'navigation_probe_before', '--json')))
    files = json.loads(run('files', '--json'))
    paths = [x['path'] for x in files]
    forbidden = ('.agents/', '.github/', 'docs/research/', '.venv/', '.codegraph/', 'extras/', 'data/', 'runtime/', 'outputs/')
    assert not any(p.startswith(forbidden) or '/node_modules/' in p or p.startswith('../') for p in paths)
    probe.write_text('def navigation_probe_after():\n    return 2\n', encoding='utf-8')
    run('sync')
    assert any(x['node']['name'] == 'navigation_probe_after' for x in json.loads(run('query', 'navigation_probe_after', '--json')))
    assert not any(x['node']['name'] == 'navigation_probe_before' for x in json.loads(run('query', 'navigation_probe_before', '--json')))
finally:
    probe.unlink(missing_ok=True)
    excluded.unlink(missing_ok=True)
    run('sync')
assert not any(x['node']['name'] == 'navigation_probe_after' for x in json.loads(run('query', 'navigation_probe_after', '--json')))
run('explore', 'create_app', '--max-files', '2')
status = run('status')
files = json.loads(run('files', '--json'))
(OUT / 'summary.json').write_text(json.dumps({'version': run('--version').strip(), 'indexed_files': len(files), 'known_symbol': True, 'known_caller_verified_in_source': True, 'excluded_probe_absent': True, 'add_rename_delete_refresh': True, 'explore': True, 'status': status, 'branch_switch_tested': False, 'comparative_evaluation': False}, indent=2), encoding='utf-8')
print((OUT / 'summary.json').read_text(encoding='utf-8'))
