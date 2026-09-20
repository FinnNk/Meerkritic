"""Reconstruct five complete propositions from the frozen C diary without changing its result."""
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path('WORKSPACE');R=ROOT/'extras/der-checkouts/vs2-interaction'
S=ROOT/'extras/der-checkouts/vs2-interaction-semantic2';E=ROOT/'extras/der-evidence/vs2-interaction/r1'
BASE='ff9af2e68d989590ebe030002e2e3789c35efef0'; D='6bf1544b1fa1f70f188ae19fd08f55df78574787'
phase=sys.argv[1]
def git(*args,cwd=S):
    return subprocess.check_output(['git','-c',f'safe.directory={R.as_posix()}',
        '-c',f'safe.directory={S.as_posix()}','-C',str(cwd),*args],text=True,encoding='utf-8').strip()
def original(path,ref=D):return git('show',f'{ref}:{path}',cwd=R)+'\n'
def write(path,content):
    p=S/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8',newline='\n')
def checkout(paths,ref=D):git('restore','--source',ref,'--staged','--worktree','--',*paths)
def comments(path,source):
    final=ast.parse(original(path));docs={n.name:ast.get_docstring(n) for n in ast.walk(final)
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and ast.get_docstring(n)}
    lines=source.splitlines(keepends=True)
    nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
        and n.name in docs and not ast.get_docstring(n) and any('app.' in ast.unparse(d) for d in n.decorator_list)]
    for node in sorted(nodes,key=lambda n:n.lineno,reverse=True):
        lines.insert(node.body[0].lineno-1,' '*node.body[0].col_offset+'"""'+docs[node.name]+'"""\n')
    return ''.join(lines)
changed=git('diff','--name-only',BASE,D,cwd=R).splitlines()
if phase=='p1':
    if not S.exists():git('worktree','add','-b','feat/vs2-interaction-corrected',str(S),BASE,cwd=R)
    checkout(['docs/development/milestone-review.md','docs/adr/ADR-0011-preserve-rule-evidence-across-revisions.md','docs/adr/README.md'])
    write('docs/adr/README.md','\n'.join(l for l in original('docs/adr/README.md').splitlines() if 'ADR-0012' not in l)+'\n')
    plan=original('docs/plans/VS2-plan.md');plan=plan[:plan.index('\n## Candidate milestone review')]
    write('docs/plans/VS2-plan.md',plan)
    backlog=original('IMPLEMENTATION_BACKLOG.yaml', 'e0f0a80')
    backlog=backlog.replace('B published in PR 12; DER vs2-rules/r1 verified; owner acceptance pending',
        'B approved and integrated via PR 12; exact reviewed tree verified; ADR-0011 implemented')
    write('IMPLEMENTATION_BACKLOG.yaml',backlog)
    title='docs: strengthen boundary review and activate the final VS2 batch'
elif phase=='p2':
    for path in ('src/semantic_reviewer/web/discovery.py','src/semantic_reviewer/web/rules.py'):
        write(path,comments(path,original(path,BASE)))
    title='docs: backfill discovery and rule HTTP caller contracts'
elif phase=='p3':
    stage='b97ce0f'
    paths=git('diff','--name-only','e0f0a80',stage,cwd=R).splitlines()
    checkout(paths,stage)
    checkout(['src/semantic_reviewer/adapters/rules.py','tests/test_rules.py',
        'src/semantic_reviewer/web/interaction.py','src/semantic_reviewer/web/rules.py'])
    path='src/semantic_reviewer/web/discovery.py';write(path,comments(path,original(path,stage)))
    path='src/semantic_reviewer/web/templates/rule.html'
    source=original(path).replace('{% if has_guidance %}<p><a href="/guidance?version={{ version_id }}">Compose guidance for this version</a></p>{% endif %}','')
    write(path,source)
    checkout(['docs/adr/README.md','docs/adr/ADR-0012-apply-review-intent-in-explicit-batches.md'])
    adr=original('docs/adr/ADR-0012-apply-review-intent-in-explicit-batches.md')
    adr=adr.replace('An explicit guidance send freezes','The next proposition will add an explicit guidance send that freezes')
    adr=adr.replace('`tests/test_guidance.py`\ncovers frozen context, invented output, provider failures, unknown completion,\ncontext bounds and advice that never applies state. Real local MAF compatibility\nis retained in external DER `vs2-interaction/r1`.',
        'Guidance runtime and compatibility confirmation belong to the next proposition.')
    write('docs/adr/ADR-0012-apply-review-intent-in-explicit-batches.md',adr)
    doc=original('docs/development/research-interaction.md')
    doc=doc[:doc.index('## Discussion and coherent guidance')]+'''## Exact-version discussion

Add immutable messages on a rule version; they remain historical after a revision.
Messages do not invoke an agent. The next proposition adds explicit coherent
guidance submission and advisory responses.
'''
    write('docs/development/research-interaction.md',doc)
    glossary=original('CONTEXT.md');write('CONTEXT.md',glossary[:glossary.index('## Guidance batch')])
    checkout(['src/semantic_reviewer/web/templates/base.html'], 'b97ce0f')
    path='src/semantic_reviewer/web/templates/base.html'
    header=original(path).splitlines()[29]
    source=(S/path).read_text(encoding='utf-8').splitlines();source[29]=header
    write(path,'\n'.join(source)+'\n')
    title='feat: save and atomically apply version-fenced research decisions'
elif phase=='p4':
    earlier='3aa2c73'
    paths=git('diff','--name-only','b97ce0f',earlier,cwd=R).splitlines()
    checkout(paths,earlier)
    finalpaths=['src/semantic_reviewer/adapters/guidance.py','src/semantic_reviewer/adapters/maf_guidance.py',
        'src/semantic_reviewer/application/guidance.py','src/semantic_reviewer/application/jobs.py','src/semantic_reviewer/domain/guidance.py',
        'src/semantic_reviewer/web/guidance.py','tests/test_guidance.py',
        'docs/adr/ADR-0012-apply-review-intent-in-explicit-batches.md','docs/development/research-interaction.md']
    checkout(finalpaths)
    path='src/semantic_reviewer/web/templates/rule.html';checkout([path])
    path='src/semantic_reviewer/web/templates/base.html';lines=(S/path).read_text(encoding='utf-8').splitlines();lines[29]=original(path).splitlines()[29];write(path,'\n'.join(lines)+'\n')
    glossary=original('CONTEXT.md');write('CONTEXT.md',glossary[:glossary.index('## Architecture projection')])
    title='feat: return advisory guidance from immutable submitted context'
elif phase=='p5':
    checkout(changed)
    title='feat: inspect architecture freshness and record the VS2 milestone review'
else:raise SystemExit('Unknown phase')
# Reassembly may alter whitespace around transitional imports; use the unchanged project formatter.
subprocess.run([str(R/'.venv/Scripts/ruff.exe'),'format',str(S)],check=True,capture_output=True)
subprocess.run([str(R/'.venv/Scripts/ruff.exe'),'check','--fix',str(S)],check=True,capture_output=True)
git('add','.')
git('commit','-m',title,'-m','Review-Unit: '+phase.upper())
sha=git('rev-parse','HEAD')
(E/(phase+'-identity.json')).write_text(json.dumps({'revision':sha,'diary':D,'base':BASE},indent=2))
print(sha)
