from pathlib import Path
import json
H=Path(__file__).resolve().parent
old=H.parent/'spirewatch-animation-v5'
for name in ['render_spirewatch.py','render_parallel.py','check_chunk_joins.py']:
 text=(old/name).read_text().replace('spirewatch-v5','spirewatch-v6').replace('scene-plan-v5','scene-plan-v6').replace('V5','V6').replace('v5:','v6:')
 (H/name).write_text(text,encoding='utf-8')
# Legacy helpers must save decoded samples in the current package.
p=H/'render_spirewatch.py';text=p.read_text().replace('import validation_legacy as old','import validation_legacy as old\nold.H=H');p.write_text(text)
c=json.loads((old/'scene-plan-v5.json').read_text());c['version']='v6'
c['visibility']={'tower_floor':0.44,'tower_head_width':58,'tower_trail_width':96,'tower_head_gain':1.3,'transit_floor':0.26,'water_displacement':1.75,'waterfall_texture_contrast':0.38,'warm_window_floor':0.16,'window_groups_per_region':5}
c['knowledge_reuse']={'source':'creative/ANIMATION_KNOWLEDGE_BANK.md','reused':['Spirewatch v3: dim-to-bright emitter travel; add-only modulation fails on saturated source','Ringfall: whole warm apertures including white cores, local spill','Basalt: visible position changes at full-scene size, no numeric-change-only approval'],'preserved':['v5 clouds','v5 original screen activity'],'avoid':['global dimming','facade-wide synchronized blink','subpixel-only water motion','static bright transit streaks hiding added particles']}
c['notes']+=['V5 rejected as nearly static apart from screen/clouds. V6 changes material/lighting contrast and spatial coverage, not global exposure.']
(H/'scene-plan-v6.json').write_text(json.dumps(c,indent=2)+'\n')
feedback={'date':'2026-10-21','user_quote':"this isn't looking good at all, i can barely see any movement appart from the pc screen and the clouds",'verdict':'V5 rejected for motion visibility','action':'Preserve v5; build v6 with source-emitter replacement, visible falls, more whole apertures, same sky/screen.'}
(H/'feedback-and-plan.json').write_text(json.dumps(feedback,indent=2)+'\n')
(old/'user-feedback-motion-2026-10-21.json').write_text(json.dumps(feedback,indent=2)+'\n')
print('V6 source/config/code initialized; v5 preserved')
