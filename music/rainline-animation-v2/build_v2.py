from pathlib import Path
import json

H=Path(__file__).resolve().parent;V1=H.parent/'rainline-animation-v1'
c=json.loads((V1/'scene-plan-v1.json').read_text(encoding='utf-8'))
c['version']='v2'
c['windows']=[[[146,0],[430,46],[430,573],[146,532]],[[507,47],[707,4],[707,602],[507,568]],[[769,0],[1671,0],[1671,940],[1510,940],[769,749]]]
c['water_polygons'][0][-3:]=[[1671,860],[1671,940],[1510,940],[769,749]]
c['water'].update(roi=[765,458,1672,941],time_scale=.14,displacement_scale=.68,reflection_contrast=.10,specular_strength=7,wavelength_range=[1.3,7.2],edge_damping_pixels=8,reflection_sigma_x=.8,reflection_sigma_y=.5)
c['water_feather']=4
c['water_polygons']=[[[769,500],[920,485],[1060,468],[1220,461],[1480,455],[1530,500],[1671,740],[1671,940],[1510,940],[769,749]]]
c['protected_exterior'][4]=[[1514,0],[1620,0],[1580,123],[1578,220],[1601,287],[1586,372],[1585,514],[1614,615],[1671,685],[1671,899],[1620,875],[1550,876],[1460,846],[1405,824],[1320,795],[1280,772],[1288,740],[1310,718],[1390,663],[1460,590],[1495,544],[1528,440],[1520,297],[1535,147]]
c['water_exclusions']=[
 [[769,470],[922,480],[935,535],[966,574],[998,610],[1017,625],[1000,646],[956,663],[846,669],[769,650]],
 [[997,448],[1015,448],[1013,585],[997,585]],
 [[1060,450],[1196,450],[1238,522],[1252,552],[1230,573],[1160,584],[1063,568]],
 [[1270,445],[1455,445],[1455,500],[1370,512],[1270,493]],
 [[1090,618],[1130,607],[1180,607],[1210,605],[1245,613],[1282,625],[1310,642],[1288,655],[1204,651],[1148,641],[1100,639]],
 [[769,665],[792,659],[818,682],[840,708],[843,734],[805,740],[769,721]]]
c['protected_exterior'] += [
 [[875,430],[896,430],[897,721],[894,735],[875,738]],
 [[993,432],[1015,432],[1015,580],[994,585]],
 [[1241,419],[1260,419],[1260,555],[1242,559]]]
c['impacts'].update(count=180,strength=10)
c['rain']['groups']=[
 dict(count=1500,life=4,vx=[-13,-6],vy=[240,340],length=[8,13],opacity=[.12,.25],mask='rain_far'),
 dict(count=650,life=2.5,vx=[-24,-12],vy=[400,540],length=[14,23],opacity=[.16,.32],mask='rain_near'),
 dict(count=160,life=2,vx=[-35,-18],vy=[600,780],length=[22,32],opacity=[.20,.40],mask='rain_near')]
c['rain']['color']=[190,207,214]
c['lights'][0].update(polygons=[[[870,338],[887,338],[895,344],[897,377],[893,384],[871,384]]],floor=.50,start=3.8,hold=3.3,transition=.45)
c['lights'][1].update(polygons=[[[1373,363],[1392,363],[1392,385],[1374,385]],[[1397,363],[1410,363],[1410,384],[1397,385]]],floor=.46,start=12.9,hold=3.7,transition=.55)
for lc in c['lights']:lc.pop('polygon')
c['lights'][0]['flickers']=[dict(start=s,hold=h,transition=tr,depth=d) for s,h,tr,d in [(1.6,.09,.06,.36),(1.89,.16,.05,.48),(10.5,.18,.08,.3),(18.3,.11,.06,.35)]]
c['lights'][1]['flickers']=[dict(start=s,hold=h,transition=tr,depth=d) for s,h,tr,d in [(6.3,.13,.06,.32),(6.65,.08,.04,.4),(17.6,.20,.10,.25)]]
c['practical_flicker']={'center':[688,441],'radius':[7,12],'spill_radius':[18,26],'events':[dict(start=8.3,hold=.10,transition=.07,depth=.43),dict(start=8.63,hold=.20,transition=.06,depth=.55),dict(start=15.4,hold=.13,transition=.08,depth=.32)]}
c['beacons']=[{'name':'near_roof_mast','center':[1013,231],'period':5,'phase':.6,'radius':1.8,'halo':7,'color':[255,64,35]}, {'name':'far_roof_mast','center':[1365,284],'period':4,'phase':2.1,'radius':1.45,'halo':5.5,'color':[255,70,38]}]
c['notes']=[
'V2 follows user rejection of window masking and weak rain/water, plus request for flicker and antenna lights.',
'Glass boundaries redrawn from source crops. Lower right water no longer cut by the incorrect v1 diagonal.',
'Whole habitat panes traced around their bezels and divider. Emission-weighted dimming preserves dark room detail and exterior structure.',
'Rain uses three depth groups, tapered trails and seeded arrival times. Baked-in source streaks remain a limitation of the immutable still.',
'Water retains the 24-wave reconstructed reflection method, with larger coherent displacement and broader waves; this is a 2D approximation.',
'V1 original code/config/media preserved; v2 renderer has a configurable input path for subsequent parameter revisions.'
]
(H/'scene-plan-v2.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
src=(V1/'render_rainline.py').read_text(encoding='utf-8')
src=src.replace('"""Rainline first draft: fixed source, water, layered rain/mist and practical lights."""','"""Rainline revised compositor: traced glass/panes, depth rain, water and practical emitters."""')
src=src.replace("self.path=H/'scene-plan-v1.json'","self.path=H/'scene-plan-v2.json'")
src=src.replace('def __init__(self):','def __init__(self,path=None):').replace("self.path=H/'scene-plan-v2.json'","self.path=Path(path) if path else H/'scene-plan-v2.json'")
src=src.replace("water[cv2.dilate(green,np.ones((3,3),np.uint8))>0]=0", "# Apply color protection only around actual vegetation, not every green reflection.\n  foliage_zone=self.poly([[[970,700],[1120,680],[1255,728],[1320,830],[1290,910],[1135,858],[1010,780]]])\n  water[(cv2.dilate(green,np.ones((3,3),np.uint8))>0)&(foliage_zone>0)]=0")
src=src.replace("self.feather(water,7)","self.feather(water,c['water_feather'])")
a=src.index('  self.lights=[];light_union=');b=src.index("  self.masks['screen']=",a)
src=src[:a]+'''  self.lights=[];light_union=np.zeros((self.h,self.w),np.float32)
  luminosity=self.base.astype(np.float32).mean(axis=2)
  for lc in c['lights']:
   ap=self.feather(self.poly(lc['polygons']),1.2)
   emission=ap*(.25+.75*np.clip((luminosity-30)/135,0,1))
   glow=cv2.GaussianBlur(ap,(0,0),1.5)*.055;glow[glow<.003]=0
   spill=self.feather(self.poly([lc['spill']]),10)*.055
   reflection=self.feather(self.poly([lc['reflection']]),8)*self.masks['water']*.17
   m=np.maximum.reduce([emission,glow,spill,reflection])*self.window_mask
   light_union=np.maximum(light_union,m);self.lights.append((lc,m))
  yy,xx=np.mgrid[:self.h,:self.w].astype(np.float32)
  pc=c['practical_flicker'];cx,cy=pc['center'];rx,ry=pc['radius'];sx,sy=pc['spill_radius']
  practical=np.exp(-((xx-cx)/rx)**4-((yy-cy)/ry)**4)+.10*np.exp(-((xx-cx)/sx)**2-((yy-cy)/sy)**2)
  practical=np.minimum(practical,1)*self.window_mask;practical[practical<.003]=0
  self.practical=practical;light_union=np.maximum(light_union,practical)
  self.masks['lights']=light_union
  self.beacons=[];beacon_union=np.zeros_like(light_union)
  for bc in c['beacons']:
   cx,cy=bc['center'];r2=(xx-cx)**2+(yy-cy)**2
   bm=np.minimum(np.exp(-r2/(2*bc['radius']**2))+.11*np.exp(-r2/(2*bc['halo']**2)),1)*self.window_mask
   bm[bm<.002]=0;self.beacons.append((bc,bm));beacon_union=np.maximum(beacon_union,bm)
  self.masks['beacons']=beacon_union
''' +src[b:]
a=src.index('   particles=[]');b=src.index("  rng=np.random.default_rng(c['impacts']",a)
src=src[:a]+'''   n=group['count'];life=group['life']
   particles=np.stack([rng.uniform(100,self.w+80,n),rng.uniform(-100,self.h+100,n),rng.uniform(0,life,n),rng.uniform(*group['vx'],n),rng.uniform(*group['vy'],n),rng.uniform(*group['length'],n),rng.uniform(*group['opacity'],n)],axis=1)
   self.rain.append((group,particles))
''' +src[b:]
a=src.index(' def rain_alpha(');b=src.index(' def impacts_layer(',a)
src=src[:a]+''' def rain_alpha(self,t):
  result=np.zeros((self.h,self.w),np.float32)
  for group,particles in self.rain:
   layer=np.zeros((self.h,self.w),np.uint8);life=group['life']
   x,y,phase,vx,vy,length,strength=particles.T
   age=(t+phase)%life;fade=smoothstep(age/.18)*smoothstep((life-age)/.18)
   px=x+vx*(age-life/2);py=y+vy*(age-life/2);dx=vx/vy*length
   inside=(px>-35)&(px<self.w+35)&(py>-35)&(py<self.h+35)&(fade>.001)
   for ax,ay,bx,ln,val in zip(px[inside],py[inside],dx[inside],length[inside],strength[inside]*fade[inside]):
    # Three overlapping trail sections give a soft tail rather than uniform white sticks.
    for low,high,weight in [(0,1,.4),(.25,.9,.72),(.5,.82,1)]:
     cv2.line(layer,(round((ax+bx*low)*256),round((ay+ln*low)*256)),(round((ax+bx*high)*256),round((ay+ln*high)*256)),round(255*val*weight),1,cv2.LINE_AA,8)
   alpha=cv2.GaussianBlur(layer.astype(np.float32)/255,(0,0),.38)*self.masks[group['mask']]
   result=1-(1-result)*(1-alpha)
  return result
''' +src[b:]
a=src.index("  if only in (None,'lights'):");b=src.index("  if only in (None,'screen'):",a)
src=src[:a]+'''  if only in (None,'lights'):
   for lc,m in self.lights:
    held=event_amount(t,self.duration,lc['start'],lc['hold'],lc['transition'])*(1-lc['floor'])
    flicker=max((event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in lc['flickers']),default=0)
    amount=1-(1-held)*(1-flicker)
    f*=1-m[...,None]*amount
   amount=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['practical_flicker']['events'])
   f*=1-self.practical[...,None]*amount
  if only in (None,'beacons'):
   for bc,bm in self.beacons:
    phase=(t-bc['phase'])%bc['period']
    pulse=float(smoothstep(phase/.16)*smoothstep((.85-phase)/.25))
    alpha=bm*(.035+.88*pulse)
    f=f*(1-alpha[...,None])+np.array(bc['color'],np.float32)*alpha[...,None]
''' +src[b:]
src=src.replace("('screen',[255,255,0])","('screen',[255,255,0]),('beacons',[255,0,0])")
src=src.replace("['water','rain','mist_far','mist_near']","['water','rain','lights','beacons']")
src=src.replace("['rain','water','mist_far','mist_near']","['rain','water','lights','beacons']")
src=src.replace("-isolated-v1-8s.mp4","-isolated-v2-8s.mp4").replace("rainline-relay-v1-","rainline-relay-v2-")
# Same renderer can now target a future parameter-only revision without copying code.
src=src.replace(" p=argparse.ArgumentParser();p.add_argument('--stage'", " global H\n p=argparse.ArgumentParser();p.add_argument('--config');p.add_argument('--stage'")
src=src.replace("a=p.parse_args();s=Rainline()", "a=p.parse_args()\n if a.config:H=Path(a.config).resolve().parent\n s=Rainline()")
src=src.replace('s=Rainline()','s=Rainline(a.config)')
src=src.replace("np.array(self.config['rain']['color'])","np.array(self.config['rain']['color'],np.float32)")
(H/'render_rainline.py').write_text(src,encoding='utf-8')
(H/'feedback-v1.txt').write_text("User: the masking on the windows looks poor, can some of the lights flicker, can the rain look better? can the antenna on the other structures have some lights on them ? is the water moving at all?\nV1 is not accepted. V2 implements this feedback; user review remains pending.\n",encoding='utf-8')
print('V2 config and revised compositor written; v1 unchanged')
