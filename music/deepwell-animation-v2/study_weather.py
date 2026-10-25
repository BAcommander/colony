"""Internal readability study; does not change the running candidate/config."""
from render_deepwell_v2 import *
import types
from weather_refinement import refined_config,render_weather
s=DeepwellV2();c=refined_config(json.loads(json.dumps(s.config)));s.config=c
for i,(old,r,m,tex,x,y) in enumerate(s.weather):
 new=next(q for group in ['atmosphere','surface_drift'] for q in c[group] if q['name']==old['name']);s.weather[i]=(new,r,m,tex,x,y)
s.weather_frame=types.MethodType(render_weather,s)
lum=s.clean.mean(2);broad=cv2.GaussianBlur(lum,(0,0),22,sigmaY=12)
s.front_texture=np.clip((cv2.GaussianBlur(lum,(0,0),3.5)-broad+2)/9,0,1).astype(np.float32)
a,b,z,d=s.sky_roi;band=np.exp(-((s.cy+b-c['sky']['veil_band_center_y'])/c['sky']['veil_band_radius_y'])**2)
sky=s.feather(s.poly([s.old_config['sky']['polygon']]),c['sky']['feather']);s.veil_mask=cut(sky,s.sky_roi)*band.astype(np.float32)
write_json('weather-refinement-proposed-config.json',c)
for t in [0,4,8,12,16]:
 Image.fromarray(s.frame(t)).save(H/f'weather-readability-study-{t:02d}.png')
 if t in [0,8]:Image.fromarray(s.frame(t,'atmosphere')).save(H/f'weather-only-study-{t:02d}.png')
print('Coherent weather and source-cloud veil study ready',flush=True)
