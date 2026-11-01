from pathlib import Path
import subprocess,json,hashlib,shutil
import cv2,numpy as np
from PIL import Image
from render_v6 import Scene,H,save,sha
def run(args,**kw):return subprocess.run(['ffmpeg','-v','error','-nostdin',*args],check=True,**kw)
def decode(path,expected=None):
 cap=cv2.VideoCapture(str(path));hs=[];times=[]
 while True:
  ok,f=cap.read()
  if not ok:break
  n=len(hs);hs.append(hashlib.sha256(f.tobytes()).hexdigest());times.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
  if n in [0,93,171,360,600,899]:cv2.imwrite(str(H/f'{path.stem}-decoded-{n:04d}.png'),f)
 cap.release();assert len(hs)==900 and max(abs(np.array(times)-np.arange(900)/30))<.0001
 if expected is not None:assert hs==expected
 return {'file':path.name,'sha256':sha(path),'frames':900,'fps':30,'seconds':30,'all_frames_decoded':True,'sequential_timestamps':True,'matches_silent_video':expected is not None},hs
def main():
 s=Scene();record=json.loads((H/'render-record.json').read_text());assert record['renderer_sha256']==sha(H/'render_v6.py')
 p=H/'Empty-Junction-v6-30s-720p.mp4';rec,hashes=decode(p);controls=[]
 for n in [0,93,171,360,899]:
  f=cv2.resize(s.frame(n/30),(1280,720),interpolation=cv2.INTER_AREA)
  expected=subprocess.check_output(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-i','pipe:0','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'],input=f.tobytes())
  actual=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
  assert actual==expected,n;controls.append(n)
 rec['exact_native_to_decoded_yuv_controls']=controls
 audio=H.parents[1]/'exports/11-empty-junction/The-Empty-Junction-1-Hour-final-SFX-v3.flac';assert sha(audio)=='84a773c68ca1a8d1115c76e2edcc914f8c955c5f60cb31436b1c5718b4982f09'
 out=H/'Empty-Junction-v6-with-approved-audio-30s-720p.mp4'
 if not out.exists():run(['-n','-i',str(p),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-t','30','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)])
 av,_=decode(out,hashes)
 x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(audio),'-t','30','-f','f32le','-ac','2','-ar','48000','pipe:1']),np.float32)
 y=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-f','f32le','-ac','2','-ar','48000','pipe:1']),np.float32)
 assert np.isfinite(y).all() and abs(y).max()<1 and 0<=len(y)-len(x)<=2048
 snr=float(10*np.log10(np.sum(x.astype(float)**2)/np.sum((x.astype(float)-y[:len(x)])**2)));assert snr>25
 av['audio']={'approved_source_sha256':sha(audio),'comparison_snr_db':snr,'whole_excerpt_compared':True,'no_added_gain_eq_or_fades':True}
 # Existing geometry is retained: stronger off states use the same complete aperture masks.
 lights=[]
 for name,m,start,hold,depth,transition in s.lights:
  if not isinstance(name,str) or name=='cabin':continue
  t=(start+transition+hold/2)%60;mask=(m>.99)&(s.src.mean(2)>150)
  if not mask.any():continue
  current=float(s.frame(t,'windows')[mask].mean());on=float(s.src[mask].mean())
  assert current<on*.40,(name,current,on)
  lights.append({'name':name,'on_mean_rgb':on,'off_mean_rgb':current,'remaining_fraction':current/on})
 save('light-off-check.json',{'complete_bright_core_masks_used':True,'windows':lights,'note':'Brightness evidence, not user visual acceptance. The inherited apertures.json preserves V5 geometry/timing; current strength is in scene-plan-v6.json.'})
 planet=Image.open(H/'ringed-planet-rgba.png');assert planet.mode=='RGBA' and planet.getextrema()[3][0]==0
 generated=Path('C:/Users/jazzs/.codex/generated_images/01a192a2-705f-7391-80a2-74e52ec3e7ea/exec-68eb5fa7-6b6a-4993-9161-aa129681b796.png')
 assert sha(generated)==sha(H/'ringed-planet-rgba.png')
 save('planet-generation.json',{'tool':'built-in image_gen','transparent_background':True,'prompt':'planet-prompt.txt','original_returned_file':str(generated),'workspace_asset':'ringed-planet-rgba.png','sha256':sha(generated),'dimensions':list(planet.size),'mode':planet.mode,'original_generated_alpha_preserved':True,'composition':'Placement, scale and atmospheric blend are explicit renderer settings; underlying scene plate is unchanged.'})
 deps=s.previous.fingerprint()['files'];deps['music/empty-junction-animation-v5/render_v5.py']=sha(H.parent/'empty-junction-animation-v5/render_v5.py')
 for rel,digest in deps.items():
  src=H.parents[1]/rel;dest=H/'dependency-snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(src,dest)
  assert sha(dest)==digest
 save('dependency-snapshot.json',deps)
 save('delivery-v6.json',{'status':'Thirty-second visual review candidate','clips':[rec,av],'source_sha256':sha(s.previous.source_path),'source_native_dimensions':[1672,941],
  'planet_asset_sha256':sha(H/'ringed-planet-rgba.png'),'preview_dimensions':[1280,720],'user_approved':False,'user_audio_mix_approved':True,
  'periodicity':'Native 60s layer states and sampled seam checks passed; this 30s review is not a loop and is not presented as a complete encoded cycle.',
  'assistant_review':'Native/decoded temporal stills; no continuous playback claim','full_4k_or_hour_created':False,'committed':False,'pushed':False})
 print('PASS: complete 30s decode, timestamps, five exact source controls, dark-window checks, alpha provenance and approved-audio comparison',flush=True)
if __name__=='__main__':main()
