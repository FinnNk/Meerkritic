"""Synthetic API/MAF compatibility only; never creates human research labels."""
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path('WORKSPACE')
REPO = ROOT/'extras/der-checkouts/vs2-grouping-p4'
sys.path[:0] = [str(REPO/'src'),str(REPO/'tests')]
from test_discovery import DiscoveryTest
from semantic_reviewer.adapters.embedding import EmbeddingProfile,LlamaEmbeddingClient
from semantic_reviewer.adapters.maf_embedding import MafEmbeddingRuntime

test = DiscoveryTest()
test.setUp()
test.execution.runtime = MafEmbeddingRuntime(LlamaEmbeddingClient(
    'http://127.0.0.1:8082', EmbeddingProfile.model_validate_json(
        (REPO/'config/models/nomic-embedding-fixture.json').read_bytes()),
    ROOT/'extras/preflight/vs2-embedding/nomic-embed-text-v1.5.f16.gguf'))
run, body = test.embed()
report = {'scope':'Synthetic compatibility; automated fixture decisions are not research labels',
          'source_revision':'125fd8c055b9c110efa1c4dd31dcc661358b32bc','run_id':run.id,'status':run.status,'result_digest':run.result_digest,'result':body}
if run.status == 'succeeded':
    cluster = test.discovery.cluster(run.id,.85)
    test.worker.run(once=True)
    final, result = test.discovery.inspect(cluster.id)
    report.update(cluster_id=final.id, cluster_status=final.status,
                  cluster_digest=final.result_digest,cluster_result=result)
target = ROOT/'extras/preflight/vs2-embedding'/('runtime-'+run.id)
shutil.copytree(test.root,target)
report['retained_runtime'] = str(target)
destination = ROOT/'extras/der-evidence/vs2-grouping/r1/live-embedding.json'
destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('result','cluster_result')}))
test.doCleanups()
if run.status != 'succeeded' or report.get('cluster_status') != 'succeeded':
    raise SystemExit(1)
