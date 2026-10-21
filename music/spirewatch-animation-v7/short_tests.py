from concurrent.futures import ProcessPoolExecutor,as_completed
from render_spirewatch import H,Spirewatch,old,save
def worker(k):
 s=Spirewatch();p=H/f'{k}-v7-test-8s.mp4';frame=s.frame;start={'tower':0,'lightning':4,'rain':12,'combined':12}[k];s.frame=lambda t,only=None:frame(t+start,only);old.encode(s,p,8,None if k=='combined' else k)
 return {'layer':k,'scene_start_seconds':start,**old.verify(s,p,240,False)}
if __name__=='__main__':
 rows=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for f in as_completed([pool.submit(worker,k) for k in ['tower','lightning','rain','combined']]):rows.append(f.result())
 save('short-tests.json',{'fingerprint':Spirewatch().fingerprint(),'clips':rows});print('Four short tests passed',flush=True)
