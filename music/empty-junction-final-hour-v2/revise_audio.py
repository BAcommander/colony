"""Reschedule the three approved SFX; preserve the chosen music and gains."""
from pathlib import Path
import json,subprocess,hashlib,shutil,math
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'music/empty-junction-music-v1'
C=H/'cache';C.mkdir(exist_ok=True);E=R/'exports/11-empty-junction';FF=shutil.which('ffmpeg');SR=48000;N=3600*SR
OLD=E/'The-Empty-Junction-1-Hour-final-SFX-v3.flac'
OLDSTEM=P/'delivery-hour-final-sfx-v3/media/The-Empty-Junction-1-Hour-SFX-only-v3.flac'
NEW=E/'The-Empty-Junction-1-Hour-final-SFX-v4.flac'
STEM=E/'The-Empty-Junction-1-Hour-SFX-only-v4.flac'
def save(n,d):(H/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16*1024**2),b''):h.update(b)
 return h.hexdigest()
def decode(p):return np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(p),'-vn','-ac','2','-ar',str(SR),'-f','f32le','pipe:1']),'<f4').reshape(-1,2)
def reader(p):return subprocess.Popen([FF,'-v','error','-i',str(p),'-vn','-ac','2','-ar',str(SR),'-f','f32le','pipe:1'],stdout=subprocess.PIPE)
def schedules(old):
 minutes=[];m=0
 patterns=[[3,2,3,2,2],[2,3,2,2,3],[2,2,3,2,3],[3,2,2,3,2],[2,3,2,3,2]]
 for group in patterns:
  for interval in group:minutes.append(m);m+=interval
 wind=[x*60 for x in minutes];assert len(wind)==25 and m==60
 off=[(s+60,wind[i+1] if i+1<len(wind) else 3600) for i,s in enumerate(wind)]
 train=[]
 for target in [110,510,930,1340,1795,2225,2650,3050,3430]:
  choices=[max(a+10,min(target,b-35,3555)) for a,b in off if a+10<=min(b-35,3555)]
  train.append(min(choices,key=lambda x:abs(x-target)))
 selected=[1,2,3,5,6,7,8,10,11,12,14,15,16,17,19,20,21,22,24]
 doubled={1,5,10,16,21};grit=[]
 for i in selected:
  offsets=[13,37] if i in doubled else [[17,27,35,21][i%4]]
  grit.extend(wind[i]+o for o in offsets)
 assert len(train)==9 and len(set(train))==9 and len(grit)==24
 assert min(np.diff(train))>250
 for t in train:assert any(t>=a and t+25<=b for a,b in off)
 for t in grit:assert any(t>=w and t+12<=w+60 for w in wind)
 return wind,train,grit,minutes
def make_loop(w,gain):
 f=np.arange(24*SR);loop=w[5*SR:29*SR].astype(float).copy();tail=f>=20*SR;t=f[tail]-20*SR
 p=t/(4*SR)*np.pi/2
 loop[tail]=w[25*SR+t]*np.cos(p)[:,None]+w[SR+t]*np.sin(p)[:,None]
 return (loop*10**(gain/20)).astype(np.float32)
def effects(first,count,starts,loop,train,grit,old):
 f=np.arange(first,first+count);env=np.zeros(count);out=np.zeros((count,2),float)
 for start in starts[0]:
  local=f-start*SR;on=(local>=0)&(local<60*SR)
  env[on]=np.maximum(0,np.minimum(1,np.minimum(local[on]/(5*SR),(60*SR-1-local[on])/(8*SR))))
 out[:]=loop[f%(24*SR)]*env[:,None]
 for name,src,duration,ins,outs,events in [('train',train,25,3,6,starts[1]),('grit',grit,12,1,2.5,starts[2])]:
  gain=10**(old[name]['gain_db']/20)
  for start in events:
   loc=f-start*SR;on=(loc>=0)&(loc<duration*SR)
   if not on.any():continue
   e=np.maximum(0,np.minimum(1,np.minimum(loc[on]/(ins*SR),(duration*SR-1-loc[on])/(outs*SR))))
   if name=='grit':e*=env[on]
   out[on]+=src[loc[on]].astype(float)*gain*e[:,None]
 return out.astype(np.float32)
def check_lossless(path,raw):
 p=reader(path);count=0;peak=0.;err=0.
 with raw.open('rb') as f:
  for sec in range(3600):
   a=f.read(SR*8);b=p.stdout.read(SR*8);assert len(a)==len(b)==SR*8
   x=np.frombuffer(a,'<f4');y=np.frombuffer(b,'<f4');assert np.isfinite(y).all()
   peak=max(peak,float(abs(y).max()));err=max(err,float(abs(x-y).max()));count+=SR
  assert not f.read(1) and not p.stdout.read(1) and p.wait()==0
 assert count==N and peak<1 and err<2.4e-7
 return {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'seconds':3600,'frames':count,'finite_unclipped':True,'sample_peak_dbfs':20*math.log10(peak),'maximum_lossless_recipe_error':err}
def main():
 old=json.loads((P/'delivery-hour-final-sfx-v3/mix-recipe.json').read_text());base=json.loads((P/'delivery-hour-v1/mix-recipe.json').read_text())
 assert sha(OLD)=='84a773c68ca1a8d1115c76e2edcc914f8c955c5f60cb31436b1c5718b4982f09'
 assert sha(OLDSTEM)=='71a3f66bca5e93a2462cfa695793c03fbbacf92a3989f45b41ac03cef074d234'
 windpath=P/'sources'/base['sources'][2]['file'];trainpath=P/'sources'/Path(old['train']['file']).name;gritpath=P/'sources'/Path(old['grit']['file']).name
 for p,h in [(windpath,base['sources'][2]['sha256']),(trainpath,old['train']['sha256']),(gritpath,old['grit']['sha256'])]:assert sha(p)==h
 wind,train,grit=map(decode,[windpath,trainpath,gritpath]);assert len(train)==25*SR and len(grit)==12*SR
 loop=make_loop(wind,old['wind']['gain_db']);ws,ts,gs,minutes=schedules(old)
 recipe={'date':'2026-11-01','request':'i think the video is fine but we need to increase the 3 sfx to provide more variance, like they need to be 25% more frequent','visual_feedback':'Video is fine; retain selected V6 treatment and current intro. Only select existing wind/quiet minutes to match revised wind timing.','duration_seconds':3600,'sample_rate':SR,'counts':{'wind':{'before':20,'after':25,'increase_percent':25},'train':{'before':7,'after':9,'increase_percent':(9/7-1)*100},'grit':{'before':19,'after':24,'increase_percent':(24/19-1)*100}},'rounding':'Nearest whole-event counts to 25% more per hour. No playback speed or event duration change.','wind_starts':ws,'wind_minutes':minutes,'train_starts':ts,'grit_starts':gs,'durations':{'wind':60,'train':25,'grit':12},'gain_db':{k:old[k]['gain_db'] for k in ['wind','train','grit']},'fade_seconds':{'wind':[5,8],'train':[3,6],'grit':[1,2.5]},'grit_follows_wind_envelope':True,'wind_source_phase':'Original 24-second source loop follows the global timeline','music':'Approved V3 mix minus its verified old SFX stem plus newly scheduled SFX. Music arrangement, level and closing fade retained within 24-bit quantization. No new music generation, EQ, compression, normalization or stretching.','source_mix':str(OLD),'source_stem':str(OLDSTEM),'source_paths':[str(p) for p in [windpath,trainpath,gritpath]],'source_hashes':[sha(p) for p in [windpath,trainpath,gritpath]]}
 save('mix-recipe.json',recipe)
 oldstarts=([x[0] for x in old['wind']['active_windows_seconds']],[x['start_seconds'] for x in old['train']['events']],[x['start_seconds'] for x in old['grit']['events']]);newstarts=(ws,ts,gs)
 wetraw=C/'mix-v4.f32';stemraw=C/'stem-v4.f32';p=reader(OLD);q=reader(OLDSTEM);old_error=0.;music_error=0.;peak=0.
 with wetraw.open('xb') as wf,stemraw.open('xb') as sf:
  for first in range(0,N,10*SR):
   count=min(10*SR,N-first);a=p.stdout.read(count*8);b=q.stdout.read(count*8);assert len(a)==len(b)==count*8
   previous=np.frombuffer(a,'<f4').reshape(-1,2);oldstem=np.frombuffer(b,'<f4').reshape(-1,2)
   reconstructed=effects(first,count,oldstarts,loop,train,grit,old)
   old_error=max(old_error,float(abs(reconstructed-oldstem).max()));assert old_error<2.5e-7,old_error
   newstem=effects(first,count,newstarts,loop,train,grit,old)
   dry=previous.astype(float)-oldstem;wet=(dry+newstem).astype(np.float32)
   music_error=max(music_error,float(abs((wet.astype(float)-newstem)-dry).max()))
   assert np.isfinite(wet).all() and abs(wet).max()<1;peak=max(peak,float(abs(wet).max()))
   wf.write(wet.tobytes());sf.write(newstem.tobytes())
   if first%(600*SR)==0:print('Rescheduled audio',first//SR,'/3600 seconds',flush=True)
 assert not p.stdout.read(1) and not q.stdout.read(1) and p.wait()==q.wait()==0
 outputs=[]
 for dest,raw in [(NEW,wetraw),(STEM,stemraw)]:
  subprocess.run([FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i',str(raw),'-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',str(dest)],check=True)
  outputs.append(check_lossless(dest,raw));print('Verified',dest.name,flush=True)
 sample=H/'Empty-Junction-more-frequent-SFX-check-6min.mp3'
 subprocess.run([FF,'-v','error','-n','-i',str(NEW),'-t','360','-c:a','libmp3lame','-b:a','192k',str(sample)],check=True)
 save('audio-delivery-validation.json',{'status':'passed','outputs':outputs,'old_stem_reconstruction_max_error':old_error,'dry_music_preservation_max_float_error':music_error,'no_level_or_duration_changes':True,'counts':recipe['counts'],'example':str(sample),'assistant_listening':False})
 print('PASS: frequency-only SFX revision; original music and gains retained',flush=True)
if __name__=='__main__':main()
