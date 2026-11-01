"""Render the selected V4 scene directly from frozen native sources to 4K."""
from pathlib import Path
import sys, json, hashlib, subprocess, shutil, time
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1];SRC=R/'music/deepwell-animation-v4';S=H/'source-snapshot';M=H/'masters'
FF=shutil.which('ffmpeg');PROBE=shutil.which('ffprobe')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16*1024**2),b''):h.update(b)
 return h.hexdigest()
def save(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def scale(w,h):return f'scale={w}:{h}:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
def convert(frame,w,h):
 return subprocess.check_output([FF,'-v','error','-threads','2','-filter_threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-i','pipe:0','-vf',scale(w,h),'-frames:v','1','-f','rawvideo','pipe:1'],input=frame.tobytes())
def selected(p,indices):
 selection='+'.join(f'eq(n\\,{n})' for n in indices)
 return subprocess.check_output([FF,'-v','error','-i',str(p),'-vf','select='+selection,'-fps_mode','vfr','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
def main():
 S.mkdir(exist_ok=True);M.mkdir(exist_ok=True)
 old=json.loads((SRC/'preview-validation.json').read_text());files=old['fingerprint']['files']
 for name,digest in files.items():
  source=SRC/name;assert sha(source)==digest,('Source changed',name)
  target=S/name;target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==digest
 save('frozen-source.json',files)
 save('user-export-request.json',{'date':'2026-11-01','verbatim':"ok i think it's decent shall we make the full version?",'scope':'V4 selected for one-hour 4K video with accepted soundtrack and current once-only Colony intro. No publication or commit/push.'})
 sys.path.insert(0,str(S));from render_deepwell_v4 import DeepwellV4
 s=DeepwellV4();finger=s.fingerprint();assert finger['masks_float32_sha256']==old['fingerprint']['masks_float32_sha256']
 indices=[0,120,300,480,599];controls={i:s.frame(i/30) for i in indices}
 decoded=selected(SRC/'Deepwell-v4-preview-20s.mp4',indices);size=1280*720*3//2
 for k,i in enumerate(indices):assert decoded[k*size:(k+1)*size]==convert(controls[i],1280,720),('Selected preview mismatch',i)
 save('preflight-validation.json',{'selected_preview_frames_exact':indices,'source_hashes_exact':True,'all_masks_exact':True,'native_dimensions':[1672,941],'upscale':'Native RGB directly to 3840x2160 Lanczos, no preview enlargement'})
 out=M/'Deepwell-v4-20s-4K.mp4';assert not out.exists()
 cmd=[FF,'-v','error','-n','-threads','4','-filter_threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-an','-vf',scale(3840,2160),'-c:v','libx264','-threads','6','-preset','veryfast','-qp','0','-bf','0','-g','600','-keyint_min','600','-sc_threshold','0','-pix_fmt','yuv420p','-x264-params','colorprim=bt709:transfer=bt709:colormatrix=bt709:range=tv','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
 try:
  for i in range(600):
   p.stdin.write(s.frame(i/30).tobytes())
   if i%60==0:print('Native 4K frame',i,'/600; elapsed',round(time.time()-start),'s',flush=True)
 finally:p.stdin.close()
 assert p.wait()==0
 decoded=selected(out,indices);size=3840*2160*3//2
 for k,i in enumerate(indices):assert decoded[k*size:(k+1)*size]==convert(controls[i],3840,2160),('4K conversion mismatch',i)
 listing=M/'three-loops.concat.txt';listing.write_text(("file '"+out.as_posix()+"'\n")*3)
 unit=M/'Deepwell-v4-60s-4K.mp4'
 subprocess.run([FF,'-v','error','-n','-f','concat','-safe','0','-i',str(listing),'-c','copy','-an','-movflags','+faststart',str(unit)],check=True)
 hashes=[]
 for file,count in [(out,600),(unit,1800)]:
  raw=subprocess.check_output([FF,'-v','error','-i',str(file),'-an','-f','framemd5','pipe:1']).decode()
  (M/(file.stem+'.framemd5')).write_text(raw)
  rows=[r.split(',') for r in raw.splitlines() if r and not r.startswith('#')]
  assert len(rows)==count
  assert all(int(r[2])==i for i,r in enumerate(rows))
  current=[r[-1].strip() for r in rows]
  if count==600:hashes=current
  else:assert current==hashes*3
  probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-of','json',str(file)]))['streams'][0]
  assert all(probe[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
  assert (probe['width'],probe['height'],probe['r_frame_rate'],probe['color_range'])==(3840,2160,'30/1','tv')
  print('Verified complete master',file.name,flush=True)
 save('master-validation.json',{'status':'passed','native_to_4k_yuv_exact_frames':indices,'source_preview_exact':True,'all_masks_unchanged':True,'full_master_decode':True,'three_repetitions_exact':True,'all_timestamps_sequential':True,'bt709_tv':True,'seam_evidence':'Same source, masks and twenty-second phase as selected V4; inherited regional and quiet-neighbour seam checks in preview-validation.json; all three 4K repetitions exact.','files':[{'file':f.name,'sha256':sha(f),'bytes':f.stat().st_size} for f in [out,unit]],'command':cmd})
 print('PASS: selected V4 frozen, native 4K master and three-repeat assembly unit verified',flush=True)
if __name__=='__main__':main()
