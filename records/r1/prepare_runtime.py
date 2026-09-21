"""Rehearse or apply source attachments without creating research judgements."""
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT=Path('WORKSPACE')
STUDY=ROOT/'extras/research/edr-0001'
E=Path(__file__).parent
phase=sys.argv[1]
assert phase in ('rehearsal','rehearsal2','rehearsal3','live')
runtime=STUDY/('source-reading-'+phase if phase.startswith('rehearsal') else 'runtime')
if phase.startswith('rehearsal'):
    runtime.mkdir(exist_ok=False)
    with sqlite3.connect((STUDY/'runtime/state.sqlite3').as_uri()+'?mode=ro',uri=True) as source:
        with sqlite3.connect(runtime/'state.sqlite3') as target: source.backup(target)
    for folder in ('datasets','results'):
        shutil.copytree(STUDY/'runtime'/folder,runtime/folder)

def snapshot():
    with sqlite3.connect((runtime/'state.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        tables={}
        for table in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
            name=table[0]
            tables[name]=[dict(row) for row in db.execute('SELECT * FROM "'+name.replace('"','""')+'"')]
    files={str(p.relative_to(runtime)):hashlib.sha256(p.read_bytes()).hexdigest()
           for folder in ('datasets','results') for p in (runtime/folder).iterdir() if p.is_file()}
    return tables,files

before,files_before=snapshot()
assert len(before['annotation'])==1, 'Human decisions changed; inspect before proceeding.'
assert not any(j['status'] in ('queued','running') for j in before['job'])
if phase=='live':
    backup=STUDY/'backups/before-source-reading.sqlite3'
    assert not backup.exists()
    with sqlite3.connect((runtime/'state.sqlite3').as_uri()+'?mode=ro',uri=True) as source:
        with sqlite3.connect(backup) as target:source.backup(target)
    (STUDY/'server-before-source-reading.json').write_bytes((STUDY/'server.json').read_bytes())

from semantic_reviewer.adapters.reading import GitHubReadingSources
from semantic_reviewer.bootstrap import build_jobs
jobs=build_jobs(runtime)
sources=GitHubReadingSources(runtime/'source-context',runtime/'state.sqlite3')
reviewed={row['job_id'] for row in before['annotation']}
results=[]
for row in json.loads((STUDY/'normalisation-results-02.json').read_bytes())['jobs']:
    if row['job_id'] in reviewed:continue
    job,_=jobs.inspect(row['job_id'])
    _,observation=jobs.datasets.observation(job.dataset_id,job.source_index)
    receipt=STUDY/'source-checks'/row['receipt']
    response=receipt.with_name(receipt.name.replace('-check.json','-response.json'))
    try:
        context=sources.attach(job,observation,response.read_bytes(),receipt.read_bytes())
        results.append({'job_id':job.id,'sha256':context.sha256,'status':'attached',
                        'code_difference':context.code_difference,'comment_difference':context.comment_difference})
    except (ValueError,OSError,sqlite3.Error) as exc:
        results.append({'job_id':job.id,'status':'failed','error':str(exc)})
after,files_after=snapshot()
assert files_before==files_after,'Original dataset/result files changed'
for name,rows in before.items():
    if name in ('_yoyo_migration','_yoyo_log','_yoyo_version','yoyo_lock','event'):continue
    newer=after[name]
    if name=='annotation':
        assert all(row['context_sha256'] is None for row in newer)
        newer=[{k:v for k,v in row.items() if k!='context_sha256'} for row in newer]
    assert sorted(rows,key=repr)==sorted(newer,key=repr),f'Existing {name} records changed'
old_events={row['sequence']:row for row in before['event']}
assert all(row==old_events[row['sequence']] for row in after['event'] if row['sequence'] in old_events)
new_events=[row for row in after['event'] if row['sequence'] not in old_events]
assert all(row['kind']=='source_context_attached' for row in new_events)
record={'phase':phase,'status':'passed' if all(r['status']=='attached' for r in results) else 'partial',
        'attached':sum(r['status']=='attached' for r in results),'results':results,
        'original_annotations_preserved':len(before['annotation']),'original_files_preserved':len(files_before),
        'old_events_preserved':len(before['event']),'new_attachment_events':len(new_events),
        'new_human_decisions':0,'model_calls':0}
path=E/(phase+'-runtime.json');assert not path.exists()
path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='results'}))
