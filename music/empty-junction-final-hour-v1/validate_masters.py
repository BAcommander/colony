"""Decode both 4K units, measure regional joins, and verify native controls."""
from produce_masters import *
import re
V=H/'verification-cache';V.mkdir(exist_ok=True)

def masks_for(s,w,h):
 result={}
 for name,mask in {**s.masks,'combined':s.active}.items():
  full=cv2.resize((mask>0).astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST)
  yy,xx=np.where(full)
  if not len(xx):continue
  a,b,z,d=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
  result[name]=(a,b,z,d,full[b:d,a:z].copy())
 return result

def metric(a,b,masks):
 diff=cv2.absdiff(a,b)
 return {k:sum(cv2.mean(diff[y:d,x:z],mask=m)[:3])/3 for k,(x,y,z,d,m) in masks.items()}

def decode_unit(s,mode,size):
 w,h=(3840,2160) if size=='4K' else (1280,720)
 path=M/f'Empty-Junction-v6-{mode}-60s-{size}.mp4';masks=masks_for(s,w,h)
 maxima={k:0. for k in masks};near=maxima.copy();first=prev=None;count=0;hashes=[];boundary={}
 log=V/f'{mode}-{size}-decode.log'
 args=[FF,'-hide_banner','-nostats','-threads','4','-i',str(path),'-an','-vf','showinfo','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
 with log.open('wb') as err:
  p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err)
  while True:
   raw=p.stdout.read(w*h*3)
   if not raw:break
   assert len(raw)==w*h*3
   f=np.frombuffer(raw,np.uint8).reshape(h,w,3);hashes.append(hashlib.sha256(raw).hexdigest())
   if first is None:first=f.copy()
   else:
    changes=metric(prev,f,masks)
    for k,value in changes.items():
     maxima[k]=max(maxima[k],value)
     if count<15 or count>=1785:near[k]=max(near[k],value)
    if count in [450,900,1350]:boundary[str(count)]=changes
   if size=='4K' and count in [0,171,900,1799]:Image.fromarray(f).save(H/f'{mode}-decoded-{count:04d}.jpg',quality=94)
   prev=f.copy();count+=1
   if count%450==0:print('Decoded',mode,size,count,'/1800',flush=True)
  assert p.wait()==0 and count==1800
 timestamps=re.findall(r'\bn:\s*(\d+)\s+pts:\s*\d+\s+pts_time:([\d.]+)',log.read_text())
 assert len(timestamps)==1800 and all(int(n)==i and abs(float(t)-i/30)<.00006 for i,(n,t) in enumerate(timestamps))
 seam=metric(prev,first,masks);checks={}
 for k,value in seam.items():
  assert value<=maxima[k]*1.1+.012,(mode,size,k,'global seam',value,maxima[k])
  assert value<=near[k]*1.25+.012,(mode,size,k,'quiet neighbour',value,near[k])
  checks[k]={'seam_mae':value,'ordinary_max':maxima[k],'neighbour_max':near[k]}
 assert hashes[0]!=hashes[-1] and len({hashes[i] for i in [0,600,1200]})==3
 result={'file':path.name,'frames':count,'all_timestamps_exact':True,'regional_seams':checks,'chunk_boundaries':boundary}
 save(f'{mode}-{size}-decode-validation.json',result)
 return result,first,prev,masks,near

def controls(s,v,mode,size):
 w,h=(3840,2160) if size=='4K' else (1280,720);path=M/f'Empty-Junction-v6-{mode}-60s-{size}.mp4'
 indices=[0,171,449,450,899,900,1349,1350,1799];sel='+'.join(f'eq(n\\,{n})' for n in indices)
 actual=subprocess.check_output([FF,'-v','error','-threads','4','-i',str(path),'-vf','select='+sel,'-fps_mode','vfr','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
 framebytes=w*h*3//2;assert len(actual)==framebytes*len(indices)
 for i,n in enumerate(indices):
  f=variants(s,v,n/30)[0 if mode=='wind' else 1]
  args=[FF,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941' if size=='4K' else '1280x720','-i','pipe:0','-frames:v','1']
  if size=='4K':args+=['-vf',SCALE]
  else:f=cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA)
  expected=subprocess.check_output(args+['-pix_fmt','yuv420p','-f','rawvideo','pipe:1'],input=f.tobytes())
  assert actual[i*framebytes:(i+1)*framebytes]==expected,(mode,size,n)
 return indices

def framehash(path,label,copy=False):
 args=[FF,'-v','error','-threads','4','-i',str(path),'-an']
 if copy:args+=['-c:v','copy']
 raw=subprocess.check_output(args+['-f','framehash','-hash','sha256','pipe:1']).decode();(V/f'{label}.sha256').write_text(raw)
 tb=None;hashes=[]
 for line in raw.splitlines():
  if line.startswith('#tb 0:'):
   a,b=map(int,line.split(':',1)[1].strip().split('/'));tb=a/b
  elif line and not line.startswith('#'):
   row=[x.strip() for x in line.split(',')]
   assert abs(int(row[2])*tb-len(hashes)/30)<1e-5
   hashes.append(row[-1])
 return hashes

def main():
 assert (H/'master-render.json').exists()
 s,v=scene('validation');results=[];joins={};ctrl={};cycles={}
 for size in ['720p','4K']:
  data={}
  for mode in ['wind','quiet']:
   result,*edges=decode_unit(s,mode,size);results.append(result);data[mode]=edges
   ctrl[mode+'-'+size]=controls(s,v,mode,size)
  for left,right in [('wind','quiet'),('quiet','quiet'),('quiet','wind')]:
   first,last,masks,near=data[right];a=data[left][1];vals=metric(a,first,masks)
   for k,val in vals.items():assert val<=max(data[left][3][k],near[k])*1.25+.012,(size,left,right,k,val)
   joins[size+'-'+left+'-'+right]=vals
  # Entire cycle decoded; exact payload and pixel sequence is wind/quiet/quiet.
  for copy in [True,False]:
   suffix='packets' if copy else 'decoded'
   hashes={mode:framehash(M/f'Empty-Junction-v6-{mode}-60s-{size}.mp4',mode+'-'+size+'-'+suffix,copy) for mode in ['wind','quiet']}
   actual=framehash(M/f'Empty-Junction-v6-cycle-180s-{size}.mp4','cycle-'+size+'-'+suffix,copy)
   assert len(actual)==5400 and actual==hashes['wind']+hashes['quiet']+hashes['quiet']
  cycles[size]={'all_5400_frames_and_timestamps':True,'wind_quiet_quiet_exact_packets_and_decoded_pictures':True}
  print('PASS',size,'units, joins, native controls and complete cycle',flush=True)
 files=json.loads((H/'master-render.json').read_text())['files']
 for entry in files:assert sha(M/entry['file'])==entry['sha256']
 save('master-validation.json',{'status':'passed','units':results,'native_yuv_controls':ctrl,'scheduled_joins':joins,'cycles':cycles,'files':files,'native_dimensions':[1672,941],'4k_upscale':'Lanczos directly from native frames','assistant_continuous_playback':False})
if __name__=='__main__':main()
