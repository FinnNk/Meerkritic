import json,sqlite3,hashlib,urllib.request,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';STUDY=ROOT/'extras/research/edr-0001';runtime=STUDY/'runtime';R=ROOT/'extras/der-checkouts/vs2-draft-repair-semantic'
i=json.loads((E/'semantic-commits.json').read_text());before=json.loads((E/'live-before.json').read_text());server=json.loads((STUDY/'server.json').read_text());assert server['code']==i['commits'][-1]
sys.path.insert(0,str(R/'src'))
from semantic_reviewer.bootstrap import build_jobs
from semantic_reviewer.application.annotations import review_actions
jobs=build_jobs(runtime);rows=json.loads((STUDY/'normalisation-results-02.json').read_text())['jobs'];actions={}
for row in rows:
 job,body=jobs.inspect(row['job_id']);assert job.artefact_sha256==row['result_sha256'];assert job.status==row['status'];actions[job.id]=review_actions(job,body);assert len(actions[job.id])==(3 if job.status=='succeeded' else 2)
for relative,digest in before['original_artefacts'].items():assert hashlib.sha256((runtime/relative).read_bytes()).hexdigest()==digest
c=sqlite3.connect(runtime/'state.sqlite3');counts={name:c.execute('select count(*) from '+name).fetchone()[0] for name in before['counts']};c.close();assert counts==before['counts']
pages=[]
for row in rows[:2]:
 with urllib.request.urlopen(row['job_url'],timeout=15) as response:body=response.read().decode();status=response.status
 assert status==200 and 'Source for your assessment' in body and 'value="edit"' in body and 'value="reject"' in body
 assert ('value="accept"' in body)==(row['status']=='succeeded');pages.append({'job_id':row['job_id'],'status':status,'actions':actions[row['job_id']]})
record={'status':'passed','recorded_at':datetime.now(timezone.utc).isoformat(),'revision':i['commits'][-1],'server':server,'counts_before':before['counts'],'counts_after':counts,'original_result_hashes_verified':len(rows),'original_artefact_files_unchanged':len(before['original_artefacts']),'http_pages':pages,'research_annotations_added':0,'model_calls_added':0,'first_job':rows[0]['job_url'],'ordered_handoff':str(STUDY/'INPUT-REVIEW.md')};(E/'live-after.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record))
