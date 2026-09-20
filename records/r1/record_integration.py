import json,subprocess,os
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';R=ROOT/'extras/der-checkouts/vs2-draft-repair';PY=R/'.venv/Scripts/python.exe';SKILL=R/'.agents/skills/double-entry-review/scripts/der.py';store=ROOT/'extras/der-evidence'
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
def run(args):
 p=subprocess.run([str(x) for x in args],env=env,capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr;return p.stdout
mapping=json.loads((E/'pr16-integration.json').read_text());baseline=json.loads((E/'baseline-checks.json').read_text());assert baseline['status']=='passed' and baseline['revision']==mapping['integrated']
event={'kind':'integration','round_id':'r2','actor':{'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'/root'},'payload':{'stage':'integrated','pr':mapping['pr'],'integrated':mapping['integrated'],'ordered_tree_mapping':mapping['ordered_tree_mapping'],'owner_approval':'FinnNk approved exact reviewed head and merged PR16','baseline':'vs2-draft-repair/r1/baseline-checks.json','baseline_tests':215,'study_registration':False}}
(E/'pr16-integration-event.json').write_text(json.dumps(event,indent=2));last=json.loads(run([PY,SKILL,'ledger','--store',store,'--pair','vs2-comparison']))['last_hash'];(E/'pr16-integration-ledger.json').write_text(run([PY,SKILL,'record','--repo',R,'--store',store,'--pair','vs2-comparison','--event',E/'pr16-integration-event.json','--expected-last',last]));print('PR16 integration recorded')
