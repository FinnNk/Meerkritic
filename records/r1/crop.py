import hashlib,json
from pathlib import Path
from PIL import Image
root=Path('WORKSPACE')
e=root/'extras/der-evidence/assessment-clarity/r1'
r=root/'extras/der-checkouts/assessment-clarity'
items=[('assessment-source.png','full-raw.png',[16,785,1248,1220]),('annotation-result.png','full-raw.png',[16,1230,1248,1770]),('annotation-assessment.png','full-raw.png',[16,1773,1248,2245]),('failed-draft-assessment.png','failed-raw.png',[16,1315,1248,2110])]
records=[]
for name,raw,rect in items:
    path=r/'docs/images'/name
    im=Image.open(e/raw);im.crop(rect).save(path)
    records.append(dict(file=name,raw=raw,crop_pixels=rect,size=list(Image.open(path).size),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
record=dict(application_revision='5efdc2e',captured_on='2026-09-20',browser='Codex in-app browser; dark appearance; full-page capture',viewport_css=[1280,720],transformation='Pixel crops only; no scaling or content edits',fixture_git_base='86a839341787e986dae6870673efeaf8251a41d0',fixture_sha256=hashlib.sha256((r/'docs/images/create_demo.py').read_bytes()).hexdigest(),images=records)
(r/'docs/images/captures-assessment-clarity.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
