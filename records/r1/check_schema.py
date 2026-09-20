import os,json,subprocess,sys,hashlib
from pathlib import Path
root=Path('WORKSPACE');e=root/'extras/der-evidence/assessment-clarity/r1';r=root/'extras/der-checkouts/assessment-clarity';b=root/'extras/der-checkouts/assessment-clarity-check-baseline'
def schema(repo):
 env=os.environ.copy();env['PYTHONPATH']=str(repo/'src')
 return json.loads(subprocess.check_output([str(repo/'.venv/Scripts/python.exe'),'-c','import json; from semantic_reviewer.domain.normalisation import IssueInterpretation; print(json.dumps(IssueInterpretation.model_json_schema()))'],env=env,text=True))
before=schema(b);after=schema(r);assert before['required']==after['required']
def remove_descriptions(v):
 if isinstance(v,dict):return {k:remove_descriptions(x) for k,x in v.items() if k!='description'}
 if isinstance(v,list):return [remove_descriptions(x) for x in v]
 return v
clean=remove_descriptions(after);assert clean['properties']['scope']['enum'][-1]=='unknown';clean['properties']['scope']['enum'].remove('unknown');assert clean==remove_descriptions(before)
sys.path.insert(0,str(r/'src'));from semantic_reviewer.domain.normalisation import IssueInterpretation
state=json.loads((e/'live-before.json').read_text());count=0
for rel,digest in state['original_artefacts'].items():
 raw=(root/'extras/research/edr-0001/runtime'/rel).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
 body=json.loads(raw)
 if body.get('interpretation') is not None:
  value=body['interpretation'];parsed=IssueInterpretation.model_validate_json(json.dumps(value));assert parsed.model_dump(mode='json')==value;count+=1
assert count==33
out=dict(status='passed',old_required_fields_preserved=True,only_validation_change='scope gains unknown; descriptions added',legacy_successful_outputs_roundtrip_unchanged=count,original_files_verified=len(state['original_artefacts']),source_artefacts_rewritten=0,new_model_calls=0)
(e/'schema-compatibility.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
