"""Back up and compare the research runtime without submitting any judgement."""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path('WORKSPACE')
STUDY = ROOT / 'extras/research/edr-0001'
RUNTIME = STUDY / 'runtime'
EVIDENCE = ROOT / 'extras/der-evidence/assessment-form/r1'
phase = sys.argv[1]
assert phase in ('before', 'after')
with sqlite3.connect((RUNTIME/'state.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    tables = {}
    for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        rows = db.execute('SELECT * FROM "'+name.replace('"','""')+'"').fetchall()
        payload = json.dumps(sorted(rows,key=repr),ensure_ascii=False,default=repr,separators=(',',':')).encode()
        tables[name] = {'rows':len(rows),'sha256':hashlib.sha256(payload).hexdigest()}
    if phase == 'before':
        backup = STUDY/'backups/before-assessment-form.sqlite3'
        assert not backup.exists()
        with sqlite3.connect(backup) as target:
            db.backup(target)
        (STUDY/'server-before-assessment-form.json').write_bytes((STUDY/'server.json').read_bytes())
files = {str(p.relative_to(RUNTIME)):hashlib.sha256(p.read_bytes()).hexdigest()
         for p in (RUNTIME/'results').glob('*.json')}
record = {'tables':tables,'artefacts':files}
if phase == 'after':
    assert record == json.loads((EVIDENCE/'live-before.json').read_text()), 'Research state changed; inspect before claiming preservation.'
path = EVIDENCE/f'live-{phase}.json'
assert not path.exists()
path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'phase':phase,'table_count':len(tables),'artefacts':len(files),'annotations':tables['annotation']['rows'],'events':tables['event']['rows']}))
