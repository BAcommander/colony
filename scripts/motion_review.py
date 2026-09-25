"""Short in-context motion diagnostics. Metrics NEVER establish artistic acceptance."""
import argparse, hashlib, json, subprocess
from pathlib import Path
import cv2
import numpy as np
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
DEPENDENCIES=['scripts/render_basalt.py','scripts/ambient_effects.py','scripts/render_ringfall.py','scripts/motion_review.py']
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fingerprint(config):
    data=json.loads(Path(config).read_text())
    return {'config':digest(config),'source':digest(ROOT/data['source']['path']),
            'code':{p:digest(ROOT/p) for p in DEPENDENCIES}}
def require_accepted(config):
    config=Path(config); path=config.with_name(config.stem+'-visual-review.json')
    if not path.exists(): raise RuntimeError('Visual review missing. Run motion_review.py, then record the actual user verdict before final export.')
    review=json.loads(path.read_text())
    if review.get('status')!='accepted' or not review.get('user_feedback') or not review.get('reviewed_at_normal_speed'):
        raise RuntimeError('Preview is not visually accepted at normal speed. Technical validation is not artistic approval.')
    if review['fingerprint']!=fingerprint(config): raise RuntimeError('Scene or renderer changed after review; create a new review.')
    full_loop=False
    for clip in review['clips']:
        if digest(ROOT/clip['path'])!=clip['sha256']: raise RuntimeError('Reviewed clip changed.')
        cap=cv2.VideoCapture(str(ROOT/clip['path']))
        frames=cap.get(cv2.CAP_PROP_FRAME_COUNT);fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
        if clip.get('layer')=='combined' and fps==30 and frames==600:full_loop=True
    if not full_loop: raise RuntimeError('A reviewed complete twenty-second, 30fps composite is required before final export.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--seconds',type=int,default=8);p.add_argument('--fps',type=int,default=30)
    a=p.parse_args()
    if not 1<=a.seconds<=20 or not 1<=a.fps<=30: p.error('seconds 1..20; fps 1..30')
    from render_basalt import Basalt
    config=Path(a.config).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    anim=Basalt(config);report={'status':'pending','user_feedback':'','reviewed_at_normal_speed':False,'fingerprint':fingerprint(config),'clips':[],
      'note':'Eight-second excerpts preserve original twenty-second timing; not seamless loops. Metrics describe changes, not perceived quality.'}
    for layer in ['sky_clouds','far_haze','plain_wind',None]:
        name=layer or 'combined';dest=out/(name+'.mp4')
        if dest.exists(): raise FileExistsError(dest)
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(a.fps),'-i','-','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);first=None;peak=np.zeros((720,1280),np.float32)
        mask=anim.active if layer is None else anim.layer_masks[layer]
        try:
            for i in range(a.seconds*a.fps):
                f=anim.frame(i/a.fps,False,only=layer)
                assert np.array_equal(f[~mask],anim.base[~mask]),name+' changed protected pixels'
                f=cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA)
                if first is None:first=f.astype(np.float32)
                peak=np.maximum(peak,np.abs(f.astype(np.float32)-first).mean(axis=2))
                proc.stdin.write(f.tobytes())
        finally:proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('Encode failed')
        cap=cv2.VideoCapture(str(dest));count=0
        while True:
            ok,frame=cap.read()
            if not ok:break
            assert frame.shape[:2]==(720,1280);count+=1
        cap.release();assert count==a.seconds*a.fps
        cv2.imwrite(str(out/(name+'-change-map.png')),cv2.applyColorMap(np.uint8(np.clip(peak*12,0,255)),cv2.COLORMAP_INFERNO))
        report['clips'].append({'path':dest.relative_to(ROOT).as_posix(),'sha256':digest(dest),'layer':name,'frames':count,'peak_temporal_mae':float(peak.max()),'fraction_full_frame_changed_above_3_levels':float((peak>3).mean())})
        print(name,report['clips'][-1],flush=True)
    (out/'review.json').write_text(json.dumps(report,indent=2))
    review_path=config.with_name(config.stem+'-visual-review.json')
    if not review_path.exists():review_path.write_text(json.dumps(report,indent=2))
    print('Review full-frame clips at 1x. Record user feedback only after received. Do not infer acceptance from metrics.',flush=True)
if __name__=='__main__':main()
