from pathlib import Path
import sys,json,hashlib,subprocess,time
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def encode(s,out,seconds,only=None):
 assert not out.exists(),f'Preserve existing {out}'
 vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
 command=['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-an','-vf',vf,'-c:v','libx264','-preset','veryfast','-qp','0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(out)]
 p=subprocess.Popen(command,stdin=subprocess.PIPE);started=time.time();count=round(seconds*30)
 try:
  for i in range(count):
   p.stdin.write(s.frame(i/30,only).tobytes())
   if i%120==0:print(out.name,i,'/',count,round(time.time()-started,1),'s',flush=True)
 finally:p.stdin.close()
 assert p.wait()==0
 return {'path':out.name,'sha256':digest(out),'seconds':seconds,'frames':count,'layer':only or 'combined','command':command}

def decode_verify(s,path,expected,loop=False,reference_hashes=None):
 # FFmpeg explicit BT.709 conversion: OpenCV's implicit colour conversion is
 # intentionally not used to judge source colour or decode the delivered clip.
 p=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-vf','scale=in_color_matrix=bt709:out_range=pc,format=rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
 size=1280*720*3;hashes=[];first=prev=None;i=0
 masks={k:cv2.resize(v.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST)>0 for k,v in {**s.layer_masks,'combined':s.active}.items()}
 positions={k:np.flatnonzero(m) for k,m in masks.items()};steps={k:[] for k in masks};first_parts={};prev_parts={}
 while True:
  raw=p.stdout.read(size)
  if not raw:break
  assert len(raw)==size
  hashes.append(hashlib.sha256(raw).hexdigest());f=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
  if i in [0,120,240,360,480,599] and expected==600:Image.fromarray(f).save(H/f'decoded-{i:04d}.png')
  flat=f.reshape(-1,3).astype(np.int16)
  for name,idx in positions.items():
   current=flat[idx]
   if i==0:first_parts[name]=current.copy()
   else:steps[name].append(float(np.abs(current-prev_parts[name]).mean()))
   prev_parts[name]=current
  i+=1
 assert p.wait()==0 and i==expected,(i,expected)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,color_space,color_transfer,color_primaries:frame=best_effort_timestamp_time','-of','json',str(path)],text=True))
 stamps=np.array([float(f['best_effort_timestamp_time']) for f in probe['frames']]);assert len(stamps)==expected and np.max(np.abs(stamps-np.arange(expected)/30))<.00001
 streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)],text=True))['streams'];assert len(streams)==1 and streams[0]['codec_type']=='video'
 checks={}
 if loop:
  assert hashes[0]!=hashes[-1]
  for name in positions:
   seam=float(np.abs(prev_parts[name]-first_parts[name]).mean());v=steps[name]
   near=max(v[:15]+v[-15:]);ordinary=max(v)
   assert seam<=ordinary*1.15+.02,(name,seam,ordinary)
   assert seam<=near*1.3+.03,(name,'quiet neighbour',seam,near)
   checks[name]={'seam_mae':seam,'ordinary_max_mae':ordinary,'quiet_neighbour_max_mae':near,'pass':True}
 if reference_hashes is not None:assert hashes==reference_hashes*3,'Repeated decoded pictures differ'
 return {'decoded_frames':i,'all_frames_decode':True,'timestamps_sequential':True,'silent':True,'bt709':probe['streams'][0],'seam_checks':checks,'three_exact_decoded_repeats':reference_hashes is not None},hashes

