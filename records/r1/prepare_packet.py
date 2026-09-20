import ast,hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-draft-repair/r1';R=ROOT/'extras/der-checkouts/vs2-draft-repair-semantic';PY=ROOT/'extras/der-checkouts/vs2-draft-repair/.venv/Scripts/python.exe';SKILL=R/'.agents/skills/double-entry-review/scripts/der.py';store=ROOT/'extras/der-evidence'
i=json.loads((E/'semantic-commits.json').read_text());env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
def run(args):
 p=subprocess.run([str(x) for x in args],env=env,capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr;return p.stdout
records=[]
for number,(label,sha) in enumerate(zip(('p1-recheck','p2-final','p3','p4'),i['commits'],strict=True),1):
 r=json.loads((E/(label+'-checks.json')).read_text());log=(E/(label+'-checks.log')).read_text(encoding='utf-8-sig');assert r['revision']==sha and r['clean'] and r['status']=='passed';assert all(c['exit_code']==0 for c in r['commands'])
 tree=ast.parse((Path(r['checkout'])/'tools/check.py').read_text(encoding='utf-8'));node=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='commands' for t in n.targets));expected=[[n.value if isinstance(n,ast.Constant) else '<python>' for n in row.elts] for row in node.elts];observed=[l.removeprefix('Running: ') for l in log.splitlines() if l.startswith('Running: ')];assert len(expected)==len(observed)
 for wanted,actual in zip(expected,observed,strict=True):
  assert actual==' '.join(wanted) if wanted[0]!='<python>' else (actual.endswith(' '+' '.join(wanted[1:])) and '.venv' in actual)
 count=int(re.search(r'Ran (\d+) tests? in',log)[1]);assert re.search(r'^OK\s*$',log,re.M) and not re.search(r'skipped=|^SKIP',log,re.M)
 records.append(dict(proposition='P'+str(number),revision=sha,tree=r['tree'],tests=count,skipped=0,status='passed',expected_checks=expected,observed_checks=observed,evidence=label+'-checks.json'))
assert [r['tests'] for r in records]==[215,225,229,229]
summary=dict(status='passed',head=i['commits'][-1],base=i['base'],checkpoints=records,test_changes={'backend_contract_tests_added':10,'browser_contract_tests_added':4,'existing_tests_removed':0,'existing_tests_altered':0},diary='diary-complete-checks.json',retained_failed_verifications=['p1-checks.json','p2-checks.json','diary-checks.json','diary-final-checks.json'],dispositions={'p1':'Intermittent Windows temporary-Git cleanup lock; unchanged exact commit passed separate recheck; cause unresolved','p2_and_diary':'Existing legacy successful-result regression found; repaired diary-first, existing test unchanged; final checkpoints verified afresh'})
(E/'verification-summary.json').write_text(json.dumps(summary,indent=2))
# Verify no existing test definitions disappeared or changed, rather than infer from totals.
def tests(rev):
 out={}
 for file in run(['git','-C',R,'ls-tree','-r','--name-only',rev,'tests']).splitlines():
  if not file.endswith('.py'):continue
  body=run(['git','-C',R,'show',rev+':'+file]);tree=ast.parse(body)
  for cls in tree.body:
   if isinstance(cls,ast.ClassDef):
    for f in cls.body:
     if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name.startswith('test_'):out[file+'::'+cls.name+'::'+f.name]=hashlib.sha256(ast.dump(f).encode()).hexdigest()
 return out
before=tests(i['base']);after=tests(i['commits'][-1]);removed=sorted(before.keys()-after.keys());altered=sorted(k for k in before.keys()&after.keys() if before[k]!=after[k]);added=sorted(after.keys()-before.keys());assert not removed and not altered and len(added)==14
(E/'test-change-identities.json').write_text(json.dumps(dict(added=added,removed=removed,altered=altered),indent=2))
(E/'equivalence.json').write_text(run([PY,SKILL,'equivalence','--repo',R,'--diary',i['diary'],'--semantic',i['commits'][-1],'--diary-base',i['base'],'--semantic-base',i['base']]))
(E/'snapshot.json').write_text(run([PY,SKILL,'snapshot','--repo',R,'--store',store,'--pair','vs2-draft-repair','--round','r1','--diary-base',i['base'],'--semantic-base',i['base'],'--diary',i['diary'],'--semantic',i['commits'][-1]]))
M=store/'pairs/vs2-draft-repair/rounds/r1/manifest.json';actor={'client':'Codex desktop','cli_version':'not exposed','model':'GPT-6','session':'/root'}
review=dict(schema_version=1,pair_id='vs2-draft-repair',round_id='r1',manifest_sha256=hashlib.sha256(M.read_bytes()).hexdigest(),semantic_tip=i['commits'][-1],actor=actor,independence='self-review',mode='full',status='complete',orientation_done=True,reviewed_commits=i['commits'],aggregate_done=True,findings=[],check_records=['review-notes.md','propositions.md','verification-summary.json','test-change-identities.json','equivalence.json','docs-check.json','architecture-delta.json','browser-check.json','upgrade-rehearsal.json','live-after.json','screenshot-check.json'],limitations=['Author self-review, not independent approval','Windows/Python 3.12 only','One unchanged P1 run hit intermittent temporary-Git cleanup lock; cause unresolved, failure and passing recheck retained','Workspace temporary-Git lock also affected corrected diary; normal OS temporary directory passed 40 isolated repetitions and is used for subsequent complete checks','No human research annotations or grouping runs; EDR remains draft'],carry_forward_record=None,platform_approval=False)
(E/'review.json').write_text(json.dumps(review,indent=2));(E/'round-validation.json').write_text(run([PY,SKILL,'check-round','--manifest',M]));(E/'review-validation.json').write_text(run([PY,SKILL,'validate-review','--manifest',M,'--report',E/'review.json']))
event={'kind':'verification','round_id':'r1','actor':actor,'payload':{'stage':'locally_prepared','base':i['base'],'diary':i['diary'],'semantic':i['commits'][-1],'summary':'All four exact semantic checkpoints and corrected frozen diary pass. Original failed attempts retained. Exact tracked-tree equivalence and full author self-review complete. Archive publication remains separate.','records':['vs2-draft-repair/r1/verification-summary.json','vs2-draft-repair/r1/review.json','vs2-draft-repair/r1/equivalence.json']}}
(E/'prepared-event.json').write_text(json.dumps(event,indent=2));last=json.loads(run([PY,SKILL,'ledger','--store',store,'--pair','vs2-draft-repair']))['last_hash'];(E/'prepared-ledger.json').write_text(run([PY,SKILL,'record','--repo',R,'--store',store,'--pair','vs2-draft-repair','--event',E/'prepared-event.json','--expected-last',last]));print(json.dumps({'head':summary['head'],'tests':[r['tests'] for r in records],'review':'complete self-review'}))
