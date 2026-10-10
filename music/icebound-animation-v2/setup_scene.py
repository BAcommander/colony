from pathlib import Path
import json
H=Path(__file__).resolve().parent
p={'scene_name':'Icebound Weather Post','version':'v2','duration':20,'fps':30,'preview_size':[1280,720],'ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe',
'baseline':'music/icebound-animation-v1/scene-plan-v1.json','feedback':'can it be snowing at all, can we put some blinking rader style lights at the top of the antenia',
'snow':{'seed':7203,'color':[225,236,248],'layers':[
 {'name':'fine','count':260,'life':20,'vx':[6,11],'vy':[12,21],'radius':[.50,.85],'opacity':[.20,.36]},
 {'name':'middle','count':130,'life':20,'vx':[10,17],'vy':[25,37],'radius':[.9,1.35],'opacity':[.28,.52]},
 {'name':'near','count':32,'life':10,'vx':[18,28],'vy':[44,60],'radius':[1.35,1.95],'opacity':[.24,.43]}]},
'beacons':[
 {'name':'upper_mast','xy':[274,55],'period':4,'pulses':[[.5,.38],[1.12,.28]],'transition':.075,'radius':1.65,'halo_radius':5.4,'halo_strength':.22},
 {'name':'side_antenna','xy':[240,107],'period':5,'pulses':[[2.1,.34],[2.68,.26]],'transition':.075,'radius':1.4,'halo_radius':4.7,'halo_strength':.18}],
'source_preservation':'V1 base renderer is unchanged. Snow is an explicit sparse foreground optical overlay; two beacon cores/glows occupy only antenna-tip regions. Underlying geometry and original motion settings stay fixed.',
'review':{'user_approved':False,'continuous_assistant_playback':False}}
f=H/'scene-plan-v2.json';assert not f.exists();f.write_text(json.dumps(p,indent=2)+'\n')
print('V2 snowfall and beacon settings saved')
