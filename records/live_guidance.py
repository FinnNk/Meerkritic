"""Run real local guidance on a copy of the synthetic Batch B live candidate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

ROOT=Path('WORKSPACE')
REPO=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'extras/der-checkouts/vs2-interaction'
sys.path.insert(0,str(REPO/'src'))
from semantic_reviewer.bootstrap import build_guidance, build_worker
from semantic_reviewer.domain.guidance import GuidanceRequest, GuidanceTarget
from semantic_reviewer.domain.interaction import DiscussionNote

identity=str(uuid4())
runtime=ROOT/'extras/preflight/vs2-guidance'/('runtime-'+identity)
shutil.copytree(ROOT/'extras/preflight/vs2-synthesis/runtime-1b250c59-74e6-4fa5-8267-1d087662eb83',runtime)
service=build_guidance(runtime)
head=service.rules.store.recent()[0]
note=DiscussionNote(id=str(uuid4()),version_id=head.version_id,actor='Automated fixture',
    text='Clarify how ownership transfer affects the proposed file closure rule.')
service.workspace.discuss(note)
request=GuidanceRequest(id=identity,actor='Automated compatibility fixture',
    instruction='Suggest a concise clarification for the selected discussion. Do not apply edits or decisions.',
    targets=(GuidanceTarget(version_id=head.version_id,expected_revision=head.revision,
        discussion_ids=(note.id,)),))
service.submit(request)
worker=build_worker(runtime,REPO/'config/routing/discovery-local.json','http://127.0.0.1:8081')
worker.run(once=True)
run,snapshot,result=service.inspect(identity)
report={'scope':'Synthetic functional compatibility, no human research labels or quality claim',
    'source_revision':subprocess.check_output(['git','-c',f'safe.directory={REPO.as_posix()}',
        '-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
    'run':run,'snapshot':snapshot,'result':result,'retained_runtime':str(runtime),
    'rule_unchanged':service.rules.store.read(head.version_id)[0]==head}
(ROOT/'extras/der-evidence/vs2-interaction/r1'/('live-guidance-'+identity+'.json')).write_text(
    json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'id':identity,'status':run['status'],'result_digest':run['result_digest'],
    'rule_unchanged':report['rule_unchanged']}))
assert run['status']=='responded',run['error']
assert report['rule_unchanged']
