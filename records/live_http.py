"""Exercise the exact final app over loopback HTTP on an isolated synthetic runtime."""
import json,socket,sys,threading,time,urllib.request,urllib.parse
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4
import uvicorn
ROOT=Path('WORKSPACE');E=ROOT/'extras/der-evidence/vs2-interaction/r1'
R=Path(sys.argv[1]);report=Path(sys.argv[2]);sys.path.insert(0,str(R/'src'))
from semantic_reviewer.asgi import build_app
from semantic_reviewer.bootstrap import build_guidance,build_architecture
from semantic_reviewer.adapters.architecture import snapshot
runtime=Path(json.loads(report.read_text())['retained_runtime']);service=build_guidance(runtime)
head=service.rules.store.recent()[0];batch=json.loads(report.read_text())['run']['id']
view=build_architecture(runtime)
projection=view.publish(asdict(snapshot(ROOT/'extras/der-checkouts/vs2-interaction-integrated-base')),asdict(snapshot(R)))
assert not view.read()['stale']
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
server=uvicorn.Server(uvicorn.Config(build_app(runtime),log_level='warning'))
thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start()
base=f'http://127.0.0.1:{port}';records=[]
def request(path,fields=None,contains=None):
 data=None if fields is None else urllib.parse.urlencode(fields).encode()
 req=urllib.request.Request(base+path,data=data,headers={'Origin':base})
 with urllib.request.urlopen(req,timeout=30) as response:
  text=response.read().decode('utf-8');assert response.status==200
  assert chr(0xc2) not in text and chr(0xc3) not in text,'Encoding damage'
  if contains:assert contains in text,contains
  records.append({'path':path,'method':'GET' if fields is None else 'POST','status':response.status,'contains':contains})
 return text
try:
 for i in range(100):
  if server.started:break
  time.sleep(.1)
 assert server.started
 for path in ('/','/rules','/review-workspace','/guidance','/rules/'+head.version_id):request(path)
 request('/guidance/'+batch,contains='Advisory response')
 request('/architecture',contains='matches the current source fingerprint')
 draft=str(uuid4());fields={'draft_id':draft,'actor':'HTTP compatibility fixture','version_0':head.version_id,'revision_0':str(head.revision),'action_0':'defer','rationale_0':'Synthetic staged intent'}
 request('/review-workspace/save',fields,'Apply this saved batch')
 assert service.rules.store.read(head.version_id)[0]==head
 request('/review-workspace/apply',{'draft_id':draft,'revision':'1'},'Applied batch')
 assert service.workspace.task(head.version_id)['state']=='deferred'
 request('/rules/'+head.version_id,contains='Review state: deferred')
 assert 'Promote candidate' not in request('/rules/'+head.version_id)
 request('/guidance/'+batch,contains='Historical context')
 restarted=build_guidance(runtime)
 assert restarted.workspace.read(draft)[0]['status']=='applied'
 assert restarted.workspace.task(head.version_id)['state']=='deferred'
 result={'source_revision':json.loads((E/'p5-identity.json').read_text())['revision'],'runtime':str(runtime),'scope':'Synthetic real loopback HTTP; no visual layout or research quality claim','projection':projection,'requests':records,'restart_retained':True,'status':'passed'}
 (E/'live-http.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps({'status':'passed','requests':len(records),'projection':projection}))
finally:
 server.should_exit=True;thread.join(15);sock.close()
