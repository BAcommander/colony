"""Source-bound Crimson Sky compositor. No generated video or moving solid geometry."""
from pathlib import Path
import argparse, json, hashlib, sys, subprocess, time
import cv2
import numpy as np
from PIL import Image, ImageOps

H=Path(__file__).resolve().parent
R=H.parents[1]
sys.path.insert(0,str(H/'dependencies'))
from ambient_effects import smoothstep, event_amount
from periodic_transport import PeriodicDust
cv2.setNumThreads(4)

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def byte(f): return np.uint8(np.rint(np.clip(f,0,255)))
def save(name,data): (H/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

class Crimson:
    def __init__(self):
        self.path=H/'scene-plan-v1.json';self.config=json.loads(self.path.read_text())
        c=self.config;source=R/c['source']['path'];assert digest(source)==c['source']['sha256']
        self.base=np.array(Image.open(source).convert('RGB'));self.h,self.w=self.base.shape[:2]
        assert [self.w,self.h]==c['source']['dimensions'];self.duration=c['duration']
        self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32);self.masks={}
        self.prepare_sky();self.prepare_dust();self.prepare_lights()
        self.layer_masks={k:m>0 for k,m in self.masks.items()}
        self.layer_masks['dust']=self.layer_masks['far_dust']|self.layer_masks['middle_dust']
        self.layer_masks['habitation']=np.logical_or.reduce([m for n,m in self.layer_masks.items() if n.startswith('light_') or n=='lantern'])
        self.active=np.logical_or.reduce(list(self.layer_masks.values()))
    def poly(self,polys,feather=2,inset=0):
        scale=3;m=np.zeros((self.h*scale,self.w*scale),np.uint8)
        for points in polys:cv2.fillPoly(m,[np.rint(np.float32(points)*scale).astype(np.int32)],255)
        d=cv2.distanceTransform(m,cv2.DIST_L2,5)/scale
        return cv2.resize(smoothstep((d-inset)/feather),(self.w,self.h),interpolation=cv2.INTER_AREA).astype(np.float32)
    def crop(self,m):
        ys,xs=np.where(m>0);a,b,z,d=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
        return (a,b,z,d),m[b:d,a:z].copy()
    def prepare_sky(self):
        c=self.config['sky']
        # Both the destination and every reachable source sample must be clear
        # of masonry, roof, world and the luminous opening. No inpainted sky.
        valid=np.uint8(self.poly([c['polygon']],1,c['source_inset'])>.99)
        opening=self.poly([c['clear_opening']],1)
        valid[opening>0]=0
        max_shift=int(np.ceil(max(c['upper_speed'],c['horizon_speed'])*30))+2
        # Mirror only the outer image boundary; scene silhouettes are never filled.
        reachable=cv2.erode(valid,np.ones((1,2*max_shift+1),np.uint8),borderType=cv2.BORDER_REFLECT_101)
        distance=cv2.distanceTransform(reachable,cv2.DIST_L2,5)
        m=smoothstep(distance/c['transport_feather']);m[m<.002]=0
        self.masks['sky_clouds']=m
        (a,b,z,d),self.sky_mask=self.crop(m);self.sky_roi=(a,b,z,d)
        self.sky_source=self.base[:d].astype(np.float32)
        self.sky_x=self.x[b:d,a:z].copy();self.sky_y=self.y[b:d,a:z].copy()
        h=smoothstep((self.sky_y-c['depth_transition'][0])/(c['depth_transition'][1]-c['depth_transition'][0]))
        self.sky_speed=c['upper_speed']*(1-h)+c['horizon_speed']*h
        self.cloud_source_support=valid
        # Quantify that no shifted sample can contain an excluded silhouette.
        assert np.all(reachable[m>0]>0)
    def sky(self,f,t):
        a,b,z,d=self.sky_roi
        transported=np.zeros((d-b,z-a,3),np.float32)
        # Two locally renewed cloud-texture fields, both travelling right.
        # sin-squared weights vanish with zero slope at their hidden reset.
        # These are sky-only fields, never a full-scene dissolve or reverse.
        for phase in (0.,30.):
            age=(t+phase)%60
            weight=np.sin(np.pi*age/60)**2
            if weight<1e-12:continue
            shift=self.sky_speed*(age-30)
            field=cv2.remap(self.sky_source,self.sky_x-shift,self.sky_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
            transported+=field*weight
        original=self.base[b:d,a:z].astype(np.float32)
        f[b:d,a:z]+=(transported-original)*self.sky_mask[...,None]
    def prepare_dust(self):
        self.dust=[];blockers=self.poly(self.config['weather_blockers'],.8)
        for c in self.config['weather']:
            m=self.poly([c['polygon']],c['feather'])*(1-blockers);m[m<.002]=0
            roi,local=self.crop(m);a,b,z,d=roi
            cfg={k:c[k] for k in ['seed','speed','optical_depth','max_opacity','color']};cfg['lifetime']=60
            cfg['gusts']=[{'x':x,'y':y,'width':w,'height':h,'route_slope':slope,'strength':1,'phase':0} for x,y,w,h,slope,age in c['gusts']]
            cfg['loop_schedule']=[{'gust_index':i,'birth_x':x-c['speed']*age,'age_at_zero':age,'fade_in':8,'fade_out':8} for i,(x,y,w,h,slope,age) in enumerate(c['gusts'])]
            self.masks[c['name']]=m
            self.dust.append((c['name'],roi,local,PeriodicDust(self.x[b:d,a:z],self.y[b:d,a:z],cfg,60)))
    def glow(self,g):
        x,y,rx,ry=g[:4];r=((self.x-x)/rx)**2+((self.y-y)/ry)**2
        f=np.exp(-r*.5).astype(np.float32);f[r>9]=0
        return f
    def prepare_lights(self):
        src=self.base.astype(np.float32);lum=src.mean(2);warm=smoothstep((src[:,:,0]-src[:,:,2]-10)/60)
        self.lights=[]
        for c in self.config['lights']:
            core=self.poly(c['polygons'],.7)*smoothstep((lum-40)/65)
            spill=np.zeros((self.h,self.w),np.float32)
            for g in c['glows']:spill=np.maximum(spill,self.glow(g)*g[4]*warm)
            m=np.maximum(core,spill);m[m<.002]=0
            self.masks['light_'+c['name']]=m
            self.lights.append((c,*self.crop(m)))
        c=self.config['lantern'];core=self.poly([c['core_polygon']],.8)*smoothstep((lum-65)/80)
        wall=self.poly([c['wall_polygon']],12)*self.glow(c['wall_glow'])*warm*.45
        floor=self.poly([c['floor_polygon']],14)*self.glow(c['floor_glow'])*warm*.31
        m=np.maximum(core,np.maximum(wall,floor));m[m<.002]=0
        self.masks['lantern']=m;self.lantern=self.crop(m)
    def frame_float(self,t,only=None,forced_dim=False):
        t=float(t)%self.duration;f=self.base.astype(np.float32)
        if only in (None,'sky_clouds'):self.sky(f,t)
        for name,(a,b,z,d),mask,weather in self.dust:
            if only in (None,name,'dust'):
                alpha,color=weather.density(t);alpha*=mask
                f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+color*alpha[...,None]
        for c,(a,b,z,d),mask in self.lights:
            if only in (None,'habitation','light_'+c['name']):
                amount=.88 if forced_dim else max(float(event_amount(t,60,start,hold,ramp))*depth for start,hold,ramp,depth in c['events'])
                f[b:d,a:z]*=1-mask[...,None]*amount
        if only in (None,'habitation','lantern'):
            c=self.config['lantern'];a1,a2,a3=c['modulation'];phase=t*2*np.pi/60
            amount=a1*(1+np.sin(phase*7+.2))*.5+a2*(1+np.sin(phase*19+.8))*.5+a3*(1+np.sin(phase*31+2))*.5
            start,hold,ramp,depth=c['brief_dip'];amount+=float(event_amount(t,60,start,hold,ramp))*depth
            if forced_dim:amount=.75
            (a,b,z,d),mask=self.lantern;f[b:d,a:z]*=1-mask[...,None]*amount
        assert np.isfinite(f).all()
        return f
    def frame(self,t,only=None):
        f=byte(self.frame_float(t,only));m=self.active if only is None else self.layer_masks[only]
        assert np.array_equal(f[~m],self.base[~m]),'Protected source pixels changed'
        return f
    def fingerprint(self):
        paths=[self.path,Path(__file__),H/'build_plan.py',H/'source-v11.png',*sorted((H/'dependencies').glob('*.py'))]
        return {'files':{p.relative_to(R).as_posix():digest(p) for p in paths},'masks':{k:hashlib.sha256(m.tobytes()).hexdigest() for k,m in self.masks.items()},'numpy':np.__version__,'opencv':cv2.__version__}

def fit_frame(frame,size):
    # The source loses only 0.25 native px at the top and bottom for exact 16:9.
    return np.array(ImageOps.fit(Image.fromarray(frame),tuple(size),Image.Resampling.LANCZOS))

def encode(s,path,seconds,only=None):
    assert not path.exists(),str(path)
    fps=s.config['fps'];w,h=s.config['preview_size'];count=round(seconds*fps)
    cmd=[s.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-vf','scale=out_color_matrix=bt709:out_range=tv','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
    try:
        for i in range(count):
            f=fit_frame(s.frame(i/fps,only),(w,h));proc.stdin.write(f.tobytes())
            if i and i%150==0:print(path.name,i,'/',count,'elapsed',round(time.time()-start,1),flush=True)
    finally:proc.stdin.close()
    assert proc.wait()==0
    return {'path':path.relative_to(R).as_posix(),'sha256':digest(path),'frames':count,'seconds':seconds,'layer':only or 'combined','silent':True}

def verify(s,path,expected,loop=False,save_samples=False):
    cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);assert fps==30
    # OpenCV's RGB conversion ignores BT.709 here; use it for timestamps only.
    # FFmpeg decodes the tagged colour correctly for all pixel/seam inspection.
    decoder=subprocess.Popen([s.config['ffmpeg'],'-v','error','-i',str(path),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    masks={n:np.uint8(fit_frame(np.repeat(m[:,:,None],3,axis=2).astype('uint8')*255,(1280,720))[:,:,0]>127) for n,m in {**s.layer_masks,'combined':s.active}.items()}
    first=prev=None;maximum={n:0. for n in masks};hashes=[];i=0
    while True:
        raw=decoder.stdout.read(720*1280*3)
        if not raw:break
        assert len(raw)==720*1280*3
        f=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
        assert cap.grab()
        assert abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/30)<.0001
        hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
        if first is None:first=f.copy()
        else:
            diff=cv2.absdiff(f,prev)
            for n,m in masks.items():maximum[n]=max(maximum[n],sum(cv2.mean(diff,mask=m)[:3])/3)
        if save_samples and i in (0,240,600,900,1200,1500,1710,1799):Image.fromarray(f).save(H/f'decoded-{i:04d}.png')
        prev=f;i+=1
    assert not cap.grab();cap.release();decoder.stdout.close();assert decoder.wait()==0
    assert i==expected,(i,expected);checks={}
    if loop:
        assert hashes[0]!=hashes[-1]
        diff=cv2.absdiff(prev,first)
        for n,m in masks.items():
            value=sum(cv2.mean(diff,mask=m)[:3])/3
            assert value<=maximum[n]*1.1+.01,(n,value,maximum[n])
            checks[n]={'seam_mae':value,'ordinary_max_mae':maximum[n],'pass':True}
    return {'frames':i,'fps':fps,'full_decode':True,'pixel_decoder':'FFmpeg RGB24 with stream colour metadata','timestamp_decoder':'OpenCV frame grab without RGB conversion','sequential_timestamps':True,'encoded_seam':checks},hashes

def samples(s):
    (H/'masks').mkdir(exist_ok=True)
    for name,m in s.masks.items():Image.fromarray(byte(m*255)).save(H/'masks'/f'{name}.png')
    for name,colors in [('weather-mask-overlay',[('sky_clouds',[50,170,255]),('far_dust',[255,170,60]),('middle_dust',[80,255,160])]),('light-mask-overlay',[(n,[80,255,120]) for n in s.masks if n.startswith('light_') or n=='lantern'])]:
        f=s.base.astype(np.float32)
        for n,col in colors:
            a=s.masks[n][...,None]*.65;f=f*(1-a)+np.float32(col)*a
        Image.fromarray(byte(f)).save(H/(name+'.png'))
    Image.fromarray(byte(s.frame_float(0,'habitation',True))).save(H/'forced-dim-lights.png')
    for t in [0,4,8,20,40,50,57,59.9666667]:Image.fromarray(fit_frame(s.frame(t),(1280,720))).save(H/f'sample-{t:06.2f}s.png')
    print('Saved masks, forced dim and temporal samples',flush=True)

def analytic(s):
    checks={};dt=1/30
    for name,m in s.layer_masks.items():
        assert np.array_equal(s.frame(0,name),s.frame(60,name)),name
        times=[-dt,0,3.1,8.2,14.1,20,23.3,30,40,47.5,50,58]
        vals=[float(abs(s.frame(t+dt,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in times]
        assert vals[0]<=max(vals[1:])*1.1+.01,(name,vals)
        eps=1/300
        left=(s.frame_float(0,name)-s.frame_float(-eps,name))[m]/eps
        right=(s.frame_float(eps,name)-s.frame_float(0,name))[m]/eps
        checks[name]={'periodic_state':True,'seam_mae':vals[0],'ordinary_sample_max':max(vals[1:]),'velocity_boundary_difference_mae':float(abs(left-right).mean()),'pass':True}
    for t in range(0,60,5):
        f=s.frame(t);assert np.array_equal(f[269:334,1127:1193],s.base[269:334,1127:1193])
    assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
    save('analytic-validation.json',{'fingerprint':s.fingerprint(),'checks':checks,'distinct_0_20_40':True,'world_and_opening_protected':True,'user_approved':False})
    print('Analytical periodicity and protection passed',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','analytic','isolated','preview'],required=True);p.add_argument('--layers',nargs='+');args=p.parse_args();s=Crimson()
    if args.stage=='samples':samples(s);return
    if args.stage=='analytic':analytic(s);return
    clips=[]
    if args.stage=='isolated':
        for layer in args.layers or ['sky_clouds','dust','habitation']:
            path=H/f'{layer}-v1-isolated-10s.mp4';item=encode(s,path,10,layer);item['validation'],_=verify(s,path,300);clips.append(item)
    else:
        path=H/'beneath-a-crimson-sky-v1-preview-60s.mp4';item=encode(s,path,60);item['validation'],hashes=verify(s,path,1800,True,True);clips.append(item)
        repeat=H/'beneath-a-crimson-sky-v1-three-loops-180s.mp4';assert not repeat.exists()
        subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
        validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
        clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
        save('decoded-frame-hashes.json',hashes)
    save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Source, masks and temporal/decoded stills; no continuous playback inspection claimed'})
    print(args.stage,'complete',flush=True)

if __name__=='__main__':main()
