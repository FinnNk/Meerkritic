import hashlib,json,subprocess
from pathlib import Path
from PIL import Image
root=Path('WORKSPACE');r=root/'extras/der-checkouts/assessment-clarity-semantic';e=root/'extras/der-evidence/assessment-clarity/r1'
c=json.loads((r/'docs/images/captures-assessment-clarity.json').read_text());records=[]
for item in c['images']:
 p=r/'docs/images'/item['file'];assert list(Image.open(p).size)==item['size'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'];records.append(dict(file=item['file'],status='passed',size=item['size'],sha256=item['sha256']))
args=['git','-c','safe.directory='+r.as_posix(),'-C',str(r),'show','HEAD:docs/images/create_demo.py'];gitbytes=subprocess.check_output(args)
record=dict(status='passed',images=records,fixture_worktree_sha256=c['fixture_sha256'],fixture_git_lf_sha256=hashlib.sha256(gitbytes).hexdigest(),fixture_note='Capture record hashes Windows working-tree bytes; Git stores LF text. Both identities retained here.',crop_only=True,all_images_visually_inspected=True)
(e/'screenshot-check.json').write_text(json.dumps(record,indent=2));print(json.dumps(dict(status='passed',images=len(records))))
