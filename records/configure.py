import json
from pathlib import Path

root = Path('WORKSPACE/extras/der-checkouts/vs2-grouping')
config = json.loads((root/'config/routing/llama-local.json').read_text())
config['inventory']['identity'] = {'id':'llama-discovery-fixture','version':'1'}
config['inventory']['models'].append({
    'id':'nomic-embed-v1.5-local','provider':'llama.cpp','family':'nomic-bert',
    'locality':'local','status':'active_current','capabilities':['embeddings'],
    'practical_input_tokens':2048,'output_tokens':0,
    'evidence':'Synthetic compatibility fixture only; see config/models/nomic-embedding-fixture.json. No comparative quality or empirical adoption claim.'})
policy = config['policies'][0]
policy['inventory'] = config['inventory']['identity']
policy['identity'] = {'id':'local-discovery-fixture','version':'1'}
policy['routes'].append({'task_class':'embedding','models':['nomic-embed-v1.5-local']})
policy['context']['reserve_output_tokens'] = 0
config['system_default'] = policy['identity']
(root/'config/routing/discovery-local.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
