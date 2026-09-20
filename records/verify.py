"""Run checkpoint-owned tests and record exact source, lock, runtime and Git identity."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path('$WORKSPACE')
REPO = ROOT/'extras/der-checkouts/vs1-validation'
E = ROOT/'extras/der-evidence/vs1-validation/r1'
PYTHON = '$USER_HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
label, revision = sys.argv[1:]
checkout = ROOT/('extras/der-checkouts/vs1-validation-'+label)
env = os.environ.copy()
env.update(UV_CACHE_DIR=str(ROOT/'extras/tool-cache/uv'), TEMP=str(ROOT/'extras/der-tmp'),
           TMP=str(ROOT/'extras/der-tmp'), PYTHONIOENCODING='utf-8', PYTHONPATH=str(checkout/'src'))
for key in ('GH_TOKEN', 'GITHUB_TOKEN'):
    env.pop(key, None)
subprocess.run(['git','-C',str(REPO),'worktree','add','--detach',str(checkout),revision],
               check=True,capture_output=True,env=env)
record = {'label':label, 'revision':revision, 'checkout':str(checkout),
          'started_at':datetime.now(timezone.utc).isoformat(), 'commands':[],
          'required_context':'Windows/Python 3.12/locked checkpoint environment'}
with (E/(label+'-checks.log')).open('w',encoding='utf-8') as log:
    def run(args):
        log.write('$ '+repr(args)+'\n'); log.flush()
        result = subprocess.run(args,cwd=checkout,env=env,stdout=log,stderr=subprocess.STDOUT)
        record['commands'].append({'argv':args,'exit_code':result.returncode})
        if result.returncode:
            record['status']='failed'
            (E/(label+'-checks.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
            raise SystemExit(result.returncode)
    run(['uv','sync','--locked','--offline','--python',PYTHON])
    run(['uv','run','--locked','python','tools/check.py'])
    run([str(checkout/'.venv/Scripts/python.exe'),'-c',
         'import semantic_reviewer,sys,sqlite3,json,importlib.metadata as m; '
         'print(json.dumps({"source":semantic_reviewer.__file__,"python":sys.version,'
         '"sqlite":sqlite3.sqlite_version,"versions":{d.metadata["Name"]:d.version '
         'for d in m.distributions()}},indent=2))'])
    run(['git','diff','--check'])
    run(['git','status','--porcelain'])
record['tree']=subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD^{tree}'],text=True).strip()
record['clean']=not subprocess.check_output(['git','-C',str(checkout),'status','--porcelain'],text=True).strip()
record['lock_sha256']=hashlib.sha256((checkout/'uv.lock').read_bytes()).hexdigest()
record['ended_at']=datetime.now(timezone.utc).isoformat()
record['status']='passed' if record['clean'] else 'failed'
(E/(label+'-checks.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'label':label,'revision':revision,'status':record['status']}))



