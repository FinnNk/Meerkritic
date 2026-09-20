import ast, hashlib, json, os, re, subprocess
from pathlib import Path
ROOT=Path('WORKSPACE'); E1=ROOT/'extras/der-evidence/vs2-comparison/r1'; E=ROOT/'extras/der-evidence/vs2-comparison/r2'; R=ROOT/'extras/der-checkouts/vs2-comparison-semantic-r2'; M=ROOT/'extras/der-evidence/pairs/vs2-comparison/rounds/r2/manifest.json'
PY=ROOT/'extras/der-checkouts/vs2-comparison/.venv/Scripts/python.exe'; SKILL=R/'.agents/skills/double-entry-review/scripts/der.py'
identity=json.loads((E/'semantic-commits.json').read_text()); records=[]
for label,sha in zip(('p1','p2','p3','p4','p5'),identity['commits'],strict=True):
 folder=E1 if label!='p5' else E
 record_label='p5-final' if label=='p5' else label
 record=json.loads((folder/(record_label+'-checks.json')).read_text()); log=(folder/(record_label+'-checks.log')).read_text(encoding='utf-8-sig')
 assert record['status']=='passed' and record['clean'] and record['revision']==sha
 assert all(c['exit_code']==0 for c in record['commands'])
 source=Path(record['checkout'])/'tools/check.py';tree=ast.parse(source.read_text(encoding='utf-8'))
 node=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='commands' for t in n.targets))
 expected=[]
 for row in node.elts:
  expected.append([n.value if isinstance(n,ast.Constant) else '<python>' for n in row.elts])
 observed=[line.removeprefix('Running: ') for line in log.splitlines() if line.startswith('Running: ')]
 assert len(expected)==len(observed)
 for wanted,actual in zip(expected,observed,strict=True):
  if wanted[0]=='<python>':assert actual.endswith(' '+' '.join(wanted[1:])) and '.venv' in actual
  else:assert actual==' '.join(wanted)
 count=int(re.search(r'Ran (\d+) tests? in',log)[1]);assert re.search(r'^OK\s*$',log,re.M)
 assert not re.search(r'skipped=|^SKIP',log,re.M)
 records.append({'proposition':label,'revision':sha,'tree':record['tree'],'status':'passed','tests':count,'skipped':0,'expected_checks':expected,'observed_checks':observed,'evidence':('r1/' if label!='p5' else 'r2/')+record_label+'-checks.json','log':('r1/' if label!='p5' else 'r2/')+record_label+'-checks.log'})
assert [r['tests'] for r in records]==[186,199,210,215,215]
summary={'status':'passed','head':identity['commits'][-1],'base':identity['base'],'environment':'Windows/Python 3.12/each checkpoint owns locked dependencies and source','checkpoints':records,'test_changes':{'lexical_shared_text_added':5,'masked_assessment_added':13,'evidence_binding_added':11,'registration_publication_added':5,'existing_tests_removed':0,'existing_tests_altered':0},'diary_evidence':['r2/diary-checks.json'],'retained_failed_verifications':['r2/p5-checks.json','r2/p5-retry-checks.json'],'failure_diagnosis':'Two full runs hit Windows WinError 32 during temporary Git directory cleanup, with no assertion failure. Isolated checks and the diagnostic full suite passed unchanged; lock holder not identified. Final canonical rerun is separately bound to the same commit.','targeted_recheck':'r2/registration-cleanup-recheck.json','superseded_unverified_checkpoint':'r1 P5 a2668e32979cdb6e4541f739741db5a47e34804f was not run; only the final documentation proposition changed in r2'}
(E/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
actor={'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'/root'}
review={'schema_version':1,'pair_id':'vs2-comparison','round_id':'r2','manifest_sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'semantic_tip':identity['commits'][-1],'actor':actor,'independence':'self-review','mode':'full','status':'complete','orientation_done':True,'reviewed_commits':identity['commits'],'aggregate_done':True,'findings':[],'check_records':['aggregate-consistency.json','test-change-identities.json','verification-summary.json','review-notes.md','docs-check.json','equivalence.json','architecture-delta.json'],'limitations':['Author self-review, not independent review','Windows/Python 3.12 only','Intermittent temporary-Git cleanup lock occurred twice; original failures and diagnostic checks retained; root cause unresolved','Source qualification and initial normalisation completed; no human study labels, registration or comparative results','Record fields are attestations; operator verifies source evidence and annotation versions'],'carry_forward_record':None,'platform_approval':False}
(E/'review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
def run(args):
 p=subprocess.run([str(a) for a in args],env=env,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
(E/'round-validation.json').write_text(run([PY,SKILL,'check-round','--manifest',M]),encoding='utf-8')
(E/'review-validation.json').write_text(run([PY,SKILL,'validate-review','--manifest',M,'--report',E/'review.json']),encoding='utf-8')
event={'kind':'verification','round_id':'r2','actor':actor,'payload':{'stage':'locally_prepared','base':identity['base'],'diary':identity['diary'],'semantic':identity['commits'][-1],'summary':'All exact semantic checkpoints pass; unchanged P1-P4 identities use exact r1 checks; new diary and final P5 checked afresh. Diary/final tracked trees equal; full author self-review complete. r1 unverified P5 retained and superseded during documentation completion. Canonical archive verified. Two r2 P5 runs failed during Windows temporary-directory cleanup; diagnostic and final canonical reruns retained separately. Lock cause remains uncertain.','records':['vs2-comparison/r2/verification-summary.json','vs2-comparison/r2/review.json','vs2-comparison/r2/equivalence.json']}}
(E/'prepared-event.json').write_text(json.dumps(event,indent=2),encoding='utf-8');store=ROOT/'extras/der-evidence'
last=json.loads(run([PY,SKILL,'ledger','--store',store,'--pair','vs2-comparison']))['last_hash']
(E/'prepared-ledger.json').write_text(run([PY,SKILL,'record','--repo',R,'--store',store,'--pair','vs2-comparison','--event',E/'prepared-event.json','--expected-last',last]),encoding='utf-8')
print(json.dumps({'status':summary['status'],'head':summary['head'],'checkpoint_tests':[r['tests'] for r in records],'review':'complete self-review'}))
