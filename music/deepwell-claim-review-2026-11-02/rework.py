"""Replace source A30–51s, with six-second handles; apply to every occurrence."""
from pathlib import Path
import json,hashlib,subprocess,shutil,math
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];C=H/'cache';D=H/'replacement-v1';D.mkdir(exist_ok=True)
SR=48000;FF=shutil.which('ffmpeg');E=R/'exports/12-deepwell-station'
recipe=json.loads((R/'music/deepwell-production-2026-11-01/delivery-hour-v1/mix-recipe.json').read_text())
src=R/'music/deepwell-production-2026-11-01/sources/Waterworks_Gallery_2026-11-01T171541.mp4'
original_mix=E/'Deepwell-Station-1-Hour-v1.flac'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def decode(p):
 r=subprocess.run([FF,'-v','error','-i',str(p),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True)
 assert not r.stderr
 return np.frombuffer(r.stdout,'<f4').reshape(-1,2)
def encode(raw,out):
 codec=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24'] if out.suffix=='.flac' else ['-c:a','libmp3lame','-b:a','192k']
 subprocess.run([FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i',str(raw),*codec,str(out)],check=True)
def small(name,x):
 raw=C/(name+'.f32');x.astype('<f4').tofile(raw);out=D/name;encode(raw,out)
 y=decode(out);assert len(y)==len(x) and np.isfinite(y).all() and abs(y).max()<1
 return {'path':str(out),'sha256':sha(out),'seconds':len(y)/SR}

def main():
 assert sha(src)==recipe['source_hashes'][str(src)]
 paths=json.loads((R/'music/deepwell-production-2026-11-01/delivery-hour-v1/delivery-paths.json').read_text())
 assert sha(original_mix)==next(x['sha256'] for x in paths['outputs'] if x['kind']=='mix' and x['path'].endswith('.flac'))
 a=decode(src);assert len(a)==240*SR
 old=a[24*SR:57*SR].copy();donor=a[90*SR:123*SR].copy()
 gain=float(np.sqrt(np.mean(old.astype(float)**2)/np.mean(donor.astype(float)**2)))
 donor*=gain
 n=len(old);k=6*SR;old_weight=np.zeros(n);new_weight=np.ones(n)
 theta=np.linspace(0,np.pi/2,k)
 old_weight[:k]=np.cos(theta);new_weight[:k]=np.sin(theta)
 old_weight[-k:]=np.sin(theta);new_weight[-k:]=np.cos(theta)
 assert not old_weight[6*SR:27*SR].any()
 patched=a.copy();patched[24*SR:57*SR]=(old*old_weight[:,None]+donor*new_weight[:,None]).astype(np.float32)
 assert np.array_equal(patched[:24*SR],a[:24*SR]) and np.array_equal(patched[57*SR:],a[57*SR:])
 assert np.array_equal(patched[30*SR:51*SR],donor[6*SR:27*SR])
 boundary=[]
 for t in [24,30,51,57]:
  i=t*SR;step=float(np.sqrt(np.mean((patched[i].astype(float)-patched[i-1])**2)))
  steps=np.sqrt(np.mean(np.diff(patched[i-SR:i+SR].astype(float),axis=0)**2,axis=1));q=float(np.quantile(steps,.999))
  assert step<=q*1.5+1e-7;boundary.append({'source_seconds':t,'sample_step':step,'nearby_step_p99_9':q})
 outputs=[small('Waterworks-Gallery-reworked-source-v1.flac',patched)]
 # Read/write the hour in10s blocks; keep the established mix outside patch windows exact.
 raw=C/'reworked-hour.f32';original_raw=C/'original-hour.f32'
 subprocess.run([FF,'-v','error','-n','-i',str(original_mix),'-vn','-ar',str(SR),'-ac','2','-f','f32le',str(original_raw)],check=True)
 baseline=np.memmap(original_raw,dtype='<f4',mode='r',shape=(3600*SR,2))
 events=[]
 for seg in recipe['music_schedule']:
  if seg['track']=='A':events.append({'start':seg['start']+24-seg['source_in'],'end':min(3600,seg['start']+57-seg['source_in']),'replacement_core_start':seg['start']+30-seg['source_in'],'replacement_core_end':min(3600,seg['start']+51-seg['source_in'])})
 with raw.open('xb') as f:
  for start in range(0,3600*SR,10*SR):
   ids=np.arange(start,min(3600*SR,start+10*SR));out=np.array(baseline[start:start+len(ids)],copy=True)
   delta=np.zeros_like(out);mask=np.zeros(len(ids),bool)
   for seg in recipe['music_schedule']:
    if seg['track']!='A':continue
    local=ids-seg['start']*SR;source=local+seg['source_in']*SR;length=(seg['source_out']-seg['source_in'])*SR
    on=(local>=0)&(local<length)&(source>=24*SR)&(source<57*SR)
    if not on.any():continue
    mask|=on;l=local[on];s=source[on];env=np.ones(len(l))
    if seg['fade_in']:
     k=seg['fade_in']*SR;head=l<k;env[head]*=np.sin(l[head]/k*np.pi/2)
    if seg['fade_out']:
     k=seg['fade_out']*SR;tail=l>=length-k;env[tail]*=np.cos((l[tail]-(length-k))/k*np.pi/2)
    original_contribution=(a[s]*10**(recipe['music_gain_db'][0]/20)*env[:,None]).astype(np.float32)
    new_contribution=(patched[s]*10**(recipe['music_gain_db'][0]/20)*env[:,None]).astype(np.float32)
    closing=np.minimum(1,(3600*SR-1-ids[on])/(20*SR)).astype(np.float32)
    delta[on]+=(new_contribution-original_contribution)*closing[:,None]
   out+=delta
   assert np.array_equal(out[~mask],baseline[start:start+len(ids)][~mask])
   assert np.isfinite(out).all() and abs(out).max()<1
   f.write(out.astype('<f4').tobytes())
 expected=np.memmap(raw,dtype='<f4',mode='r',shape=(3600*SR,2))
 outputs.append(small('Deepwell-before-replacement-75s.mp3',baseline[1175*SR:1250*SR]))
 outputs.append(small('Deepwell-after-replacement-75s.mp3',expected[1175*SR:1250*SR]))
 outputs.append(small('Deepwell-first-occurrence-after-75s.mp3',expected[10*SR:85*SR]))
 print('Source patch and three listening checks ready; all',len(events),'occurrences replaced.',flush=True)
 dest=E/'Deepwell-Station-1-Hour-claim-rework-v1.flac';encode(raw,dest)
 proc=subprocess.Popen([FF,'-v','error','-i',str(dest),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
 count=0;maxerr=0.;outsideerr=0.;peak=0.
 while True:
  data=proc.stdout.read(10*SR*8)
  if not data:break
  y=np.frombuffer(data,'<f4').reshape(-1,2);ids=np.arange(count,count+len(y));mask=np.zeros(len(y),bool)
  for ev in events:mask|=(ids>=ev['start']*SR)&(ids<ev['end']*SR)
  maxerr=max(maxerr,float(np.max(abs(y-expected[count:count+len(y)]))))
  if (~mask).any():outsideerr=max(outsideerr,float(np.max(abs(y[~mask]-baseline[count:count+len(y)][~mask]))))
  assert np.isfinite(y).all();peak=max(peak,float(abs(y).max()));count+=len(y)
 assert proc.wait()==0 and count==3600*SR and maxerr<2.4e-7 and outsideerr==0 and peak<1
 outputs.append({'path':str(dest),'sha256':sha(dest),'seconds':3600,'recipe_max_error':maxerr,'outside_patch_windows_max_error':outsideerr,'sample_peak_dbfs':20*math.log10(peak),'full_decode':True})
 save('replacement-recipe.json',{'date':'2026-11-02','user_request':'the better solution would be to rework those20seconds','status':'Replacement listening candidate; pending user verdict and fresh YouTube claim check','source':str(src),'source_sha256':sha(src),'source_patch_seconds':[24,57],'fully_replaced_source_interval_seconds':[30,51],'donor_source_seconds':[90,123],'donor_fixed_gain_db':20*math.log10(gain),'crossfade_handles_seconds':6,'old_claimed_source_weight_in_core':0,'hour_events':events,'occurrences_replaced':len(events),'existing_source_gains_sfx_schedule_joins_duration_and_closing_fade_preserved':True,'hour_audio_path':str(dest),'originals_preserved':True,'new_video_muxed':False,'no_pitch_or_speed_change':True,'new_generation':False,'claim_clearance':'Unverified; replacing the primary music source does not prove which component triggered the match or guarantee clearance','assistant_listening':False})
 save('validation.json',{'status':'passed','source_boundary_checks':boundary,'output_files':outputs,'all_unaffected_hour_samples_exact':outsideerr==0,'all_hour_samples_compared':True,'claim_check_performed':False,'user_review_pending':True})
 print(json.dumps({'seconds':3600,'replacements':len(events),'unaffected_samples_exact':outsideerr==0,'peak_dbfs':20*math.log10(peak)}),flush=True)
if __name__=='__main__':main()
