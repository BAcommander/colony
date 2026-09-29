"""Render the accepted Floodplain v2 source frames at 4K and verify delivery."""
from pathlib import Path
import sys, json, hashlib, subprocess, time
import cv2, numpy as np
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from render_floodplain import Floodplain, digest

def main():
 p=R/'final/04-floodplain-keeper';a=p/'delivery-v2';a.mkdir(exist_ok=True)
 scene=Floodplain(p/'animation-v2/scene-plan-v2.json')
 accepted=json.loads((p/'animation-v2/delivery-validation.json').read_text())
 assert scene.fingerprint()==accepted['fingerprint'],'Accepted scene dependencies changed'
 master=p/'video-4k-v2.mp4';repeat=R/'exports/04-floodplain-keeper/animation-v2/floodplain-keeper-v2-three-loops-4k-60s.mp4'
 assert not master.exists() and not repeat.exists(),'Preserve existing deliveries'
 fps=30;count=600;w,h=3840,2160
 cmd=[scene.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{scene.w}x{scene.h}','-r','30','-i','pipe:0','-vf','scale=3840:2160:flags=lanczos','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(master)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
 try:
  for i in range(count):
   proc.stdin.write(scene.frame(i/fps).tobytes())
   if i and i%150==0:print('4K render',i,'/',count,round(time.time()-start,1),'s',flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0
 print('4K render complete; full decode and seam validation',flush=True)
 # Quantify each encoded region, using the unchanged gate from the preview.
 masks={k:cv2.resize(v.astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST)>0 for k,v in {**scene.layer_masks,'combined':scene.active}.items()}
 boxes={}
 for k,m in masks.items():
  yy,xx=np.where(m);box=(xx.min(),yy.min(),xx.max()+1,yy.max()+1);x0,y0,x1,y1=box;boxes[k]=(box,m[y0:y1,x0:x1])
 del masks
 first={};last={};deltas={k:[] for k in boxes};hashes=[];timestamps=[]
 cap=cv2.VideoCapture(str(master));assert cap.get(cv2.CAP_PROP_FPS)==30
 i=0
 while True:
  ok,f=cap.read()
  if not ok:break
  assert f.shape==(h,w,3);timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
  if i==0:cv2.imwrite(str(a/'decoded-frame.jpg'),f,[cv2.IMWRITE_JPEG_QUALITY,94])
  hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
  for k,((x0,y0,x1,y1),m) in boxes.items():
   vals=f[y0:y1,x0:x1][m].astype(np.int16)
   if i==0:first[k]=vals
   else:deltas[k].append(float(np.abs(vals-last[k]).mean()))
   last[k]=vals
  i+=1
  if i%150==0:print('4K decoded',i,'/',count,flush=True)
 cap.release();assert i==count
 assert np.max(np.abs(np.array(timestamps)-np.arange(count)/fps))<.0001
 checks={}
 for k in boxes:
  seam=float(np.abs(last[k]-first[k]).mean());ordinary=max(deltas[k]);assert seam<=ordinary*1.1+.01,(k,seam,ordinary)
  checks[k]={'seam_mae':seam,'ordinary_max_mae':ordinary,'pass':True}
 assert hashes[0]!=hashes[-1],'Duplicate endpoint'
 subprocess.run([scene.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(master),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
 cap=cv2.VideoCapture(str(repeat));i=0
 while True:
  ok,f=cap.read()
  if not ok:break
  assert abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/fps)<.0001
  assert hashlib.sha256(f.tobytes()).hexdigest()==hashes[i%count],i
  i+=1
  if i%600==0:print('Repeated 4K payload verified',i,'/1800',flush=True)
 cap.release();assert i==1800
 report={'date':'2026-09-29','accepted_preview_fingerprint':accepted['fingerprint'],'delivery_script_sha256':digest(__file__),'master':{'path':master.relative_to(R).as_posix(),'bytes':master.stat().st_size,'sha256':digest(master),'dimensions':[w,h],'fps':fps,'frames':count,'seconds':20,'audio':False,'codec':'H.264 lossless QP0 yuv420p','source_detail':'1672x941 native source frames upscaled with Lanczos; no added native detail'},'validation':{'full_decode':True,'sequential_timestamps':True,'no_duplicate_endpoint':True,'source_protection':'Every generated source frame checked by unchanged renderer','encoded_seam':checks},'repeat':{'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'bytes':repeat.stat().st_size,'decoded_frames':i,'three_payloads_identical':True,'sequential_timestamps':True},'user_approval':{'quote':"then i think we're good where are the files so i can put them into the tool and make the next video?",'scope':'V2 preview look accepted; requested editor handoff. New 4K export not separately playback reviewed.'}}
 (a/'delivery-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('4K master and repeated payload validation passed',flush=True)
if __name__=='__main__':main()
