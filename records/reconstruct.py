"""Reassemble only frozen diary content into planned, checkpoint-verifiable propositions."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import textwrap

ROOT = Path('WORKSPACE')
R = ROOT/'extras/der-checkouts/vs2-grouping'
S = ROOT/'extras/der-checkouts/vs2-grouping-semantic'
E = ROOT/'extras/der-evidence/vs2-grouping/r1'
BASE = 'c9ef38f48b10d7876fe26babee36f2f15f258bf3'
DIARY = '0c1f39f31ba6ecba36d4568eaa66ebc54056079b'
phase = sys.argv[1]

def git(*args, cwd=S):
    return subprocess.check_output(['git','-c',f'safe.directory={R.as_posix()}',
        '-c',f'safe.directory={S.as_posix()}','-C',str(cwd),*args],text=True,encoding='utf-8').strip()

def original(path):
    return subprocess.check_output(['git','-c',f'safe.directory={R.as_posix()}',
        '-C',str(R),'show',f'{DIARY}:{path}']).decode('utf-8')

def write(path, content):
    target=S/path;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(content,encoding='utf-8',newline='\n')

def checkout(paths):
    for path in paths: write(path,original(path))

def remove(source, names):
    tree=ast.parse(source);lines=source.splitlines(keepends=True)
    nodes=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.name in names]
    for node in sorted(nodes,key=lambda n:n.lineno,reverse=True):
        start=min([node.lineno]+[d.lineno for d in node.decorator_list])-1
        del lines[start:node.end_lineno]
    return ''.join(lines)

changed=git('diff','--name-only',BASE,DIARY,cwd=R).splitlines()
if phase=='p1':
    if not S.exists():git('worktree','add','-b','feat/vs2-grouping',str(S),BASE,cwd=R)
    checkout(['AGENTS.md','docs/plans/VS2-plan.md','docs/development/README.md',
              'docs/adr/ADR-0009-freeze-explicit-annotation-selections.md','docs/adr/README.md'])
    write('docs/adr/README.md','\n'.join(line for line in original('docs/adr/README.md').splitlines()
                                        if 'ADR-0010' not in line)+'\n')
    title='docs: activate autonomous stacked delivery for remaining VS2 batches'
elif phase=='p2':
    paths=['config/models/nomic-embedding-fixture.json','config/routing/discovery-local.json',
        'src/semantic_reviewer/routing/selection.py','src/semantic_reviewer/application/embeddings.py',
        'src/semantic_reviewer/domain/grouping.py','src/semantic_reviewer/adapters/local_http.py',
        'src/semantic_reviewer/adapters/llama.py','src/semantic_reviewer/adapters/embedding.py',
        'src/semantic_reviewer/adapters/maf_embedding.py','tests/test_embeddings.py']
    checkout(paths)
    path='src/semantic_reviewer/domain/grouping.py'
    write(path,remove(original(path),{'cluster_vectors'}))
    title='feat: execute pinned local embeddings through MAF'
elif phase=='p3':
    checkout(changed)
    path='src/semantic_reviewer/domain/grouping.py'
    write(path,remove(original(path),{'cluster_vectors'}))
    path='src/semantic_reviewer/application/discovery.py'
    source=remove(original(path),{'cluster','coherent','write_members','read_members'})
    source=source.replace('Literal["embedding", "clustering"]','Literal["embedding"]')
    lines=source.splitlines(keepends=True)
    lines=[line for line in lines if not any(line.startswith('    '+field+':') for field in
            ('embedding_run','embedding_digest','threshold','minimum_size'))]
    source=''.join(lines)
    tree=ast.parse(source);lines=source.splitlines(keepends=True)
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=='run.request.kind == \'embedding\'')
    block=''.join(lines[node.body[0].lineno-1:node.body[-1].end_lineno])
    block=''.join(line[4:] if line.startswith('    ') else line for line in block.splitlines(keepends=True))
    lines[node.lineno-1:node.end_lineno]=[block]
    write(path,''.join(lines))
    path='src/semantic_reviewer/adapters/discovery.py'
    write(path,remove(original(path),{'write_members','read_members'}))
    path='src/semantic_reviewer/web/discovery.py'
    source=remove(original(path),{'cluster'})
    source=source.replace('run_id: str, page: int = Query(1, ge=1, le=10)','run_id: str')
    source=source.replace('summary, snapshot =','summary, _ =')
    a=source.index('            records =');b=source.index('        except LookupError',a)
    source=source[:a]+source[b:]
    source='\n'.join(line for line in source.splitlines() if not any(
        line.strip().startswith('"'+key+'":') for key in ('rows','page','total')))+'\n'
    write(path,source)
    path='src/semantic_reviewer/web/templates/discovery_run.html';source=original(path)
    a=source.index("{% if run.status == 'succeeded'");b=source.index('<details><summary>Exact run provenance',a)
    write(path,source[:a]+source[b:])
    path='tools/run.py';source=original(path)
    a=source.index('    cluster =');b=source.index('    discovery =',a);source=source[:a]+source[b:]
    a=source.index('            elif args.command == "cluster":');b=source.index('            elif args.run_id:',a)
    source=source[:a]+source[b:]
    source=source.replace('("embed", "cluster", "discovery")','("embed", "discovery")')
    write(path,source)
    path='tests/test_discovery.py';source=remove(original(path),{
        'test_clustering_replay_preserves_membership_and_terminal_state',
        'test_failed_embedding_cannot_supply_clustering','test_vector_checksum_fails_before_clustering',
        'test_browser_submits_only_same_origin_and_shows_verified_groups','VectorTest'})
    write(path,source)
    path='docs/development/discovery.md';source=original(path)
    a=source.index('## Local worker')
    source='# Reproducible embeddings\n\nQueue embeddings from a frozen selection in the harness and inspect its exact\ninputs, usage and immutable vector provenance. Clustering follows in the next proposition.\n\n'+source[a:]
    source='\n'.join(line for line in source.splitlines() if ' cluster <embedding-run-id>' not in line)+'\n'
    a=source.index('The threshold above');b=source.index('## Evidence and limits',a)
    source=source[:a]+source[b:]
    source=source.replace('memberships are another immutable Parquet file.','membership files follow in the clustering proposition.')
    source=source.replace('and a cluster from synthetic interpretations','from synthetic interpretations')
    write(path,source)
    write('README.md',original('README.md').replace('reproducible grouping and the limits of the current exploratory method.',
          'embedding provenance and compatibility limitations.'))
    write('IMPLEMENTATION_BACKLOG.yaml',original('IMPLEMENTATION_BACKLOG.yaml').replace(
        'A2/A3 implemented candidate; DER review and owner acceptance pending',
        'A2 implemented candidate; A3 follows at the next semantic checkpoint'))
    title='feat: queue and inspect immutable embedding runs'
elif phase=='p4':
    checkout(changed)
    title='feat: group pinned vectors with inspectable memberships and outliers'
else:
    raise SystemExit('Unknown phase')

if phase in ('p2','p3'):
    subprocess.run([str(R/'.venv/Scripts/ruff.exe'),'check','--fix','--select','F401,I001','.'],cwd=S,check=True)
    subprocess.run([str(R/'.venv/Scripts/ruff.exe'),'format','.'],cwd=S,check=True)
git('add','.')
git('commit','-m',title,'-m',f'Review-Unit: {phase.upper()}')
sha=git('rev-parse','HEAD')
(E/(phase+'-identity.json')).write_text(json.dumps({'revision':sha,'title':title},indent=2),encoding='utf-8')
print(json.dumps({'phase':phase,'revision':sha}))
if phase=='p4':
    if git('rev-parse','HEAD^{tree}') != git('rev-parse',DIARY+'^{tree}'):
        raise SystemExit('Final tree differs from frozen diary')
