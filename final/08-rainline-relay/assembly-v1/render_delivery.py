"""Render native v3 minute frames to 4K, checking every encoded regional step."""
from pathlib import Path
import sys,json,subprocess,time,hashlib
import cv2,numpy as np
sys.path.insert(0,'G:/AI/colony/music/rainline-renderer')
from render_rainline import Rainline

R=Path('G:/AI/colony'); H=R/'music/rainline-animation-v5'
P=R/'final/08-rainline-relay'; D=P/'delivery-v5'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    D.mkdir(exist_ok=True)
    s=Rainline(H/'scene-plan-v5.json'); prior=json.loads((H/'preview-validation.json').read_text(encoding='utf-8'))
    assert s.fingerprint()==prior['fingerprint']
    master=P/'video-4k-v5-20s.mp4'; count=600; fps=30; w,h=3840,2160
    if '--verify-only' not in sys.argv:
        assert not master.exists(),'Preserve existing media'
        assert s.duration==20
        cmd=[s.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{s.w}x{s.h}','-r','30','-i','pipe:0','-vf','scale=3840:2160:flags=lanczos:out_color_matrix=bt709:out_range=tv','-an','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-bf','0','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(master)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE); begin=time.monotonic()
        try:
            for i in range(count):
                proc.stdin.write(s.frame(i/fps).tobytes())
                if (i+1)%90==0:print(f'4K rendered {i+1}/{count}; {time.monotonic()-begin:.0f}s',flush=True)
        finally:proc.stdin.close()
        assert proc.wait()==0
    print('Checking all 600 encoded frames and regional/composite loop seams',flush=True)
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
    assert hashes[0]!=hashes[300]
    seam=cv2.absdiff(prev,first);checks={}
    for k,m in masks.items():
        value=sum(cv2.mean(seam,mask=m)[:3])/3
        assert value<=maximum[k]*1.1+.01,(k,value,maximum[k])
        checks[k]={'seam_mae':value,'ordinary_max_mae':maximum[k],'pass':True}
    report={'date':'2026-10-10','preview_fingerprint':prior['fingerprint'],'delivery_script_sha256':sha(__file__),
       'master':{'path':master.relative_to(R).as_posix(),'sha256':sha(master),'bytes':master.stat().st_size,'dimensions':[w,h],'fps':30,'frames':count,'seconds':20,'audio':False,'codec':'H.264 lossless QP0 yuv420p','source_detail':'1672x941 native frames upscaled with Lanczos'},
       'validation':{'full_decode':True,'sequential_timestamps':True,'no_duplicate_endpoint':True,'distinct_0_10_seconds':True,'encoded_seam':checks},
       'user_authorization':{'quote':'yeah that’s good, can you use our tool to make the final hour long 4k video for scene 8 now?','scope':'Use latest twenty-second v5 animation for requested final assembly; no separate full 4K playback approval claimed'},
       'repeat_validation':'Existing 720p triple-repeat verified; final one-hour Colony assembly will verify all 180 encoded repetitions and decoded master identity.'}
    (D/'delivery-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('4K master passed all encoded seam and frame checks',flush=True)
if __name__=='__main__':main()
