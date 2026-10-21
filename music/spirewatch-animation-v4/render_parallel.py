"""Four contiguous chunks share the exact native scene/timebase; lossless concat."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import subprocess,json
from render_spirewatch import H,Spirewatch,old,save,sha

def worker(index):
 s=Spirewatch();start=index*15;out=H/'render-parts'/f'part-{index:02d}.mp4'
 frame=s.frame
 s.frame=lambda t,only=None:frame(t+start,only)
 old.encode(s,out,15)
 return {'index':index,'start_seconds':start,'duration':15,'path':str(out),'sha256':sha(out),'fingerprint':s.fingerprint()}

def main():
 out=H/'spirewatch-v4-preview-60s.mp4';assert not out.exists()
 (H/'render-parts').mkdir(exist_ok=True)
 results=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  jobs=[pool.submit(worker,i) for i in range(4)]
  for job in as_completed(jobs):
   results.append(job.result());print('Chunk completed',results[-1]['index'],flush=True)
 results.sort(key=lambda r:r['index']);assert all(r['fingerprint']==results[0]['fingerprint'] for r in results)
 concat=H/'render-parts/concat.txt'
 concat.write_text(''.join("file 'part-%02d.mp4'\n"%i for i in range(4)),encoding='utf-8')
 c=json.loads((H/'scene-plan-v4.json').read_text())
 subprocess.run([c['ffmpeg'],'-v','error','-n','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(out)],check=True)
 save('parallel-render.json',{'workers':4,'chunks':results,'timeline':'Four contiguous 15-second chunks sampled at original absolute scene time, not four repeated clips','encoder':'Same lossless H264/yuv420p conversion as isolated/native encoder','complete_preview_sha256':sha(out)})
 print('Complete corrected minute assembled from contiguous chunks',flush=True)
if __name__=='__main__':main()
