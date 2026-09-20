import sqlite3,json,hashlib
from pathlib import Path
root=Path('WORKSPACE');s=root/'extras/research/edr-0001';e=root/'extras/der-evidence/assessment-clarity/r1'
c=sqlite3.connect(s/'runtime/state.sqlite3');assert c.execute('select count(*) from annotation').fetchone()[0]==0
path=s/'backups/before-assessment-clarity.sqlite3';assert not path.exists();d=sqlite3.connect(path);c.backup(d);d.close();c.close()
(e/'live-backup.json').write_text(json.dumps(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2))
(s/'server-before-assessment-clarity.json').write_bytes((s/'server.json').read_bytes())
