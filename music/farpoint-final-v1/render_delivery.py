"""Render native v6 minute frames to 4K, checking every encoded regional step."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,importlib.util
import cv2,numpy as np
from PIL import Image
# Load the immutable shared effect snapshot used for the saved preview.
snapshot=Path('G:/AI/colony/music/farpoint-animation-v6/dependency-snapshot/ambient_effects.py')
spec=importlib.util.spec_from_file_location('ambient_effects',snapshot)
module=importlib.util.module_from_spec(spec);sys.modules['ambient_effects']=module;spec.loader.exec_module(module)
sys.path.insert(0,'G:/AI/colony/music/farpoint-animation-v6')
from render_farpoint_v6 import FarpointV6

R=Path('G:/AI/colony'); H=R/'music/farpoint-animation-v6'
P=R/'final/10-nightward-station'; D=P/'delivery-v6'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    D.mkdir(exist_ok=True)
    s=FarpointV6(); prior=json.loads((H/'preview-validation.json').read_text(encoding='utf-8'))
    actual=s.fingerprint(); effective=json.loads(json.dumps(actual))
    effective['files']['scripts/ambient_effects.py']=sha(snapshot)
    expected=json.loads(json.dumps(prior['fingerprint']))
    versions={'preview':expected.pop('versions'),'delivery':effective.pop('versions')}
    assert effective==expected,'Source, masks or loaded renderer differs from preview'
    samples=[]
    for t in [0,5,8,13,20,30,40,50,57,59+29/30]:
        p=H/f'sample-{t:06.2f}s.png'
        current=cv2.resize(s.frame(t),(1280,720),interpolation=cv2.INTER_AREA)
        assert np.array_equal(current,np.array(Image.open(p).convert('RGB'))),f'Saved sample differs at {t}'
        samples.append(t)
    print('All ten saved preview source states match exactly using preserved effect snapshot',flush=True)
    master=P/'video-4k-v6-60s.mp4'; count=1800; fps=30; w,h=3840,2160
    if '--verify-only' not in sys.argv:
        assert not master.exists(),'Preserve existing media'
        assert s.duration==60
        s.h,s.w=s.base.shape[:2]
        cmd=[s.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{s.w}x{s.h}','-r','30','-i','pipe:0','-vf','scale=3840:2160:flags=lanczos:out_color_matrix=bt709:out_range=tv','-an','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-bf','0','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(master)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE); begin=time.monotonic()
        try:
            for i in range(count):
                proc.stdin.write(s.frame(i/fps).tobytes())
                if (i+1)%90==0:print(f'4K rendered {i+1}/{count}; {time.monotonic()-begin:.0f}s',flush=True)
        finally:proc.stdin.close()
        assert proc.wait()==0
    print('Checking all 1800 encoded frames and regional/composite loop seams',flush=True)
    # cv2 masked means avoid large advanced-index copies, retaining every pixel.
    masks={k:cv2.resize(v.astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST) for k,v in {**s.layer_masks,'combined':s.active}.items()}
    maximum={k:0. for k in masks}; cap=cv2.VideoCapture(str(master))
    assert cap.get(cv2.CAP_PROP_FPS)==fps
    first=prev=None; hashes=[]; i=0
    while True:
        ok,f=cap.read()
        if not ok:break
        assert f.shape==(h,w,3)
        assert abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/fps)<.0001
        hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
        if first is None:first=f.copy();cv2.imwrite(str(D/'decoded-frame.jpg'),f,[cv2.IMWRITE_JPEG_QUALITY,94])
        else:
            diff=cv2.absdiff(f,prev)
            for k,m in masks.items():maximum[k]=max(maximum[k],sum(cv2.mean(diff,mask=m)[:3])/3)
        if i==240:cv2.imwrite(str(D/'decoded-frame-8s.jpg'),f,[cv2.IMWRITE_JPEG_QUALITY,94])
        prev=f;i+=1
        if i%150==0:print(f'4K decoded and checked {i}/{count}',flush=True)
    cap.release();assert i==count and hashes[0]!=hashes[-1]
    assert len({hashes[i] for i in [0,600,1200]})==3
    seam=cv2.absdiff(prev,first);checks={}
    for k,m in masks.items():
        value=sum(cv2.mean(seam,mask=m)[:3])/3
        assert value<=maximum[k]*1.1+.01,(k,value,maximum[k])
        checks[k]={'seam_mae':value,'ordinary_max_mae':maximum[k],'pass':True}
    report={'date':'2026-10-10','preview_fingerprint':prior['fingerprint'],'runtime_versions':versions,'dependency_resolution':{'ambient_effects':str(snapshot),'sha256':sha(snapshot),'saved_preview_sample_times_exact':samples},'delivery_script_sha256':sha(__file__),
       'master':{'path':master.relative_to(R).as_posix(),'sha256':sha(master),'bytes':master.stat().st_size,'dimensions':[w,h],'fps':30,'frames':count,'seconds':60,'audio':False,'codec':'H.264 lossless QP0 yuv420p','source_detail':'1672x941 native frames upscaled with Lanczos'},
       'validation':{'full_decode':True,'sequential_timestamps':True,'no_duplicate_endpoint':True,'distinct_0_20_40_seconds':True,'encoded_seam':checks},
       'user_authorization':{'quote':'i think for now lets just build out the full farpoint with this. since the track was only 5 minutes do you recommend 1 hour?','scope':'Use latest sixty-second v6 animation for requested final assembly; no separate full 4K playback approval claimed'},
       'repeat_validation':'Existing 720p triple-repeat verified; final one-hour Colony assembly will verify all 60 encoded repetitions and decoded master identity.'}
    (D/'delivery-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('4K master passed all encoded seam and frame checks',flush=True)
if __name__=='__main__':main()
