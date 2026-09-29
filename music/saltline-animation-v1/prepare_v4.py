from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H/'scene-plan-v3.json').read_text());c['trial_version']='v4';c['version']='v4';c['trial_seconds']=12
c['previous_feedback']={'date':'2026-09-29','verbatim':'far dust is good, foreground looks too much as is fake, did we do anything with the lights on the buildings or the sunlight? can we try?','scope':'Far dust v3 accepted; foreground v3 rejected; try building lights and sunlight'}
c['approved_layers']={'far_dust':{'version':'v3','scope':'look in eight-second forward-motion prototype; not periodic loop','feedback':'far dust is good'}}
c['enabled_motion']=['sky','far_dust']
c['status']='Far dust retained; foreground dust disabled; building lights and localized sunlight trial'
def light(name,pts,start,hold,transition=.4):return {'name':name,'polygons':pts,'floor':.12,'events':[{'start':start,'hold':hold,'transition':transition}],'spill_pad':8,'spill_sigma':2,'spill_strength':.1}
c['lights']=[
 light('foreground-left-room',[[[727,651],[744,652],[750,656],[751,675],[746,680],[725,679],[719,674],[719,658]]],1,3.5,.35),
 light('foreground-middle-room',[[[817,653],[835,654],[841,659],[841,679],[834,683],[815,681],[810,675],[810,661]]],7,3.5,.5),
 light('ridge-middle-habitat',[[[1358,389],[1362,389],[1362,399],[1358,399]],[[1365,389],[1369,389],[1369,399],[1365,399]]],4.2,3.2,.4),
 light('ridge-left-habitat',[[[1254,391],[1258,391],[1258,402],[1254,402]],[[1261,391],[1265,391],[1265,402],[1261,402]]],9,2.7,.35),
 {'name':'service-lamp','ellipse':[1134,708,4,5],'floor':.3,'spill_pad':15,'spill_sigma':4,'spill_strength':.09,'dark_offset':[0,0,0],'events':[{'start':5.2,'hold':.22,'transition':.035,'depth':.55},{'start':5.6,'hold':.14,'transition':.025,'depth':.4}]}]
c['sunlight']={'polygons':[[[0,495],[107,495],[113,650],[101,677],[0,690]]],'feather':24,'start_x':-100,'speed':28,'center_y':574,'width':65,'height':100,'attenuation':.18,'scope':'passing cloud shadow confined to existing bright dry-crust sunlight; fixed sun and steady whole-scene exposure'}
p=H/'scene-plan-v4.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
