"""20-second Saltline loop adapter; preserves the accepted v5 renderer as history."""
from pathlib import Path
import argparse,json,hashlib,subprocess,time
import cv2,numpy as np
from PIL import Image
from render_saltline import Saltline,HERE,ROOT,digest
from periodic_transport import PeriodicDust,smooth
from render_floodplain import encode,verify

class SaltlineLoop(Saltline):
    def __init__(self,config='scene-plan-v6.json'):
        super().__init__(config)
        self.dust['far_dust']=PeriodicDust(*self.grids['far_dust'],self.config['far_dust'],self.duration)
        # Parent retains the accepted light masks and events. Replace only sunlight timing.
        self.sun_mask=self.masks.pop('sunlight')

    def frame(self,t,only=None,prototype=False):
        t=float(t)%self.duration
        f=super().frame(t,only,False).astype(np.float32)
        if only in (None,'sunlight'):
            c=self.config['sunlight'];x0,y0,x1,y1=self.sun_roi
            age=(t+c.get('age_at_zero',0))%self.duration
            center=c['start_x']+c['speed']*age
            field=np.exp(-.5*(((self.sun_x-center)/c['width'])**2+((self.sun_y-c['center_y'])/c['height'])**2))
            fade=smooth(age/c['fade_in'])*smooth((self.duration-age)/c['fade_out'])
            alpha=self.sun_mask[y0:y1,x0:x1]*field*c['attenuation']*fade
            f[y0:y1,x0:x1]*=1-alpha[...,None]*np.array([.9,1,1.03])
        f=np.uint8(np.rint(np.clip(f,0,255)))
        mask=self.active if only is None else self.layer_masks[only]
        assert np.array_equal(f[~mask],self.base[~mask]),'Protected pixels changed'
        return f

    def fingerprint(self):
        files=['render_saltline_loop.py','periodic_transport.py','render_saltline.py','dust_transport.py']
        return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'code_sha256':{name:digest(HERE/name) for name in files},'root_dependencies_sha256':{name:digest(ROOT/'scripts'/name) for name in ('render_floodplain.py','ambient_effects.py','water_surface.py')},'effective_masks_sha256':{name:hashlib.sha256(mask.tobytes()).hexdigest() for name,mask in self.layer_masks.items()}}

def analytic(scene):
    checks={};times=np.arange(0,scene.duration,.5)
    for name,mask in scene.layer_masks.items():
        a=scene.frame(0,name);b=scene.frame(scene.duration,name);assert np.array_equal(a,b)
        seam=float(np.abs(scene.frame(-1/30,name)[mask].astype(float)-a[mask]).mean())
        ordinary=[float(np.abs(scene.frame(t+1/30,name)[mask].astype(float)-scene.frame(t,name)[mask]).mean()) for t in times]
        assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary))
        checks[name]={'endpoint_identical':True,'last_to_first_source_mae':seam,'ordinary_source_step_mae_max_sampled':max(ordinary),'seam_pass':True}
    mask=scene.layer_masks['far_dust'];dust=[]
    for t in np.arange(0,scene.duration,1):
        delta=float(np.abs(scene.frame(t,'far_dust')[mask].astype(float)-scene.base[mask]).mean());dust.append(delta)
    assert not np.array_equal(scene.frame(0),scene.frame(10)),'Must be a genuine twenty-second scene cycle'
    return {'layer_checks':checks,'far_dust_source_delta_by_second':dust,'note':'Coverage and seam diagnostics, not artistic visibility or user approval','effect_speed_deviations_percent':{'clouds':0,'far_dust':0,'sunlight':0},'supporting_light_schedules':'Same twenty-second events as accepted v5; no duration scaling'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','preview'],required=True);p.add_argument('--config',default='scene-plan-v6.json');a=p.parse_args()
    scene=SaltlineLoop(a.config);version=scene.config['version'];report=analytic(scene)
    report['fingerprint']=scene.fingerprint();report['user_approval']=False
    for t in [0,4,8,12,16,19+29/30]:
        Image.fromarray(scene.frame(t)).save(HERE/(f'{version}-loop-sample-{t:.3f}s.png'))
    (HERE/(version+'-analytic-validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('Analytic layer seams and coverage checked',json.dumps(report['far_dust_source_delta_by_second']),flush=True)
    if a.stage=='samples':return
    clip=HERE/(f'saltline-{version}-loop-20s.mp4');item=encode(scene,clip,scene.duration)
    item['validation']=verify(scene,clip,600,True)
    repeat=HERE/(f'saltline-{version}-three-loops-60s.mp4');assert not repeat.exists()
    subprocess.run([scene.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(clip),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
    repeat_validation=verify(scene,repeat,1800,True)
    cap=cv2.VideoCapture(str(repeat));hashes=[]
    while True:
        ok,f=cap.read()
        if not ok:break
        hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
    cap.release();assert hashes[:600]==hashes[600:1200]==hashes[1200:]
    cap=cv2.VideoCapture(str(clip));ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(HERE/(version+'-decoded-frame.png')),f)
    delivery={'fingerprint':scene.fingerprint(),'preview':item,'repeated_preview':{'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':repeat_validation,'three_decoded_payloads_identical':True},'analytic_report':version+'-analytic-validation.json','duration_seconds':20,'fps':30,'frames':600,'size':[1280,720],'silent':True,'source_detail':'1672x941 native; 720p preview, not 4K final','user_approval':False,'prior_acceptance':'V5 twelve-second look accepted; new periodic timeline awaits visual review','inspection':'Full-composition temporal samples and decoded frame; no continuous-playback claim'}
    (HERE/(version+'-delivery-validation.json')).write_text(json.dumps(delivery,indent=2)+'\n')
    print('20-second preview and three repeats fully decoded; layer/encoded seams passed',flush=True)
if __name__=='__main__':main()
