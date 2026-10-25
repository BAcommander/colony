"""Preserve initial native tests and select corrected tiny-pane/core coverage."""
from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent;A=H/'history'/'initial-pane-steam-study';assert not A.exists();A.mkdir(parents=True)
for name in ['scene-plan-v3.json','render_deepwell_v3.py','analytic-validation.json','changed-mask-review.png','window-all-dim-diagnostic.png','window-source-mask-dim-comparison.png']:
 shutil.copy2(H/name,A/name)
for p in H.glob('sample-*.png'):shutil.copy2(p,A/p.name)
c=json.loads((H/'scene-plan-v3.json').read_text());by_id={p['id']:p for p in c['window_panes']['panes']}
by_id['M3']['polygon']=[[1565.5,191.8],[1569.6,190.3],[1569.6,213.6],[1565.5,214.7]]
by_id['M4']['polygon']=[[1571.6,189.9],[1574.8,188.8],[1574.8,212.5],[1571.6,213.8]]
by_id['L2']['polygon']=[[1480.3,230.1],[1491.7,229.0],[1491.7,240.9],[1480.3,241.9]]
for line in c['window_panes']['fixed_mullion_lines']:
 if line[0]==1573:line[:]=[1570,192,1570,214]
c['window_panes']['bright_core_controls']=[[1610,188],[1653,185],[1668,185],[1567,204],[1568,204],[1572,204],[1573,204],[1486,232],[1487,232]]
for light in c['lights']:light['polygons']=[p['polygon'] for p in c['window_panes']['panes'] if p['group']==light['name']]
for steam in c['steam']:steam['opacity']*=2.2
(H/'scene-plan-v3.json').write_text(json.dumps(c,indent=2)+'\n')
(A/'README.txt').write_text('Internal native study, not delivered/approved. Full panes already corrected the v2 boxes on stone/pillars, but source pixel inspection found x1573/y204 is a white lamp core, not a mullion. Actual dark stile is x1570. M3/M4 trace and fixed-stile guard corrected; explicit saturated/bright-core controls added. Initial steam was too faint in normal full-composition stills; the 2.2x optical-depth study retains thin rising filaments and is selected. This multiplier is a setting, not an artistic improvement percentage. Original config/code/stills retained here.\n')
print('Corrected narrow bright-pane trace and clearer vapor selection saved.')
