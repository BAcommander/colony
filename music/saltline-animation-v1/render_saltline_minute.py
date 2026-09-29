"""One-minute Saltline delivery, reusing the preserved twenty-second atmosphere."""
import argparse, copy, hashlib, json, subprocess, time
from pathlib import Path
import cv2, numpy as np
from PIL import Image
from render_saltline import HERE, ROOT, digest, event_amount
from render_saltline_loop import SaltlineLoop
from periodic_transport import PeriodicDust

class SaltlineMinute(SaltlineLoop):
    def __init__(self, config='scene-plan-v7.json'):
        super().__init__(config)
        assert self.duration == 60 and self.config['atmosphere_period_seconds'] == 20
        # Share immutable source/grids/masks; only the atmosphere's clock and lights differ.
        self.atmosphere = copy.copy(self)
        self.atmosphere.duration = self.config['atmosphere_period_seconds']
        self.atmosphere.lights = []
        self.atmosphere.dust = dict(self.dust)
        self.atmosphere.dust['far_dust'] = PeriodicDust(*self.grids['far_dust'], self.config['far_dust'], self.atmosphere.duration)

    def frame(self, t, only=None, prototype=False):
        t = float(t) % self.duration
        f = SaltlineLoop.frame(self.atmosphere, t, only).astype(np.float32)
        if only in (None, 'lights'):
            for light, (x0,y0,x1,y1), mask in self.lights:
                amount = max((event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e.get('depth',1) for e in light['events']),default=0)
                patch = f[y0:y1,x0:x1]
                dark = patch*light['floor']+np.array(light.get('dark_offset',[4,3,2]))
                alpha = mask*amount
                f[y0:y1,x0:x1] = patch*(1-alpha[...,None])+dark*alpha[...,None]
        f = np.uint8(np.rint(np.clip(f,0,255)))
        mask = self.active if only is None else self.layer_masks[only]
        assert np.array_equal(f[~mask],self.base[~mask]), 'Protected pixels changed'
        return f

    def fingerprint(self):
        result = super().fingerprint()
        result['code_sha256']['render_saltline_minute.py'] = digest(__file__)
        return result

def prepare():
    path = HERE/'scene-plan-v7.json'
    assert not path.exists(), 'Preserve existing configuration'
    c = json.loads((HERE/'scene-plan-v6.json').read_text())
    c.update(version='v7',trial_version='v7',duration=60,atmosphere_period_seconds=20,
             status='Requested one-minute 4K delivery; irregular longer hut off periods; visual review pending')
    c['previous_feedback'] = {'date':'2026-09-30','verbatim':"if we're doing a longer loop , can the lights in the huts stay off for longer intervals or be more random, do that then make the 1 minute 4k loop",'scope':'Extend complete scene to sixty seconds and use longer independent hut light schedules'}
    rng = np.random.default_rng(20260930)
    for light, start in zip(c['lights'][:4], [2.7,20.1,11.4,51.7]):
        hold1, gap, hold2 = np.round(rng.uniform([10,12,10],[18,21,18]),3)
        second = start+float(hold1)+float(gap)
        assert second+hold2 < start+60
        light['events'] = [{'start':round(start,3),'hold':float(hold1),'transition':.45},
                           {'start':round(second%60,3),'hold':float(hold2),'transition':.55}]
    c['lights'][4]['events'] = [{'start':15.2,'hold':.22,'transition':.035,'depth':.55},
                               {'start':41.6,'hold':.14,'transition':.025,'depth':.4}]
    c['light_schedule_note'] = 'Seed 20260930; two independent irregular 10-18 second off events per hut aperture, varied intervening on holds, smooth switching and cyclic wrap. Unmapped door/other windows stay steady. Randomness is frozen for reproducibility, not regenerated each loop.'
    c['far_dust']['loop_note'] = 'Preserve v6 twenty-second local gust renewals within the sixty-second scene; unchanged coverage, geometry, opacity and speed.'
    path.write_text(json.dumps(c,indent=2)+'\n')
    print('Saved irregular hut events:',json.dumps({l['name']:l['events'] for l in c['lights'][:4]}),flush=True)

def analytic(scene):
    checks = {}
    for name, mask in scene.layer_masks.items():
        first = scene.frame(0,name)
        assert np.array_equal(first,scene.frame(scene.duration,name))
        seam = float(np.abs(scene.frame(-1/30,name)[mask].astype(float)-first[mask]).mean())
        ordinary = []
        for t in np.arange(0,scene.duration,.5):
            ordinary.append(float(np.abs(scene.frame(t+1/30,name)[mask].astype(float)-scene.frame(t,name)[mask]).mean()))
        assert seam <= max(ordinary)*1.1+.01,(name,seam,max(ordinary))
        checks[name] = {'endpoint_identical':True,'last_to_first_source_mae':seam,'ordinary_source_step_mae_max_sampled':max(ordinary),'seam_pass':True}
    reference = SaltlineLoop('scene-plan-v6.json')
    for layer in ('sky','far_dust','sunlight'):
        for t in (0,3,9,17,23,41,59+29/30):
            assert np.array_equal(scene.frame(t,layer),reference.frame(t%20,layer)),layer
    distinct = {str(t):not np.array_equal(scene.frame(0),scene.frame(t)) for t in (20,40)}
    assert all(distinct.values()), 'Minute must not be three identical twenty-second clips'
    mask = scene.layer_masks['far_dust']
    coverage = [float(np.abs(scene.frame(t,'far_dust')[mask].astype(float)-scene.base[mask]).mean()) for t in range(20)]
    return {'fingerprint':scene.fingerprint(),'layer_checks':checks,'atmosphere_identical_to_v6_at_sampled_times':True,
            'distinct_from_frame_zero_at_seconds':distinct,'far_dust_source_delta_by_second_of_local_period':coverage,
            'effect_speed_deviations_percent':{'clouds':0,'far_dust':0,'sunlight':0},
            'lights':{l['name']:l['events'] for l in scene.config['lights']},'user_review':False,
            'inspection':'Source seam, coverage and protection diagnostics; not continuous playback or user approval'}

def encode_pair(scene):
    outputs = [(HERE/'saltline-v7-loop-60s-720p.mp4',1280,720),
               (ROOT/'final/05-saltline-receiver/video-4k-v7-60s.mp4',3840,2160)]
    for path,w,h in outputs: assert not path.exists(), str(path)
    processes = []
    for path,w,h in outputs:
        cmd = [scene.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{scene.w}x{scene.h}',
               '-r','30','-i','pipe:0','-vf',f'scale={w}:{h}:flags=lanczos','-an','-c:v','libx264','-preset','veryfast',
               '-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
        processes.append(subprocess.Popen(cmd,stdin=subprocess.PIPE))
    started = time.time()
    try:
        for i in range(round(scene.duration*30)):
            data = scene.frame(i/30).tobytes()
            for proc in processes: proc.stdin.write(data)
            if (i+1)%150 == 0: print('Single source pass: 720p + 4K',i+1,'/1800',round(time.time()-started,1),'s',flush=True)
    finally:
        for proc in processes: proc.stdin.close()
    assert all(proc.wait()==0 for proc in processes)
    return outputs

def validate(scene,path,w,h,reference_hashes=None):
    boxes = {}
    for name,mask in {**scene.layer_masks,'combined':scene.active}.items():
        m = cv2.resize(mask.astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST)>0
        yy,xx = np.where(m);box=(xx.min(),yy.min(),xx.max()+1,yy.max()+1)
        x0,y0,x1,y1=box;boxes[name]=(box,m[y0:y1,x0:x1].copy())
    first={};last={};maxima={k:0. for k in boxes};hashes=[]
    cap=cv2.VideoCapture(str(path));assert cap.get(cv2.CAP_PROP_FPS)==30
    assert cap.get(cv2.CAP_PROP_FRAME_WIDTH)==w and cap.get(cv2.CAP_PROP_FRAME_HEIGHT)==h
    i=0
    while True:
        ok,f=cap.read()
        if not ok: break
        assert f.shape==(h,w,3)
        assert abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/30)<.0001, i
        sha=hashlib.sha256(f.tobytes()).hexdigest();hashes.append(sha)
        if reference_hashes is not None: assert sha==reference_hashes[i%len(reference_hashes)],i
        if i==0: cv2.imwrite(str(HERE/f'v7-decoded-{w}x{h}.jpg'),f,[cv2.IMWRITE_JPEG_QUALITY,94])
        for name,((x0,y0,x1,y1),mask) in boxes.items():
            vals=f[y0:y1,x0:x1][mask].astype(np.int16)
            if i==0: first[name]=vals
            else: maxima[name]=max(maxima[name],float(np.abs(vals-last[name]).mean()))
            last[name]=vals
        i+=1
        if i%150==0: print('Decoded',path.name,i,flush=True)
    cap.release()
    count=round(scene.duration*30)*(3 if reference_hashes is not None else 1)
    assert i==count,(i,count)
    checks={}
    for name in boxes:
        seam=float(np.abs(last[name]-first[name]).mean())
        assert seam<=maxima[name]*1.1+.01,(name,seam,maxima[name])
        checks[name]={'seam_mae':seam,'ordinary_max_mae':maxima[name],'pass':True}
    assert hashes[0]!=hashes[-1]
    if reference_hashes is None: assert hashes[0]!=hashes[600] and hashes[0]!=hashes[1200]
    probe=subprocess.run([scene.config['ffmpeg'],'-hide_banner','-i',str(path)],capture_output=True,text=True)
    assert 'Audio:' not in probe.stderr
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'bytes':path.stat().st_size,
            'dimensions':[w,h],'frames':i,'fps':30,'seconds':i/30,'silent':True,'full_decode':True,
            'sequential_timestamps':True,'no_duplicate_endpoint':True,'encoded_seam':checks,
            'repeated_decoded_payloads_identical':reference_hashes is not None},hashes

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','samples','render'],required=True);a=p.parse_args()
    if a.stage=='prepare': prepare();return
    scene=SaltlineMinute()
    report_path=HERE/'v7-analytic-validation.json'
    report=json.loads(report_path.read_text()) if a.stage=='render' and report_path.exists() else None
    if report is None or report['fingerprint']!=scene.fingerprint():
        report=analytic(scene)
        report_path.write_text(json.dumps(report,indent=2)+'\n')
        for t in (0,8,18,28,38,48,58,59+29/30):
            Image.fromarray(scene.frame(t)).save(HERE/f'v7-loop-sample-{t:.3f}s.png')
    print('Analytical seams passed; v6 atmosphere preserved exactly at sampled times',flush=True)
    if a.stage=='samples': return
    outputs=encode_pair(scene)
    preview,hashes=validate(scene,*outputs[0]);master,_=validate(scene,*outputs[1])
    repeat=HERE/'saltline-v7-three-loops-180s-720p.mp4';assert not repeat.exists()
    subprocess.run([scene.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(outputs[0][0]),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
    repeated,_=validate(scene,repeat,1280,720,hashes)
    delivery={'date':'2026-09-30','fingerprint':scene.fingerprint(),'master':master,'preview':preview,'repeat':repeated,
              'source_detail':'1672x941 artwork upscaled to 3840x2160 with Lanczos; no added native detail',
              'encoder':'H.264 lossless QP0 yuv420p','source_protection':'Asserted for every generated source frame',
              'timeline':'Genuine sixty-second hut schedule, with unchanged twenty-second local atmosphere cycles',
              'prior_acceptance':'V5 look accepted. New longer light schedule and sixty-second delivery await user visual review.',
              'inspection':'Temporal full-composition samples and decoded frame inspection; no continuous-playback claim',
              'user_approval':False,'media_backup':'Local delivery; new media remains ignored pending review'}
    (HERE/'v7-delivery-validation.json').write_text(json.dumps(delivery,indent=2)+'\n')
    print('One-minute 4K and 720p delivery plus three repeated 720p cycles fully verified',flush=True)

if __name__=='__main__': main()
