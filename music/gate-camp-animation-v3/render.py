"""Gate Camp V3: steady periodic water, attached light and shared camp wind."""
from pathlib import Path
import argparse,json,math,sys
import cv2,numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'scene-animation-core'))
from core import *

class PortalWater:
    def __init__(self,base,geometry,cfg):
        self.roi=geometry['portal_roi'];self.src=base[roi_slice(self.roi)].astype(np.float32);self.y,self.x=np.indices(self.src.shape[:2],dtype=np.float32)
        self.safe=polygon_mask(self.roi,[geometry['aperture']],.1)>.99;dist=cv2.distanceTransform(np.pad(self.safe.astype(np.uint8),1),cv2.DIST_L2,5)[1:-1,1:-1]
        self.mask=smooth((dist-3)/9);self.taper=smooth((dist-3)/76);self.cfg=cfg;self.geometry=geometry
        self.fields=self.light_fields(self.x-157,self.y-174)
        blur=cv2.GaussianBlur(self.src*self.safe[...,None],(0,0),2.8)/np.maximum(cv2.GaussianBlur(self.safe.astype(np.float32),(0,0),2.8)[...,None],1e-5)
        self.texture=blur+.88*(self.src-blur)
    def light_fields(self,x,y):
        fields=[]
        for deg,wavelength,curve,weight,cycles in zip([63,128],[116,82],[16,10],[.66,.34],self.cfg['water_highlight_cycles_per_minute']):
            theta=math.radians(deg);along=x*math.cos(theta)+y*math.sin(theta);across=x*math.sin(theta)-y*math.cos(theta)
            fields.append((2*np.pi*(along+curve*np.sin(across/51+.7))/wavelength,2*np.pi*cycles/60,weight))
        return fields
    @staticmethod
    def light(fields,t):return sum(weight*(.5+.5*np.cos(phase-rate*t))**3 for phase,rate,weight in fields)
    def maps(self,t):
        dx=np.zeros_like(self.x);dy=np.zeros_like(self.y);phase=2*math.pi*t/60
        for wave,cycles in zip(self.geometry['waves'],self.cfg['water_wave_cycles_per_minute']):
            angle=math.radians(wave['direction_degrees']);nx=math.cos(angle);ny=math.sin(angle);theta=2*np.pi*(self.x*nx+self.y*ny)/wave['wavelength_px']-phase*cycles+wave['phase_radians'];v=wave['displacement_px']*np.sin(theta);dx+=nx*v;dy+=ny*v
        dx+=self.cfg['bounded_drift_native_px'][0]*math.sin(phase);dy+=self.cfg['bounded_drift_native_px'][1]*math.sin(phase)
        return (self.x+dx*self.taper).astype(np.float32),(self.y+dy*self.taper).astype(np.float32)
    def apply(self,f,t):
        mx,my=self.maps(t);value=cv2.remap(self.texture,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101);band=self.light(self.fields,t)
        value*=.90+.115*band[...,None];value+=(np.float32([181,222,247])-value)*(.13*band[...,None]);r=roi_slice(self.roi);f[r]+=(value-f[r])*self.mask[...,None]
    def audit(self,t):
        mx,my=self.maps(t);active=self.mask>0;x=mx[active];y=my[active];xl=np.floor(x).astype(int);xh=np.ceil(x).astype(int);yl=np.floor(y).astype(int);yh=np.ceil(y).astype(int)
        assert xl.min()>=0 and xh.max()<self.safe.shape[1] and yl.min()>=0 and yh.max()<self.safe.shape[0]
        assert all(np.all(self.safe[ys,xs]) for ys in [yl,yh] for xs in [xl,xh])
        xx=np.gradient(mx,axis=1);xy=np.gradient(mx,axis=0);yx=np.gradient(my,axis=1);yy=np.gradient(my,axis=0);minimum=float((xx*yy-xy*yx)[active].min());assert minimum>.25;return minimum

class Scene(SceneBase):
    def __init__(self):
        self.root=ROOT;self.renderer_path=Path(__file__);self.config_path=HERE/'settings.json';self.cfg=json.loads(self.config_path.read_text());self.source_path=ROOT/self.cfg['source'];self.fps=self.cfg['fps'];self.base=np.array(Image.open(self.source_path).convert('RGB'));self.h,self.w=self.base.shape[:2];self.regions={};self.masks={};self.allowed=np.zeros((self.h,self.w),bool)
        seed=ROOT/'creative/animation-development/2026-11-05-16-17/geometry-seeds.json';self.extra_inputs=[seed];geometry=json.loads(seed.read_text())['17']['portal_geometry'];self.portal=PortalWater(self.base,geometry,self.cfg);self.register('portal_water',self.portal.roi,self.portal.mask)
        self.spillroi=[1006,412,1422,557];self.sy,self.sx=grid(self.spillroi)
        stones=[[[1093,434],[1396,434],[1378,469],[1336,469],[1307,494],[1060,494],[1068,473]],[[1053,484],[1341,484],[1336,540],[1015,542]],[[1390,447],[1416,450],[1416,477],[1379,475]]]
        self.spill=polygon_mask(self.spillroi,stones,3)*np.exp(-.5*((self.sx-1247)/148)**2-.5*((self.sy-431)/91)**2)
        # Keep warm practicals and rail silhouettes out of stone response.
        src=self.base[roi_slice(self.spillroi)].astype(np.float32);self.spill*=1-smooth((src[...,0]-src[...,2]*1.2-35)/50)
        self.spill_fields=self.portal.light_fields((self.sx-1259)*1.25,155+(self.sy-435)*2.7);self.register('portal_steps_light',self.spillroi,self.spill)
        self.rimroi=[1037,35,1490,442];ry,rx=grid(self.rimroi);r=np.sqrt(((rx-1258)/208)**2+((ry-268)/231)**2)
        # Only inner ring material faces the watery emitter. Chevron apertures stay warm.
        self.rim=smooth((r-.76)/.05)*smooth((1.01-r)/.08);src=self.base[roi_slice(self.rimroi)].astype(np.float32);self.rim*=1-smooth((src[...,0]-src[...,2]*1.1-15)/55);self.rim*=polygon_mask(self.rimroi,[[[1050,105],[1131,46],[1350,40],[1472,163],[1483,390],[1393,437],[1077,437],[1040,325]]],4)
        # Remove aperture completely; this mask is attached to the actual carved ring.
        aperture_full=np.zeros((self.h,self.w),np.float32);aperture_full[roi_slice(self.portal.roi)]=polygon_mask(self.portal.roi,[geometry['aperture']],.1);self.rim*=1-aperture_full[roi_slice(self.rimroi)];self.rim_fields=self.portal.light_fields((rx-1259)*.8,(ry-268)*1.2);self.register('inner_ring_light',self.rimroi,self.rim)
        clouds=[[[226,221],[338,230],[455,263],[459,279],[360,266],[274,254],[225,249]],[[578,244],[647,236],[739,251],[742,276],[689,286],[623,271],[579,270]],[[923,229],[988,211],[1032,212],[1031,260],[962,277],[930,266]],[[1487,164],[1546,141],[1628,119],[1650,128],[1631,145],[1558,171],[1490,191]]]
        self.cloud=Clouds(self.base,[214,115,1660,300],clouds,3.2,feather=7);self.register('clouds',self.cloud.roi,self.cloud.mask)
        self.hazes=[]
        for name,roi,polys,speed,scale,strength in [
            ('far_basin',[290,382,1018,510],[[[301,421],[386,405],[482,404],[594,418],[648,398],[825,400],[905,416],[1009,410],[1005,448],[902,449],[839,466],[797,466],[774,444],[745,454],[722,480],[700,482],[681,460],[647,448],[618,453],[610,487],[582,488],[569,466],[542,464],[520,477],[446,481],[404,474],[379,462],[300,450]]],4.2,40,.09),
            ('near_ground',[573,523,1530,767],[[[784,595],[890,566],[1035,557],[1159,550],[1268,564],[1372,587],[1498,626],[1467,675],[1331,650],[1230,645],[1125,671],[1005,669],[888,643]],[[1047,683],[1160,684],[1300,711],[1415,729],[1482,749],[1380,760],[1240,736],[1121,726]]],14,20,.058)]:
            mask=polygon_mask(roi,polys,16);sheet=Sheet(roi,51+len(self.hazes),speed,scale);self.hazes.append((name,roi,mask,sheet,strength));self.register(name,roi,mask)
        self.canopyroi=[0,0,942,446];self.cy,self.cx=grid(self.canopyroi);self.canopy=polygon_mask(self.canopyroi,[[[212,4],[859,4],[536,67],[393,114],[225,163]],[[5,87],[109,111],[100,301],[86,413],[5,435]]],15,5);self.canopy_src=self.base[roi_slice(self.canopyroi)].astype(np.float32);self.register('canopy',self.canopyroi,self.canopy)
        asset=HERE.parent/'scene16-17-first-draft-assets';cleanpath=asset/'gate-motion-background.png';clean=np.array(Image.open(cleanpath).convert('RGB'));self.extra_inputs.append(cleanpath);self.elements=[]
        for name,roi,anchor,kind,amount in [('rope',[517,280,576,623],[565,618],'wire',.85),('scrub',[737,535,810,594],[775,584],'bend',2.0)]:
            p=asset/f'gate-{name}-mask.png';self.extra_inputs.append(p);mask=np.array(Image.open(p))/255.;element=Element(self.base,clean,roi,mask,anchor,kind,amount,.8);self.elements.append(element);self.register(name,roi,element.allowed)
        self.steam=Vapour([303,508,391,608],[352,605],72,8,-.4,10,.5,.040,(191,185,171));self.register('cup_steam',self.steam.roi,self.steam.mask)
        self.lights=[]
        for i,(roi,center,radius,depth) in enumerate([([125,122,231,277],[182,207],[31,46],.7),([26,75,289,445],[148,215],[75,142],.22),([94,456,342,622],[203,532],[96,70],.10)]):
            src=self.base[roi_slice(roi)].astype(np.float32);mask=ellipse(roi,center,radius,.01)*smooth((src[...,0]-src[...,2]*1.18-20)/50);self.lights.append((roi,mask,depth));self.register('lantern_'+str(i),roi,mask)
        # Tiny portal-facing cup/case edge receives a small, distance-attenuated response.
        self.fgrimroi=[316,599,435,692];src=self.base[roi_slice(self.fgrimroi)].astype(float);self.fgrim=ellipse(self.fgrimroi,[391,638],[25,41],.01)*smooth((src[...,2]-src[...,0]*.6)/55);self.register('foreground_blue_rim',self.fgrimroi,self.fgrim)
        self.screenroi=[0,459,156,637];self.screenmask=polygon_mask(self.screenroi,[[[0,471],[118,474],[145,614],[0,629]]],3,2);self.screen_y,self.screen_x=grid(self.screenroi);self.register('laptop',self.screenroi,self.screenmask)
        self.radioroi=[217,547,269,611];self.radio=ellipse(self.radioroi,[238,556],[1.6,1.0],.01)+ellipse(self.radioroi,[247,558],[1.1,.8],.01);self.radio=np.minimum(self.radio,1);self.register('radio',self.radioroi,self.radio)
        roverpath=asset/'expedition-rover-sprite.png';self.extra_inputs.append(roverpath);self.rover=np.array(Image.open(roverpath).convert('RGBA'));self.roverroi=[1140,531,1672,817];self.rovermask=polygon_mask(self.roverroi,[[[1145,536],[1273,535],[1384,580],[1501,620],[1671,665],[1671,812],[1551,788],[1400,746],[1264,671],[1145,639]]],2)
        # Source practical at x1527 and its near rocks remain in front.
        yy,xx=grid(self.roverroi);self.rovermask*=1-polygon_mask(self.roverroi,[[[1515,637],[1545,637],[1546,794],[1511,794]],[[1620,690],[1671,690],[1671,815],[1620,800]]],1)
        self.register('rover',self.roverroi,self.rovermask)
        self.rover_cache={}

    def wind(self,t):return .20+.8*max(envelope(t,*event) for event in self.cfg['wind_gusts_seconds'])

    def rover_at(self,t):
        a,b,c,d=self.cfg['rover_review_enter_park_reverse_seconds']
        if t<a or t>d:return None
        if t<b:u=smooth((t-a)/(b-a));x=1736+(1211-1736)*u;y=789+(618-789)*u;width=103+(85-103)*u
        elif t<c:x,y,width=1211,618,85
        else:u=smooth((t-c)/(d-c));x=1211+(1736-1211)*u;y=618+(789-618)*u;width=85+(103-85)*u
        return x,y,int(round(width))

    def apply_rover(self,f,t):
        state=self.rover_at(t)
        if state is None:return
        x,y,width=state;height=round(width*self.rover.shape[0]/self.rover.shape[1])
        if width not in self.rover_cache:
            sprite=scaled_rgba(self.rover,(width,height));# Dawn exposure integration; no rectangular backdrop.
            sprite[...,:3]=np.uint8(np.clip(sprite[...,:3].astype(float)*[.69,.74,.88],0,255));self.rover_cache[width]=sprite
        clip=np.zeros((self.h,self.w),np.float32);clip[roi_slice(self.roverroi)]=self.rovermask
        a,b,c,d=self.roverroi;yy,xx=grid(self.roverroi);shadow=np.exp(-.5*((xx-x)/(width*.45))**2-.5*((yy-y)/(width*.07))**2)*self.rovermask*.28;r=roi_slice(self.roverroi);f[r]*=1-shadow[...,None]
        add_rgba(f,self.rover_cache[width],x-width*.5,y-height*.94,clip=clip)

    def frame(self,t,only=None):
        t=t%60;f=self.base.astype(np.float32);wind=self.wind(t);do=lambda name:only is None or name in only
        if do('clouds'):self.cloud.apply(f,t)
        if do('haze'):
            for name,roi,mask,sheet,strength in self.hazes:
                alpha=mask*sheet.at(t)*strength*(.35+.9*wind);r=roi_slice(roi)
                color=np.float32([123,143,161] if name=='far_basin' else [154,142,127]);f[r]+=(color-f[r])*alpha[...,None]
        if do('canopy'):
            phase=2*math.pi*t/60;dx=self.canopy*(np.sin(self.cx/81+self.cy/99-phase*3)+.35*np.sin(self.cx/43-phase*7))*self.cfg['canopy_displacement_native_px']*wind
            mx=(self.cx+dx).astype(np.float32);my=(self.cy+self.canopy*np.sin(self.cx/115-phase*2)*.65*wind).astype(np.float32)
            safe=cv2.remap(np.float32(self.canopy>0),mx,my,cv2.INTER_LINEAR)>.999;value=cv2.remap(self.canopy_src,mx,my,cv2.INTER_LINEAR);m=self.canopy*safe;value*=1+.025*np.cos(self.cx/81+self.cy/99-phase*3)[...,None]*wind*m[...,None];r=roi_slice(self.canopyroi);f[r]+=(value-f[r])*m[...,None]
        if do('elements'):
            for element in self.elements:element.apply(f,t,wind)
        if do('rover'):self.apply_rover(f,t)
        if do('water'):self.portal.apply(f,t)
        if do('light'):
            band=self.portal.light(self.spill_fields,t);r=roi_slice(self.spillroi);strength=self.spill*(.22+.78*band);f[r]+=strength[...,None]*np.float32(self.cfg['portal_light_rgb_lift'])
            band=self.portal.light(self.rim_fields,t);r=roi_slice(self.rimroi);f[r]+=self.rim[...,None]*(.2+.8*band[...,None])*np.float32([2,12,24])
            r=roi_slice(self.fgrimroi);f[r]+=self.fgrim[...,None]*(.45+.4*math.sin(2*math.pi*t/60*11))*np.float32([.5,2.0,3.2])
        if do('lantern'):
            dip=max(envelope(t,start,.06,.08,.30)*depth for start,depth in zip(self.cfg['lantern_dip_seconds'],[.65,.35,.3]))
            for roi,mask,depth in self.lights:
                r=roi_slice(roi);f[r]=linear_rgb(rgb_linear(f[r])*(1-mask[...,None]*dip*depth))
        if do('laptop'):
            # Draw in a normalized screen plane, then perspective-map onto existing glass.
            plane=np.zeros((150,170,4),np.uint8);phase=2*math.pi*t/60;pos=(round(57+21*math.sin(phase)),round(71+19*math.cos(phase)))
            cv2.circle(plane,pos,3,(142,220,221,135),1,cv2.LINE_AA);cv2.line(plane,(pos[0]-5,pos[1]),(pos[0]+5,pos[1]),(119,192,209,110),1)
            for i in range(7):cv2.line(plane,(140,25+i*5),(148+(int(t*.5)+i)%5,25+i*5),(109,185,205,110),1)
            dst=np.float32([[0,12],[118,15],[145,155],[0,170]]);matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[169,0],[169,149],[0,149]]),dst);overlay=cv2.warpPerspective(plane,matrix,(156,178),flags=cv2.INTER_LINEAR);alpha=overlay[...,3]/255*self.screenmask;r=roi_slice(self.screenroi);f[r]=f[r]*(1-alpha[...,None])+overlay[...,:3]*alpha[...,None]
        if do('radio'):
            receive=max(envelope(t,start,.15,1.4,.5) for start in self.cfg['radio_receive_seconds']);pulse=.65+.35*math.sin(2*math.pi*t*3)**2;r=roi_slice(self.radioroi);f[r]+=self.radio[...,None]*receive*pulse*np.float32([32,91,57])
        if do('steam'):self.steam.apply(f,t)
        return self.finish(f)

def main():
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=60);p.add_argument('--start',type=float,default=0);p.add_argument('--only');p.add_argument('--output');p.add_argument('--samples',action='store_true');args=p.parse_args();scene=Scene()
    if args.samples:save_samples(scene,HERE/'evidence',[0,12,18,26.55,38,53.35]);print(json.dumps(scene.input_hashes(),indent=2));return
    encode(scene,HERE/(args.output or 'Gate-Camp-V3-first-draft-60s.mp4'),args.seconds,args.start,args.only.split(',') if args.only else None)
if __name__=='__main__':main()
