"""A/B/A music audition with independently scheduled reused water and wind."""
from prepare_samples import H,S,V,C,FF,SR,sha,save,decode,measure,rmsdb
from pathlib import Path
import json,subprocess,shutil,math
import numpy as np
R=H.parents[1];D=H/'combined-review-v1';D.mkdir(exist_ok=True)
def record(n,d):(D/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def loop(src,start,end,overlap,gain):
 n=round((end-start-overlap)*SR);x=src[round((start+overlap)*SR):round(end*SR)].astype(float).copy()
 cross=round(overlap*SR);phase=np.arange(cross)/cross*np.pi/2
 x[-cross:]=src[round((end-overlap)*SR):round(end*SR)]*np.cos(phase)[:,None]+src[round(start*SR):round((start+overlap)*SR)]*np.sin(phase)[:,None]
 x=(x*10**(gain/20)).astype(np.float32);assert len(x)==n
 seam=float(np.sqrt(np.mean((x[0].astype(float)-x[-1])**2)))
 differences=np.sqrt(np.mean(np.diff(x.astype(float),axis=0)**2,axis=1));ordinary=float(np.quantile(differences,.999))
 assert seam<=ordinary*1.5+1e-7
 return x,{'seconds':n/SR,'trim':[start,end],'overlap_seconds':overlap,'gain_db':gain,'seam_sample_rms_step':seam,'ordinary_step_99_9_percentile':ordinary}
def write_audio(path,x):
 args=[FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0']
 args+=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24'] if path.suffix=='.flac' else ['-c:a','libmp3lame','-b:a','192k']
 subprocess.run(args+[str(path)],input=x.astype('<f4').tobytes(),check=True)
 y=decode(path);assert y.shape==x.shape and np.isfinite(y).all() and abs(y).max()<1
 error=x.astype(float)-y;snr=float(10*np.log10(np.sum(x.astype(float)**2)/np.sum(error**2)));maxerror=float(abs(error).max())
 assert maxerror<2.4e-7 if path.suffix=='.flac' else snr>20
 return {'path':str(path),'sha256':sha(path),'seconds':len(x)/SR,'full_decode':True,'finite_unclipped':True,'sample_peak_dbfs':20*math.log10(float(abs(y).max())),'gain_recipe_snr_db':snr,'max_absolute_error':maxerror}
def main():
 intake=json.loads((H/'sample-intake.json').read_text());sources=[]
 for item in intake['sources']:
  assert sha(item['source_copy'])==item['source_sha256'];sources.append(decode(item['source_copy']))
 water_source=R/'final/09-offshore-night-office/music/water-mix-v1/Clear_ocean_water_re_#1-1791650516724.mp3'
 wind_source=R/'music/empty-junction-music-v1/sources/Soft_wind_moving_thr_#4-1793463971195.mp3'
 water_hash='7ad78fbee2c965c4ec6e4372d38898b89d5fd77bd4dc3d2adf2b987bf9a7b2c2';wind_hash='324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34'
 for p,h in [(water_source,water_hash),(wind_source,wind_hash)]:
  assert sha(p)==h;dest=S/p.name
  if not dest.exists():shutil.copy2(p,dest)
  assert sha(dest)==h
 water=decode(S/water_source.name);wind=decode(S/wind_source.name)
 seconds=480;n=seconds*SR;dry=np.zeros((n,2),np.float32)
 gains=[r['audition']['fixed_gain_db'] for r in intake['sources']]
 segments=[{'track':'A','source_in':0,'source_out':224,'start':0,'fade_in':0,'fade_out':20},
 {'track':'B','source_in':4,'source_out':220,'start':204,'fade_in':20,'fade_out':28},
 {'track':'A','source_in':4,'source_out':224,'start':392,'fade_in':28,'fade_out':0}]
 for seg in segments:
  idx=0 if seg['track']=='A' else 1;start=int(seg['start']*SR);length=int((seg['source_out']-seg['source_in'])*SR);count=min(length,n-start);local=np.arange(count)
  env=np.ones(count)
  if seg['fade_in']:
   k=int(seg['fade_in']*SR);env[:min(k,count)]*=np.sin(local[:min(k,count)]/k*np.pi/2)
  if seg['fade_out']:
   k=int(seg['fade_out']*SR);tail=local>=length-k;env[tail]*=np.cos((local[tail]-(length-k))/k*np.pi/2)
  gain=10**(gains[idx]/20);piece=sources[idx][int(seg['source_in']*SR):int(seg['source_in']*SR)+count]
  dry[start:start+count]+=(piece*gain*env[:,None]).astype(np.float32)
 print('Built both music joins without stretching or normalization',flush=True)
 water_loop,water_loop_record=loop(water,1,29,2,-12.9)
 wind_loop,wind_loop_record=loop(wind,1,29,4,1.85)
 events={'water':[[25,75],[185,255],[320,375],[440,480]],'wind':[[105,165],[360,420]]}
 layers={}
 for name,material,ins,outs in [('water',water_loop,8,12),('wind',wind_loop,8,12)]:
  layer=np.zeros((n,2),np.float32)
  for start,end in events[name]:
   first=int(start*SR);last=int(end*SR);f=np.arange(first,last);local=f-first;length=last-first
   env=np.maximum(0,np.minimum(1,np.minimum(local/(ins*SR),(length-1-local)/(outs*SR))))
   layer[first:last]=material[f%len(material)]*env[:,None]
  layers[name]=layer
 stem=layers['water']+layers['wind'];wet=dry+stem
 closing=np.ones(n,np.float32);closing[-10*SR:]=np.linspace(1,0,10*SR,dtype=np.float32)
 for x in [dry,wet,stem]:x*=closing[:,None]
 assert np.isfinite(wet).all() and abs(wet).max()<1
 off=np.ones(n,bool)
 for name in events:
  for a,b in events[name]:off[a*SR:b*SR]=False
 assert np.array_equal(dry[off],wet[off]);assert not stem[off].any()
 quiet_error=float(np.max(abs((wet.astype(float)-stem)-dry)))
 recipe={'date':'2026-11-01','user_request':'lets use both like we did with junction, we also had a water SFX we made before right? should be in the repo, and what about the wind we had too? can we combine it all?','status':'Combined listening candidate; both tracks selected for use, new joins and SFX balance unapproved','seconds':seconds,'music':{'source_intake':'../sample-intake.json','gains_db':gains,'segments':segments,'joins_seconds':[[204,224],[392,420]],'crossfade_curve':'Equal-power cosine/sine','trim_reason':'A strong terminal fade begins around225s. B falls gradually through its final minute; the longer B-to-A overlap fills the late tail. Subsequent source entrances begin at4s to bypass initial near-silence. These are listening candidates, not guaranteed musical joins.'},'water':{'source':str(water_source),'local_copy':str(S/water_source.name),'sha256':water_hash,'reuse':'Shoreless gentle rolling/rippling exterior water, not a newly generated pump sound','nominal_isolated_lufs_before_envelope':-40.0,'loop':water_loop_record,'events':events['water'],'fade_in_seconds':8,'fade_out_seconds':12},'wind':{'source':str(wind_source),'local_copy':str(S/wind_source.name),'sha256':wind_hash,'reuse':'Junction soft wind; source gain 6dB lower for this sheltered-gallery audition','nominal_isolated_lufs_before_envelope':-41.0,'loop':wind_loop_record,'events':events['wind'],'fade_in_seconds':8,'fade_out_seconds':12},'source_viewpoint':'Exterior sounds heard quietly from the sheltered gallery; water and wind independently scheduled','effects_period_seconds':{'water':26,'wind':24},'sfx_fades_inside_events':True,'ending':'One ten-second review closing fade; no production opening or extra opening fade','processing':'Fixed gains and fades only. No EQ, compression, pitch shift, time stretch, or paid generation.','assistant_listening':False,'no_effects_off_window_samples_match_dry_exactly':True,'mixed_minus_stem_vs_dry_max_float_error':quiet_error}
 record('mix-recipe.json',recipe)
 outputs=[]
 for file,data in [('Deepwell-both-music-water-wind-8min-v1.flac',wet),('Deepwell-both-music-water-wind-8min-v1.mp3',wet),('Deepwell-both-music-dry-8min-v1.flac',dry),('Deepwell-water-wind-only-8min-v1.flac',stem)]:
  outputs.append(write_audio(D/file,data));print('Verified',file,flush=True)
 examples=[]
 for file,data,a,b in [('Deepwell-quick-water-wind-check-2min-v1.mp3',wet,20,140),('Deepwell-A-to-B-dry-join-90s-v1.mp3',dry,180,270),('Deepwell-B-to-A-dry-join-90s-v1.mp3',dry,372,462)]:
  result=write_audio(D/file,data[a*SR:b*SR]);result['full_mix_range_seconds']=[a,b];examples.append(result)
 levels=measure(D/'Deepwell-both-music-water-wind-8min-v1.flac','deepwell-combined-v1');assert levels['tp']<-2
 record('delivery-validation.json',{'status':'passed','outputs':outputs,'examples':examples,'full_mix_measurements':levels,'both_original_music_hashes_unchanged':all(sha(x['source_copy'])==x['source_sha256'] for x in intake['sources']),'original_sfx_hashes_unchanged':sha(water_source)==water_hash and sha(wind_source)==wind_hash,'source_period_boundary_checks':[water_loop_record,wind_loop_record],'full_decode_and_recipe_comparison':True,'assistant_listening':False,'user_balance_join_review':'pending'})
 print('PASS: combined A/B/A review, separate dry/stem and both join auditions',flush=True)
if __name__=='__main__':main()
