"""Freeze V6, render identical native wind/quiet states and deliver 4K units."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import sys,json,hashlib,subprocess,shutil,time
import numpy as np,cv2
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1];V6=R/'music/empty-junction-animation-v6';SNAP=H/'source-snapshot'
M=H/'masters';PARTS=H/'render-cache';FF=shutil.which('ffmpeg');FPS=30
SCALE='scale=3840:2160:flags=lanczos:out_color_matrix=bt709:out_range=tv,setsar=1'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16*1024**2),b''):h.update(b)
 return h.hexdigest()
def save(name,v):(H/name).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def freeze():
 data=json.loads((V6/'dependency-snapshot.json').read_text());review=json.loads((V6/'render-record.json').read_text())
 data['music/empty-junction-animation-v6/render_v6.py']=review['renderer_sha256']
 data['music/empty-junction-animation-v6/ringed-planet-rgba.png']=json.loads((V6/'delivery-v6.json').read_text())['planet_asset_sha256']
 for rel,digest in data.items():
  src=R/rel;assert sha(src)==digest,('Changed V6 dependency',rel)
  dst=SNAP/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(src,dst)
  assert sha(dst)==digest
 save('frozen-source.json',data)
 save('user-export-request.json',{'verbatim':'ok are we happy, can we make the full export?','version_selected_for_production':'V6','user_authorized_final_assembly':True,'detailed_visual_verdict_separately_reported':False,'audio':'Approved one-hour V3 mix','scope':'One-hour 4K video with once-only current Colony opening; no publication or new music generation'})
def scene(label):
 sys.path.insert(0,str(SNAP/'music/empty-junction-animation-v6'))
 import render_v6 as v
 folder=PARTS/label/'diagnostics';folder.mkdir(parents=True,exist_ok=True)
 asset=folder/'ringed-planet-rgba.png'
 if not asset.exists():shutil.copy2(SNAP/'music/empty-junction-animation-v6/ringed-planet-rgba.png',asset)
 v.H=folder;v.v5.H=folder;s=v.Scene();cv2.setNumThreads(2)
 return s,v
def common(s,v,t):
 t=float(t)%60;f=s.src.copy();a,b,z,d=s.planet_roi;alpha=s.planet_alpha
 f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+s.planet_color*alpha[...,None]
 f[:350]+=s.clouds(t)*s.masks['clouds'][:350,:,None]
 for item in s.fogs:
  a,b,z,d=item[1];alpha,col=s.mist(t,item);f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+col*alpha[...,None]
 for name,roi,m,start,hold,depth,transition in s.light_regions:
  amount=s.previous.amount(t,name['events']) if isinstance(name,dict) else s.previous.amount(t,[{'start':start,'hold':hold,'depth':depth,'transition':transition}])
  a,b,z,d=roi;emission=np.maximum(f[b:d,a:z]-np.float32([14,19,28]),0);f[b:d,a:z]-=emission*m[...,None]*amount
 for name,roi,mask,fields in s.retained:
  if name!='yard_powder':f=s.previous.apply_extra(f,t,name,roi,mask,fields,1)
 for name,roi,core,halo,period,phase in s.beacons:
  age=(t+phase)%period;pulse=float(v.smooth(age/.18)*v.smooth((.71-age)/.25));a,b,z,d=roi
  alpha=core*pulse*.97;local=f[b:d,a:z]*(1-alpha[...,None])+np.float32([255,55,31])*alpha[...,None]
  local+=halo[...,None]*np.float32([130,12,5])*pulse;f[b:d,a:z]=local
 return f
def variants(s,v,t):
 q=common(s,v,t);w=q.copy()
 for name,roi,mask,fields in s.retained:
  if name=='yard_powder':w=s.previous.apply_extra(w,t,name,roi,mask,fields,s.previous.wind_envelope(t))
 q,w=v.byte(q),v.byte(w);powder=s.masks['yard_powder']>0
 assert np.array_equal(q[~powder],w[~powder]);assert np.array_equal(w[~s.active],s.base[~s.active])
 return w,q
def preflight():
 s,v=scene('preflight');times=[0,3.1,5.7,12,20,29+29/30,44,59+29/30]
 # Beacons are spatially disjoint from powder, so moving powder after them is exact.
 assert not any(np.any((s.masks['yard_powder']>0)&(m>0)) for k,m in s.masks.items() if k.startswith('beacon_'))
 for t in times:
  w,q=variants(s,v,t);assert np.array_equal(w,s.frame(t)),('Accepted V6 changed',t)
  Image.fromarray(cv2.resize(w,(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'preflight-{t:06.2f}.png')
 indices=[0,93,171,360,899];selection='+'.join(f'eq(n\\,{n})' for n in indices)
 actual=subprocess.check_output([FF,'-v','error','-i',str(V6/'Empty-Junction-v6-30s-720p.mp4'),'-vf','select='+selection,'-fps_mode','vfr','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
 size=1280*720*3//2
 for j,n in enumerate(indices):
  f=cv2.resize(variants(s,v,n/30)[0],(1280,720),interpolation=cv2.INTER_AREA)
  expected=subprocess.check_output([FF,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-i','pipe:0','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'],input=f.tobytes())
  assert actual[j*size:(j+1)*size]==expected,('Preview identity',n)
 save('preflight-validation.json',{'native_states_match_selected_v6':times,'selected_preview_yuv_exact_at_frames':indices,'only_wind_powder_omitted_in_quiet_unit':True,'beacons_and_powder_disjoint':True,'source_native_dimensions':[1672,941],'4k_method':'Native RGB rendered directly then Lanczos upscaled to 3840x2160 with BT.709 conversion; no 720p enlargement'})
 print('PASS: frozen V6 source and native production adapter match selected preview',flush=True)
def encoder(path,size):
 assert not path.exists(),path
 is4k=size=='4K';dimensions='1672x941' if is4k else '1280x720'
 args=[FF,'-v','error','-n','-threads','4','-filter_threads','2','-f','rawvideo','-pix_fmt','rgb24','-s',dimensions,'-r','30','-i','pipe:0']
 if is4k:args+=['-vf',SCALE]
 args+=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-qp','0','-bf','0','-g','450','-keyint_min','450','-sc_threshold','0','-pix_fmt','yuv420p']
 if is4k:args+=['-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']
 return subprocess.Popen(args+['-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
def worker(index):
 s,v=scene(f'part-{index}');folder=PARTS/f'part-{index}';procs={}
 for mode in ['wind','quiet']:
  for size in ['4K','720p']:procs[(mode,size)]=encoder(folder/f'{mode}-{size}.mp4',size)
 start=time.time()
 try:
  for i in range(450):
   t=(index*450+i)/30;wind,quiet=variants(s,v,t)
   for mode,f in [('wind',wind),('quiet',quiet)]:
    procs[(mode,'4K')].stdin.write(f.tobytes());procs[(mode,'720p')].stdin.write(cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA).tobytes())
   if i%150==0:print('Native/4K part',index,'frame',i,'/450','elapsed',round(time.time()-start),flush=True)
 finally:
  for p in procs.values():p.stdin.close()
 for p in procs.values():assert p.wait()==0
 result={'part':index,'start_seconds':index*15,'frames':450,'files':{p.name:sha(p) for p in folder.glob('*.mp4')}}
 (folder/'render.json').write_text(json.dumps(result,indent=2)+'\n');return result
def concat(paths,out):
 assert not out.exists(),out
 listing=out.with_suffix('.concat.txt');listing.write_text(''.join("file '"+str(p.resolve()).replace('\\','/')+"'\n" for p in paths),encoding='utf-8')
 subprocess.run([FF,'-v','error','-n','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(out)],check=True)
def main():
 M.mkdir(exist_ok=True);PARTS.mkdir(exist_ok=True);freeze();preflight();results=[]
 with ProcessPoolExecutor(max_workers=2) as pool:
  for done in as_completed([pool.submit(worker,i) for i in range(4)]):results.append(done.result());print('Completed paired native/4K part',results[-1]['part'],flush=True)
 for size in ['4K','720p']:
  for mode in ['wind','quiet']:concat([PARTS/f'part-{i}'/f'{mode}-{size}.mp4' for i in range(4)],M/f'Empty-Junction-v6-{mode}-60s-{size}.mp4')
  wind=M/f'Empty-Junction-v6-wind-60s-{size}.mp4';quiet=M/f'Empty-Junction-v6-quiet-60s-{size}.mp4'
  concat([wind,quiet,quiet],M/f'Empty-Junction-v6-cycle-180s-{size}.mp4')
 save('master-render.json',{'parts':sorted(results,key=lambda x:x['part']),'files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in M.glob('*.mp4')],'native_unchanged':True,'adapter_sha256':sha(__file__),'wind_schedule':'60 seconds active, 120 seconds quiet; other motion remains identical','fps':30})
 print('Paired 4K/720p units and scheduled cycle rendered; full validation next',flush=True)
if __name__=='__main__':main()
