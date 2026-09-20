from pathlib import Path
import sqlite3,json,hashlib,shutil,subprocess
from semantic_reviewer.bootstrap import build_jobs
from semantic_reviewer.application.annotations import review_actions
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';real=ROOT/'extras/research/edr-0001/runtime';copy=ROOT/'extras/research/edr-0001/upgrade-rehearsal';copy.mkdir(exist_ok=False)
def snapshot(path):
 c=sqlite3.connect(path);out={}
 for name, in c.execute("select name from sqlite_master where type='table' and name not like '%yoyo%' and name not like 'sqlite_%'"):
  rows=c.execute('select * from "'+name+'"').fetchall();out[name]={'count':len(rows),'sha256':hashlib.sha256(repr(sorted(rows,key=repr)).encode()).hexdigest()}
 c.close();return out
before=snapshot(real/'state.sqlite3');src=sqlite3.connect(real/'state.sqlite3');dst=sqlite3.connect(copy/'state.sqlite3');src.backup(dst);src.close();dst.close();shutil.copytree(real/'results',copy/'results')
jobs=build_jobs(copy);after=snapshot(copy/'state.sqlite3');assert before==after
records=json.loads((real.parent/'normalisation-results-02.json').read_text())['jobs'];actions={}
for row in records:
 job,body=jobs.inspect(row['job_id']);assert job.artefact_sha256==row['result_sha256'];allowed=review_actions(job,body);expected=('accept','edit','reject') if row['status']=='succeeded' else ('edit','reject');assert allowed==expected,(job.id,allowed);actions[job.id]=allowed
assert before['annotations']['count']==0
record={'status':'passed','source':'dedicated study database via SQLite online backup','before':before,'after':after,'unchanged_application_tables':before==after,'succeeded_reviewable':33,'failed_reviewable':22,'actions':actions,'research_annotations':0,'model_calls':0,'revision':subprocess.check_output(['git','-c','safe.directory=WORKSPACE/extras/der-checkouts/vs2-draft-repair','-C','WORKSPACE/extras/der-checkouts/vs2-draft-repair','rev-parse','HEAD'],text=True).strip()}
(E/'upgrade-rehearsal.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k not in ('before','after','actions')}))
