"""Render and validate a source-mapped Glacier loop at 720p and 4K in one frame pass."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import cv2,numpy as np,imageio_ffmpeg
from render_glacier import Glacier
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoder(path,size):
 return subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','30','-i','-','-an','-c:v','libx264','-preset','medium','-qp','0','-pix_fmt','yuv420p','-g','300','-bf','0','-movflags','+faststart','-metadata','title=Ambient Colony - Glacier Sanctuary - 60 second loop',str(path)],stdin=subprocess.PIPE)
def validate(path,size,anim,count):
 cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);first=prev=None;steps=[];n=0
 mask=cv2.resize(anim.masks['combined'].astype(np.uint8),size,interpolation=cv2.INTER_NEAREST)
 mask=cv2.dilate(mask,np.ones((7,7),np.uint8))>0
 while True:
  ok,f=cap.read()
  if not ok:break
  assert f.shape[:2]==(size[1],size[0]);current=f[mask].astype(np.float32)
  if first is None:first=current.copy()
  if prev is not None:steps.append(float(np.abs(current-prev).mean()))
  if n==90:cv2.imwrite(str(path.with_suffix('.jpg')),cv2.resize(f,(1280,720)))
  prev=current;n+=1
 cap.release();assert n==count and fps==30
 seam=float(np.abs(prev-first).mean());assert seam<=max(steps)*1.25+.02,(seam,max(steps))
 return {'path':path.relative_to(ROOT).as_posix(),'dimensions':size,'decoded_frames':n,'fps':fps,'duration_seconds':n/fps,'encoded_seam_mae':seam,'ordinary_max_mae':max(steps),'ordinary_mean_mae':float(np.mean(steps)),'sha256':sha(path),'bytes':path.stat().st_size}
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default='creative/glacier-sanctuary/animation/scene-plan-v11.json');a=p.parse_args()
 config=ROOT/a.config;anim=Glacier(config);duration=anim.config['loop_seconds'];count=duration*30
 assert duration==60 and anim.config['review']['approved'];out=config.parent/'final-v11';out.mkdir(exist_ok=True)
 paths=[(out/'glacier-sanctuary-v11-60s-720p.mp4',(1280,720)),(out/'glacier-sanctuary-v11-60s-4k.mp4',(3840,2160))]
 for path,size in paths:assert not path.exists(),path
 pipes=[encoder(path,size) for path,size in paths]
 try:
  for i in range(count):
   frame=anim.frame(i/30);assert np.array_equal(frame[~anim.masks['combined']],anim.base[~anim.masks['combined']])
   for pipe,(path,size) in zip(pipes,paths):pipe.stdin.write(cv2.resize(frame,size,interpolation=cv2.INTER_LANCZOS4).tobytes())
   if i%90==0:print(f'Rendered {i}/{count} frames',flush=True)
 finally:
  for pipe in pipes:pipe.stdin.close()
 for pipe in pipes:assert pipe.wait()==0
 outputs=[]
 for path,size in paths:
  print('Decoding and checking '+path.name,flush=True);outputs.append(validate(path,size,anim,count));print(json.dumps(outputs[-1]),flush=True)
 report={'status':'accepted v10 look; sixty-second v11 delivery verified','source':anim.config['source'],'config_sha256':sha(config),'code_sha256':{s:sha(ROOT/'scripts'/s) for s in ['render_glacier.py','water_surface.py','ambient_effects.py','render_glacier_delivery.py']},'outputs':outputs,'audio':False,'unique_timeline_seconds':60,'not_a_repeated_20_second_export':True,'endpoint_pixels_equal':bool(np.array_equal(anim.frame(0),anim.frame(60))),'inspection':'Analytic/encoded checks and sampled decoded frames; no assistant continuous playback review claimed','resolution_note':'4K output upscaled from 1672x941 source','user_acceptance':'ok i think we can go with this, extend it out into the 60 second loop ij 4k?'}
 (out/'delivery-validation.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
