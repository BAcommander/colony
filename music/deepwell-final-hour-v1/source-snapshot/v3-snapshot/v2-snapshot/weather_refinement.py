"""Coherent, terrain-guided moving wisps with invisible local lifecycle resets."""
import numpy as np
from ambient_effects import smoothstep
def render_weather(scene,f,t,enabled):
 for c,r,m,texture,x,y in scene.weather:
  if c['name'] not in enabled:continue
  offset=(x+r[0])/2900+(y+r[1])/1700+c['seed']*.013
  detail=scene.transport(texture,t,c['speed'],x,y,offset)
  forms=c.get('forms',[]);body=np.zeros_like(x)
  for form in forms:
   age=(t/20+form['phase'])%1
   visibility=float(smoothstep(age/.16)*smoothstep((1-age)/.24))
   cx=form['anchor_x']+c['speed']*20*(age-.5)
   if 'route' in c:
    points=np.asarray(c['route']);cy=float(np.interp(cx+r[0],points[:,0],points[:,1]))-r[1]+form['y_offset']
   else:cy=c['center_y']-r[1]+c.get('slope',0)*(cx-(r[2]-r[0])/2)+form['y_offset']
   width=form['width'];height=form['height']*(.8+.32*age)
   curl=1.1*np.sin((x-cx)/23-2*np.pi*age*2+form['phase']*7)+.5*np.sin((x-cx)/11-2*np.pi*age)
   head=np.exp(-((x-cx)/width)**2-((y-cy-curl)/height)**2)
   tail=np.exp(-((x-cx+width*.7)/(width*1.5))**2-((y-cy-curl*.7+.8)/(height*.65))**2)*.42
   body=np.maximum(body,np.clip(head+tail,0,1)*visibility*form['strength'])
  density=body*(.72+.28*detail)
  alpha=m*density*c['opacity'];a,b,z,d=r;patch=f[b:d,a:z]
  f[b:d,a:z]=patch*(1-alpha[...,None])+np.float32(c['color'])*alpha[...,None]

def refined_config(c):
 for group in ['atmosphere','surface_drift']:
  for ac in c[group]:
   rng=np.random.default_rng(ac['seed']+3000);w=ac['roi'][2]-ac['roi'][0];surface=group=='surface_drift'
   ac['opacity']={'far_drift':.26,'basin_haze':.27,'brine_wisps':.20,'salt_far':.24,'salt_middle':.24}[ac['name']]
   ac['color']={'far_drift':[226,231,235],'basin_haze':[222,229,234],'brine_wisps':[213,223,230],'salt_far':[191,203,213],'salt_middle':[191,203,213]}[ac['name']]
   ac['speed']={'far_drift':7.0,'basin_haze':10.5,'brine_wisps':10.0,'salt_far':16.0,'salt_middle':20.0}[ac['name']]
   count=5 if w>600 else 4
   ac['forms']=[{'anchor_x':float(w*(.12+i*.76/(count-1))),'phase':float((i*.373+ac['seed']*.013)%1),'width':float(rng.uniform(34,62) if surface else rng.uniform(48,93)),'height':float(rng.uniform(2.1,3.2) if surface else rng.uniform(4.0,8.5)),'y_offset':float(rng.uniform(-2.5,2.5)),'strength':float(rng.uniform(.84,1))} for i in range(count)]
 c['sky']['veil_opacity']=.30;c['sky']['veil_speed']=8.5;c['sky']['veil_band_radius_y']=43
 return c
