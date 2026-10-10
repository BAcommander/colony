from pathlib import Path
import json,random
H=Path(__file__).resolve().parent;H.mkdir(exist_ok=True)
c={'scene_name':'Icebound Weather Post','version':'v3-minute','duration':60,'fps':30,'preview_size':[1280,720],'ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe','user_request':'ok do your 60s suggestion','baseline':'music/icebound-animation-v2/approved-v2-preview.json','weather_cycle_seconds':20,'weather_speed_change_percent':0,'schedule_seed':7303,'windows':{
'main_room_right':[[7.8,7.5],[31.2,8.9],[55.4,7.4]],
'habitat_one_window':[[4.9,9.6],[28.6,12.1],[51.2,6.2]],
'habitat_two_window':[[15.4,11.2],[40.3,7.9]]},
'entrance_events':[{'start':4.3,'hold':.65,'transition':.16,'depth':.58},{'start':5.2,'hold':.3,'transition':.08,'depth':.35},{'start':23.6,'hold':1.7,'transition':.45,'depth':.25},{'start':38.2,'hold':.53,'transition':.16,'depth':.44},{'start':39.04,'hold':.28,'transition':.075,'depth':.28},{'start':52.1,'hold':1.15,'transition':.35,'depth':.23}],
'beacon_events':{},'review':{'v2_look_accepted':True,'new_schedule_approved':False},'note':'Genuine sixty-second lighting timeline over the accepted twenty-second weather cycles. Full frames are composited per timestamp; this is not three copies of the v2 video.'}
rng=random.Random(c['schedule_seed'])
for name,count,phase in [('upper_mast',12,.5),('side_antenna',10,2.1)]:
 gaps=[rng.uniform(.78,1.22) for _ in range(count)];gaps=[g/sum(gaps)*60 for g in gaps];t=phase;events=[]
 for gap in gaps:
  events.extend([[round(t%60,4),round(rng.uniform(.31,.39),4)],[round((t+rng.uniform(.59,.72))%60,4),round(rng.uniform(.25,.30),4)]])
  t+=gap
 c['beacon_events'][name]=events
f=H/'scene-plan-v3.json';assert not f.exists();f.write_text(json.dumps(c,indent=2)+'\n')
print('Minute-long lighting schedule saved')
