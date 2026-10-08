"""V12 source-bound minute compositor; frozen v1 utilities, freshly mapped geometry."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time
import cv2
import numpy as np
from PIL import Image

H=Path(__file__).resolve().parent
R=H.parents[1]
sys.path.insert(0,str(H/'dependencies'))
import crimson_v1 as old
from ambient_effects import smoothstep, event_amount
old.H=H
old.R=R
byte,fit_frame,digest=old.byte,old.fit_frame,old.digest
cv2.setNumThreads(4)
def save(n,v): (H/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def linear(x):
    v=x/255.; return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def srgb(x):
    v=np.maximum(x,0);return 255*np.where(v<=.0031308,v*12.92,1.055*v**(1/2.4)-.055)

class Crimson(old.Crimson):
    def __init__(self):
        self.path=H/'scene-plan-v2.json';self.config=json.loads(self.path.read_text(encoding='utf-8'))
        c=self.config; source=R/c['source']['path'];assert digest(source)==c['source']['sha256']
        self.base=np.array(Image.open(source).convert('RGB')); self.h,self.w=self.base.shape[:2]
        assert [self.w,self.h]==c['source']['dimensions'];self.duration=c['duration']
        self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32);self.masks={}
        self.prepare_sky();self.prepare_dust();self.prepare_lights();self.prepare_events()
        self.layer_masks={k:m>0 for k,m in self.masks.items()}
        self.layer_masks['dust']=self.layer_masks['far_dust']|self.layer_masks['middle_dust']
        self.layer_masks['habitation']=np.logical_or.reduce([m for n,m in self.layer_masks.items() if n.startswith('light_') or n=='lantern'])
        self.layer_masks['storm_context']=self.layer_masks['sky_clouds']|self.layer_masks['storm']
        self.active=np.logical_or.reduce(list(self.layer_masks.values()))
        self.layer_masks['baseline']=self.active.copy()
        self.sky_phase=self.config['sky']['depth_phase_seconds']*smoothstep((self.sky_y-115)/285)
        self.original_sky=self.base[self.sky_roi[1]:self.sky_roi[3],self.sky_roi[0]:self.sky_roi[2]].astype(np.float32)
    def prepare_lights(self):
        super().prepare_lights()
        c=self.config['lantern'];src=self.base.astype(np.float32)
        warm=smoothstep((src[:,:,0]-src[:,:,2]-10)/60)
        objects=self.poly(c['object_polygons'],9)*self.glow(c['object_glow'])*warm*.20
        m=np.maximum(self.masks['lantern'],objects);m[m<.002]=0
        self.masks['lantern']=m;self.lantern=self.crop(m)
    def sky(self,f,t,baseline=False):
        a,b,z,d=self.sky_roi;transported=np.zeros_like(self.original_sky);total=np.zeros_like(self.sky_mask)
        c=self.config['sky'];phases=[0,30] if baseline else c['phase_offsets']
        for phase in phases:
            age=(t+phase+(0 if baseline else self.sky_phase))%60
            weight=np.sin(np.pi*age/60)**(2 if baseline else c['weight_power'])
            shift=self.sky_speed*(age-30)
            field=cv2.remap(self.sky_source,self.sky_x-shift,self.sky_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
            transported+=field*np.asarray(weight)[...,None];total+=weight
        transported/=np.maximum(total[...,None],1e-8)
        f[b:d,a:z]+=(transported-self.original_sky)*self.sky_mask[...,None]
    def prepare_events(self):
        self.storm_fields=[];union=np.zeros((self.h,self.w),np.float32)
        for e in self.config['storm']['events']:
            field=np.zeros_like(union)
            for g in e['centres']:field=np.maximum(field,self.glow(g)*g[4])
            field*=self.masks['sky_clouds'];field[field<.005]=0
            union=np.maximum(union,field);self.storm_fields.append((e,*self.crop(field)))
        self.masks['storm']=union
        c=self.config['red'];core=self.poly(c['core_polygons'],.85)
        # Two narrow existing pane interiors; leave the vertical stone divider fixed.
        divider=self.poly([[[605.2,359],[606.8,359],[606.8,384],[605.2,384]]],.3)
        core*=1-divider
        spill=self.poly([c['spill_polygon']],3)*self.glow(c['spill_glow'])*(1-core)*.80
        m=np.maximum(core,spill);m[m<.002]=0;self.masks['red_embers']=m
        (a,b,z,d),_=self.crop(m);self.red_roi=(a,b,z,d)
        # Source-derived shading retains the recessed pane detail instead of painting a flat red arch.
        texture=.26+.74*smoothstep((self.base[b:d,a:z].astype(np.float32).mean(2)-20)/45)
        self.red_emission=core[b:d,a:z,None]*texture[...,None]*np.float32(c['linear_core'])+spill[b:d,a:z,None]*np.float32(c['linear_spill'])
        self.red_emission[m[b:d,a:z]==0]=0
    @staticmethod
    def pulse(t,e):
        dt=(t-e['time']+30)%60-30
        # Compact, zero-slope endpoints, finite durations. Peak follows cue by rise.
        def one(v):return float(smoothstep(v/e['rise'])*smoothstep((e['rise']+e['decay']-v)/e['decay']))
        value=one(dt)
        if 'secondary' in e:value+=one(dt-e['secondary'][0])*e['secondary'][1]
        return value
    def storm(self,f,t):
        for e,(a,b,z,d),mask in self.storm_fields:
            strength=self.pulse(t,e)*e['strength']
            if strength<1e-10:continue
            region=f[b:d,a:z]
            # Density and internal detail follow the transported clouds, not fixed sky pixels.
            density=smoothstep((178-region[:,:,0])/80)
            density=cv2.GaussianBlur(density,(0,0),1.2)
            detail=cv2.GaussianBlur(region[:,:,0],(0,0),2)-cv2.GaussianBlur(region[:,:,0],(0,0),10)
            sculpt=np.clip(.64+detail/42,.18,1)
            amount=mask*density*sculpt*strength
            illumination=amount[...,None]*np.float32(self.config['storm']['linear_color'])
            transformed=srgb(linear(region)+illumination)
            f[b:d,a:z]=np.where((amount>0)[...,None],transformed,region)
    def red_amount(self,t):
        amount=0.
        for start,rise,hold,decay,strength in self.config['red']['events']:
            age=(t-start)%60
            value=float(smoothstep(age/rise)*smoothstep((rise+hold+decay-age)/decay))*strength
            amount=max(amount,value)
        return amount
    def frame_float(self,t,only=None,forced_dim=False):
        t=float(t)%60;f=self.base.astype(np.float32)
        if only in (None,'sky_clouds','baseline','storm_context'):self.sky(f,t,baseline=only=='baseline')
        for name,(a,b,z,d),mask,weather in self.dust:
            if only in (None,name,'dust','baseline'):
                alpha,color=weather.density(t);alpha*=mask
                f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+color*alpha[...,None]
        if only in (None,'storm','storm_context'):self.storm(f,t)
        for c,(a,b,z,d),mask in self.lights:
            if only in (None,'habitation','light_'+c['name'],'baseline'):
                amount=.88 if forced_dim else max(float(event_amount(t,60,start,hold,ramp))*depth for start,hold,ramp,depth in c['events'])
                f[b:d,a:z]*=1-mask[...,None]*amount
        if only in (None,'habitation','lantern','baseline'):
            c=self.config['lantern'];a1,a2,a3=c['modulation'];phase=t*2*np.pi/60
            amount=a1*(1+np.sin(phase*7+.2))*.5+a2*(1+np.sin(phase*19+.8))*.5+a3*(1+np.sin(phase*31+2))*.5
            start,hold,ramp,depth=c['brief_dip'];amount+=float(event_amount(t,60,start,hold,ramp))*depth
            if forced_dim:amount=.75
            (a,b,z,d),mask=self.lantern;f[b:d,a:z]*=1-mask[...,None]*amount
        if only in (None,'red_embers'):
            amount=self.red_amount(t)
            if amount>0:
                a,b,z,d=self.red_roi;region=f[b:d,a:z]
                changed=srgb(linear(region)+self.red_emission*amount)
                f[b:d,a:z]=np.where((self.red_emission.sum(2)>0)[...,None],changed,region)
        assert np.isfinite(f).all();return f
    def fingerprint(self):
        paths=[self.path,Path(__file__),H/'source-v12.png',H/'production-prompt.txt',*sorted((H/'dependencies').glob('*.py'))]
        return {'files':{p.relative_to(R).as_posix():digest(p) for p in paths},'masks':{k:hashlib.sha256(m.tobytes()).hexdigest() for k,m in self.masks.items()},'numpy':np.__version__,'opencv':cv2.__version__}

def samples(s):
    old.samples(s)
    for t in [8.52,21,33.37,39.35,48,56.31]:Image.fromarray(fit_frame(s.frame(t),(1280,720))).save(H/f'sample-{t:06.2f}s.png')
    for n in ['storm','red_embers']:
        f=s.base.astype(np.float32);a=s.masks[n][...,None]*.65
        Image.fromarray(byte(f*(1-a)+np.float32([250,35,160])*a)).save(H/f'{n}-mask-overlay.png')
    Image.fromarray(s.frame(21,'red_embers')[337:400,584:625]).resize((328,504)).save(H/'inspection/red-peak-crop.png')
    Image.fromarray(s.base[337:400,584:625]).resize((328,504)).save(H/'inspection/red-baseline-crop.png')

def analytic(s):
    dt=1/30;checks={}
    for name,m in s.layer_masks.items():
        assert np.array_equal(s.frame(0,name),s.frame(60,name)),name
        times=[-dt,0,3.1,8.4,8.52,14.1,20,23.3,30,33.2,39.2,40,47.5,50,56.2,58]
        vals=[float(abs(s.frame(t+dt,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in times]
        assert vals[0]<=max(vals[1:])*1.1+.01,(name,vals)
        eps=1/300
        left=(s.frame_float(0,name)-s.frame_float(-eps,name))[m]/eps
        right=(s.frame_float(eps,name)-s.frame_float(0,name))[m]/eps
        checks[name]={'periodic_state':True,'seam_mae':vals[0],'ordinary_sample_max':max(vals[1:]),'velocity_boundary_difference_mae':float(abs(left-right).mean()),'pass':True}
    opening=s.poly([s.config['sky']['clear_opening']],1)>0
    gold=np.zeros((s.h,s.w),bool);gold[277:345,480:501]=True
    for t in [0,8.52,20,21,33.37,39.35,40,48,56.31,59.99]:
        f=s.frame(t);assert np.array_equal(f[opening|gold],s.base[opening|gold])
    coverage={}
    for name in ['sky_clouds','far_dust','middle_dust']:
        mask=s.layer_masks[name]
        coverage[name]=[float(abs(s.frame(t+4,name)[mask].astype(float)-s.frame(t,name)[mask]).mean()) for t in [0,20,40,54]]
        assert min(coverage[name])>.01,(name,coverage[name])
    assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
    assert not np.array_equal(s.frame(0,'sky_clouds'),s.frame(30,'sky_clouds'))
    save('analytic-validation.json',{'fingerprint':s.fingerprint(),'checks':checks,'distinct_0_20_40':True,'world_opening_and_main_gold_window_exact':True,'four_interval_motion_coverage':coverage,'sky_not_repeated_30s':True,'user_approved':False})
    print('Analytic protection, periodicity and complete-minute coverage passed',flush=True)

def encode(s,path,seconds,only=None,start_time=0):
    assert not path.exists(),str(path)
    fps=s.config['fps'];w,h=s.config['preview_size'];count=round(seconds*fps)
    cmd=[s.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-vf','scale=out_color_matrix=bt709:out_range=tv','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);started=time.time()
    try:
        for i in range(count):
            f=fit_frame(s.frame(start_time+i/fps,only),(w,h));proc.stdin.write(f.tobytes())
            if i and i%150==0:print(path.name,i,'/',count,'elapsed',round(time.time()-started,1),flush=True)
    finally:proc.stdin.close()
    assert proc.wait()==0
    return {'path':path.relative_to(R).as_posix(),'sha256':digest(path),'frames':count,'seconds':seconds,'start_time':start_time,'layer':only or 'combined','silent':True}

def quiet_seam(s,path):
    # Decode only five frames at each end, preserving the real delivery colour conversion.
    frames=[]
    for start in [0,60-5/30]:
        raw=subprocess.check_output([s.config['ffmpeg'],'-v','error','-ss',str(start),'-i',str(path),'-frames:v','5','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        f=np.frombuffer(raw,np.uint8).reshape(-1,720,1280,3);assert len(f)==5;frames.append(f)
    pre,post=frames[1],frames[0];sequence=np.concatenate([pre,post]);checks={}
    for name,m in {**s.layer_masks,'combined':s.active}.items():
        mask=fit_frame(np.repeat(m[:,:,None],3,2).astype('uint8')*255,(1280,720))[:,:,0]>127
        steps=[float(cv2.absdiff(sequence[i],sequence[i-1])[mask].mean()) for i in range(1,10)]
        normal=steps[:4]+steps[5:];value=steps[4]
        assert value<=max(normal)*1.1+.01,(name,value,max(normal))
        checks[name]={'seam':value,'quiet_adjacent_max':max(normal),'pass':True}
    return checks

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','analytic','isolated','preview'],required=True);p.add_argument('--layers',nargs='+');a=p.parse_args();s=Crimson()
    if a.stage=='samples':samples(s);return
    if a.stage=='analytic':analytic(s);return
    clips=[]
    if a.stage=='isolated':
        tests={'sky_clouds':(0,10),'dust':(40,10),'storm_context':(6,10),'lantern':(35,10),'red_embers':(17,10),'baseline':(6,10),'combined':(6,10)}
        for n in a.layers or tests:
            start,duration=tests[n];path=H/f'{n}-v2-isolated-10s.mp4'
            item=encode(s,path,duration,None if n=='combined' else n,start);item['validation'],_=old.verify(s,path,300);clips.append(item)
    else:
        path=H/'beneath-a-crimson-sky-v2-preview-60s.mp4'
        item=encode(s,path,60);item['validation'],hashes=old.verify(s,path,1800,True,True)
        item['quiet_join_validation']=quiet_seam(s,path);clips.append(item)
        repeat=H/'beneath-a-crimson-sky-v2-three-loops-180s.mp4';assert not repeat.exists()
        subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
        validation,repeated=old.verify(s,repeat,5400,True);assert repeated==hashes*3
        clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
        save('decoded-frame-hashes.json',hashes)
    save(a.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Native/full-composition temporal and decoded stills; no continuous playback inspection claimed.'})
    print(a.stage,'complete',flush=True)
if __name__=='__main__':main()
