"""Source-space local animation helpers shared by the two first-draft scenes."""
from pathlib import Path
import hashlib, json, math, subprocess, time
import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image

cv2.setNumThreads(1)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def smooth(x):
    v=np.clip(x,0,1);return v*v*(3-2*v)

def roi_slice(roi):
    a,b,c,d=roi;return np.s_[b:d,a:c]

def polygon_mask(roi,polygons,feather=2,inset=0):
    a,b,c,d=roi;m=np.zeros((d-b,c-a),np.uint8)
    for p in polygons:cv2.fillPoly(m,[np.rint(np.float32(p)-[a,b]).astype(np.int32)],1)
    dist=cv2.distanceTransform(np.pad(m,1),cv2.DIST_L2,5)[1:-1,1:-1]
    return smooth((dist-inset)/max(feather,.1)).astype(np.float32)

def grid(roi,step=1):
    a,b,c,d=roi;return np.mgrid[b:d:step,a:c:step].astype(np.float32)

def envelope(t,start,rise,hold,fall,period=60):
    age=(t-start)%period;return float(smooth(age/rise)*smooth((rise+hold+fall-age)/fall))

def rgb_linear(x):
    v=x/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)

def linear_rgb(v):
    v=np.maximum(v,0);return 255*np.where(v<=.0031308,v*12.92,1.055*v**(1/2.4)-.055)

def ellipse(roi,center,radius,cutoff=.001):
    y,x=grid(roi);cx,cy=center;rx,ry=radius;m=np.exp(-.5*(((x-cx)/rx)**2+((y-cy)/ry)**2));m[m<cutoff]=0;return m

class Sheet:
    """Toroidal low-pass noise; explicit coordinate wrapping closes forward transport."""
    def __init__(self,roi,seed=1,speed=-5,scale_y=60,period=60,step=2):
        self.roi=roi;self.step=step;self.speed=speed;self.period=period
        self.y,self.x=grid(roi,step);self.scale_y=scale_y
        rng=np.random.default_rng(seed);n=rng.normal(size=(64,64))
        ky,kx=np.meshgrid(np.fft.fftfreq(64),np.fft.fftfreq(64),indexing='ij')
        f=np.fft.ifft2(np.fft.fft2(n)*np.exp(-(kx*kx+ky*ky)*160)).real
        f=(f-f.min())/(f.max()-f.min());self.field=f.astype(np.float32)
    def at(self,t):
        tile=abs(self.speed)*self.period if self.speed else 120
        u=((self.x-self.speed*t)*64/tile)%64;v=(self.y*64/self.scale_y)%64
        f=cv2.remap(self.field,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
        a,b,c,d=self.roi;return cv2.resize(f,(c-a,d-b),interpolation=cv2.INTER_LINEAR)

class Clouds:
    def __init__(self,base,roi,polygons,speed=-3,period=60,feather=8):
        self.roi=roi;self.src=base[roi_slice(roi)].astype(np.float32);self.period=period;self.speed=speed
        self.safe=polygon_mask(roi,polygons,.1,0)>.99;self.mask=polygon_mask(roi,polygons,feather,3)
        self.y,self.x=np.indices(self.safe.shape,dtype=np.float32)
        xx=np.arange(self.safe.shape[1])[None,:]
        l=np.maximum.accumulate(np.where(self.safe,-1,xx),axis=1)
        r=np.minimum.accumulate(np.where(self.safe,self.safe.shape[1],xx)[:,::-1],axis=1)[:,::-1]
        self.taper=smooth(np.minimum(xx-l,r-xx)/max(abs(speed)*period*2,180)).astype(np.float32)
    def maps(self,t):
        for phase in [0,19,41]:
            age=(t+phase)%self.period;w=math.sin(math.pi*age/self.period)**8
            yield (self.x-self.taper*self.speed*(age-self.period/2)).astype(np.float32),w
    def apply(self,f,t):
        value=np.zeros_like(self.src);total=0
        for mx,w in self.maps(t):
            if w<1e-12:continue
            value+=cv2.remap(self.src,mx,self.y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)*w;total+=w
        r=roi_slice(self.roi);f[r]+=(value/max(total,1e-9)-self.src)*self.mask[...,None]
    def audit(self,t):
        active=self.mask>0;yy=self.y[active].astype(int);minimum=1
        for mx,w in self.maps(t):
            if w<1e-12:continue
            x=mx[active];l=np.floor(x).astype(int);r=np.ceil(x).astype(int)
            assert l.min()>=0 and r.max()<self.safe.shape[1]
            assert np.all(self.safe[yy,l]) and np.all(self.safe[yy,r])
            good=active[:,:-1]&active[:,1:];minimum=min(minimum,float(np.diff(mx,axis=1)[good].min()))
        assert minimum>.25;return minimum

class Vapour:
    def __init__(self,roi,anchor,seed=1,rise=8,drift=-.6,life=10,interval=.5,strength=.035,color=(205,207,203),period=60):
        self.roi=roi;self.y,self.x=grid(roi);self.anchor=anchor;self.rise=rise;self.drift=drift;self.life=life;self.interval=interval;self.strength=strength;self.color=np.float32(color);self.period=period
        self.variants=np.random.default_rng(seed).uniform(.75,1.25,(round(period/interval),4));self.mask=np.ones(self.y.shape,np.float32)
    def field(self,t):
        tau=np.zeros_like(self.x);latest=int(math.floor(t/self.interval))
        for born in range(latest-math.ceil(self.life/self.interval),latest+1):
            age=t-born*self.interval
            if age<=0 or age>=self.life:continue
            v=self.variants[born%len(self.variants)];fade=smooth(age/.7)*smooth((self.life-age)/(self.life*.32))
            x=self.anchor[0]+self.drift*age+math.sin(age*.8+v[1]*3)*min(age,2)*.7;y=self.anchor[1]-self.rise*age
            dx=(self.x-x)/(.85+age*.72*v[2]);dy=(self.y-y)/(1.4+age*.85*v[3])
            texture=.8+.14*np.sin(dx*2.3+dy*1.7+v[0]*4)+.06*np.sin(dx*5-dy*3)
            tau+=np.exp(-.5*(dx*dx+dy*dy))*texture*fade*v[0]*self.strength
        alpha=np.minimum(-np.expm1(-tau),.32)*self.mask
        return alpha
    def apply(self,f,t,gain=1):
        alpha=self.field(t)*gain;r=roi_slice(self.roi);f[r]+=(self.color-f[r])*alpha[...,None]

class Element:
    """Original source pixels over a generated clean background, locally displaced."""
    def __init__(self,base,clean,roi,mask,anchor,kind='rotate',amount=.8,phase=0):
        self.roi=roi;self.mask=mask;self.anchor=anchor;self.kind=kind;self.amount=amount;self.phase=phase
        self.src=base[roi_slice(roi)].astype(np.float32);self.clean=clean[roi_slice(roi)].astype(np.float32)
        self.y,self.x=np.indices(mask.shape,dtype=np.float32)
        expanded=cv2.dilate(np.uint8(mask>.001),np.ones((7,7),np.uint8)).astype(np.float32)
        self.allowed=expanded
    def apply(self,f,t,wind=1):
        a,b,c,d=self.roi;r=roi_slice(self.roi)
        patch=f[r];patch+=(self.clean-patch)*self.mask[...,None]
        phase=2*math.pi*t/60
        if self.kind=='rotate':
            angle=self.amount*(math.sin(phase*3+self.phase)+.28*math.sin(phase*7+self.phase))*wind
            matrix=cv2.getRotationMatrix2D((self.anchor[0]-a,self.anchor[1]-b),angle,1)
            premul=cv2.warpAffine(self.src*self.mask[...,None],matrix,(c-a,d-b),flags=cv2.INTER_LINEAR)
            alpha=cv2.warpAffine(self.mask,matrix,(c-a,d-b),flags=cv2.INTER_LINEAR)
        else:
            ay=self.anchor[1]-b;height=max(1,ay-float(np.where(self.mask>0)[0].min()))
            bend=np.clip((ay-self.y)/height,0,1)
            if self.kind=='wire':bend=np.sin(np.pi*np.clip(self.y/max(1,d-b-1),0,1));value=self.amount*math.sin(phase*77+self.phase)*wind
            else:value=self.amount*math.sin(phase*3+self.phase)*wind
            mx=(self.x-bend*value).astype(np.float32)
            premul=cv2.remap(self.src*self.mask[...,None],mx,self.y,cv2.INTER_LINEAR);alpha=cv2.remap(self.mask,mx,self.y,cv2.INTER_LINEAR)
        patch*=1-alpha[...,None];patch+=premul

def add_rgba(f,rgba,x,y,opacity=1,clip=None):
    h,w=rgba.shape[:2];a=max(0,int(round(x)));b=max(0,int(round(y)));c=min(f.shape[1],int(round(x))+w);d=min(f.shape[0],int(round(y))+h)
    if c<=a or d<=b:return
    sx=a-int(round(x));sy=b-int(round(y));v=rgba[sy:sy+d-b,sx:sx+c-a].astype(np.float32)
    alpha=v[...,3]/255*opacity
    if clip is not None:alpha*=clip[b:d,a:c]
    f[b:d,a:c]*=1-alpha[...,None];f[b:d,a:c]+=v[...,:3]*alpha[...,None]

def sprite_canvas(width,height):return np.zeros((height,width,4),np.uint8)

def scaled_rgba(canvas,size):
    value=canvas.astype(np.float32);a=value[...,3]/255;rgb=value[...,:3]*a[...,None]
    alpha=cv2.resize(a,size,interpolation=cv2.INTER_AREA);premul=cv2.resize(rgb,size,interpolation=cv2.INTER_AREA)
    out=np.zeros((*alpha.shape,4),np.float32);out[...,:3]=premul/np.maximum(alpha[...,None],1e-7);out[...,3]=alpha*255
    return np.uint8(np.clip(np.rint(out),0,255))

class SceneBase:
    def register(self,name,roi,mask):
        self.regions[name]=roi;self.masks[name]=mask
        self.allowed[roi_slice(roi)]|=mask>0
    def finish(self,f):return np.uint8(np.clip(np.rint(f),0,255))
    def input_hashes(self):
        paths=[self.source_path,self.config_path,Path(__file__),self.renderer_path,*self.extra_inputs]
        return {p.relative_to(self.root).as_posix():sha(p) for p in paths}

def encode(scene,target,seconds=60,start=0,only=None):
    target=Path(target);assert not target.exists(),target;partial=target.with_suffix('.partial.mp4')
    fps=scene.fps;w,h=1280,720
    args=[FFMPEG,'-v','error','-n','-f','rawvideo','-pixel_format','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-an','-vf','scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-qp','0','-preset','veryfast','-threads','4','-g',str(fps*5),'-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-movflags','+faststart',str(partial)]
    protected=~scene.allowed;ref=scene.base[protected];begin=time.monotonic()
    with subprocess.Popen(args,stdin=subprocess.PIPE) as process:
        try:
            for index in range(round(seconds*fps)):
                frame=scene.frame(start+index/fps,only=only)
                assert np.array_equal(frame[protected],ref),(target.name,index,'protected pixels')
                process.stdin.write(cv2.resize(frame,(w,h),interpolation=cv2.INTER_AREA).tobytes())
                if index%(fps*5)==0:print(f'{target.name}: {index/fps:.0f}/{seconds}s ({time.monotonic()-begin:.1f}s)',flush=True)
        finally:process.stdin.close()
        assert process.wait()==0
    partial.rename(target)

def save_samples(scene,folder,times):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    colours=[(255,100,75),(85,205,255),(120,245,165),(230,180,80)]
    overlay=scene.base.astype(np.float32)
    for i,(name,m) in enumerate(scene.masks.items()):
        r=roi_slice(scene.regions[name]);overlay[r]+=(np.float32(colours[i%4])-overlay[r])*np.clip(m,0,1)[...,None]*.33
    Image.fromarray(np.uint8(np.clip(overlay,0,255))).save(folder/'mask-overlay.png')
    for t in times:Image.fromarray(cv2.resize(scene.frame(t),(1280,720),interpolation=cv2.INTER_AREA)).save(folder/f'combined-{t:05.2f}s.png')
