from pathlib import Path
import json,subprocess
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-interaction/r1'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';SKILL=ROOT/'extras/der-checkouts/vs2-interaction/.agents/skills/double-entry-review/scripts/der.py'
actor={'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'vs2-interaction-2026-09-20'}
pr=json.loads((E/'pr12-current.json').read_text(encoding='utf-8-sig'));assert pr['state']=='MERGED' and pr['mergeCommit']['oid']=='ff9af2e68d989590ebe030002e2e3789c35efef0'
assert any(r['state']=='APPROVED' and r['author']['login']=='FinnNk' and r['commit']['oid']==pr['headRefOid'] for r in pr['reviews'])
event={'kind':'integration','round_id':'r1','actor':actor,'payload':{'stage':'integrated','pr':pr['url'],'reviewed':pr['headRefOid'],'integrated':pr['mergeCommit']['oid'],'merged_at':pr['mergedAt'],'ordered_mapping_record':'vs2-interaction/r1/pr12-integration.json','post_merge_checks':'vs2-interaction/r1/integrated-base-checks.json','note':'Factual observation after owner merge. Prior checks/approval retain reviewed identities; no retrospective readiness event is manufactured.'}}
(E/'pr12-integration-event.json').write_text(json.dumps(event,indent=2))
cmd=[PY,str(SKILL),'record','--repo',str(ROOT/'extras/der-checkouts/vs2-interaction-archive'),'--store',str(ROOT/'extras/der-evidence'),'--pair','vs2-rules','--event',str(E/'pr12-integration-event.json'),'--expected-last','1345c3c2186d816d9bf9a04f4acec27f3dacf7f68ad572c0c144cc1ab7f1cc43']
r=subprocess.run(cmd,capture_output=True,text=True);(E/'pr12-integration-ledger.json').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
# Capture the newly appended canonical event bytes in the final batch archive.
files=sorted((ROOT/'extras/der-evidence/pairs/vs2-rules/events').glob('*.json'))
(E/'pr12-canonical-integration-event.json').write_bytes(files[-1].read_bytes())
print(r.stdout)
