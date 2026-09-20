import ast, hashlib, json, os, re, subprocess
from pathlib import Path

ROOT = Path('WORKSPACE')
E = ROOT/'extras/der-evidence/assessment-clarity/r1'
R = ROOT/'extras/der-checkouts/assessment-clarity-semantic'
STORE = ROOT/'extras/der-evidence'
PY = ROOT/'extras/der-checkouts/assessment-clarity/.venv/Scripts/python.exe'
SKILL = R/'.agents/skills/double-entry-review/scripts/der.py'
env = os.environ.copy()
env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(R))

def run(args):
    p = subprocess.run([str(a) for a in args], cwd=R, env=env, capture_output=True, text=True, encoding='utf-8')
    assert p.returncode == 0, p.stdout+p.stderr
    return p.stdout.strip()

def save(name, value):
    (E/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

i = json.loads((E/'semantic-commits.json').read_text())
records = []
for label, sha in [('diary', i['diary']), *zip(('p1','p2','p3'), i['commits'])]:
    rec = json.loads((E/(label+'-checks.json')).read_text())
    assert rec['status'] == 'passed' and rec['clean']
    assert run(['git', 'rev-parse', rec['revision']]) == sha
    assert run(['git', 'rev-parse', sha+'^{tree}']) == rec['tree']
    log = (E/(label+'-checks.log')).read_text(encoding='utf-8')
    tree = ast.parse(run(['git','show',sha+':tools/check.py']))
    node = next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='commands' for t in n.targets))
    expected = [[n.value if isinstance(n,ast.Constant) else '<python>' for n in row.elts] for row in node.elts]
    observed = [line.removeprefix('Running: ') for line in log.splitlines() if line.startswith('Running: ')]
    assert len(expected) == len(observed)
    for wanted, actual in zip(expected, observed, strict=True):
        assert actual == ' '.join(wanted) if wanted[0] != '<python>' else actual.endswith(' '+' '.join(wanted[1:])) and '.venv' in actual
    assert re.search(r'^OK\s*$', log, re.M) and not re.search(r'skipped=|^SKIP', log, re.M)
    count = int(re.search(r'Ran (\d+) tests? in', log)[1])
    records.append(dict(label=label, revision=sha, tree=rec['tree'], tests=count, skipped=0, status='passed', expected_checks=expected, observed_checks=observed, evidence=label+'-checks.json'))
assert [v['tests'] for v in records] == [233,229,233,233]

def tests(rev):
    found = {}
    for path in run(['git','ls-tree','-r','--name-only',rev,'tests']).splitlines():
        if not path.endswith('.py'): continue
        tree = ast.parse(run(['git','show',rev+':'+path]))
        for cls in tree.body:
            if isinstance(cls,ast.ClassDef):
                for f in cls.body:
                    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name.startswith('test_'):
                        found[path+'::'+cls.name+'::'+f.name] = hashlib.sha256(ast.dump(f).encode()).hexdigest()
    return found

before, after = tests(i['base']), tests(i['commits'][-1])
changes = dict(added=sorted(after.keys()-before.keys()), removed=sorted(before.keys()-after.keys()), altered=sorted(k for k in before.keys()&after.keys() if before[k]!=after[k]))
assert len(changes['added']) == 4 and not changes['removed'] and len(changes['altered']) == 1
save('test-change-identities.json', changes)
save('verification-summary.json', dict(status='passed', base=i['base'], head=i['commits'][-1], checkpoints=records, test_changes=changes, retained_failure='implementation-checks.json', failure_disposition='Existing provenance test expected v2; deliberate prompt update requires v3. Expectation corrected diary-first, remaining assertions preserved. All final checkpoints passed afresh.'))

for name, arguments in [
    ('equivalence.json',['equivalence','--repo',R,'--diary',i['diary'],'--semantic',i['commits'][-1],'--diary-base',i['base'],'--semantic-base',i['base']]),
    ('snapshot.json',['snapshot','--repo',R,'--store',STORE,'--pair','assessment-clarity','--round','r1','--diary-base',i['base'],'--semantic-base',i['base'],'--diary',i['diary'],'--semantic',i['commits'][-1]])
]:
    (E/name).write_text(run([PY,SKILL,*arguments]),encoding='utf-8')
manifest = STORE/'pairs/assessment-clarity/rounds/r1/manifest.json'
actor = dict(client='Codex desktop',cli_version='not exposed',model='GPT-6',session='/root')
review = dict(schema_version=1,pair_id='assessment-clarity',round_id='r1',manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),semantic_tip=i['commits'][-1],actor=actor,independence='self-review',mode='full',status='complete',orientation_done=True,reviewed_commits=i['commits'],aggregate_done=True,findings=[],check_records=['review-notes.md','propositions.md','verification-summary.json','test-change-identities.json','equivalence.json','docs-check.json','architecture-delta.json','browser-check.json','schema-compatibility.json','live-before.json'],limitations=['Author self-review, not independent approval','Windows/Python 3.12 only','No model rerun or human research judgement','Earlier screenshot exports and failed prompt-version expectation retained'],carry_forward_record=None,platform_approval=False)
save('review.json', review)
for name,args in [('round-validation.json',['check-round','--manifest',manifest]),('review-validation.json',['validate-review','--manifest',manifest,'--report',E/'review.json'])]:
    (E/name).write_text(run([PY,SKILL,*args]),encoding='utf-8')
event=dict(kind='verification',round_id='r1',actor=actor,payload=dict(stage='locally_prepared',base=i['base'],diary=i['diary'],semantic=i['commits'][-1],records=['assessment-clarity/r1/verification-summary.json','assessment-clarity/r1/review.json'],note='Chronology is retained by materiality.md, discoveries.md and diary commits; this event records completed preparation, not an earlier setup time.'))
save('prepared-event.json',event)
(E/'prepared-ledger.json').write_text(run([PY,SKILL,'record','--repo',R,'--store',STORE,'--pair','assessment-clarity','--event',E/'prepared-event.json','--expected-last','none']),encoding='utf-8')
print(json.dumps(dict(head=i['commits'][-1],status='locally_prepared',tests=[r['tests'] for r in records])))
