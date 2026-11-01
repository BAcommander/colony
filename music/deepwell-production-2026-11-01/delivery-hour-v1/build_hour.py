"""Extend the accepted Deepwell balance from original sources, not review loops."""
from pathlib import Path
import sys,json,subprocess,shutil,math
import numpy as np
H=Path(__file__).resolve().parent;P=H.parent;R=H.parents[2]
sys.path.insert(0,str(P))
from prepare_samples import decode,sha,measure,SR,FF
from build_combined_review import loop
C=H/'cache';C.mkdir(exist_ok=True);E=R/'exports/12-deepwell-station';N=3600*SR
def save(n,x):(H/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def schedules():
 music=[];start=0;idx=0
 while start<3600:
  which=idx%2;source_in=0 if idx==0 else 4;source_out=224 if which==0 else 220
  length=source_out-source_in;fade_in=0 if idx==0 else 20 if which==1 else 28;fade_out=20 if which==0 else 28
  music.append({'track':'A' if which==0 else 'B','index':which,'source_in':source_in,'source_out':source_out,'start':start,'natural_end':start+length,'output_end':min(3600,start+length),'fade_in':fade_in,'fade_out':fade_out})
  start+=length-fade_out;idx+=1
 patterns=[
 {'water':[[25,75],[185,255],[320,375],[440,480]],'wind':[[105,165],[360,420]],'pump':[[80,100],[275,295],[420,440]]},
 {'water':[[15,70],[170,225],[305,375],[430,480]],'wind':[[90,150],[345,405]],'pump':[[70,90],[255,275],[405,425]]},
 {'water':[[35,95],[190,245],[310,360],[440,480]],'wind':[[115,175],[350,410]],'pump':[[95,115],[265,285],[415,435]]},
 {'water':[[20,70],[175,245],[300,350],[435,480]],'wind':[[100,160],[345,405]],'pump':[[75,95],[255,275],[410,430]]}]
 order=[0,1,2,3,1,3,2,1];events={name:[] for name in ['water','wind','pump']}
 for block,which in enumerate(order):
  for name in events:
   for a,b in patterns[which][name]:
    a+=block*480;b+=block*480
    if a<3600:events[name].append([a,min(b,3600)])
 for a,b in events['pump']:
  assert b-a==20
  for name in ['water','wind']:assert all(b<=lo or a>=hi for lo,hi in events[name])
 assert all(b-a==60 for a,b in events['wind'])
 return music,events,order
def audio_reader(path):return subprocess.Popen([FF,'-v','error','-i',str(path),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
def validate(path,raw,lossless):
 p=audio_reader(path);n=0;peak=err=energy=error=0.
 with raw.open('rb') as ref:
  while True:
   a=ref.read(SR*8);b=p.stdout.read(SR*8)
   if not a:assert not b;break
   assert len(a)==len(b)==SR*8
   x=np.frombuffer(a,'<f4');y=np.frombuffer(b,'<f4');assert np.isfinite(y).all()
   delta=x.astype(float)-y;err=max(err,float(abs(delta).max()));peak=max(peak,float(abs(y).max()));energy+=float(np.sum(x.astype(float)**2));error+=float(np.sum(delta**2));n+=SR
 assert p.wait()==0 and n==N and peak<1
 snr=10*math.log10(energy/error)
 assert err<2.4e-7 if lossless else snr>20
 return {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'seconds':3600,'sample_frames_per_channel':n,'all_finite':True,'clipping_samples':0,'sample_peak_dbfs':20*math.log10(peak),'full_sample_recipe_max_error':err,'full_sample_recipe_snr_db':snr}
def main():
 E.mkdir(parents=True,exist_ok=True)
 approved=json.loads((P/'combined-review-v4/mix-recipe.json').read_text());intake=json.loads((P/'sample-intake.json').read_text());prior=json.loads((P/'combined-review-v4/delivery-validation.json').read_text())
 music_sources=[];fingerprint={}
 for item in intake['sources']:
  assert sha(item['source_copy'])==item['source_sha256'];music_sources.append(decode(item['source_copy']));fingerprint[item['source_copy']]=item['source_sha256']
 materials={};loop_records={}
 for name in ['water','wind']:
  item=approved[name];assert sha(item['local_copy'])==item['sha256'];fingerprint[item['local_copy']]=item['sha256']
  spec=item['loop'];materials[name],loop_records[name]=loop(decode(item['local_copy']),*spec['trim'],spec['overlap_seconds'],spec['gain_db'])
 pump=approved['pump'];assert sha(pump['source'])==pump['sha256'];fingerprint[pump['source']]=pump['sha256']
 materials['pump']=decode(pump['source'])*10**(pump['gain_db']/20)
 golden_path=P/'combined-review-v4/Deepwell-both-music-water-wind-pump-8min-v4.flac'
 assert sha(golden_path)==next(x['sha256'] for x in prior['outputs'] if x['path']==str(golden_path));golden=decode(golden_path)
 music,events,order=schedules();gains=approved['music']['gains_db'];raws={k:C/(k+'-hour.f32') for k in ['mix','dry','sfx']}
 save('mix-recipe.json',{'date':'2026-11-01','user_request':'yeah that sounds good now, lets get the 1 hour version ready','approval_scope':'Current balance accepted and hour extension requested; no claim of a full-hour listening session or new animation approval.','seconds':3600,'sample_rate':SR,'channels':2,'source_hashes':fingerprint,'music_gain_db':gains,'music_schedule':music,'crossfades':'A→B20s, B→A28s, equal-power cosine/sine; same source regions as accepted review','sfx_gain_db':{'water':approved['water']['loop']['gain_db'],'wind':approved['wind']['loop']['gain_db'],'pump':pump['gain_db']},'sfx_events':events,'sfx_event_counts':{k:len(v) for k,v in events.items()},'sfx_fade_seconds':{'water':[8,12],'wind':[8,12],'pump':[3,5]},'source_loops':loop_records,'sfx_schedule_design':'First eight minutes retain accepted event timing. Later eight-minute blocks use staggered patterns with comparable event density; pump remains in exterior-sound gaps. Short source loops follow the global clock independently of music joins.','sfx_block_pattern_order':order,'closing_fade_seconds':20,'production_opening_fade_baked':False,'initial_music':'First source retains its generated entrance; no new production opening fade. Apply current Colony opening once during video assembly.','review_closing_fade_removed':True,'no_eq_compression_stretching_or_new_generation':True,'new_4k_video':False})
 maxprefix=0.;peak=0.;silent_samples=0;join_sums={};join_ref={}
 handles={k:p.open('xb') for k,p in raws.items()}
 try:
  for first in range(0,N,10*SR):
   count=min(10*SR,N-first);f=np.arange(first,first+count);dry=np.zeros((count,2),np.float32)
   for seg in music:
    loc=f-seg['start']*SR;length=(seg['source_out']-seg['source_in'])*SR;on=(loc>=0)&(loc<length)
    if not on.any():continue
    local=loc[on];env=np.ones(len(local))
    if seg['fade_in']:
     k=seg['fade_in']*SR;head=local<k;env[head]*=np.sin(local[head]/k*np.pi/2)
    if seg['fade_out']:
     k=seg['fade_out']*SR;tail=local>=length-k;env[tail]*=np.cos((local[tail]-(length-k))/k*np.pi/2)
    src=music_sources[seg['index']][seg['source_in']*SR+local]
    dry[on]+=(src*10**(gains[seg['index']]/20)*env[:,None]).astype(np.float32)
   stem=np.zeros_like(dry);active=np.zeros(count,bool)
   for name in ['water','wind','pump']:
    ins,outs=(3,5) if name=='pump' else (8,12)
    for a,b in events[name]:
     loc=f-a*SR;length=(b-a)*SR;on=(loc>=0)&(loc<length)
     if not on.any():continue
     active|=on;local=loc[on];env=np.maximum(0,np.minimum(1,np.minimum(local/(ins*SR),(length-1-local)/(outs*SR))))
     phase=local if name=='pump' else f[on]%len(materials[name])
     stem[on]+=materials[name][phase]*env[:,None]
   wet=dry+stem
   if first<470*SR:
    take=min(count,470*SR-first);maxprefix=max(maxprefix,float(np.max(abs(wet[:take]-golden[first:first+take]))));assert maxprefix<1e-6,('Accepted mix changed',maxprefix)
   closing=np.minimum(1,(N-1-f)/(20*SR)).astype(np.float32)
   for name,data in [('mix',wet),('dry',dry),('sfx',stem)]:
    data*=closing[:,None];assert np.isfinite(data).all() and abs(data).max()<1;handles[name].write(data.tobytes())
   assert np.array_equal(wet[~active],dry[~active]) and not stem[~active].any();silent_samples+=int((~active).sum())*2
   peak=max(peak,float(abs(wet).max()))
   if first%(600*SR)==0:print('Rendered',first//SR,'/3600 seconds',flush=True)
 finally:
  for h in handles.values():h.close()
 assert maxprefix<1e-6
 # All later dry music handovers must repeat their corresponding accepted join.
 dry=np.memmap(raws['dry'],dtype='<f4',mode='r',shape=(N,2));joins=[]
 for seg in music[1:]:
  a=seg['start'];length=seg['fade_in'];b=a+length
  if b>3580:continue
  kind='A-to-B' if seg['track']=='B' else 'B-to-A';piece=dry[a*SR:b*SR]
  if kind not in join_ref:join_ref[kind]=piece.copy()
  else:assert np.array_equal(piece,join_ref[kind]),('Changed repeated join',kind,a)
  joins.append({'kind':kind,'start':a,'end':b,'identical_to_first_join':True})
 outputs=[]
 for name,kind,ext in [('Deepwell-Station-1-Hour-v1','mix','flac'),('Deepwell-Station-1-Hour-v1','mix','mp3'),('Deepwell-Station-1-Hour-dry-music-v1','dry','flac'),('Deepwell-Station-1-Hour-SFX-only-v1','sfx','flac')]:
  dest=E/(name+'.'+ext);args=[FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i',str(raws[kind])]
  args+=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24'] if ext=='flac' else ['-c:a','libmp3lame','-b:a','192k']
  subprocess.run(args+[str(dest)],check=True);entry=validate(dest,raws[kind],ext=='flac');entry['kind']=kind;outputs.append(entry);print('Full decode/recipe verified:',dest.name,flush=True)
 levels=measure(E/'Deepwell-Station-1-Hour-v1.flac','deepwell-final-hour-v1');assert levels['tp']<-2
 for path,digest in fingerprint.items():assert sha(path)==digest
 save('delivery-validation.json',{'status':'passed','outputs':outputs,'full_mix_measurements':levels,'source_hashes_unchanged':True,'accepted_first470_seconds_max_absolute_error':maxprefix,'prefix_note':'Compare to accepted v4 FLAC before its ten-second review closing fade. Quantization differences under1e-6; no musical or SFX gain change.','all_repeated_dry_joins_exact':joins,'sfx_off_samples_exact_dry':silent_samples,'all_audio_frames_compared':True,'samples_per_channel':N,'closing_fade_seconds':20,'last_sample_zero':True,'assistant_listening':False,'full_hour_user_review':'not yet reported','new_video_export':False})
 print('PASS: exact one-hour mixed MP3/FLAC, dry music and SFX stems',flush=True)
if __name__=='__main__':main()
