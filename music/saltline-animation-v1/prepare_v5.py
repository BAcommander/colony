from pathlib import Path
import json, copy
H=Path(__file__).resolve().parent
c=json.loads((H/'scene-plan-v4.json').read_text());c['trial_version']='v5';c['version']='v5'
c['previous_feedback']={'date':'2026-09-29','verbatim':'did you tone down the distant fog? i struggle to see it now,','scope':'Distant dust visibility in longer v4 preview questioned'}
c['status']='Distant dust resupplied as earlier gusts leave view; v4 lighting/sunlight retained'
first=copy.deepcopy(c['far_dust']['gusts'][0]);first['x']=665
second=copy.deepcopy(c['far_dust']['gusts'][1]);second['x']=735
c['far_dust']['incoming_gusts']=[{'start':6,'fade_in':1.5,'texture_index':0,'gust':first},{'start':7.5,'fade_in':1.5,'texture_index':1,'gust':second}]
c['far_dust']['replenishment_note']='New arrivals from left side of basin replace outgoing gusts; original colour, optical depth, maximum opacity, speed, mask and gust shape retained. Incoming births fade locally, not a full-frame transition.'
p=H/'scene-plan-v5.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
