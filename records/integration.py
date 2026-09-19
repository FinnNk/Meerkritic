import hashlib, json, subprocess
from pathlib import Path

root = Path('$WORKSPACE')
repo = root/'extras/der-checkouts/vs1-annotation'
old = root/'extras/der-checkouts/vs1-normalisation-owned'
e = root/'extras/der-evidence/vs1-annotation/r1'
def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()
prior = ['e4cfb02c8059a2ee33a5bb3f562b98a6adbd6ee2','9a9c24cb20a83f031f8f28efceef345c5233a754','f0d94ca12ffd15af15fc3c19bd437b525e4aed69','0a2a62d61f01e24e48f784f76ee84a793052b923','fc30a333e950270356d99b29ab06cf84ca91154c']
merged = git(repo,'rev-list','--reverse','f1478217..b9ffa2ee').splitlines()
mapping = [{'reviewed': a, 'integrated': b, 'same_tree': git(old,'rev-parse',a+'^{tree}') == git(repo,'rev-parse',b+'^{tree}')} for a,b in zip(prior,merged,strict=True)]
assert all(x['same_tree'] for x in mapping)
record = {'pr':'https://github.com/FinnNk/Meerkritic/pull/6','owner_approved_reviewed_head':prior[-1],
          'merged_at':'2026-09-19T23:24:17Z','integration_head':merged[-1],'ordered_mapping':mapping,
          'post_merge_checks':{'status':'passed','tests':72,'checkout':str(repo),'revision':merged[-1],
                               'log':'clean-main-checks.log','sha256':hashlib.sha256((e/'clean-main-checks.log').read_bytes()).hexdigest()},
          'limitation':'Main workspace Ruff crashed in presence of inaccessible unrelated temporary directories. Retained base-checks.log; unchanged quality gates passed in a clean checkout of exact merged main.'}
(e/'pr6-integration.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
actor={'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'meerkritic-vs1-normalisation-2026-09-19'}
(e/'pr6-integration-event.json').write_text(json.dumps({'kind':'observation','round_id':'r2','actor':actor,'payload':{'stage':'integrated','evidence':str(e/'pr6-integration.json'),**record}},indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
