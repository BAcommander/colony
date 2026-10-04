from pathlib import Path
import json
H=Path(__file__).resolve().parent;V2=H.parent/'rainline-animation-v2';SHARED=H.parent/'rainline-renderer';SHARED.mkdir(exist_ok=True)
c=json.loads((V2/'scene-plan-v2.json').read_text(encoding='utf-8'));c['version']='v3'
c['water'].update(displacement_scale=.45,time_scale=.12,reflection_contrast=.08,specular_strength=6)
c['impacts']['strength']=8
c['lights'][0]['polygons']=[[[776,341],[800,341],[800,385],[776,385],[773,381],[773,348]],[[805,341],[824,341],[824,385],[804,385],[804,345]],[[866,342],[868,340],[888,340],[891,343],[892,347],[892,380],[888,386],[866,386]]]
c['lights'][0].update(glow_gain=0,spill_gain=0,reflection_gain=0)
c['lights'][0]['floor']=.60
for bc in c['beacons']:
 bc.update(period=5,alternate_color=[65,225,118])
c['screen'].update(strength=48)
c['radio_meter']['strength']=.055
c['room']={'lamp_bounds':[[146,435],[248,427],[254,446],[150,466]],'desk_polygon':[[0,622],[369,606],[529,641],[527,680],[0,758]],'desk_center':[190,663],'desk_radius':[180,42],'lamp_events':[{'start':7.6,'hold':.16,'transition':.15,'depth':.07},{'start':16.4,'hold':.24,'transition':.18,'depth':.055}],'meter_roi':[226,571,271,575]}
c['notes']=[
'V3 requested: alternate red/green antenna beacons, correct middle building mask, add foreground room life, water between v1 and v2.',
'Near habitat glass is now traced with supersampled mattes across the three visible panes; tree and frame stay excluded. Inaccurate rectangular near-building spill/reflection masks are removed.',
'Water displacement .45 is exactly halfway between v1 .22 and v2 .68; speed .12 sits between .10 and .14. Keep the corrected v2 water geometry and rain.',
'Room has stronger screen telemetry, a restrained radio level strip and small desk-lamp variation coupled to a warm local desk spill; no geometry or camera motion.',
'Beacons alternate red and green on successive pulses, staggered between masts; dark gaps avoid an orange color blend.',
'V1/v2 code/config/media preserved. V3 uses a shared configurable renderer for subsequent revisions.'
]
(H/'scene-plan-v3.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
src=(V2/'render_rainline.py').read_text(encoding='utf-8')
src=src.replace('"""Rainline revised compositor: traced glass/panes, depth rain, water and practical emitters."""','"""Configurable Rainline compositor, including precise glass, room activity and alternating beacons."""')
src=src.replace("ap=self.feather(self.poly(lc['polygons']),1.2)","ap=self.aperture(lc['polygons'])")
src=src.replace("* .055","*.055")
src=src.replace("* .17","*.17")
src=src.replace("* .055","*.055")
src=src.replace("(0,0),1.5)*.055","(0,0),1.5)*lc.get('glow_gain',.055)")
src=src.replace("[lc['spill']]),10)*.055","[lc['spill']]),10)*lc.get('spill_gain',.055)")
src=src.replace("self.masks['water']*.17","self.masks['water']*lc.get('reflection_gain',.17)")
mark="  self.masks['rain']=np.maximum(self.masks['rain_near'],self.masks['rain_far'])"
src=src.replace(mark,'''  rc=c.get('room')
  if rc:
   aperture=self.poly([rc['lamp_bounds']]).astype(np.float32)
   # Include saturated white core; bound the luminosity matte to the lamp mouth.
   core=aperture*np.clip((luminosity-145)/70,0,1)
   core=cv2.GaussianBlur(core,(0,0),.55)*aperture
   cx,cy=rc['desk_center'];rx,ry=rc['desk_radius']
   warm=np.clip((r-b-12)/90,0,1).astype(np.float32)
   desk=np.exp(-((xx-cx)/rx)**2-((yy-cy)/ry)**2)*warm*self.feather(self.poly([rc['desk_polygon']]),18)*.45
   self.room_lamp=np.maximum(core,desk);self.room_lamp[self.room_lamp<.002]=0
   self.masks['room']=self.room_lamp.copy()
   mx0,my0,mx1,my1=rc['meter_roi'];self.masks['room'][my0:my1,mx0:mx1]=1
''' +mark)
src=src.replace(' def poly(self,shapes):',''' def aperture(self,shapes):
  # Supersampling preserves curved corners without carving a rectangular dim patch.
  out=np.zeros((self.h,self.w),np.float32)
  for points in shapes:
   p=np.asarray(points,np.float32);x0=max(0,int(p[:,0].min())-2);y0=max(0,int(p[:,1].min())-2)
   x1=min(self.w,int(p[:,0].max())+3);y1=min(self.h,int(p[:,1].max())+3)
   high=np.zeros(((y1-y0)*4,(x1-x0)*4),np.uint8)
   cv2.fillPoly(high,[np.rint((p-[x0,y0])*4).astype(np.int32)],255)
   soft=cv2.GaussianBlur(high.astype(np.float32)/255,(0,0),1.4)
   low=cv2.resize(soft,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA);low[low<.01]=0
   out[y0:y1,x0:x1]=np.maximum(out[y0:y1,x0:x1],low)
  return out
 def poly(self,shapes):''')
# Crop multiplicative/additive layers to their active bounds; same masks and math.
src=src.replace("  self.active=np.logical_or.reduce(list(self.layer_masks.values()))", "  self.active=np.logical_or.reduce(list(self.layer_masks.values()))\n  self.regions={}\n  for name,m in self.masks.items():\n   ys,xs=np.where(m>0)\n   if len(xs):self.regions[name]=(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)")
a=src.index("  if only in (None,'beacons'):");b=src.index("  if only in (None,'screen'):",a)
src=src[:a]+'''  if only in (None,'beacons'):
   for bc,bm in self.beacons:
    age=(t-bc['phase'])%self.duration;phase=age%bc['period']
    pulse=float(smoothstep(phase/.16)*smoothstep((.85-phase)/.25))
    if pulse>0:
     color=bc.get('alternate_color',bc['color']) if int(age//bc['period'])%2 else bc['color']
     cx,cy=bc['center'];radius=int(bc['halo']*4)+2;x0=max(0,cx-radius);x1=min(self.w,cx+radius+1);y0=max(0,cy-radius);y1=min(self.h,cy+radius+1)
     alpha=bm[y0:y1,x0:x1,None]*(.90*pulse)
     f[y0:y1,x0:x1]=f[y0:y1,x0:x1]*(1-alpha)+np.array(color,np.float32)*alpha
  if only in (None,'room') and 'room' in self.config:
   rc=self.config['room'];slow=.025*(.5-.5*np.cos(2*np.pi*t/20))
   brief=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in rc['lamp_events'])
   x0,y0,x1,y1=self.regions['room'];f[y0:y1,x0:x1]*=1-self.room_lamp[y0:y1,x0:x1,None]*(slow+brief)
   x0,y0,x1,y1=rc['meter_roi'];x=np.arange(x1-x0,dtype=np.float32)
   level=.48+.16*np.sin(2*np.pi*t*3/20)+.12*np.sin(2*np.pi*t*7/20+.7)+.06*np.sin(2*np.pi*t*13/20)
   bar=np.clip((level*(x1-x0)-x)/1.5,0,1)*(.65+.35*np.cos(x*np.pi/2)**2)
   stripe=np.array([.22,.8,.8,.22],np.float32)[:,None]*bar[None,:]
   f[y0:y1,x0:x1]+=stripe[...,None]*np.array([19,13,3],np.float32)
''' +src[b:]
src=src.replace("['water','rain','lights','beacons']","['water','lights','room','beacons']")
src=src.replace("self.masks['room'][my0:my1,mx0:mx1]=1", "self.masks['room'][my0:my1,mx0:mx1]=1\n   self.masks['room']=np.maximum.reduce([self.masks['room'],self.masks['screen'],self.masks['radio']])")
src=src.replace("if only in (None,'screen'):","if only in (None,'screen','room'):").replace("if only in (None,'radio'):","if only in (None,'radio','room'):")
src=src.replace("['rain','water','lights','beacons']","['water','lights','room','beacons']")
src=src.replace("('beacons',[255,0,0])","('beacons',[255,0,0]),('room',[255,190,0])")
src=src.replace("out=H/f'{layer}-isolated-v2-8s.mp4'","out=H/f\"{layer}-isolated-{s.config['version']}-8s.mp4\"")
src=src.replace("out=H/'rainline-relay-v2-preview-20s.mp4'","out=H/f\"rainline-relay-{s.config['version']}-preview-20s.mp4\"")
src=src.replace("repeat=H/'rainline-relay-v2-three-loops-60s.mp4'","repeat=H/f\"rainline-relay-{s.config['version']}-three-loops-60s.mp4\"")
src=src.replace("p.add_argument('--config');", "p.add_argument('--config',required=True);")
(SHARED/'render_rainline.py').write_text(src,encoding='utf-8')
(H/'feedback-v2.txt').write_text('User: could the anetenna cycle between red and green, the mask in the middle building still needs work. can we do anything with the room scene in the forground/ the water is also too much now can we find a middle ground\nV2 needs revision. V3 remains pending user review.\n',encoding='utf-8')
print('V3 configuration and shared renderer prepared; v1/v2 preserved')
