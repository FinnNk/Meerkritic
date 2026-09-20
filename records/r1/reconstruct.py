import json,subprocess,os
from pathlib import Path
root=Path('WORKSPACE'); e=root/'extras/der-evidence/vs2-comparison/r1'; diary=root/'extras/der-checkouts/vs2-comparison'; semantic=root/'extras/der-checkouts/vs2-comparison-semantic-r1'; common=root/'working'; base='f5b23e44e4f13237a9f505f2f8182e0561813efe'; frozen='ccedd3d85b965d4f6a08e095ca8345e8895985a5'
record=json.loads((e/'diary-checks.json').read_bytes());assert record['status']=='passed' and record['revision']==frozen and record['clean']
plan='''# Frozen semantic propositions: vs2-comparison/r1

Verified diary ccedd3d85b965d4f6a08e095ca8345e8895985a5, tree 9e8c7ccfb9ef4ff4c6a4b1197445626fdd360c24.
Base f5b23e44e4f13237a9f505f2f8182e0561813efe. Windows/Python 3.12, checkpoint-owned locked environment for every unit and final tip. No tests retired or weakened.

Objective: provide the fixed EDR comparison and human-rating evidence workflow without producing unregistered research comparisons or supplying human judgements.

| Unit | Complete proposition | Prerequisites | Required evidence |
| --- | --- | --- | --- |
| P1 | Both methods can use exactly the same interpretation text; the prescribed lexical baseline has deterministic groups and representatives. | Existing interpretation/grouping contracts | Inclusive Jaccard boundary, transitivity, empty tokens, case folding, ties, input bounds, unchanged discovery tests; 186 total tests expected |
| P2 | Equal masked budgets, membership deduplication and complete ratings yield exact fixed criteria with explicit failure/insufficiency. | P1 shared grouping semantics | Missing/foreign/uncertain ratings, shared groups, review cap, coverage boundaries, 75% and 10pp thresholds, retries and resource bounds; 199 total |
| P3 | A comparison binds the same immutable selection, text, vectors and stored worker attempts; replay detects changed methods and queue time does not inflate execution. | P1/P2 and existing discovery ports | Real SQLite/Parquet/MAF fixture path, drift/corruption, failed and repeated attempts, pinned profile, missing timestamps, retry accounting; 210 total |
| P4 | Commands check prospective registration, publish immutable assessment files and freeze submitted ratings before revealing scores; the operator can reproduce the workflow. | P3 data binding and P2 assessment | Isolated Git registration, identity/configuration drift, complete CLI fixture publication, no fixture research claim, pre-registration failure; 215 total |
| P5 | Existing guides, planning and integration records describe the delivered tooling and remaining human/registration gates. | P1-P4 | Markdown links/tables, source-manifest hashes, actual CLI help, full 215 tests, architecture before/after/delta |

Compare alternatives: a four-unit series would combine stored-evidence binding and registration/publication. Their contracts have different trust boundaries and independent tests, so use five units within one PR. Splitting into more PRs adds owner overhead without an unmerged external dependency. A failure showing that P3 cannot be assessed without P4 would challenge this boundary; its direct application tests supply the independent caller.

Map from actual diary: P1 derives 0a5f750; P2 derives 5403e7a plus later criterion tests in e58220f; P3 derives e58220f, ba47256 and 59e1a2c; P4 derives e58220f, ba47256 and guide clarification in 59e1a2c; P5 derives b310a2f and ccedd3d. No clean chronology is claimed for the diary. No final content changes are authorised by this reconstruction.

Research limitation: records verify consistency, not identity authentication or undisclosed activity. Registered-code changes require an explicit amendment and cannot silently reuse a different registration. No new study UI/database or automatic adoption. Review is author self-review; owner approval remains independent.
'''
(e/'propositions.md').write_text(plan,encoding='utf-8')
units=[('feat: share interpretation text and add the fixed lexical baseline',['src/semantic_reviewer/domain/grouping.py','src/semantic_reviewer/application/discovery.py','tests/test_study_grouping.py']),('feat: assess masked groups against fixed study criteria',['src/semantic_reviewer/domain/study.py','tests/test_study.py']),('feat: bind comparisons to exact stored inputs and attempts',['src/semantic_reviewer/application/comparison.py','tests/test_comparison.py']),('feat: publish registered comparison and rating evidence',['tools/study_compare.py','tests/test_study_cli.py','docs/development/study-comparison.md'])]
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(common),GIT_CONFIG_KEY_1='safe.directory',GIT_CONFIG_VALUE_1=str(diary),GIT_CONFIG_KEY_2='safe.directory',GIT_CONFIG_VALUE_2=str(semantic))
def git(repo,*args,binary=False):
 p=subprocess.run(['git','-C',str(repo),*map(str,args)],env=env,capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace'))
 return p.stdout if binary else p.stdout.decode('utf-8').strip()
changed=git(diary,'diff','--name-only',base,frozen).splitlines();used={p for _,paths in units for p in paths};units.append(('docs: backfill comparison workflow and integration status',[p for p in changed if p not in used]));assert set(changed)=={p for _,paths in units for p in paths}
git(common,'worktree','add','-b','feat/vs2-comparison',semantic,base);commits=[]
for number,(message,paths) in enumerate(units,1):
 for path in paths:
  target=semantic/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(git(diary,'show',f'{frozen}:{path}',binary=True))
 git(semantic,'add','--',*paths);git(semantic,'commit','-m',message,'-m',f'Review-Unit: P{number}')
 commits.append(git(semantic,'rev-parse','HEAD'))
assert git(semantic,'rev-parse','HEAD^{tree}')==record['tree']
identity={'base':base,'diary':frozen,'commits':commits,'tree':record['tree']};(e/'semantic-commits.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
skill=semantic/'.agents/skills/double-entry-review/scripts/der.py';py=diary/'.venv/Scripts/python.exe'
for name,args in [('equivalence',['equivalence','--repo',semantic,'--diary',frozen,'--semantic',commits[-1],'--diary-base',base,'--semantic-base',base]),('snapshot',['snapshot','--repo',semantic,'--store',root/'extras/der-evidence','--pair','vs2-comparison','--round','r1','--diary-base',base,'--semantic-base',base,'--diary',frozen,'--semantic',commits[-1]])]:
 p=subprocess.run([str(py),str(skill),*map(str,args)],env=env,capture_output=True,text=True,encoding='utf-8');(e/(name+'.json')).write_text(p.stdout,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
print(json.dumps(identity))
