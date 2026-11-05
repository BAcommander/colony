"""Back Before Dawn: native-first atmospheric workshop with causal light sources."""
from pathlib import Path
import argparse, json, math, sys
import cv2
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE/'dependencies'))
from core import (SceneBase,Sheet,polygon_mask,roi_slice,grid,smooth,
                  envelope,ellipse,rgb_linear,linear_rgb,sha,scaled_rgba,
                  add_rgba,encode,save_samples)

class Scene(SceneBase):
    effect_groups=['foliage','rain','road','drips','cabin','scope','lamp','dust','traffic']
    review_details=[
        {'label':'Cabin-systems-and-reflections','start':73,'seconds':23,'roi':[960,310,1230,570]},
        {'label':'Workbench-scope-and-lamp','start':23,'seconds':16,'roi':[112,16,365,325]},
        {'label':'Street-rain-and-passing-car','start':53,'seconds':23,'roi':[1418,230,1672,585]},
        {'label':'Bonnet-and-practical-light','start':24,'seconds':12,'roi':[80,398,1000,554]}
    ]

    def __init__(self,attention_mode=None):
        self.root=ROOT;self.source_path=ROOT/'creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/concept-v1.png'
        self.config_path=HERE/'settings.json';self.renderer_path=Path(__file__)
        self.cfg=json.loads(self.config_path.read_text());assert sha(self.source_path)==self.cfg['source_sha256']
        self.fps=self.cfg['fps'];self.base=np.array(Image.open(self.source_path).convert('RGB'))
        self.height,self.width=self.base.shape[:2];self.regions={};self.masks={};self.allowed=np.zeros(self.base.shape[:2],bool)
        self.mode=attention_mode or self.cfg['attention_mode'];self.schedule=self.cfg['schedules'][self.mode];self.period=self.schedule['period']
        self.extra_inputs=[HERE/'dependencies/core.py'];self.assets_ready=[]
        self._prepare_rain();self._prepare_road();self._prepare_electrics();self._prepare_practicals();self._prepare_foliage();self._prepare_vehicle()

    def wind(self,t):
        return .25+.75*max(envelope(t,*event,period=self.period) for event in self.schedule['gusts'])

    def lamp_dip(self,t):
        return max(depth*envelope(t,start,.055,.10,.33,self.period) for start,depth in self.schedule['lamp_dips'])

    def _prepare_rain(self):
        cfg=self.cfg['rain'];self.rain_roi=cfg['roi'];roi=self.rain_roi
        self.rain_mask=polygon_mask(roi,[cfg['opening']],2,1)*(1-polygon_mask(roi,[cfg['hero_exclusion'],cfg['fin_exclusion']],.1))
        self.ry,self.rx=grid(roi);self.rain_lamp=ellipse(roi,[1589,205],[105,205],.001)
        self.register('exterior_rain',roi,self.rain_mask);rng=np.random.default_rng(cfg['seed']);self.rain=[]
        for count,cycles,length,alpha in cfg['families']:
            for _ in range(count):self.rain.append((rng.uniform(800,1710),rng.uniform(0,640),cycles,length*rng.uniform(.7,1.3),alpha*rng.uniform(.65,1.2)))
        self.drips=[(1568,4.1),(1646,12.7),(1605,26.3),(1661,39.4),(1533,52.2)]

    def _prepare_road(self):
        cfg=self.cfg['wet_road'];roi=cfg['roi'];self.road_roi=roi
        self.road_safe=(polygon_mask(roi,cfg['polygons'],.1)>0)&(polygon_mask(roi,[cfg['protected_parked_car']],.1)==0)
        clearance=cv2.distanceTransform(np.pad(self.road_safe.astype(np.uint8),1),cv2.DIST_L2,5)[1:-1,1:-1]
        self.road_mask=polygon_mask(roi,cfg['polygons'],4,2)*smooth((clearance-2)/3)
        self.register('wet_road',roi,self.road_mask);self.wy,self.wx=grid(roi);self.ly,self.lx=np.indices(self.road_mask.shape,dtype=np.float32)
        self.road_source=self.base[roi_slice(roi)].astype(np.float32);self.road_noise=Sheet(roi,185,3,28,period=60,step=1)
        # Ripple points are accepted only in independently traced wet surfaces.
        rng=np.random.default_rng(193);self.impacts=[];a,b,c,d=roi
        for born in np.arange(0,60,cfg['ripple_interval_seconds']):
            for _ in range(100):
                x,y=rng.uniform(a,c),rng.uniform(b,d)
                if self.road_mask[min(d-b-1,int(y-b)),min(c-a-1,int(x-a))]>.9:break
            else:continue
            self.impacts.append((float(born),x,y,rng.uniform(3.0,6.8),rng.uniform(.8,1.2)))

    def _prepare_electrics(self):
        self.banks=[]
        for i,bank in enumerate(self.cfg['cabin_banks']):
            roi=bank['roi'];src=self.base[roi_slice(roi)].astype(np.float32);peak=src.max(2);chroma=peak-src.min(2)
            # White cores and coloured apertures share the same source programme.
            mask=smooth((peak-83)/80)*smooth((np.maximum(chroma,peak-95)-17)/45)
            mask*=polygon_mask(roi,[[[roi[0],roi[1]],[roi[2]-1,roi[1]],[roi[2]-1,roi[3]-1],[roi[0],roi[3]-1]]],1)
            self.banks.append((bank,mask,src));self.register('cabin_'+bank['name'],roi,mask)
        self.receivers=[]
        specs=[('console_rim',[995,332,1131,459],[[[998,333],[1127,334],[1128,384],[1092,391],[1090,441],[1028,449],[1019,390],[998,387]]],[1059,385],[67,59],0,[13,9,3]),
               ('door_recess',[975,368,1081,554],[[[981,376],[1024,380],[1042,454],[1075,484],[1063,539],[985,543]]],[1010,447],[38,74],2,[10,6,2]),
               ('seat_edge',[1090,380,1202,568],[[[1131,382],[1185,391],[1194,430],[1167,490],[1160,556],[1130,551],[1141,487],[1110,435]]],[1155,432],[44,72],4,[8,5,2])]
        for name,roi,polys,center,radius,bank,color in specs:
            mask=polygon_mask(roi,polys,4)*ellipse(roi,center,radius,.01);src=self.base[roi_slice(roi)].astype(np.float32)
            # These are material receivers; saturating source lamps are not filled over.
            mask*=1-smooth((src.max(2)-160)/70);self.receivers.append((roi,mask,bank,np.float32(color)));self.register('receiver_'+name,roi,mask)
        scope=self.cfg['scope'];self.scope_roi=scope['roi'];self.scope_mask=polygon_mask(self.scope_roi,[scope['glass_quad']],1.1,1)
        self.register('scope_glass',self.scope_roi,self.scope_mask);self.scope_src=self.base[roi_slice(self.scope_roi)].astype(np.float32)
        # Remove the old phosphor trace only, retaining source grid, glass and casing.
        src=self.scope_src;green=smooth((src[...,1]-src[...,0]*1.1-12)/50)*smooth((src[...,2]-src[...,0]*.8-10)/50)
        self.scope_clean=src+(np.float32([10,27,29])-src)*green[...,None]*.92
        a,b,c,d=self.scope_roi;quad=(np.float32(scope['glass_quad'])-np.float32([a,b])).astype(np.float32)
        self.scope_matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[83,0],[83,79],[0,79]]),quad)

    def _prepare_practicals(self):
        self.lights=[]
        specs=[('core',[170,64,269,84],ellipse([170,64,269,84],[219,74],[43,4.7],.02),1),
               ('pegboard',[102,79,379,307],polygon_mask([102,79,379,307],[[[172,80],[266,80],[372,293],[108,293]]],13)*ellipse([102,79,379,307],[218,171],[83,100],.01),.31),
               ('bench',[88,285,350,345],polygon_mask([88,285,350,345],[[[99,298],[342,299],[340,326],[97,330]]],5),.24)]
        for name,roi,mask,depth in specs:
            src=self.base[roi_slice(roi)].astype(np.float32)
            qualify=smooth((src.max(2)-160)/70) if name=='core' else smooth((src[...,0]-src[...,2]*1.10-7)/45)
            mask*=qualify;self.lights.append((roi,mask,depth));self.register('work_lamp_'+name,roi,mask)
        roi=[82,398,1002,554];src=self.base[roi_slice(roi)].astype(np.float32)
        plane=polygon_mask(roi,[[[172,438],[449,408],[859,425],[998,454],[485,551],[85,490]]],7,3)
        warm=smooth((src[...,0]-src[...,2]*1.14-9)/45);highlight=smooth((src.max(2)-100)/85)
        self.hood_mask=plane*warm*highlight;self.hood_roi=roi;self.register('bonnet_lamp_reflection',roi,self.hood_mask)
        # Sparse non-emissive motes cross the actual warm lamp beam.
        self.dust_roi=[132,93,324,303];self.dy,self.dx=grid(self.dust_roi)
        self.dust_mask=polygon_mask(self.dust_roi,[[[196,94],[239,94],[317,297],[138,297]]],15)
        self.register('lamp_dust',self.dust_roi,self.dust_mask);rng=np.random.default_rng(188);self.dust=rng.uniform(0,1,(18,5))

    def _prepare_foliage(self):
        self.foliage=[];cfg=self.cfg['foliage'];roi=cfg['roi'];src=self.base[roi_slice(roi)].astype(np.float32)
        for i,(poly,amount) in enumerate(zip(cfg['polygons'],cfg['displacement_native_px'])):
            # The mask cuts through a crown rather than isolating a complete branch.
            # Keep that internal chord fixed: never reveal inferred sky beneath it.
            mask=polygon_mask(roi,[poly],6);yy,xx=np.indices(mask.shape,dtype=np.float32)
            obj={'roi':roi,'source':src,'mask':mask,'amount':amount,'phase':i*2.2,'x':xx,'y':yy};self.foliage.append(obj);self.register('foliage_'+str(i),roi,mask)

    def foliage_maps(self,obj,t,wind):
        phase=2*math.pi*(t%60)/60
        dx=obj['amount']*math.sin(phase*3+obj['phase'])*wind
        dy=obj['amount']*.22*math.sin(phase*2+obj['phase'])*wind
        return (obj['x']+obj['mask']*dx).astype(np.float32),(obj['y']+obj['mask']*dy).astype(np.float32)

    def apply_foliage(self,f,t,wind):
        for obj in self.foliage:
            mx,my=self.foliage_maps(obj,t,wind);value=cv2.remap(obj['source'],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101);r=roi_slice(obj['roi'])
            f[r]+=(value-obj['source'])*obj['mask'][...,None]

    def _prepare_vehicle(self):
        path=HERE/'assets/passing-sedan.png';meta=HERE/'assets/passing-sedan.json';self.vehicle=None
        if not path.exists() or not meta.exists():self.assets_ready.append('passing-sedan assets missing');return
        self.extra_inputs.extend([path,meta]);self.vehicle=np.array(Image.open(path).convert('RGBA'));self.vehicle_meta=json.loads(meta.read_text());self.vehicle_cache={}
        self.vehicle_roi=self.cfg['passing_car']['roi'];roi=self.vehicle_roi
        self.vehicle_mask=polygon_mask(roi,[[[1430,285],[1671,285],[1671,346],[1430,346]]],1)
        self.vehicle_mask*=1-polygon_mask(roi,[self.cfg['rain']['hero_exclusion']],.1)
        self.register('passing_vehicle',roi,self.vehicle_mask)
        self.vehicle_light_roi=[1414,298,1672,579];self.vy,self.vx=grid(self.vehicle_light_roi)
        road_full=np.zeros(self.base.shape[:2],np.float32);road_full[roi_slice(self.road_roi)]=self.road_mask
        self.vehicle_light_mask=road_full[roi_slice(self.vehicle_light_roi)]
        self.register('passing_lamp_reflections',self.vehicle_light_roi,self.vehicle_light_mask)

    def road_maps(self,t):
        field=self.road_noise.at(t%60)-.5;amount=self.cfg['wet_road']['displacement_px'];dx=field*amount*self.road_mask
        return (self.lx+dx).astype(np.float32),(self.ly+np.sin(self.wx*.09+self.wy*.1-2*np.pi*(t%60)/60*11)*.12*self.road_mask).astype(np.float32)

    def apply_road(self,f,t,wind):
        mx,my=self.road_maps(t);safe=cv2.remap(self.road_safe.astype(np.float32),mx,my,cv2.INTER_LINEAR)>.999
        value=cv2.remap(self.road_source,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101);mask=self.road_mask*safe;r=roi_slice(self.road_roi);f[r]+=(value-f[r])*mask[...,None]
        ripple=np.zeros(self.road_mask.shape,np.float32);life=self.cfg['wet_road']['ripple_life_seconds']
        for born,x,y,maxradius,variant in self.impacts:
            age=((t%60)-born)%60
            if age>=life:continue
            radius=.6+maxradius*age/life;distance=np.sqrt((self.wx-x)**2+((self.wy-y)/.24)**2)
            fade=smooth(age/.12)*smooth((life-age)/.65);ring=np.exp(-.5*((distance-radius)/.55)**2)-.42*np.exp(-.5*((distance-radius-1.1)/.7)**2)
            ripple+=ring*fade*variant
        # The light/dark pair breaks up the existing photographed reflection.
        source_luma=self.road_source.mean(2);gain=1.3+smooth((source_luma-70)/90)*2.8
        f[r]+=ripple[...,None]*self.road_mask[...,None]*gain[...,None]*(.6+.4*wind)*np.float32([.82,.92,1.0])

    def apply_rain(self,f,t,wind):
        roi=self.rain_roi;a,b,c,d=roi;layer=np.zeros(self.rain_mask.shape,np.float32);env=t%60
        for x,y,cycles,length,alpha in self.rain:
            yy=(y+env*cycles*640/60)%640-34;xx=x-(yy-y)*.105+math.sin(env*2*math.pi/60*3+x*.003)*wind*1.1
            cv2.line(layer,(round(xx-a),round(yy-b)),(round(xx-a-length*.12),round(yy-b+length)),alpha,1,cv2.LINE_AA)
        alpha=np.minimum(layer,.35)*self.rain_mask*(.65+.55*self.rain_lamp)*(.7+.3*wind);r=roi_slice(roi);f[r]+=(np.float32([159,181,202])-f[r])*alpha[...,None]

    def apply_drips(self,f,t):
        a,b,c,d=self.rain_roi;layer=np.zeros(self.rain_mask.shape,np.float32)
        for x,start in self.drips:
            age=((t%60)-start)%60
            if age>2.2:continue
            y=31+82*age+84*age*age;length=5+age*5
            cv2.line(layer,(round(x-a),round(y-b)),(round(x-a-1),round(y-b+length)),.25*smooth(age/.15)*smooth((2.2-age)/.3),1,cv2.LINE_AA)
        alpha=layer*self.rain_mask;r=roi_slice(self.rain_roi);f[r]+=(np.float32([186,197,206])-f[r])*alpha[...,None]

    def bank_signal(self,t,i):
        bank=self.cfg['cabin_banks'][i];start=self.schedule['panel_starts'][i]
        return 1-bank['depth']*envelope(t,start,.25,bank['hold'],.85,self.period)

    def apply_cabin(self,f,t):
        signals=[]
        for i,(bank,mask,src) in enumerate(self.banks):
            signal=self.bank_signal(t,i);signals.append(signal);gain=np.ones(mask.shape,np.float32)*signal
            if i==3:
                age=(t-self.schedule['diagnostic_start'])%self.period
                if age<12:
                    head=age/12;xx=np.linspace(0,1,mask.shape[1])[None,:];pulse=np.exp(-.5*((xx-head)/.13)**2)*smooth(age/.7)*smooth((12-age)/.7);gain+=pulse*.65
            r=roi_slice(bank['roi']);f[r]=linear_rgb(rgb_linear(f[r])*(1-mask[...,None]+mask[...,None]*gain[...,None]))
        for roi,mask,bank,color in self.receivers:f[roi_slice(roi)]+=mask[...,None]*(signals[bank]-1)*color

    def apply_scope(self,f,t):
        plane=np.zeros((80,84,3),np.float32);phase=2*math.pi*(t%60)/60
        points=[]
        for x in range(84):
            y=39+13*math.sin(x*.115-phase*8)+5*math.sin(x*.24+phase*5)
            points.append([x,round(y)])
        cv2.polylines(plane,[np.int32(points)],False,(52,178,179),1,cv2.LINE_AA)
        halo=cv2.GaussianBlur(plane,(0,0),1.1);plane+=halo*.7
        a,b,c,d=self.scope_roi;v=cv2.warpPerspective(plane,self.scope_matrix,(c-a,d-b),flags=cv2.INTER_LINEAR)
        value=self.scope_clean+v;mask=self.scope_mask;r=roi_slice(self.scope_roi);f[r]+=(value-f[r])*mask[...,None]

    def apply_lamp(self,f,t):
        dip=self.lamp_dip(t)
        for roi,mask,depth in self.lights:
            r=roi_slice(roi);f[r]=linear_rgb(rgb_linear(f[r])*(1-mask[...,None]*dip*depth))
        r=roi_slice(self.hood_roi);f[r]=linear_rgb(rgb_linear(f[r])*(1-self.hood_mask[...,None]*dip*.19))

    def apply_dust(self,f,t):
        alpha=np.zeros(self.dust_mask.shape,np.float32)
        for v in self.dust:
            age=((t%60)+v[0]*60)%20;fade=smooth(age/3)*smooth((20-age)/4)
            x=151+v[1]*140+math.sin(age*.3+v[3]*6)*2;y=109+v[2]*160+age*.65
            alpha+=np.exp(-.5*(((self.dx-x)/(.45+v[4]*.35))**2+((self.dy-y)/.6)**2))*fade*.09
        alpha*=self.dust_mask*(1-self.lamp_dip(t));r=roi_slice(self.dust_roi);f[r]+=(np.float32([178,151,108])-f[r])*alpha[...,None]

    def vehicle_state(self,t):
        cfg=self.cfg['passing_car'];duration=cfg['duration_seconds']
        for start in self.schedule['passing_car_starts']:
            age=(t-start)%self.period
            if age<duration:
                u=age/duration;pos=np.float32(cfg['start_xy'])*(1-u)+np.float32(cfg['end_xy'])*u;width=round(cfg['width_native_px'][0]*(1-u)+cfg['width_native_px'][1]*u)
                return float(pos[0]),float(pos[1]),width
        return None

    def apply_vehicle(self,f,t):
        state=self.vehicle_state(t)
        if state is None or self.vehicle is None:return
        x,y,width=state;height=round(width*self.vehicle.shape[0]/self.vehicle.shape[1]);a,b,c,d=self.vehicle_roi
        if width not in self.vehicle_cache:
            sprite=scaled_rgba(self.vehicle,(width,height));sprite[...,:3]=np.uint8(np.clip(sprite[...,:3].astype(np.float32)*[.65,.71,.83],0,255));self.vehicle_cache[width]=sprite
        full=np.zeros(self.base.shape[:2],np.float32);full[roi_slice(self.vehicle_roi)]=self.vehicle_mask
        top=y-height*.94;left=x-width*.5
        # Shadow and headlamp bounce use the body's true visible coverage, not a fade.
        yy,xx=grid(self.vehicle_roi);shadow=np.exp(-.5*((xx-x)/(width*.44))**2-.5*((yy-y)/(width*.05))**2)*self.vehicle_mask*.25;r=roi_slice(self.vehicle_roi);f[r]*=1-shadow[...,None]
        for hx,hy in self.vehicle_meta['headlights_normalized']:
            cx=left+hx*width;cy=top+hy*height
            if cx<0 or cx>=self.width or cy<0 or cy>=self.height:continue
            visible=full[min(self.height-1,round(cy)),min(self.width-1,round(cx))]
            if visible<=0:continue
            bloom=np.exp(-.5*((self.vx-cx)/7)**2-.5*((self.vy-(y+3))/2.2)**2)*self.vehicle_light_mask*visible
            f[roi_slice(self.vehicle_light_roi)]+=bloom[...,None]*np.float32([14,13,9])
        add_rgba(f,self.vehicle_cache[width],left,top,clip=full)

    def audit(self,t):
        mx,my=self.road_maps(t);active=self.road_mask>0
        # Finite source padding is protected in addition to the output contour.
        xl=np.floor(mx[active]).astype(int);xh=np.ceil(mx[active]).astype(int);yl=np.floor(my[active]).astype(int);yh=np.ceil(my[active]).astype(int)
        assert min(xl.min(),yl.min())>=0 and xh.max()<self.road_safe.shape[1] and yh.max()<self.road_safe.shape[0]
        assert all(np.all(self.road_safe[ys,xs]) for ys in [yl,yh] for xs in [xl,xh])
        jac=np.gradient(mx,axis=1)*np.gradient(my,axis=0)-np.gradient(mx,axis=0)*np.gradient(my,axis=1);minimum=float(jac[active].min());assert minimum>.5
        foliage_minimum=1.0
        for obj in self.foliage:
            mx,my=self.foliage_maps(obj,t,self.wind(t));active=obj['mask']>0;xx=mx[active];yy=my[active]
            assert np.floor(xx).min()>=0 and np.ceil(xx).max()<obj['source'].shape[1] and np.floor(yy).min()>=0 and np.ceil(yy).max()<obj['source'].shape[0]
            jac=np.gradient(mx,axis=1)*np.gradient(my,axis=0)-np.gradient(mx,axis=0)*np.gradient(my,axis=1);foliage_minimum=min(foliage_minimum,float(jac[active].min()))
        assert foliage_minimum>.5
        return {'road_source_taps_safe':True,'minimum_road_jacobian':minimum,'foliage_source_taps_safe':True,'minimum_foliage_jacobian':foliage_minimum,'required_assets_present':not self.assets_ready}

    def frame(self,t,only=None):
        t=float(t)%self.period;env=t%60;wind=self.wind(t);f=self.base.astype(np.float32);do=lambda name:only is None or name in only
        if do('foliage'):self.apply_foliage(f,t,wind)
        if do('road'):self.apply_road(f,t,wind)
        if do('traffic'):self.apply_vehicle(f,t)
        if do('rain'):self.apply_rain(f,t,wind)
        if do('drips'):self.apply_drips(f,t)
        if do('cabin'):self.apply_cabin(f,t)
        if do('scope'):self.apply_scope(f,t)
        if do('lamp'):self.apply_lamp(f,t)
        if do('dust'):self.apply_dust(f,t)
        return self.finish(f)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=120);parser.add_argument('--start',type=float,default=0);parser.add_argument('--only');parser.add_argument('--output');parser.add_argument('--samples',action='store_true');parser.add_argument('--allow-pending-assets',action='store_true');parser.add_argument('--attention-mode',choices=['review120','production600']);args=parser.parse_args();scene=Scene(args.attention_mode)
    if scene.assets_ready and not args.allow_pending_assets:raise RuntimeError('Required source assets pending: '+', '.join(scene.assets_ready))
    if args.samples:save_samples(scene,HERE/'evidence',[0,16,27.55,60,80,94.35,111]);print(json.dumps(scene.input_hashes(),indent=2));return
    encode(scene,HERE/(args.output or 'Back-Before-Dawn-v1-first-draft-120s.mp4'),args.seconds,args.start,args.only.split(',') if args.only else None)
if __name__=='__main__':main()
