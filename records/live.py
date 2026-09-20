"""Exercise the pinned real local runtime; every judgement is explicitly test-only."""
import json, os, sqlite3, subprocess, sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import httpx, duckdb

repo=Path('$WORKSPACE/extras/der-checkouts/vs1-validation')
root=Path('$WORKSPACE/extras/preflight/vs1-validation/runtime')
e=Path('$WORKSPACE/extras/der-evidence/vs1-validation/r1')
sys.path.insert(0,str(repo/'src'))
from semantic_reviewer.bootstrap import build_annotations, build_review_index
from semantic_reviewer.adapters.routing_journal import SQLiteRoutingJournal

dataset='crc-py-manual-4176ac0'
env=os.environ.copy()
env.update(PYTHONPATH=str(repo/'src'),PYTHONIOENCODING='utf-8',TEMP='$WORKSPACE/extras/der-tmp',TMP='$WORKSPACE/extras/der-tmp')
for key in ('GH_TOKEN','GITHUB_TOKEN'): env.pop(key,None)
result={'started_at':datetime.now(timezone.utc).isoformat(),'runtime':str(root),'jobs':[],
        'warning':'Automated functional decisions in an isolated public-data runtime; not owner annotations or model-quality evidence.'}
service=build_annotations(root)
def worker(label,endpoint='http://127.0.0.1:8081'):
    argv=[sys.executable,'tools/run.py','--data-root',str(root),'worker','--routing','config/routing/llama-local.json','--endpoint',endpoint,'--once']
    with (e/(label+'.log')).open('w',encoding='utf-8') as log:
        subprocess.run(argv,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
def record(job_id):
    job,bundle=service.jobs.inspect(job_id)
    result['jobs'].append({'job':asdict(job),'usage':bundle.get('usage') if bundle else None,
                          'framework':bundle.get('framework') if bundle else None,
                          'annotation':asdict(service.store.get(job_id)) if service.store.get(job_id) else None,
                          'log':service.jobs.jobs.log(job_id)})
    (e/'live.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
with httpx.Client(base_url='http://127.0.0.1:8003',trust_env=False,timeout=30,headers={'Origin':'http://127.0.0.1:8003'}) as client:
    assert client.get('/').status_code==200
    assert client.get(f'/datasets/{dataset}').status_code==200
    actions=iter(('accept','edit','reject'))
    action=next(actions)
    for attempt in range(1,7):
        response=client.post(f'/datasets/{dataset}/observations/0/normalise')
        assert response.status_code==303
        job_id=response.headers['location'].split('/')[-1]
        assert service.jobs.jobs.get(job_id).status=='queued'
        worker('live-worker-'+str(attempt))
        job,bundle=service.jobs.inspect(job_id)
        if job.status!='succeeded':
            record(job_id)
            continue
        form={'decision':action,'notes':'Automated functional verification only; not an owner judgement.'}
        if action=='edit':
            edited=dict(bundle['interpretation'])
            edited['issue_statement']='Functional-test edit: '+edited['issue_statement'][:3900]
            form['edited_json']=json.dumps(edited)
        response=client.post(f'/jobs/{job_id}/annotation',data=form)
        assert response.status_code==303, response.text
        assert 'This decision is recorded' in client.get(response.headers['location']).text
        record(job_id)
        action=next(actions,None)
        if action is None: break
    assert action is None, 'Three successful results were not available within six explicit test invocations.'
    failed=service.jobs.enqueue(dataset,0)
    worker('live-provider-failure','http://127.0.0.1:9')
    job,bundle=service.jobs.inspect(failed.id)
    assert job.status=='failed' and bundle['usage']['measurement']['outcome']=='provider_failure'
    assert client.get('/jobs/'+job.id).status_code==200
    record(job.id)
    interrupted=service.jobs.enqueue(dataset,0)
    subprocess.run([sys.executable,'-c',
        'from pathlib import Path; from semantic_reviewer.adapters.jobs import SQLiteJobs; import os; '
        'SQLiteJobs(Path(r"'+str(root/'state.sqlite3')+'")).claim("crash-probe"); os._exit(0)'],env=env,check=True)
    worker('live-restart-recovery')
    assert service.jobs.jobs.get(interrupted.id).status=='failed'
    record(interrupted.id)
    restarted=build_annotations(root)
    result['progress']=restarted.store.progress(dataset)
    assert result['progress']['reviewed_results']==3 and result['progress']['reviewed_sources']==1
    assert '3 / 3' in client.get(f'/datasets/{dataset}/progress').text
    manifest=Path('$WORKSPACE/extras/der-evidence/pairs/vs1-annotation/rounds/r1/manifest.json')
    event=Path('$WORKSPACE/extras/der-evidence/pairs/vs1-annotation/events/00000002.json')
    ref=build_review_index(root).index(manifest,event)
    assert 'owner_review_ready' in client.get('/reviews').text
    result['review_reference']=asdict(ref)
target=root/'usage.parquet'
result['exported_usage']=SQLiteRoutingJournal(root/'state.sqlite3').export_usage(target)
with duckdb.connect() as db:
    result['analytics']=db.execute('SELECT outcome,count(*),sum(input_tokens),sum(output_tokens) FROM read_parquet(?) GROUP BY outcome ORDER BY outcome',[str(target)]).fetchall()
with sqlite3.connect(root/'state.sqlite3') as db:
    result['artefact_counts']=db.execute('SELECT type,count(*) FROM artefact GROUP BY type ORDER BY type').fetchall()
    result['annotation_events']=db.execute("SELECT count(*) FROM event WHERE kind='annotation_recorded'").fetchone()[0]
    result['sqlite_mode']=db.execute('PRAGMA journal_mode').fetchone()[0]
assert result['annotation_events']==3 and result['sqlite_mode']=='wal'
result['completed_at']=datetime.now(timezone.utc).isoformat()
(e/'live.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'progress':result['progress'],'analytics':result['analytics'],'artefacts':result['artefact_counts']}))
