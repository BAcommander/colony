"""Reuse the earlier analyser, changing only its FFmpeg path discovery."""
from pathlib import Path
import sys, json, hashlib, shutil, subprocess, concurrent.futures
H=Path(__file__).resolve().parent;P=H.parent;R=P.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(H/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 src=R/'scripts/analyze_ambient_audio.py';adapter=H/'analyzer_snapshot.py'
 original=src.read_text(encoding='utf-8')
 assert original.count('import imageio_ffmpeg')==1 and original.count('imageio_ffmpeg.get_ffmpeg_exe()')==1
 modified=original.replace('import imageio_ffmpeg','import shutil').replace('imageio_ffmpeg.get_ffmpeg_exe()',"shutil.which('ffmpeg') or 'ffmpeg'")
 adapter.write_text(modified,encoding='utf-8')
 shutil.copy2(R/'scripts/ambient_audio_report.html',H/'ambient_audio_report.html')
 save('method-adapter.json',{'original_script':str(src),'original_sha256':sha(src),'snapshot_sha256':sha(adapter),'change':'Only replace unavailable imageio_ffmpeg binary discovery with PATH lookup. All audio measurement and report functions unchanged. No library install.','body_window_seconds':[20,180],'body_reason':'Equal 160-second interior window excludes generated entrance and long ending fades; separate from complete four-minute source measurements.','reference_scope':'Archived thirty-minute published/reference mixes, including SFX, versus four-minute dry generation sources; not matched duration or composition.'})
 ff=shutil.which('ffmpeg');items=json.loads((P/'sample-intake.json').read_text())['sources']
 cache=H/'cache';cache.mkdir(exist_ok=True)
 def job(pair):
  name,item=pair;source=Path(item['source_copy']);assert sha(source)==item['source_sha256']
  body=cache/(name+'-20-180s.flac')
  subprocess.run([ff,'-v','error','-n','-ss','20','-i',str(source),'-t','160','-vn','-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',str(body)],check=True)
  for kind,file in [('full',source),('body',body)]:
   out=H/(name+'-'+kind)
   subprocess.run([sys.executable,str(adapter),str(file),'--out',str(out),'--ffmpeg',ff],check=True)
  return name
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(job,zip(['waterworks','sheltered'],items)):print('Completed',result,flush=True)
if __name__=='__main__':main()
