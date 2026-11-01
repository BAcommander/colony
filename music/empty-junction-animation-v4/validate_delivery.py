"""Full decode, source-conversion, seam, payload and approved-audio controls."""
from pathlib import Path
import json,hashlib,argparse,subprocess,datetime,shutil
import cv2,numpy as np
from PIL import Image
from render_junction_v4 import Junction,H,R,save,digest,byte
def run(s,args,**kw):return subprocess.run([s.config['ffmpeg'],'-v','error','-nostdin',*args],check=True,**kw)
def probe(s,p):
 exe=str(Path(s.config['ffmpeg']).with_name('ffprobe.exe'))
 return json.loads(subprocess.check_output([exe,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
def yuv(s,frame):
 return subprocess.check_output([s.config['ffmpeg'],'-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-i','pipe:0','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'],input=frame.tobytes())
def actual_yuv(s,p,n):
 return subprocess.check_output([s.config['ffmpeg'],'-v','error','-i',str(p),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
def verify(s,p,count,loop=False,expected=None,quiet=False):
 info=probe(s,p);vs=next(x for x in info['streams'] if x['codec_type']=='video');assert (vs['width'],vs['height'])==(1280,720)
 names=['sky_clouds','pass_weather','yard_powder','cabin_exhaust','habitation']
 masks={n:cv2.resize(s.layer_masks[n].astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST) for n in names}
 masks['combined']=cv2.resize(s.active.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST)
 deltas={n:[] for n in masks};cap=cv2.VideoCapture(str(p));first=prev=None;hashes=[];times=[]
 while True:
  ok,frame=cap.read()
  if not ok:break
  i=len(hashes);assert frame.shape==(720,1280,3);times.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
  hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
  if first is None:first=frame.copy()
  else:
   delta=cv2.absdiff(frame,prev)
   for n,m in masks.items():deltas[n].append(sum(cv2.mean(delta,mask=m)[:3])/3)
  if i in [0,240,600,1080,1799] and count==1800:cv2.imwrite(str(H/f'{p.stem}-decoded-{i:04d}.png'),frame)
  prev=frame
 fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
 assert len(hashes)==count and fps==30,(p,len(hashes),fps)
 assert np.max(np.abs(np.array(times)-np.arange(count)/30))<.0001,'Timestamps'
 if expected is not None:assert hashes==expected,'Decoded payload sequence changed'
 seams={}
 if loop:
  assert hashes[0]!=hashes[-1],'Duplicate endpoint'
  delta=cv2.absdiff(prev,first)
  for n,m in masks.items():
   seam=sum(cv2.mean(delta,mask=m)[:3])/3;ordinary=max(deltas[n]);near=max(deltas[n][:12]+deltas[n][-12:])
   assert seam<=ordinary*1.1+.01,(p,n,'ordinary',seam,ordinary)
   assert seam<=near*1.4+.015,(p,n,'quiet neighbour',seam,near)
   seams[n]={'seam_mae':seam,'ordinary_max_mae':ordinary,'quiet_neighbour_max_mae':near,'pass':True}
 return {'file':p.name,'sha256':digest(p),'bytes':p.stat().st_size,'frames':count,'seconds':count/30,'fps':30,
  'all_frames_decoded':True,'sequential_timestamps':True,'loop_seams':seams,'audio_streams':sum(x['codec_type']=='audio' for x in info['streams']),
  'exact_expected_picture_sequence':expected is not None},hashes
def isolated(s):
 results=[]
 for layer in ['yard_powder','cabin_exhaust']:
  p=H/f'{layer}-v4-isolated-8s.mp4';record,_=verify(s,p,240)
  assert record['audio_streams']==0
  controls=[]
  for n in [0,60,180,239]:
   frame=cv2.resize(s.frame(n/30,layer),(1280,720),interpolation=cv2.INTER_AREA)
   assert yuv(s,frame)==actual_yuv(s,p,n),(layer,n,'Direct source conversion')
   controls.append({'frame':n,'direct_native_to_decoded_yuv_exact':True})
  record['direct_conversion_controls']=controls;results.append(record)
 save('isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':results,'note':'Encoded with initial sky configuration; isolated sky is static source in both versions. Current source-to-YUV controls confirm principal-effect pictures unchanged.'})
 print('Principal clips fully decoded; eight direct native-to-YUV controls exact',flush=True)
def concat(s,files,out):
 listing=H/(out.stem+'-concat.txt');listing.write_text(''.join("file '"+str(p.resolve()).replace('\\','/')+"'\n" for p in files),encoding='utf-8')
 if not out.exists():run(s,['-n','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(out)])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['isolated','delivery'],required=True);a=parser.parse_args();s=Junction()
 if a.stage=='isolated':isolated(s);return
 render=json.loads((H/'render-record.json').read_text(encoding='utf-8'));assert render['fingerprint']==s.fingerprint(),'Renderer changed after encoding'
 clips=[];hashes=[]
 for name in ['wind','quiet']:
  p=H/f'Empty-Junction-v4-{name}-minute-720p.mp4';print('Decoding full '+name+' minute',flush=True)
  rec,hs=verify(s,p,1800,True);assert rec['audio_streams']==0;clips.append(rec);hashes.append(hs)
  for n in [0,239,901,1799]:
   w,q=s.variants(n/30);frame=cv2.resize(w if name=='wind' else q,(1280,720),interpolation=cv2.INTER_AREA)
   assert yuv(s,frame)==actual_yuv(s,p,n),(name,n,'Direct native source')
  rec['direct_native_to_decoded_yuv_controls']=[0,239,901,1799]
  print(name+' minute: complete decode, regional/quiet-neighbour seam and source controls passed',flush=True)
 wind=H/'Empty-Junction-v4-wind-minute-720p.mp4';quiet=H/'Empty-Junction-v4-quiet-minute-720p.mp4'
 cycle=H/'Empty-Junction-v4-scheduled-cycle-180s-720p.mp4';concat(s,[wind,quiet,quiet],cycle)
 cycleHashes=hashes[0]+hashes[1]+hashes[1]
 rec,hs=verify(s,cycle,5400,True,cycleHashes);clips.append(rec);print('Three-minute scheduled cycle exact',flush=True)
 repeated=H/'Empty-Junction-v4-three-cycles-540s-720p.mp4'
 if not repeated.exists():run(s,['-n','-stream_loop','2','-i',str(cycle),'-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(repeated)])
 rec,_=verify(s,repeated,16200,True,cycleHashes*3);clips.append(rec);print('Three complete scheduled cycles exact',flush=True)
 audio=R/'exports/11-empty-junction/The-Empty-Junction-1-Hour-final-SFX-v3.flac'
 av=json.loads((R/'music/empty-junction-music-v1/delivery-hour-final-sfx-v3/delivery-validation.json').read_text())
 approved=json.loads((R/'music/empty-junction-music-v1/delivery-hour-final-sfx-v3/user-approval-2026-10-31.json').read_text())
 assert approved['user_current_mix_approved'] and digest(audio)==next(x['sha256'] for x in av['outputs'] if x['file'].endswith('final-SFX-v3.flac'))
 preview=H/'Empty-Junction-v4-with-approved-audio-4min-720p.mp4';listing=H/'combined-preview-concat.txt'
 listing.write_text(''.join("file '"+str(p.resolve()).replace('\\','/')+"'\n" for p in [wind,quiet,quiet,wind]),encoding='utf-8')
 if not preview.exists():run(s,['-n','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','240','-movflags','+faststart',str(preview)])
 rec,_=verify(s,preview,7200,False,cycleHashes+hashes[0]);assert rec['audio_streams']==1
 expected=subprocess.check_output([s.config['ffmpeg'],'-v','error','-i',str(audio),'-t','240','-map','0:a:0','-ac','2','-ar','48000','-f','f32le','pipe:1'])
 actual=subprocess.check_output([s.config['ffmpeg'],'-v','error','-i',str(preview),'-map','0:a:0','-ac','2','-ar','48000','-f','f32le','pipe:1'])
 x=np.frombuffer(expected,np.float32);full=np.frombuffer(actual,np.float32);assert np.isfinite(full).all() and np.max(np.abs(full))<1
 assert 0<=len(full)-len(x)<=2048,(len(full),len(x));y=full[:len(x)]
 diff=y.astype(np.float64)-x;snr=float(10*np.log10(np.sum(x.astype(np.float64)**2)/np.sum(diff**2)));assert snr>20,snr
 rec['audio']={'source':audio.relative_to(R).as_posix(),'source_sha256':digest(audio),'requested_seconds':240,'reference_stereo_frames':len(x)//2,
  'decoded_stereo_frames':len(full)//2,'aac_trailing_padding_frames':(len(full)-len(x))//2,'all_decoded_samples_finite':True,'no_clipping':True,
  'full_duration_sample_comparison_snr_db':snr,'added_gain_eq_fades_or_processing':False,'intro':'No production opening in this motion-review excerpt.'}
 clips.append(rec)
 cap=cv2.VideoCapture(str(preview))
 for t in [0,16,59.9666667,60,125,180,198,226,239.9666667]:
  cap.set(cv2.CAP_PROP_POS_FRAMES,round(t*30));ok,frame=cap.read();assert ok;cv2.imwrite(str(H/f'combined-decoded-{round(t*30):05d}.png'),frame)
 cap.release()
 snapshot={}
 for rel,h in s.fingerprint()['files'].items():
  if not rel.endswith('.py'):continue
  dest=H/'dependency-snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(R/rel,dest)
  assert digest(dest)==h;snapshot[rel]=dest.relative_to(H).as_posix()
 save('dependency-snapshot.json',snapshot)
 save('delivery-v4.json',{'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'technically verified review candidate',
  'fingerprint':s.fingerprint(),'clips':clips,'source_unchanged':digest(s.source_path)==s.config['source']['sha256'],
  'principal_motion_tests':'isolated-validation.json','native_analytic_checks':'analytic-validation.json','upscaling':'None for preview. Source native 1672x941 downsampled to 1280x720.',
  'visual_review':'Full-size temporal and decoded stills inspected; no continuous assistant playback or artistic acceptance claimed.',
  'user_animation_approved':False,'user_audio_mix_approved':True,'final_4k_or_hour_video_created':False})
 print('PASS: silent units/cycles, exact pictures, source controls and four-minute approved-audio preview',flush=True)
if __name__=='__main__':main()
