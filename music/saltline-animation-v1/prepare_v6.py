from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H/'scene-plan-v5.json').read_text());c['version']='v6';c['trial_version']='v6';c.pop('trial_seconds',None)
c['status']='Genuine twenty-second periodic timeline derived from accepted v5 look; new complete-loop review pending'
c['previous_feedback']={'date':'2026-09-29','verbatim':'could the loop be 20 seconds?','scope':'Make an actual twenty-second loop from accepted v5 look'}
c['far_dust']['loop_schedule']=[
 {'gust_index':0,'birth_x':665,'age_at_zero':6,'fade_in':2,'fade_out':5},
 {'gust_index':0,'birth_x':665,'age_at_zero':16,'fade_in':2,'fade_out':5},
 {'gust_index':1,'birth_x':685,'age_at_zero':13.25,'fade_in':2,'fade_out':5},
 {'gust_index':2,'birth_x':-156,'age_at_zero':8,'fade_in':2,'fade_out':4}]
c['far_dust']['loop_note']='Twenty-second local gust lifetimes, staggered renewal, zero-weight resets, unchanged 20 px/s travel and original colour/optical depth/cap/shape/mask. No forward prototype repeated as a shorter cycle.'
c['sunlight'].update({'fade_in':1,'fade_out':1.5,'age_at_zero':0,'loop_note':'Same 28 px/s cloud-shadow travel, width and attenuation; local reset faded to zero outside visible sunlight patch'})
c['approved_layers']={'v5_look':{'feedback':'perfect, commit and push everything','scope':'Accepted twelve-second look; v6 periodic timing remains a new delivery'}}
p=H/'scene-plan-v6.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
