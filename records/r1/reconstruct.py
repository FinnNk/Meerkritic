import ast, json, os, subprocess
from pathlib import Path
ROOT=Path('WORKSPACE'); E=ROOT/'extras/der-evidence/vs2-study-tools/r1'
R=ROOT/'extras/der-checkouts/vs2-study-tools'; S=ROOT/'extras/der-checkouts/vs2-study-tools-semantic'
BASE='cd0a4d8c9a254e3027513274b39ce3f65cf227d2'; DIARY='9e47863265c21f27ac07b4b3613d0b1aec2fe3c1'
PY=R/'.venv/Scripts/python.exe'
env=os.environ.copy(); env.update(GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R),GIT_CONFIG_KEY_1='safe.directory',GIT_CONFIG_VALUE_1=str(S),GIT_CONFIG_KEY_2='safe.directory',GIT_CONFIG_VALUE_2=str(ROOT/'working'))
def run(args,cwd=R):
 r=subprocess.run([str(a) for a in args],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8')
 if r.returncode: raise RuntimeError(r.stdout+r.stderr)
 return r.stdout.strip()
def git(*args): return run(['git',*args],S)
def body(path): return subprocess.check_output(['git','show',DIARY+':'+path],cwd=R,env=env).decode('utf-8')
def write(path,text):
 p=S/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def commit(message):
 git('add','.');git('diff','--cached','--check');git('commit','-m',message)
 return git('rev-parse','HEAD')
assert run(['git','rev-parse','HEAD'])==DIARY
assert not run(['git','status','--porcelain'])
# Preserve supplemental binding for early runner invocations that accepted an abbreviated/ref argument.
bindings=[]
for label in ('baseline','implementation','diary'):
 rec=json.loads((E/(label+'-checks.json')).read_text())
 checkout=Path(rec['checkout'])
 head=run(['git','-c','safe.directory='+str(checkout),'rev-parse','HEAD'],checkout)
 tree=run(['git','-c','safe.directory='+str(checkout),'rev-parse','HEAD^{tree}'],checkout)
 assert rec['status']=='passed' and rec['tree']==tree
 assert not run(['git','-c','safe.directory='+str(checkout),'status','--porcelain'],checkout)
 bindings.append({'label':label,'recorded_revision_argument':rec['revision'],'observed_detached_head':head,'tree':tree,'record':label+'-checks.json'})
assert bindings[-1]['observed_detached_head']==DIARY
(E/'bound-check-identities.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8')
run(['git','worktree','add','-b','feat/vs2-study-tools',str(S),BASE])
git('cherry-pick','--no-commit','ce7bb20','69abf53')
commits=[commit('docs: record study agreement and freeze input preparation')]
path='src/semantic_reviewer/domain/study_preparation.py'; text=body(path); tree=ast.parse(text)
parts=[]
for node in tree.body:
 if isinstance(node,ast.ClassDef) or isinstance(node,ast.FunctionDef) and node.name=='preparation_progress':continue
 if isinstance(node,ast.ImportFrom) and node.module in ('typing','pydantic'):continue
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('Digest','Text') for t in node.targets):continue
 part=ast.get_source_segment(text,node)
 if isinstance(node,ast.ImportFrom) and node.module=='collections':part='from collections import defaultdict'
 parts.append(part)
write(path,'\n\n\n'.join(parts)+'\n')
path='tests/test_study_preparation.py'; text=body(path); tree=ast.parse(text)
imports='import hashlib\nimport json\nimport unittest\n\nfrom semantic_reviewer.domain.study_preparation import prepare_sample\n'
parts=[imports]
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ('source_rows','prepare'):
  parts.append(ast.get_source_segment(text,node))
 if isinstance(node,ast.ClassDef):
  methods=[m for m in node.body if isinstance(m,ast.FunctionDef) and m.name in ('test_reproducible_bounded_sample_accounts_for_every_source_without_text','test_deduplication_retains_lowest_original_index_and_exposure_precedes_sampling','test_invalid_records_fail_instead_of_silently_reducing_pool')]
  lines=text.splitlines()
  parts.append('class StudyPreparationTest(unittest.TestCase):\n'+'\n\n'.join('\n'.join(lines[m.lineno-1:m.end_lineno]) for m in methods))
write(path,'\n\n\n'.join(parts)+'\n')
run([PY,'-m','ruff','format','src/semantic_reviewer/domain/study_preparation.py','tests/test_study_preparation.py'],S)
commits.append(commit('feat: freeze reproducible study candidates and exclusions'))
for path in ('src/semantic_reviewer/domain/study_preparation.py','tests/test_study_preparation.py','tools/study_inputs.py','docs/development/study-preparation.md'):
 write(path,body(path))
commits.append(commit('feat: retain bounded human input-review attempts'))
git('cherry-pick',DIARY)
commits.append(git('rev-parse','HEAD'))
assert git('rev-parse','HEAD^{tree}')==run(['git','rev-parse',DIARY+'^{tree}'])
(E/'semantic-commits.json').write_text(json.dumps({'base':BASE,'diary':DIARY,'commits':commits,'tree':git('rev-parse','HEAD^{tree}')},indent=2),encoding='utf-8')
print(json.dumps({'commits':commits,'equivalent_tree':git('rev-parse','HEAD^{tree}')}))
