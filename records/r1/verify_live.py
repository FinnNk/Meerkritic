import hashlib,json,sqlite3,urllib.request
from pathlib import Path
root=Path('WORKSPACE');e=root/'extras/der-evidence/assessment-clarity/r1';s=root/'extras/research/edr-0001';r=s/'runtime';b=json.loads((e/'live-before.json').read_text())
c=sqlite3.connect((r/'state.sqlite3').as_uri()+'?mode=ro',uri=True);counts={n:c.execute('select count(*) from '+n).fetchone()[0] for n in b['counts']};c.close();assert counts==b['counts']
for path,digest in b['original_artefacts'].items():assert hashlib.sha256((r/path).read_bytes()).hexdigest()==digest
pages=[]
for row in json.loads((s/'normalisation-results-02.json').read_text())['jobs'][:2]:
 with urllib.request.urlopen(row['job_url']) as response:html=response.read().decode();status=response.status
 assert status==200 and 'How to assess the fields' in html and 'Assessment notes and evidence limitations' in html and 'class="source-panel" open' in html
 assert ('value="accept"' in html)==(row['status']=='succeeded')
 pages.append(dict(job_id=row['job_id'],http_status=status,original_status=row['status'],clarified_fields=True))
record=dict(status='passed',server=json.loads((s/'server.json').read_text()),counts=counts,unchanged_original_outputs=len(b['original_artefacts']),research_decisions_added=0,model_calls_added=0,pages=pages)
(e/'live-after.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
p=s/'INPUT-REVIEW.md';old=p.read_text(encoding='utf-8');backup=s/'INPUT-REVIEW-before-assessment-clarity.md';assert not backup.exists();backup.write_text(old,encoding='utf-8')
p.write_text(old.replace('Expand **Source for your assessment**.','Read the open **Source for your assessment** panel.')+'\n## Clarified assessment meanings\n\nImpact scope describes the affected code, not the area needed for investigation;\nunknown is available. Applicability limits are exceptions, while missing evidence\nand further investigation belong in assessment notes. Attribute your additional\nadvice separately from the source. Notes are not interpretation text for grouping.\n\nThe first walkthrough is paused and remains unsaved. Its preliminary judgements\nand the agent\'s corrections are retained in walkthrough-feedback-01.md and\nwalkthrough-feedback-02.md. Resume that input; do not create duplicate decisions.\nThe initial model pass and fixed study order remain unchanged.\n',encoding='utf-8')
