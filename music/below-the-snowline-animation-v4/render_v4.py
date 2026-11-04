"""Snowline V4: a continuous two-minute weather/base-activity review, not a tiled loop."""
from pathlib import Path
import sys, json, math, time, subprocess, argparse, hashlib
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import numpy as np
from PIL import Image

H=Path(__file__).resolve().parent
ROOT=H.parents[1]
W,HEIGHT,FPS=1280,720,30
S=np.array([W/1672,HEIGHT/941],np.float32)
cv2.setNumThreads(1)

def smooth(x):
    v=np.clip(x,0,1); return v*v*(3-2*v)
def pulse(t,start,end,rise=2,fall=2):
    return float(smooth((t-start)/rise)*smooth((end-t)/fall))
def point(x,y):return tuple(np.rint(np.array([x,y])*S).astype(int))
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value): (H/name).write_text(json.dumps(value,indent=2),encoding='utf-8')

class Scene:
    def __init__(self):
        self.c=json.loads((H/'v2-scene.json').read_text(encoding='utf-8'))
        self.base=np.array(Image.open(H/'source.png').convert('RGB').resize((W,HEIGHT),Image.Resampling.LANCZOS))
        self.y,self.x=np.mgrid[:HEIGHT,:W].astype(np.float32)
        self.glass=self.poly(self.c['glass'],8)
        self.g=json.loads((H/'geometry-v4.json').read_text(encoding='utf-8'))
        self.sky=self.poly(self.g['cloud_safe_polygon'],30)*self.glass
        self.flight_mask=self.poly(self.g['cloud_safe_polygon'],1)*self.glass
        self.bridge=self.poly(self.c['bridge_guard'],1)
        self.skyvalid=(self.sky>.995).astype(np.float32)
        self.protected=self.glass<.001
        self.windows=[(c,self.poly(c['poly'],1)) for c in self.c['windows']]
        self.buttons=[(c,self.poly(c['poly'],1.4)) for c in self.g['physical_lenses']]
        self.keys=[self.poly((np.array(p)-[4,6]).tolist(),.8) for p in self.c['keys']]
        self.radar=self.poly(self.c['radar'],1.5);self.readout=self.poly(self.c['readout'],1.2)
        self.lamp=self.poly(self.c['lamp_poly'],2)
        self.spill=self.poly(self.c['spill_poly'],24)*.1
        self.bridgeglass=self.poly([[800,398],[1401,393],[1402,428],[797,433]],1)
        for x in [809,868,926,983,1040,1098,1154,1211,1269,1325,1384]:
            cv2.line(self.bridgeglass,point(x,393),point(x,434),0,4,cv2.LINE_AA)
            cv2.line(self.bridgeglass,point(x,430),point(x+54,395),0,3,cv2.LINE_AA)
        self.fog=[]
        for i,fc in enumerate(self.c['fog']):
            m=self.poly(fc['poly'],fc['feather']*1.3)*self.glass*(1-self.bridge)
            self.fog.append((m,self.texture(100+i),i))
        # A deeper bank occupies the channel behind the foreground cliffs.
        self.valley=self.poly([[1058,451],[1298,449],[1410,520],[1488,645],[1326,658],[1190,558]],65)*(1-self.bridge)*self.glass
        self.valleytex=self.texture(63)
        self.ledge=self.poly([[422,244],[588,252],[762,282],[790,308],[606,289],[425,268]],9)*self.glass
        self.ledgetex=self.texture(34)
        self.scans=[(c,self.poly(c['poly'],.7)) for c in self.c['habitat_screens']]
        warm=(self.base[:,:,0].astype(float)-self.base[:,:,2]>30)&(self.base[:,:,0]>140)
        self.bridge_lamps=[]
        for c in self.c['bridge_lights']:
            x=c['poly'][0][0]
            mask=self.poly([[x-8,384],[x+32,384],[x+32,400],[x-8,400]],1.3)*warm
            if mask.any():self.bridge_lamps.append(mask)
        self.flakes=[];rng=np.random.default_rng(70311)
        for count,vx,vy,rad,opacity in [(520,30,12,.5,.30),(210,75,22,.9,.42),(44,145,35,1.5,.32)]:
            for _ in range(count):
                self.flakes.append((rng.uniform(-W,W),rng.uniform(-HEIGHT,HEIGHT),vx*rng.uniform(.7,1.3),vy*rng.uniform(.7,1.3),rad*rng.uniform(.7,1.3),opacity*rng.uniform(.65,1),rng.uniform(0,6.3)))
        asset=np.asarray(Image.open(H/'assets/lambda-shuttle-master.png').convert('RGBA'),np.float32)
        asset[:,:,3]/=255;asset[:,:,:3]*=asset[:,:,3,None]
        self.ship_sprites={}
        for width in [43,34]:
            hh=round(width*asset.shape[0]/asset.shape[1])
            rgba=cv2.resize(asset,(width,hh),interpolation=cv2.INTER_AREA)
            self.ship_sprites[(width,False)]=rgba
            self.ship_sprites[(width,True)]=rgba[:,::-1].copy()
        self.cannon_strip_masks=[]
        for a,b in self.g['cannon_strips']:
            m=np.zeros((HEIGHT,W),np.uint8);cv2.line(m,point(*a),point(*b),255,1,cv2.LINE_AA)
            self.cannon_strip_masks.append(m.astype(np.float32)/255)
        self.wind_events=json.loads((H/'events.json').read_text(encoding='utf-8'))['wind']
        # Small ROI used for source-derived cloud transport; samples and destinations both exclude geometry.
        ys,xs=np.where(self.sky>0);self.skyroi=(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)
        self.full_active=np.maximum.reduce([self.glass,self.radar,self.readout,self.lamp,self.spill]+[m for _,m in self.windows]+[m for _,m in self.buttons]+self.keys)
        # Coffee steam is the only animation above the mug.
        self.steamroi=(point(260,490)[0],point(260,490)[1],point(338,604)[0],point(338,604)[1])
        a,b,c,d=self.steamroi;self.full_active[b:d,a:c]=1
        self.rois={}
        for m in [self.glass,self.radar,self.readout,self.lamp,self.spill,self.valley,self.ledge,self.bridgeglass]+[m for _,m in self.windows]+[m for _,m in self.buttons]+self.keys+[m for _,m in self.scans]+[m for m,_,_ in self.fog]+self.bridge_lamps+self.cannon_strip_masks:
            yy,xx=np.where(m>0);self.rois[id(m)]=(int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1)

    def poly(self,pts,feather=1):
        mask=np.zeros((HEIGHT,W),np.uint8)
        cv2.fillPoly(mask,[np.rint(np.array(pts)*S).astype(np.int32)],1)
        if feather:return smooth(cv2.distanceTransform(mask,cv2.DIST_L2,5)/(feather*S[0])).astype(np.float32)
        return mask.astype(np.float32)

    def texture(self,seed):
        # Integer Fourier modes form a torus: wrapping has no discontinuous row/column.
        rng=np.random.default_rng(seed);yy,xx=np.mgrid[:128,:256].astype(np.float32)
        noise=np.zeros((128,256),np.float32)
        for i in range(32):
            kx=int(rng.integers(1,7));ky=int(rng.integers(0,5))
            amp=1.0/(1+kx*kx+ky*ky)
            noise+=amp*np.cos(2*np.pi*(xx*kx/256+yy*ky/128)+rng.uniform(0,2*np.pi))
        return np.clip(.5+noise*.6,0,1).astype(np.float32)

    def blend(self,f,color,alpha):
        f[:]=f*(1-alpha[...,None])+np.asarray(color,np.float32)*alpha[...,None]

    def tint_mask(self,f,color,mask,amount):
        a,b,z,d=self.rois[id(mask)];self.blend(f[b:d,a:z],color,mask[b:d,a:z]*amount)

    def dim_mask(self,f,mask,amount):
        a,b,z,d=self.rois[id(mask)];f[b:d,a:z]*=1-mask[b:d,a:z,None]*amount

    def gust(self,t):
        return max([0.0]+[pulse(t,e['start'],e['end'],e['rise'],e['fall']) for e in self.wind_events])

    def foglayer(self,f,mask,texture,t,scale,speed,opacity,color):
        x0,y0,x1,y1=self.rois[id(mask)]
        mx=(self.x[y0:y1,x0:x1]/scale[0]*256-speed*t).astype(np.float32)
        my=(self.y[y0:y1,x0:x1]/scale[1]*128+3*np.sin(t/19)).astype(np.float32)
        density=cv2.remap(texture,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
        a=mask[y0:y1,x0:x1]*density*opacity
        self.blend(f[y0:y1,x0:x1],color,a)

    def plume(self,f,t,anchor,height,width,drift,opacity,phase=0):
        ax,ay=point(*anchor);hh=height*S[1];ww=width*S[0];dd=drift*S[0]
        x0=max(0,int(ax-ww*3-abs(dd)));x1=min(W,int(ax+ww*3+abs(dd)))
        y0=max(0,int(ay-hh));y1=min(HEIGHT,ay+1)
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32);u=(ay-yy)/hh
        center=ax+dd*u+np.sin(u*8-t*.8+phase)*u*ww*.45
        shape=np.exp(-.5*((xx-center)/(1.2+ww*u))**2)
        flow=.62+.25*np.sin(u*15-t*1.4+phase)+.13*np.sin(u*27-t*2.3)
        a=shape*flow*smooth(u/.08)*smooth((1-u)/.45)*opacity
        a*=self.glass[y0:y1,x0:x1]
        self.blend(f[y0:y1,x0:x1],[205,222,235],a)

    def interior(self,f,t):
        for i,(wc,m) in enumerate(self.windows):
            age=(t-i*7.2)%37;dip=pulse(age,2,11,2.3,3)*(.32 if i<4 else .18)
            self.dim_mask(f,m,dip)
        for i,(c,m) in enumerate(self.buttons):
            # Re-light the original lens; no solid colour fill and no invented switches.
            level=.38+.62*pulse((t-c['phase'])%19,0,10,1.2,1.8)
            if i==1:level=max(level,pulse(t,24.5,32,.3,1)*(.8+.2*np.sin(t*4)**2))
            self.dim_mask(f,m,1-level)
        for i,m in enumerate(self.keys):self.dim_mask(f,m,.64*pulse((t-i*.9)%17,0,3.2,.6,1.1))
        for i,m in enumerate(self.bridge_lamps):self.dim_mask(f,m,.45*pulse((t-i*3.1)%43,0,6,1.7,2.4))
        # Readout bars change inside original screen geometry.
        for i,(x0,x1,y0,y1) in enumerate([(44,62,471,522),(65,82,471,520),(91,105,471,521),(44,61,528,564),(91,97,526,561),(106,122,525,558)]):
            a,b=point(x0,y0);c,d=point(x1,y1)
            level=.35+.6*(.5+.5*np.sin(t/(2.7+i*.65)+i))
            m=self.readout[b:d,a:c]
            yy=np.arange(d-b)[:,None]/max(1,d-b)
            amount=.13+.74*smooth((1-level-yy)*14)
            f[b:d,a:c]*=1-(m*amount)[...,None]
        # A visible tapered radar sweep and slowly moving contacts.
        x0,y0=point(50,255);x1,y1=point(185,399)
        xx=self.x[y0:y1,x0:x1];yy=self.y[y0:y1,x0:x1]
        cx,cy=np.array([119,330])*S;angle=np.arctan2((yy-cy)/.96,xx-cx)
        delta=(angle-t*2*np.pi/12)%(2*np.pi);radius=np.hypot(xx-cx,(yy-cy)/.96)
        m=self.radar[y0:y1,x0:x1]
        a=m*np.exp(-delta/.40)*smooth((65*S[0]-radius)/(7*S[0]))*.40
        self.blend(f[y0:y1,x0:x1],[89,207,239],a)
        for i in range(4):
            theta=i*1.7+t/(50+i*20);rr=(25+i*6)*S[0]
            bx=cx+rr*np.cos(theta);by=cy+rr*np.sin(theta)
            amp=.22+.55*(.5+.5*np.sin(t*1.1+i))
            aa=np.exp(-((xx-bx)**2+(yy-by)**2)/(2*(1.15*S[0])**2))*m*amp
            self.blend(f[y0:y1,x0:x1],[151,234,246],aa)
        for i,(c,m) in enumerate(self.scans):
            a,b,z,d=self.rois[id(m)]
            scan=.3+.7*(.5+.5*np.sin(self.y[b:d,a:z]*1.4-t*(1+i*.23)))
            self.blend(f[b:d,a:z],c['color'],m[b:d,a:z]*scan*.5)
        lampdip=.055*(.5+.5*np.sin(t/10.7))+.08*pulse(t,69,76,1.8,2.5)
        self.dim_mask(f,self.lamp,lampdip);self.dim_mask(f,self.spill,lampdip)
        # Steam follows the mug rim, spreading gradually upwards.
        a,b,z,d=self.steamroi;xx=self.x[b:d,a:z];yy=self.y[b:d,a:z]
        ax,ay=np.array([289,596])*S;u=(ay-yy)/(100*S[1]);valid=(u>0)&(u<1)
        center=ax+14*S[0]*u+u*S[0]*(5*np.sin(u*8-t*1.4)+3*np.sin(u*13-t*.9))
        steam=np.exp(-.5*((xx-center)/(1+4*S[0]*np.maximum(u,0)))**2)
        alpha=steam*(.65+.35*np.sin(u*19-t*1.8))*smooth(u/.1)*smooth((1-u)/.5)*valid*.25
        self.blend(f[b:d,a:z],[198,192,179],alpha)

    def traffic(self,f,t):
        # Tiny figures inside the glazed bridge: structural mask occludes their motion.
        people=np.zeros((HEIGHT,W),np.float32)
        for start,end,xa,xb,phase in [(7,69,807,1388,0),(75,119,1375,986,2)]:
            if start<t<end:
                q=(t-start)/(end-start);x=xa+(xb-xa)*q;y=421+2*np.sin(q*np.pi)
                px,py=point(x,y);fade=pulse(t,start,end,2,2)
                head=point(x,y-13);cv2.circle(people,head,2,fade,-1,cv2.LINE_AA)
                cv2.line(people,point(x,y-10),point(x,y-3),fade,3,cv2.LINE_AA)
                stride=2*np.sin(t*4.5+phase)
                cv2.line(people,point(x,y-3),point(x-2-stride,y),fade,1,cv2.LINE_AA)
                cv2.line(people,point(x,y-3),point(x+2+stride,y),fade,1,cv2.LINE_AA)
        a,b,z,d=self.rois[id(self.bridgeglass)]
        self.blend(f[b:d,a:z],[40,52,62],people[b:d,a:z]*self.bridgeglass[b:d,a:z]*.64)
        self.shuttle_pass(f,t,24,62,False,43)
        self.shuttle_pass(f,t,86,114,True,34)

    def shuttle_pass(self,f,t,start,end,reverse,width):
        if not start<t<end:return
        q=(t-start)/(end-start);u=1-q if reverse else q
        x=925+465*u;y=186-30*u-9*np.sin(q*np.pi)
        sprite=self.ship_sprites[(width,reverse)]
        hh,ww=sprite.shape[:2];cx,cy=np.array([x,y])*S
        left=cx-ww/2;top=cy-hh/2;x0=int(np.floor(left))-2;y0=int(np.floor(top))-2
        transform=np.float32([[1,0,left-np.floor(left)+2],[0,1,top-np.floor(top)+2]])
        rgba=cv2.warpAffine(sprite,transform,(ww+4,hh+4),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        opacity=pulse(t,start,end,4,5)*.93
        mask=self.flight_mask[y0:y0+hh+4,x0:x0+ww+4]
        alpha=rgba[:,:,3]*opacity*mask
        rgb=rgba[:,:,:3]*.80+np.float32([151,173,192])*rgba[:,:,3,None]*.20
        f[y0:y0+hh+4,x0:x0+ww+4]=f[y0:y0+hh+4,x0:x0+ww+4]*(1-alpha[:,:,None])+rgb*(opacity*mask[:,:,None])

    def hardware(self,f,t):
        charge=max([0.0]+[float(smooth((t-a)/10)*smooth((b-t)/4)) for a,b in self.g['charge_cycles']])
        # Recessed barrel strips and small original-geometry power nodes charge slowly.
        for i,m in enumerate(self.cannon_strip_masks):
            self.tint_mask(f,[113,207,236],m,charge*(.48+.10*np.sin(t*1.8+i)**2))
        for i,(x,y) in enumerate(self.g['cannon_nodes']):
            level=charge*(.35+.65*smooth((charge-i*.16)/.36))
            self.light(f,x,y,[245,139,50],level*.72,1.05,3)
        for x,y in self.g['cannon_muzzles']:
            self.light(f,x,y,[157,224,248],charge*.9,.85,5)
        # Lights are attached to the actual feed mast, tower joint and roof sensor.
        for c in self.g['beacons']:
            age=(t+c['phase'])%c['period']
            level=pulse(age,0,.75,.15,.28)*c['peak']
            self.light(f,*c['xy'],c['color'],level,.8,3.5)

    def light(self,f,x,y,color,level,core,glow):
        if level<=0:return
        cx,cy=np.array([x,y])*S;radius=int(np.ceil(glow*S[0]*3))
        x0=max(0,int(cx)-radius);x1=min(W,int(cx)+radius+2);y0=max(0,int(cy)-radius);y1=min(HEIGHT,int(cy)+radius+2)
        xx=self.x[y0:y1,x0:x1];yy=self.y[y0:y1,x0:x1];r2=(xx-cx)**2+(yy-cy)**2
        a=(.82*np.exp(-r2/(2*(core*S[0])**2))+.08*np.exp(-r2/(2*(glow*S[0])**2)))*level
        self.blend(f[y0:y1,x0:x1],color,a)

    def sky_layer(self,f,t):
        a,b,z,d=self.skyroi;xx=self.x[b:d,a:z];yy=self.y[b:d,a:z]
        moving=np.zeros((d-b,z-a,3),np.float32);weights=np.zeros((d-b,z-a),np.float32)
        for phase in [0,.5]:
            age=(t/95+phase)%1;weight=np.sin(np.pi*age)**4
            mx=(xx-(age-.5)*150*S[0]).astype(np.float32)
            valid=cv2.remap(self.skyvalid,mx,yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
            weightmap=smooth((valid-.999)/.001)*weight
            moved=cv2.remap(self.base,mx,yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
            moving+=moved*weightmap[...,None];weights+=weightmap
        moving/=np.maximum(weights[...,None],1e-6)
        alpha=self.sky[b:d,a:z]*smooth(weights/.15)*.95
        f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+moving*alpha[...,None]
        return f

    def frame(self,t):
        f=self.base.astype(np.float32);gust=self.gust(t)
        self.interior(f,t)
        self.sky_layer(f,t)
        # A soft cloud shadow changes exterior contrast with the gust, not the cabin.
        shade=(.015+.045*gust)*(.5+.5*np.sin(t/18+self.x/W*2))
        f*=1-(self.glass*shade)[...,None]
        for mask,tex,i in self.fog:
            self.foglayer(f,mask,tex,t,[380,140 if i<2 else 45],1.6+i*.7,(.19+.22*gust)*(1 if i<2 else .7),[197,218,234])
        self.foglayer(f,self.valley,self.valleytex,t,[440,210],1.2,.22+.30*gust,[192,215,233])
        self.foglayer(f,self.ledge,self.ledgetex,t,[245,46],4.4,.08+.34*gust,[229,238,246])
        self.plume(f,t,[489,224],62,12,22+15*gust,.17,0)
        self.plume(f,t,[616,286],57,10,25+18*gust,.18,2)
        self.traffic(f,t)
        # Snow travels continuously; density and streak length follow the wind envelope.
        snow=np.zeros((HEIGHT,W),np.uint8)
        displacement=t*1.08+2.2*np.sin(t/13)
        for sx,sy,vx,vy,r,opacity,phase in self.flakes:
            x=(sx+vx*S[0]*displacement+8*np.sin(t/7+phase))%(W+80)-40
            y=(sy+vy*S[1]*t+4*np.sin(t/5+phase))%(HEIGHT+50)-25
            amount=opacity*(.35+.65*gust)
            fade=float(smooth((x-275)/35)*smooth((1250-x)/30)*smooth((y+5)/25)*smooth((570-y)/35))
            value=int(255*amount*fade)
            if value<2 or y<0 or y>=HEIGHT or x<0 or x>=W:continue
            trail=(1+gust*4)*(r/.8)
            cv2.line(snow,(round(x),round(y)),(round(x-trail),round(y-trail*.28)),value,1 if r<1.1 else 2,cv2.LINE_AA)
        snow=cv2.GaussianBlur(snow,(3,3),.45).astype(np.float32)/255
        self.blend(f,[231,241,249],snow*self.glass)
        self.hardware(f,t)
        out=np.uint8(np.rint(np.clip(f,0,255)))
        assert np.isfinite(f).all()
        return out

def encode_segment(index):
    scene=Scene();start=index*20;out=H/'cache'/f'part-{index:02}.mp4'
    if out.exists():raise RuntimeError('Preserve existing segment '+str(out))
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','pipe:0','-an','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-preset','veryfast','-qp','0','-threads','2','-g','60','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);started=time.time()
    try:
        for i in range(600):proc.stdin.write(scene.frame(start+i/FPS).tobytes())
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('Encoder failed')
    return {'part':index,'seconds_to_render':round(time.time()-started,2),'sha256':digest(out)}

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['samples','render']);args=p.parse_args()
    (H/'cache').mkdir(exist_ok=True)
    if args.stage=='samples':
        scene=Scene();started=time.time()
        for t in [0,18,35,48,72,96,119]:Image.fromarray(scene.frame(t)).save(H/f'sample-{t:03}.png')
        grid=Image.new('RGB',(1280,720))
        for i,t in enumerate([0,35,48,96]):
            im=Image.open(H/f'sample-{t:03}.png').resize((640,360));grid.paste(im,((i%2)*640,(i//2)*360))
        grid.save(H/'temporal-contact-sheet.jpg',quality=94)
        print('Sample frame average seconds',round((time.time()-started)/7,3),flush=True)
        return
    results=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(encode_segment,i) for i in range(6)]):
            result=future.result();results.append(result);print(json.dumps(result),flush=True)
    save('render-results.json',results)

if __name__=='__main__':main()
