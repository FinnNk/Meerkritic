"""Fresh public-data compatibility check; decisions are functional fixtures only."""
import hashlib, json, os, shutil, sqlite3, subprocess, sys
from pathlib import Path
from dataclasses import asdict
import httpx

R=Path(sys.argv[1]).resolve()
E=Path('$WORKSPACE/extras/der-evidence/vs1-architecture-review/r1/semantic-live')
root=Path(sys.argv[2]).resolve()
root.mkdir(parents=True,exist_ok=False)
old=Path('$WORKSPACE/extras/preflight/vs1-validation-final/runtime')
sys.path.insert(0,str(R/'src'))
from semantic_reviewer.bootstrap import build_jobs,build_annotations,build_artefact_index
from semantic_reviewer.adapters.state import SQLiteState

# Only copy immutable public source bytes. Registration revalidates their pin.
(root/'datasets').mkdir()
manifest=json.loads((R/'config/datasets/crc-py-manual.json').read_text())
name=manifest['source_sha256']+'.json'
shutil.copyfile(old/'datasets'/name,root/'datasets'/name)
jobs=build_jobs(root)
dataset=jobs.datasets.register(manifest['id'])
assert dataset.row_count==1030
annotations=build_annotations(root,jobs)
env=os.environ.copy()
env.update(PYTHONPATH=str(R/'src'),TEMP='$WORKSPACE/extras/der-tmp',TMP='$WORKSPACE/extras/der-tmp')
for key in ('GH_TOKEN','GITHUB_TOKEN'): env.pop(key,None)
record={'source_revision':manifest['revision'],'source_sha256':manifest['source_sha256'],
        'source_checkout':str(R),'runtime':str(root),'jobs':[],
        'purpose':'Compatibility only; automated functional decisions, not owner research judgements.'}
record['server_health']=httpx.get('http://127.0.0.1:8081/health',trust_env=False,timeout=5).json()
for attempt in range(3):
 job=jobs.enqueue(dataset.id,0)
 with (E/f'live-worker-{attempt}.log').open('w') as log:
  subprocess.run([sys.executable,'tools/run.py','--data-root',str(root),'worker','--routing','config/routing/llama-local.json','--endpoint','http://127.0.0.1:8081','--once'],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
 current,bundle=jobs.inspect(job.id)
 record['jobs'].append({'job':asdict(current),'usage':bundle['usage'],'framework':bundle['framework']})
 (E/'live.json').write_text(json.dumps(record,indent=2))
 if current.status!='succeeded': continue
 assert '/no_think' not in bundle['request']['system']
 assert bundle['request']['prompt_version']=='normalisation-v2'
 provider=json.loads(bundle['provider_request']) if isinstance(bundle['provider_request'],str) else bundle['provider_request']
 assert provider['adapter_version']=='llama-native-v2'
 assert provider['template_request']['messages'][0]['content'].endswith('/no_think')
 assert provider['template_request']['chat_template_kwargs']['enable_thinking'] is False
 edited=dict(bundle['interpretation']); edited['issue_statement']='Functional compatibility edit: '+edited['issue_statement'][:3900]
 annotations.decide(job.id,'edit','Automated compatibility test only.',json.dumps(edited))
 assert jobs.inspect(job.id)[0].artefact_sha256==current.artefact_sha256
 break
else: raise AssertionError('No successful interpretation in three explicit test invocations; see retained attempts.')
assert build_annotations(root,build_jobs(root)).store.progress(dataset.id)['reviewed_results']==1
record['indexed']=build_artefact_index(root).index_referenced()
# Migrate a backup of prior public functional runtime, without changing its rows.
copy=root/'upgrade.sqlite3'
with sqlite3.connect(old/'state.sqlite3') as source, sqlite3.connect(copy) as target:
 source.backup(target)
 tables=['dataset','job','annotation','event','artefact']
 prior={table:list(target.execute('SELECT * FROM '+table)) for table in tables}
SQLiteState(copy)
with sqlite3.connect(copy) as target:
 after={table:list(target.execute('SELECT * FROM '+table)) for table in tables}
assert prior==after
record['upgrade_preserved_rows']={key:len(value) for key,value in after.items()}
record['prompt_control_boundary']='Task prompt clean; Qwen control retained in versioned provider request'
record['status']='passed'
(E/'live.json').write_text(json.dumps(record,indent=2))
print(json.dumps({'status':record['status'],'jobs':len(record['jobs']),'upgrade_preserved_rows':record['upgrade_preserved_rows']}))
