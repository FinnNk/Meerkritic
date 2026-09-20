"""Reconstruct the recorded registry and synthesis propositions from frozen content."""
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path('WORKSPACE')
R=ROOT/'extras/der-checkouts/vs2-rules'; S=ROOT/'extras/der-checkouts/vs2-rules-semantic'
E=ROOT/'extras/der-evidence/vs2-rules/r1'
BASE='e81c2e867e714f2fed72d235eb44ba035b4bf302'
DIARY='ebd6d9eff6d74340ba15266217b6d9ce063d4dbf'
phase=sys.argv[1]
def git(*args,cwd=S):
    return subprocess.check_output(['git','-c',f'safe.directory={R.as_posix()}',
        '-c',f'safe.directory={S.as_posix()}','-C',str(cwd),*args],text=True,encoding='utf-8').strip()
def original(path): return git('show',f'{DIARY}:{path}',cwd=R)+'\n'
def write(path,content):
    target=S/path;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(content,encoding='utf-8',newline='\n')
def checkout(paths):
    # Git restore retains exact frozen bytes/modes, including Markdown final newlines.
    git('restore','--source',DIARY,'--staged','--worktree','--',*paths)
changed=git('diff','--name-only',BASE,DIARY,cwd=R).splitlines()
if phase=='p1':
    if not S.exists():git('worktree','add','-b','feat/vs2-rules',str(S),BASE,cwd=R)
    checkout(['docs/plans/VS2-plan.md','IMPLEMENTATION_BACKLOG.yaml',
        'docs/adr/ADR-0010-own-discovery-runs-under-one-worker.md','docs/adr/README.md'])
    write('docs/adr/README.md','\n'.join(l for l in original('docs/adr/README.md').splitlines()
        if 'ADR-0011' not in l)+'\n')
    title='docs: activate rule discovery against the integrated grouping prerequisite'
elif phase=='p2':
    paths=['CONTEXT.md','docs/adr/README.md','docs/adr/ADR-0011-preserve-rule-evidence-across-revisions.md',
        'docs/development/rules.md','src/semantic_reviewer/domain/rules.py',
        'src/semantic_reviewer/application/rules.py','src/semantic_reviewer/adapters/rules.py',
        'src/semantic_reviewer/adapters/migrations/010_rules.sql','src/semantic_reviewer/web/rules.py',
        'src/semantic_reviewer/web/templates/rule.html','src/semantic_reviewer/web/templates/rules.html',
        'src/semantic_reviewer/web/templates/rule_conflict.html','src/semantic_reviewer/web/templates/base.html',
        'src/semantic_reviewer/web/app.py','src/semantic_reviewer/asgi.py','tests/test_rules.py']
    checkout(paths)
    # Compose only the established registry contract. The later synthesis worker owns MAF imports.
    source=git('show',f'{BASE}:src/semantic_reviewer/bootstrap.py',cwd=R)+'\n'
    source=source.replace('from semantic_reviewer.application.jobs import JobService, Worker',
        'from semantic_reviewer.application.jobs import JobService, Worker\nfrom semantic_reviewer.application.rules import RuleService')
    final=original('src/semantic_reviewer/bootstrap.py')
    source+='\n\n'+final[final.index('def build_rules('):]
    write('src/semantic_reviewer/bootstrap.py',source)
    # Document current registry behaviour and the explicit next application, not a working model UI.
    docs=original('docs/development/rules.md')
    start=docs.index('## Evidence and research decisions')
    end=docs.index('## Failures, provenance and limits')
    write('docs/development/rules.md','# Inspect and challenge candidate rules\n\n'
        'This checkpoint exposes immutable registry publication through RuleService.propose\n'
        'and human inspection in **Rule registry**. A caller supplies a verified cluster,\n'
        'definition and origin; tests use explicit synthetic human-origin proposals.\n'
        'The next proposition adds routed MAF synthesis, queue submission and CLI access.\n\n'+docs[start:end])
    adr=original('docs/adr/ADR-0011-preserve-rule-evidence-across-revisions.md')
    adr=adr.replace('Synthesis uses the existing corpus queue', 'The planned synthesis application uses the existing corpus queue')
    adr=adr.replace('`tests/test_synthesis.py` challenges real MAF orchestration with\ncontrolled provider outputs, invalid references, provider/context failures and\ninterruption after publication.',
        'The next proposition will supply synthesis runtime and interrupted-publication checks.')
    write('docs/adr/ADR-0011-preserve-rule-evidence-across-revisions.md',adr)
    title='feat: preserve immutable rule versions and fenced research decisions'
elif phase=='p3':
    checkout(changed)
    title='feat: synthesise traceable rule candidates through routed MAF workflows'
else: raise SystemExit('Unknown phase')
git('add','.')
git('commit','-m',title,'-m','Review-Unit: '+phase.upper())
sha=git('rev-parse','HEAD')
(E/(phase+'-identity.json')).write_text(json.dumps({'revision':sha,'diary':DIARY,'base':BASE},indent=2))
print(sha)
