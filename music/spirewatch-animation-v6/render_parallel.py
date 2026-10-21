from concurrent.futures import ProcessPoolExecutor,as_completed
import subprocess
from render_spirewatch import H,Spirewatch,old,save,sha
def worker(i):
 s=Spirewatch();frame=s.frame;s.frame=lambda t,only=None:frame(t+i*15,only)
 p=H/'render-parts'/f'part-{i:02d}.mp4';old.encode(s,p,15)
 return {'index':i,'start':i*15,'sha256':sha(p),'fingerprint':s.fingerprint()}
if __name__=='__main__':
 out=H/'spirewatch-v6-preview-60s.mp4';assert not out.exists();(H/'render-parts').mkdir(exist_ok=True)
 results=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  jobs=[pool.submit(worker,i) for i in range(4)]
  for job in as_completed(jobs):results.append(job.result());print('Chunk complete',results[-1]['index'],flush=True)
 results.sort(key=lambda x:x['index']);assert all(r['fingerprint']==results[0]['fingerprint'] for r in results)
 concat=H/'render-parts/concat.txt';concat.write_text(''.join("file 'part-%02d.mp4'\n"%i for i in range(4)))
 subprocess.run([Spirewatch().config['ffmpeg'],'-v','error','-n','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(out)],check=True)
 save('parallel-render.json',{'chunks':results,'sha256':sha(out),'contiguous_absolute_time':True});print('Complete v6 minute assembled',flush=True)
