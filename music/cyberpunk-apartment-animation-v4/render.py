"""Native-first city V4: independent clocks, source-bound lighting and traffic."""
from pathlib import Path
import argparse, json, math, sys
import cv2, numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'scene-animation-core'))
from core import *

ROADS=[
 [[876,331],[1010,354],[1150,380],[1275,402],[1400,424],[1537,452]],
 [[876,334],[1010,357],[1150,383],[1275,405],[1400,427],[1537,455]],
 [[681,454],[814,458],[963,463],[1120,466],[1265,469]],
 [[681,458],[814,462],[963,467],[1120,470],[1265,473]],
 [[1080,568],[1114,579],[1154,596],[1203,616],[1266,641],[1500,752],[1770,884]],
 [[1080,572],[1114,583],[1154,600],[1203,620],[1266,645],[1460,738],[1700,850]]]
FOG=[[[705,135],[783,156],[838,197],[873,208],[911,239],[904,269],[861,248],[805,239],[757,211],[705,221]],[[904,288],[924,265],[942,245],[961,226],[974,251],[963,288],[935,318],[901,330]],[[1024,303],[1052,279],[1103,276],[1118,293],[1099,309],[1062,312]],[[1283,337],[1315,328],[1345,350],[1378,364],[1396,383],[1390,399],[1347,390],[1300,370],[1283,367]],[[1482,134],[1520,112],[1568,91],[1579,139],[1554,163],[1509,199],[1488,217]]]

def line_mask(shape,points,width):
    a=np.zeros(shape,np.uint8);cv2.polylines(a,[np.int32(points)],False,255,width,cv2.LINE_AA);return a/255.

def route(points):
    p=np.float32(points);length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];return p,length

def on_route(p,s,d):
    i=min(len(p)-2,max(0,int(np.searchsorted(s,d,side='right')-1)));u=(d-s[i])/(s[i+1]-s[i]);v=p[i+1]-p[i];v/=np.linalg.norm(v);return p[i]+u*(p[i+1]-p[i]),v

class Scene(SceneBase):
    def __init__(self):
        self.root=ROOT;self.config_path=HERE/'settings.json';self.cfg=json.loads(self.config_path.read_text());self.source_path=ROOT/self.cfg['source'];self.renderer_path=Path(__file__);self.fps=self.cfg['fps']
        self.base=np.array(Image.open(self.source_path).convert('RGB'));self.h,self.w=self.base.shape[:2];self.regions={};self.masks={};self.allowed=np.zeros((self.h,self.w),bool)
        asset=HERE.parent/'scene16-17-first-draft-assets';seed_path=ROOT/'creative/animation-development/2026-11-05-16-17/geometry-seeds.json';self.extra_inputs=[seed_path]
        seeds=json.loads(seed_path.read_text())['16'];full=[0,0,self.w,self.h]
        self.glass=polygon_mask(full,seeds['glass_polygons'],2,1)
        self.cloud=Clouds(self.base,[694,80,1585,402],FOG,self.cfg['cloud_speed_native_px_s']);self.register('clouds',self.cloud.roi,self.cloud.mask)
        self.mist=Sheet([430,110,1580,620],21,-7,100);self.mistmask=polygon_mask(self.mist.roi,FOG,12)*.085;self.register('gap_mist',self.mist.roi,self.mistmask)
        # Retraced against native rooftops, bridge deck, piers and fixed boats; the
        # legacy broad bay masks include foreground masonry and are only seeds.
        water_polys=[[[703,478],[735,478],[736,491],[706,492]],[[1081,478],[1237,479],[1237,523],[1192,523],[1175,516],[1174,502],[1126,501],[1124,524],[1101,517],[1083,516]],[[1282,518],[1316,519],[1318,570],[1283,577]],[[1336,554],[1371,559],[1391,571],[1386,637],[1343,637],[1336,612]]]
        self.waterroi=[700,471,1435,645];self.water=polygon_mask(self.waterroi,water_polys,3,2);self.wy,self.wx=grid(self.waterroi);self.water_src=self.base[roi_slice(self.waterroi)].astype(np.float32);self.water_noise=Sheet(self.waterroi,3,-3,18)
        self.register('water',self.waterroi,self.water)
        self.floorroi=[885,690,1523,780];self.floor=polygon_mask(self.floorroi,[seeds['floor_polygon']],7)*np.clip((self.base[roi_slice(self.floorroi)][...,2].astype(float)-self.base[roi_slice(self.floorroi)][...,0]*.75)/28,0,1);self.fy,self.fx=grid(self.floorroi);self.register('floor_reflection',self.floorroi,self.floor)
        self.signs=[];self.sign_halos=[]
        for i,spec in enumerate(seeds['existing_neon_boxes_and_phases']):
            x0,y0,x1,y1,phase,freq=spec;roi=[x0,y0,x1,y1];src=self.base[roi_slice(roi)].astype(np.float32);lum=src.max(axis=2);sat=src.max(axis=2)-src.min(axis=2)
            mask=smooth((lum-85)/85)*smooth((np.maximum(sat,lum-90)-20)/50);mask*=polygon_mask(roi,[[[x0,y0],[x1-1,y0],[x1-1,y1-1],[x0,y1-1]]],1)
            self.signs.append((roi,mask,phase,freq,src));self.register('sign_'+str(i),roi,mask)
            halo_roi=[max(0,x0-8),max(0,y0-8),min(self.w,x1+8),min(self.h,y1+8)];ha,hb,hc,hd=halo_roi;seed=np.zeros((hd-hb,hc-ha),np.float32);seed[y0-hb:y1-hb,x0-ha:x1-ha]=mask
            halo=cv2.GaussianBlur(seed,(0,0),3);halo[halo<.002]=0;halo*=self.glass[roi_slice(halo_roi)];palette=np.mean(src[mask>.4],axis=0) if np.any(mask>.4) else np.float32([140,180,230]);palette=palette/max(palette.max(),1)*5
            self.sign_halos.append((halo_roi,halo,palette));self.register('sign_haze_'+str(i),halo_roi,halo)
        # Independent occupied aperture groups; narrow bright-source masks preserve masonry.
        self.windows=[]
        for i,roi in enumerate([[828,358,873,484],[978,406,1027,534],[1457,369,1500,437],[549,434,605,489],[715,346,762,418]]):
            src=self.base[roi_slice(roi)].astype(np.float32);mask=smooth((src[...,0]-src[...,2]*1.10-8)/25)*smooth((src.max(2)-85)/65)
            self.windows.append((roi,mask,i));self.register('windows_'+str(i),roi,mask)
        self.beacons=[]
        # Actual source cores, not new floating coordinates.
        for i,(x,y) in enumerate([[1043,8],[1149,10],[622,151],[1481,151],[1375,174],[1211,179]]):
            roi=[x-6,y-5,x+7,y+7];src=self.base[roi_slice(roi)].astype(np.float32);mask=smooth((src[...,0]-src[...,1]*1.3-10)/35)*smooth((src[...,0]-65)/60);self.beacons.append((roi,mask,i));self.register('beacon_'+str(i),roi,mask)
        occ=polygon_mask(full,seeds['traffic_occluders'],1)
        self.traffic_clip=self.glass*(1-occ);traffic=np.zeros((self.h,self.w),np.float32)
        for i,p in enumerate(ROADS):traffic=np.maximum(traffic,line_mask(traffic.shape,p,15 if i<4 else 30))
        self.register('traffic',full,traffic*self.traffic_clip);self.routes=[route(p) for p in ROADS]
        rng=np.random.default_rng(87);self.births=[]
        for i in range(6):
            candidates=np.sort(rng.uniform(0,60,11 if i<4 else 9));kept=[];minimum=.8 if i<4 else .5
            for birth in candidates:
                # Reserve a safe gap around the longer commuter vehicle.
                if i==0 and abs((birth-self.cfg['bus_start_seconds']+30)%60-30)<1.0:continue
                if not kept or birth-kept[-1]>=minimum:kept.append(float(birth))
            if len(kept)>1 and kept[0]+60-kept[-1]<minimum:kept.pop()
            self.births.append(np.float32(kept))
        self.ferryroute=route([[1030,484],[1100,486],[1170,488],[1259,491],[1290,493]])
        self.ferryroi=[1077,478,1254,502];self.ferrymask=polygon_mask(self.ferryroi,[[[1080,479],[1252,479],[1252,500],[1080,500]]],2)
        self.register('ferry',self.ferryroi,self.ferrymask)
        self.rainroi=[425,0,1672,665];self.rainmask=self.glass[roi_slice(self.rainroi)];self.register('rain',self.rainroi,self.rainmask)
        rng=np.random.default_rng(44);self.rain_particles=[]
        for i in range(460):self.rain_particles.append((rng.uniform(425,1672),rng.uniform(0,730),int(rng.integers(11,19)),rng.uniform(3,9),rng.uniform(.05,.16)))
        self.drops=[]
        for i in range(17):
            self.drops.append((rng.uniform(460,1610),rng.uniform(110,480),float(rng.uniform(0,60)),rng.uniform(1.1,2.2),rng.uniform(24,58)))
        self.drops.extend([(1124,280,7,1.7,35),(1127,271,7,1.2,45)])
        self.steam=Vapour([563,631,650,729],[608,723],8,8,-.8,10,.5,.038,(201,195,183));self.register('cup_steam',self.steam.roi,self.steam.mask)
        self.vents=[]
        # No unambiguous vent grille is visible here: use gap mist, not a wall emitter.
        for roi,anchor,seed,poly in [([886,313,951,410],[926,403],45,[[891,333],[911,320],[946,348],[946,393],[923,407],[894,391]]),([1436,310,1510,407],[1481,401],46,[[1440,340],[1460,332],[1503,352],[1506,392],[1473,400],[1445,383]])]:
            v=Vapour(roi,anchor,seed,4,-2,10,.5,.027,(144,165,187));v.mask*=self.glass[roi_slice(roi)]*polygon_mask(roi,[poly],7);self.vents.append(v);self.register('gap_wisps_'+str(seed),roi,v.mask)
        self.lamproi=[625,678,772,841];y,x=grid(self.lamproi);src=self.base[roi_slice(self.lamproi)].astype(np.float32)
        core=ellipse(self.lamproi,[704,711],[29,15],.01)*smooth((src.max(2)-130)/80)
        spill=ellipse(self.lamproi,[704,793],[35,23],.01)*smooth((src[...,0]-src[...,2]*1.2-15)/60)
        self.lamp=np.maximum(core,spill*.75);self.register('table_lamp',self.lamproi,self.lamp)
        clean_path=asset/'city-plant-background-aligned.png';clean=np.array(Image.open(clean_path).convert('RGB'));self.extra_inputs.append(clean_path);self.leaves=[]
        for i,anchor in enumerate([[229,401],[302,383]]):
            p=asset/f'city-leaf-{i+1}-mask.png';self.extra_inputs.append(p);mask=np.array(Image.open(p))/255.;v=Element(self.base,clean,[125,300,425,545],mask,anchor,amount=self.cfg['leaf_rotation_degrees'],phase=i*2.3);self.leaves.append(v);self.register('leaf_'+str(i),v.roi,v.allowed)

    def sign_state(self,t,phase,freq):
        p=2*math.pi*t/60;programme=.88+.12*math.sin(p*(freq+2)+phase);dip=envelope(t,(11+phase*7)%60,.16,1.2,.65)
        return programme-.62*dip

    def traffic(self,f,t):
        layer=np.zeros((self.h,self.w,4),np.uint8)
        for i,(p,s) in enumerate(self.routes):
            speed=self.cfg['traffic_speed_native_px_s'][i]
            for j,birth in enumerate(self.births[i]):
                age=(t-birth)%60;d=age*speed
                if d>s[-1]:continue
                if i%2:d=s[-1]-d
                pos,v=on_route(p,s,d);v*=(-1 if i%2 else 1);near=np.clip((pos[1]-530)/120,0,1) if i>=4 else 0;length=4.5+near*4;width=1.7+near*1.8
                self.draw_vehicle(layer,pos,v,length,width,i%2,j)
        # One source-road commuter vehicle; same route, no new elevated rail.
        age=(t-self.cfg['bus_start_seconds'])%60;p,s=self.routes[0];d=age*self.cfg['traffic_speed_native_px_s'][0]
        if d<s[-1]:
            pos,v=on_route(p,s,d);self.draw_vehicle(layer,pos,v,20,4.5,0,3,bus=True)
        alpha=layer[...,3].astype(np.float32)/255*self.traffic_clip;r=alpha>0
        f[r]=f[r]*(1-alpha[r,None])+layer[...,:3][r]*alpha[r,None]

    @staticmethod
    def draw_vehicle(layer,pos,v,length,width,direction,variant,bus=False):
        n=np.array([-v[1],v[0]]);body=np.array([pos-v*length*.5-n*width*.5,pos+v*length*.5-n*width*.5,pos+v*length*.5+n*width*.5,pos-v*length*.5+n*width*.5]);poly=np.rint(body).astype(np.int32)
        reflected=pos+n*(width*.8+1);cv2.line(layer,tuple(np.rint(reflected-v*length*.40).astype(int)),tuple(np.rint(reflected+v*length*.38).astype(int)),(116,166,190,65) if direction==0 else (175,69,82,65),2,cv2.LINE_AA)
        cv2.fillConvexPoly(layer,poly,(61+variant%3*9,72,84,255),cv2.LINE_AA)
        cv2.line(layer,tuple(np.rint(pos-v*length*.27).astype(int)),tuple(np.rint(pos+v*length*.27).astype(int)),(102,165,187,255),2 if bus else 1,cv2.LINE_AA)
        front=pos+v*length*.50;color=(235,248,255,255) if direction==0 else (255,96,88,255)
        for side in [-1,1]:cv2.circle(layer,tuple(np.rint(front+n*width*.32*side).astype(int)),1,color,-1,cv2.LINE_AA)

    def rain(self,f,t):
        roi=self.rainroi;a,b,c,d=roi;layer=np.zeros((d-b,c-a),np.float32)
        for x,y,cycles,length,opacity in self.rain_particles:
            yy=(y+t*cycles*730/60)%730-35;xx=x-(yy-y)*.12
            xx=425+(xx-425)%1247
            cv2.line(layer,(round(xx-a),round(yy)),(round(xx-a-1.4),round(yy+length)),opacity,1,cv2.LINE_AA)
        alpha=layer*self.rainmask;r=roi_slice(roi);f[r]+=(np.float32([167,195,221])-f[r])*alpha[...,None]
        # Moving bead lenses sample the already lit exterior, never frame/interior pixels.
        exterior=f[r].copy();yy,xx=np.indices(alpha.shape,dtype=np.float32)
        for index,(x,y,start,radius,travel) in enumerate(self.drops):
            age=(t-start)%60
            if age>24:continue
            fade=smooth(age/2)*smooth((24-age)/3);cy=y+travel*smooth(age/24);cx=x-math.sin(age*.12)*1.2
            if index>=17:
                merge=smooth((age-11)/5);cx=cx*(1-merge)+1125*merge;cy=cy*(1-merge)+(278+40*smooth(age/24))*merge
                if index==18:fade*=1-merge
                else:radius*=1+.22*merge
            rx=radius*(1+.25*smooth((age-10)/4));ry=rx*1.65;left=max(0,int(cx-a-4));right=min(c-a,int(cx-a+5));top=max(0,int(cy-8));bottom=min(d-b,int(cy+9))
            if right<=left or bottom<=top:continue
            dx=xx[top:bottom,left:right]-(cx-a);dy=yy[top:bottom,left:right]-cy;shape=np.exp(-.5*((dx/rx)**2+(dy/ry)**2));mask=shape*self.rainmask[top:bottom,left:right]*fade
            mx=(xx[top:bottom,left:right]+dx*.5*shape).astype(np.float32);my=(yy[top:bottom,left:right]+dy*.5*shape).astype(np.float32)
            safe=cv2.remap(self.rainmask,mx,my,cv2.INTER_LINEAR)> .999;mask*=safe
            sample=cv2.remap(exterior,mx,my,cv2.INTER_LINEAR);patch=f[r][top:bottom,left:right];patch+=(sample-patch)*mask[...,None]*.75;patch+=mask[...,None]*np.float32([10,16,20])

    def ferry(self,f,t):
        age=(t-self.cfg['ferry_start_seconds'])%60;p,s=self.ferryroute;d=age*12
        if d>s[-1]:return
        pos,v=on_route(p,s,d);a,b,c,e=self.ferryroi;layer=np.zeros((self.h,self.w,4),np.uint8);n=np.array([-v[1],v[0]])
        hull=np.rint([pos-v*10-n*2.4,pos+v*11,pos-v*8+n*2.4]).astype(np.int32);cv2.fillConvexPoly(layer,hull,(112,132,146,255),cv2.LINE_AA)
        cv2.line(layer,tuple(np.rint(pos-v*5).astype(int)),tuple(np.rint(pos+v*3).astype(int)),(210,222,220,255),2,cv2.LINE_AA)
        for sign in [-1,1]:cv2.line(layer,tuple(np.rint(pos-v*10+sign*n*2).astype(int)),tuple(np.rint(pos-v*36+sign*n*6).astype(int)),(127,158,181,90),1,cv2.LINE_AA)
        local=layer[b:e,a:c].astype(np.float32);alpha=local[...,3]/255*self.ferrymask;patch=f[b:e,a:c];patch*=1-alpha[...,None];patch+=local[...,:3]*alpha[...,None]

    def frame(self,t,only=None):
        t=t%60;f=self.base.astype(np.float32);do=lambda name:only is None or name in only
        if do('clouds'):self.cloud.apply(f,t)
        if do('mist'):
            r=roi_slice(self.mist.roi);alpha=self.mist.at(t)*self.mistmask;f[r]+=(np.float32([125,151,177])-f[r])*alpha[...,None]
        signals=[]
        for roi,mask,phase,freq,src in self.signs:
            state=self.sign_state(t,phase,freq);signals.append(state)
            if do('signs'):
                r=roi_slice(roi);f[r]+=(src*state-src)*mask[...,None]
        if do('signs'):
            for state,(roi,mask,palette) in zip(signals,self.sign_halos):f[roi_slice(roi)]+=mask[...,None]*(state-.85)*palette
        if do('water'):
            phase=2*np.pi*t/60;noise=self.water_noise.at(t);r=roi_slice(self.waterroi)
            # Surface sampling is confined to an inset wet region, with stationary banks.
            dx=(noise-.5)*1.3*self.water;mx=(self.wx-self.waterroi[0]+dx).astype(np.float32);my=self.wy-self.waterroi[1]
            safe=cv2.remap(np.float32(self.water>0),mx,my,cv2.INTER_LINEAR)>.999;v=cv2.remap(self.water_src,mx,my,cv2.INTER_LINEAR)
            f[r]+=(v-f[r])*(self.water*safe)[...,None]
            response=(signals[1]-.85)*ellipse(self.waterroi,[1101,511],[14,45],.01)+(signals[4]-.85)*ellipse(self.waterroi,[1369,582],[19,54],.01)
            f[r]+=self.water[...,None]*(response[...,None]*np.float32([23,15,36])+(noise-.5)[...,None]*np.float32([2,3,4]))
        if do('reflections'):
            r=roi_slice(self.floorroi);wave=np.sin(self.fx*.04+self.fy*.21-2*np.pi*t/60*9);response=.5*(signals[0]+signals[1])-.85;f[r]+=self.floor[...,None]*(response*18+wave[...,None]*.8)*np.float32([1,.6,1.25])
        if do('windows'):
            for roi,mask,i in self.windows:
                state=1-.73*envelope(t,8+i*8,.6,4+i*.3,1.0);r=roi_slice(roi);f[r]*=1-mask[...,None]*(1-state)
            for roi,mask,i in self.beacons:
                state=.26+.74*envelope(t,i*.41,.15,.5,.45,5+i%2);r=roi_slice(roi);f[r]+=self.base[r]*(state-1)*mask[...,None]
        if do('traffic'):self.traffic(f,t)
        if do('ferry'):self.ferry(f,t)
        if do('rain'):self.rain(f,t)
        if do('vents'):
            for v in self.vents:v.apply(f,t,.7+.3*math.sin(2*math.pi*t/60*2)**2)
        if do('steam'):self.steam.apply(f,t)
        if do('lamp'):
            dip=0
            for start,depth in zip(self.cfg['lamp_dip_seconds'],self.cfg['lamp_dip_depth']):dip=max(dip,depth*envelope(t,start,.055,.08,.28))
            r=roi_slice(self.lamproi);f[r]=linear_rgb(rgb_linear(f[r])*(1-self.lamp[...,None]*dip))
        if do('leaves'):
            for leaf in self.leaves:leaf.apply(f,t)
        return self.finish(f)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=60);parser.add_argument('--start',type=float,default=0);parser.add_argument('--only');parser.add_argument('--output');parser.add_argument('--samples',action='store_true');args=parser.parse_args();scene=Scene()
    if args.samples:save_samples(scene,HERE/'evidence',[0,10,20.55,36,47.3,55]);print(json.dumps(scene.input_hashes(),indent=2));return
    encode(scene,HERE/(args.output or 'Cyberpunk-Apartment-V4-first-draft-60s.mp4'),args.seconds,args.start,args.only.split(',') if args.only else None)
if __name__=='__main__':main()
