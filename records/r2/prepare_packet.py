import ast, hashlib, json, os, re, subprocess
from pathlib import Path

ROOT = Path('WORKSPACE')
E = ROOT/'extras/der-evidence/source-reading/r2'
R = ROOT/'extras/der-checkouts/source-reading-semantic'
STORE = ROOT/'extras/der-evidence'
PY = ROOT/'extras/der-checkouts/source-reading/.venv/Scripts/python.exe'
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
for label, sha in [('diary', i['diary']), *zip(('p1','p2','p3','p4','p5'), i['commits'])]:
    record_dir = E.parent/'r1' if label in ('p1','p2','p3') else E
    rec = json.loads((record_dir/(label+'-checks.json')).read_text())
    assert rec['status'] == 'passed' and rec['clean']
    assert run(['git', 'rev-parse', rec['revision']]) == sha
    assert run(['git', 'rev-parse', sha+'^{tree}']) == rec['tree']
    log = (record_dir/(label+'-checks.log')).read_text(encoding='utf-8')
    tree = ast.parse(run(['git','show',sha+':tools/check.py']))
    node = next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='commands' for t in n.targets))
    expected = [[n.value if isinstance(n,ast.Constant) else '<python>' for n in row.elts] for row in node.elts]
    observed = [line.removeprefix('Running: ') for line in log.splitlines() if line.startswith('Running: ')]
    assert len(expected) == len(observed)
    for wanted, actual in zip(expected, observed, strict=True):
        assert actual == ' '.join(wanted) if wanted[0] != '<python>' else actual.endswith(' '+' '.join(wanted[1:])) and '.venv' in actual
    assert re.search(r'^OK\s*$', log, re.M) and not re.search(r'skipped=|^SKIP', log, re.M)
    count = int(re.search(r'Ran (\d+) tests? in', log)[1])
    records.append(dict(label=label, revision=sha, tree=rec['tree'], tests=count, skipped=0, status='passed', expected_checks=expected, observed_checks=observed, evidence=str(record_dir.name)+'/'+label+'-checks.json'))
assert [v['tests'] for v in records] == [253,241,253,253,253,253]

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
assert len(changes['added']) == 12 and not changes['removed'] and len(changes['altered']) == 1
save('test-change-identities.json', changes)
save('verification-summary.json', dict(status='passed', base=i['base'], head=i['commits'][-1], checkpoints=records, test_changes=changes, retained_failure='../r1/targeted-first.log', failure_disposition='Existing test spy now forwards keyword arguments; selection evidence is checked; numeric GitHub redirects retained and standalone importer bound to its checkout. Failed diagnostics and incomplete rehearsals retained; final checkpoints pass afresh.'))

for name, arguments in [
    ('equivalence.json',['equivalence','--repo',R,'--diary',i['diary'],'--semantic',i['commits'][-1],'--diary-base',i['base'],'--semantic-base',i['base']]),
    ('snapshot.json',['snapshot','--repo',R,'--store',STORE,'--pair','source-reading','--round','r2','--diary-base',i['base'],'--semantic-base',i['base'],'--diary',i['diary'],'--semantic',i['commits'][-1]])
]:
    (E/name).write_text(run([PY,SKILL,*arguments]),encoding='utf-8')
manifest = STORE/'pairs/source-reading/rounds/r2/manifest.json'
actor = dict(client='Codex desktop',cli_version='not exposed',model='GPT-6',session='/root')
review = dict(schema_version=1,pair_id='source-reading',round_id='r2',manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),semantic_tip=i['commits'][-1],actor=actor,independence='self-review',mode='changes',status='complete',orientation_done=True,reviewed_commits=i['commits'][3:],aggregate_done=True,findings=[],check_records=['review-notes.md','propositions.md','verification-summary.json','test-change-identities.json','equivalence.json','docs-check.json','architecture-delta.json','browser-check.json','carry-forward.json','range-diff.txt'],limitations=['Author self-review, not independent approval','Windows/Python 3.12 only','No model rerun or human research judgement','Earlier targeted failure retained; cross-tab research-save discrepancy requires separate reconciliation'],carry_forward_record='carry-forward.json',platform_approval=False)
save('review.json', review)
for name,args in [('round-validation.json',['check-round','--manifest',manifest]),('review-validation.json',['validate-review','--manifest',manifest,'--report',E/'review.json'])]:
    (E/name).write_text(run([PY,SKILL,*args]),encoding='utf-8')
event=dict(kind='verification',round_id='r2',actor=actor,payload=dict(stage='locally_prepared',base=i['base'],diary=i['diary'],semantic=i['commits'][-1],records=['source-reading/r2/verification-summary.json','source-reading/r2/review.json'],note='Chronology is retained by materiality.md, discoveries.md and diary commits; this event records completed preparation, not an earlier setup time.'))
save('prepared-event.json',event)
(E/'prepared-ledger.json').write_text(run([PY,SKILL,'record','--repo',R,'--store',STORE,'--pair','source-reading','--event',E/'prepared-event.json','--expected-last',json.loads(run([PY,SKILL,'ledger','--store',STORE,'--pair','source-reading']))['last_hash']]),encoding='utf-8')
print(json.dumps(dict(head=i['commits'][-1],status='locally_prepared',tests=[r['tests'] for r in records])))
