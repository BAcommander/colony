"""Render only the revised sky/atmosphere; preserve unchanged water/room clips."""
from render_deepwell_v2 import *
s=DeepwellV2();clips=[]
for group in ['sky','atmosphere']:
 out=H/f'deepwell-v2-{group}-isolated-8s.mp4';item=encode(s,out,8,group);item['validation'],_=decode_verify(s,out,240);clips.append(item);print(group,'refined isolated verified',flush=True)
write_json('isolated-refined-weather-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Source and native temporal stills; selected decoded stills follow. Continuous playback not claimed.'})
