from pathlib import Path
import subprocess,json,hashlib,shutil
import cv2,numpy as np
from PIL import Image
from render_v5 import Scene,H,write,sha

def run(args,**kw):return subprocess.run(['ffmpeg','-v','error','-nostdin',*args],check=True,**kw)
def verify(s,path,expected=None):
 cap=cv2.VideoCapture(str(path));times=[];hashes=[];first=prev=None
 masks={n:cv2.resize(m.astype(np.float32),(1280,720),interpolation=cv2.INTER_AREA)>.05 for n,m in {
  'clouds':s.masks['clouds'],'mist':np.maximum(s.masks['far_mist'],s.masks['middle_mist']),
  'windows':np.maximum.reduce([m for k,m in s.masks.items() if k.startswith('window_')]),'combined':s.active}.items()}
 deltas={k:[] for k in masks}
 while True:
  ok,f=cap.read()
  if not ok:break
  i=len(hashes);times.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000);hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
  if first is None:first=f.copy()
  else:
   delta=cv2.absdiff(f,prev).mean(2)
   for k,m in masks.items():deltas[k].append(float(delta[m].mean()))
  if i in (0,180,600,960,1320,1799):cv2.imwrite(str(H/f'{path.stem}-decoded-{i:04d}.png'),f)
  prev=f
 cap.release();count=3600 if expected else 1800
 assert len(hashes)==count and max(abs(np.array(times)-np.arange(count)/30))<.0001
 if expected:assert hashes==expected
 seam=cv2.absdiff(first,prev).mean(2);checks={}
 for k,m in masks.items():
  v=float(seam[m].mean());near=max(deltas[k][:15]+deltas[k][-15:]);ordinary=max(deltas[k])
  assert v<=near*1.5+.06,(k,v,near)
  assert v<=ordinary*1.2+.06,(k,v,ordinary)
  checks[k]={'seam_mae':v,'neighbour_max':near,'ordinary_max':ordinary}
 return {'file':path.name,'sha256':sha(path),'frames':count,'all_frames_decoded':True,'all_timestamps_checked':True,'regional_seams':checks,'exact_repetition':bool(expected)},hashes

def controls(s,path):
 values=[]
 for n in [0,179,600,960,1320,1799]:
  f=cv2.resize(s.frame(n/30),(1280,720),interpolation=cv2.INTER_AREA)
  ref=subprocess.check_output(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-i','pipe:0','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'],input=f.tobytes())
  actual=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
  diff=np.frombuffer(ref,np.uint8).astype(float)-np.frombuffer(actual,np.uint8)
  rmse=float(np.sqrt(np.mean(diff**2)));assert rmse==0,(n,rmse)
  values.append({'frame':n,'yuv_rmse':rmse,'direct_native_to_decoded_yuv_exact':True,'qp':0})
 return values

def main():
 s=Scene();p=H/'Empty-Junction-v5-60s-720p.mp4'
 record=json.loads((H/'render-record.json').read_text());assert record['renderer_sha256']==sha(H/'render_v5.py')
 assert not np.array_equal(s.frame(0,'clouds'),s.frame(30,'clouds')),'Cloud field unexpectedly repeats at 30s'
 a=(s.clouds(0)+s.sky_original).mean(2)[155:205,850:1100].astype(np.float32)
 b=(s.clouds(10)+s.sky_original).mean(2)[155:205,850:1100].astype(np.float32)
 shift,response=cv2.phaseCorrelate(a,b,cv2.createHanningWindow((250,50),cv2.CV_32F))
 write('cloud-direction-check.json',{'interval_seconds':10,'native_roi':[850,155,1100,205],'estimated_shift_xy':list(shift),'correlation_response':response,'half_minute_duplicate':False,'interpretation':'Texture tracking diagnostic, not a perceptual motion-quality score.'})
 base,hashes=verify(s,p);print('Full minute and regional seams verified',flush=True)
 base['direct_source_controls']=controls(s,p)
 repeated=H/'Empty-Junction-v5-two-loops-120s-720p.mp4'
 if not repeated.exists():run(['-n','-stream_loop','1','-i',str(p),'-c','copy','-an','-movflags','+faststart',str(repeated)])
 rep,_=verify(s,repeated,hashes*2);print('Exact repeated picture sequence verified',flush=True)
 audio=H.parents[1]/'exports/11-empty-junction/The-Empty-Junction-1-Hour-final-SFX-v3.flac'
 assert sha(audio)=='84a773c68ca1a8d1115c76e2edcc914f8c955c5f60cb31436b1c5718b4982f09'
 av=H/'Empty-Junction-v5-with-approved-audio-60s-720p.mp4'
 if not av.exists():run(['-n','-i',str(p),'-i',str(audio),'-t','60','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(av)])
 av_record,av_hashes=verify(s,av);assert av_hashes==hashes
 ref=subprocess.check_output(['ffmpeg','-v','error','-i',str(audio),'-t','60','-f','f32le','-ac','2','-ar','48000','pipe:1'])
 actual=subprocess.check_output(['ffmpeg','-v','error','-i',str(av),'-f','f32le','-ac','2','-ar','48000','pipe:1'])
 x=np.frombuffer(ref,np.float32);y=np.frombuffer(actual,np.float32);assert 0<=len(y)-len(x)<=2048 and np.isfinite(y).all() and abs(y).max()<1
 snr=float(10*np.log10(np.sum(x.astype(float)**2)/np.sum((x.astype(float)-y[:len(x)])**2)));assert snr>25
 av_record['audio']={'approved_source_sha256':sha(audio),'seconds':60,'full_sample_comparison_snr_db':snr,'unchanged_mix_gain_eq_fades':True,'no_clipping':True}
 # Before/after detail comparison uses decoded previews at the same time and magnification.
 comparison=H/'Empty-Junction-v4-v5-details-20s.mp4'
 if not comparison.exists():
  filter_graph='[0:v]split=3[a][b][c];[1:v]split=3[d][e][f];'+\
   '[a]crop=460:200:500:60,scale=640:278[as];[d]crop=460:200:500:60,scale=640:278[ds];'+\
   '[b]crop=460:120:390:230,scale=640:167[bs];[e]crop=460:120:390:230,scale=640:167[es];'+\
   '[c]crop=180:48:925:295,scale=640:171[cs];[f]crop=180:48:925:295,scale=640:171[fs];'+\
   '[as][ds]hstack[top];[bs][es]hstack[mid];[cs][fs]hstack[bottom];[top][mid][bottom]vstack=inputs=3,pad=1280:660:0:44:color=black,'+\
   "drawtext=fontfile='C\\:/Windows/Fonts/segoeui.ttf':text='V4 — previous':x=20:y=10:fontsize=23:fontcolor=white,"+\
   "drawtext=fontfile='C\\:/Windows/Fonts/segoeui.ttf':text='V5 — rebuilt':x=660:y=10:fontsize=23:fontcolor=white[out]"
  run(['-n','-i',str(H.parent/'empty-junction-animation-v4/Empty-Junction-v4-wind-minute-720p.mp4'),'-i',str(p),'-filter_complex',filter_graph,'-map','[out]','-t','20','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(comparison)])
 cap=cv2.VideoCapture(str(comparison));n=0
 while True:
  ok,f=cap.read()
  if not ok:break
  if n==360:cv2.imwrite(str(H/'comparison-decoded-12s.png'),f)
  n+=1
 cap.release();assert n==600
 deps=s.previous.fingerprint()['files'];snapshot={}
 for rel,h in deps.items():
  src=H.parents[1]/rel;dest=H/'dependency-snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(src,dest)
  assert sha(dest)==h;snapshot[rel]=h
 snapshot['music/empty-junction-animation-v5/render_v5.py']=sha(H/'render_v5.py')
 write('dependency-snapshot.json',snapshot)
 write('delivery-v5.json',{'status':'Technically checked visual review candidate; user verdict pending','clips':[base,rep,av_record],
  'comparison':{'file':comparison.name,'sha256':sha(comparison),'all_600_frames_decoded':True,'same_time_and_crop':True},
  'source_sha256':sha(s.previous.source_path),'source_dimensions':[1672,941],'preview_dimensions':[1280,720],
  'retained_layers':['cabin_exhaust','yard_powder'],'replaced_layers':['all window apertures','cloud extraction/transport','far/middle mist; old terrain stripe removed'],
  'user_approved':False,'assistant_inspection':'Native/decoded temporal stills and enlarged comparisons; not continuous playback',
  'full_final_4k_hour_created':False})
 print('PASS: delivery and comparison verified',flush=True)

if __name__=='__main__':main()
