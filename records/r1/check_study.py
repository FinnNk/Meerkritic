import json,hashlib,sqlite3
from pathlib import Path
root=Path('WORKSPACE');r=root/'extras/research/edr-0001/runtime';e=root/'extras/der-evidence/assessment-clarity/r1'
c=sqlite3.connect((r/'state.sqlite3').as_uri()+'?mode=ro',uri=True)
counts={name:c.execute('select count(*) from '+name).fetchone()[0] for name in ('job','event','annotation','discovery_run')}
assert counts['annotation']==0 and counts['discovery_run']==0,counts
old=json.loads((root/'extras/der-evidence/vs2-draft-repair/r1/live-before.json').read_text())
for p,digest in old['original_artefacts'].items():assert hashlib.sha256((r/p).read_bytes()).hexdigest()==digest
record=dict(status='passed',counts=counts,original_artefacts=old['original_artefacts'],unchanged_original_artefacts=len(old['original_artefacts']),server=json.loads((root/'extras/research/edr-0001/server.json').read_text()))
(e/'live-before.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k!='original_artefacts'}))
c.close()
