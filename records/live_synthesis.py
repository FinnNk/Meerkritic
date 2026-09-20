"""Exercise real embedding and generation on explicitly synthetic interpretations."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('WORKSPACE')
REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'extras/der-checkouts/vs2-rules'
sys.path[:0] = [str(REPO/'src'), str(REPO/'tests')]
from test_discovery import DiscoveryTest
from test_selections import SelectionsTest
from semantic_reviewer.adapters.embedding import EmbeddingProfile, LlamaEmbeddingClient
from semantic_reviewer.adapters.maf_embedding import MafEmbeddingRuntime
from semantic_reviewer.adapters.maf_synthesis import MafSynthesisRuntime
from semantic_reviewer.adapters.llama import LlamaClient
from semantic_reviewer.adapters.rules import SQLiteRules
from semantic_reviewer.application.rules import RuleService
from semantic_reviewer.application.synthesis import RuleSynthesisExecution

test = DiscoveryTest()
test.setUp()
test.issue.update(issue_statement='A function opens a file and leaks its handle on an exception path.',
    proposed_invariant='Every acquired file handle must be closed on every exit unless ownership is transferred.',
    actionable_engineering_concern='uncertain', generalisable='uncertain', coarse_categories=['resource_management'])
test.execution.runtime = MafEmbeddingRuntime(LlamaEmbeddingClient(
    'http://127.0.0.1:8082', EmbeddingProfile.model_validate_json(
        (REPO/'config/models/nomic-embedding-fixture.json').read_bytes()),
    ROOT/'extras/preflight/vs2-embedding/nomic-embed-text-v1.5.f16.gguf'))
rules = RuleService(test.discovery, SQLiteRules(test.database, test.files), test.files)
test.execution.synthesis = RuleSynthesisExecution(test.discovery, rules, test.routing,
    MafSynthesisRuntime(LlamaClient('http://127.0.0.1:8081')))
annotations = []
for index, issue in enumerate((
    'A file handle remains open when JSON parsing throws before the close call.',
    'An early return skips the close call for a newly opened output file.',
)):
    test.issue.update(issue_statement=issue)
    annotations.append(SelectionsTest.choose(test, index))
selection = test.selections.freeze(SelectionsTest.request(test, *annotations))
embedded = test.discovery.embed(selection.id)
test.worker.run(once=True)
embedded, _ = test.discovery.inspect(embedded.id)
assert embedded.status == 'succeeded', embedded.error
cluster = test.discovery.cluster(embedded.id, .5)
test.worker.run(once=True)
run = test.discovery.synthesise(cluster.id, 0)
test.worker.run(once=True)
run, body = test.discovery.inspect(run.id)
trace = test.files.read_json(body['trace_digest']) if body.get('trace_digest') else None
report = {'scope':'Synthetic API/MAF compatibility only; fixture decisions are not human labels.',
    'source_revision':subprocess.check_output(['git','-c',f'safe.directory={REPO.as_posix()}',
        '-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
    'embedding_run':embedded.id, 'cluster_run':cluster.id, 'synthesis_run':run.id,
    'status':run.status, 'result_digest':run.result_digest, 'result':body, 'trace':trace}
target = ROOT/'extras/preflight/vs2-synthesis'/('runtime-'+run.id)
shutil.copytree(test.root,target)
report['retained_runtime'] = str(target)
destination = ROOT/'extras/der-evidence/vs2-rules/r1'/('live-'+run.id+'.json')
destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('result','trace')}))
test.doCleanups()
assert run.status == 'succeeded', run.error
assert body.get('rule_version'), body.get('insufficiency_reason')
