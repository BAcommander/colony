"""Mix existing wind into the approved music and reuse the current V2 scene."""
from pathlib import Path
import subprocess,hashlib,json,math,shutil
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];C=H/'cache';C.mkdir(exist_ok=True)
SR=48000;FF=shutil.which('ffmpeg');PROBE=shutil.which('ffprobe')
M=R/'music/below-the-snowline-production-2026-11-01/paired-loop-v1/Below-the-Snowline-paired-loop-9min-v1.flac'
W=R/'music/sfx-library/assets/wind-soft-exterior-01.mp3'
V=R/'music/below-the-snowline-animation-v2/Below-the-Snowline-v2-preview-20s.mp4'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def save(n,x):(H/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def decode(p):
 r=subprocess.run([FF,'-v','error','-i',str(p),'-map','0:a:0','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True)
 assert not r.stderr
 x=np.frombuffer(r.stdout,'<f4').reshape(-1,2);assert np.isfinite(x).all();return x
def audio(name,x):
 raw=C/(name+'.f32');x.astype('<f4').tofile(raw);p=H/name
 codec=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24'] if p.suffix=='.flac' else ['-c:a','libmp3lame','-b:a','192k']
 subprocess.run([FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i',str(raw),*codec,str(p)],check=True)
 return p
def validate_audio(p,x):
 y=decode(p);assert y.shape==x.shape and abs(y).max()<1
 energy=error=0.;maxerr=0.
 for i in range(0,len(x),10*SR):
  a=x[i:i+10*SR].astype(float);e=a-y[i:i+10*SR];energy+=float(np.sum(a*a));error+=float(np.sum(e*e));maxerr=max(maxerr,float(abs(e).max()))
 snr=10*math.log10(energy/max(error,1e-30))
 assert maxerr<2.4e-7 if p.suffix=='.flac' else snr>20
 return {'path':str(p),'sha256':sha(p),'seconds':len(y)/SR,'all_samples_finite_unclipped':True,'recipe_snr_db':snr,'max_recipe_error':maxerr,'sample_peak_dbfs':20*math.log10(float(abs(y).max()))}
def video(name,seconds,audio_path,expected):
 p=H/name
 subprocess.run([FF,'-v','error','-n','-stream_loop','-1','-i',str(V),'-i',str(audio_path),'-map','0:v:0','-map','1:a:0','-t',str(seconds),'-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(SR),'-movflags','+faststart',str(p)],check=True)
 record=validate_audio(p,expected[:seconds*SR])
 def packets(path):
  raw=subprocess.check_output([FF,'-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','framehash','-hash','sha256','pipe:1']).decode()
  return [[s.strip() for s in line.split(',')] for line in raw.splitlines() if line and not line.startswith('#')]
 base=packets(V);out=packets(p);assert len(base)==600 and len(out)==seconds*30
 assert all(row[-1]==base[i%600][-1] for i,row in enumerate(out))
 # Check full rendered file decodes, including reused video and encoded audio.
 subprocess.run([FF,'-v','error','-xerror','-i',str(p),'-f','null','-'],stdout=subprocess.DEVNULL,check=True)
 probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
 vs=next(s for s in probe['streams'] if s['codec_type']=='video')
 assert (vs['width'],vs['height'],vs['r_frame_rate'])==(1280,720,'30/1')
 assert int(vs['nb_frames'])==seconds*30 and abs(float(probe['format']['duration'])-seconds)<.05
 record.update(video_packets_match_repeated_original=True,full_audio_video_decode=True,frames=seconds*30,dimensions=[1280,720])
 print('Verified',name,flush=True);return record
def main():
 assert sha(M)=='987b1509075da8a9202f24a6b765f4e2b6d88d90cb90c28bdaf8719af77b252b'
 assert sha(W)=='324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34'
 assert sha(V)=='8c45915b623a26a4968938c3ae1615ab02640563773d96aa868b3d8bbd641df3'
 dry=decode(M);wind=decode(W);assert len(dry)==540*SR and len(wind)==30*SR
 # The established24s wind cycle uses source1–29s with4s equal-power overlap.
 loop=wind[5*SR:29*SR].copy();k=4*SR;phase=np.arange(k)/k*np.pi/2
 loop[-k:]=(wind[25*SR:29*SR]*np.cos(phase)[:,None]+wind[1*SR:5*SR]*np.sin(phase)[:,None]).astype(np.float32)
 loop*=10**(4.85/20)
 step=float(np.sqrt(np.mean((loop[0].astype(float)-loop[-1])**2)));q=float(np.quantile(np.sqrt(np.mean(np.diff(loop.astype(float),axis=0)**2,axis=1)),.999));assert step<q*1.5
 stem=np.zeros_like(dry);active=np.zeros(len(dry),bool);events=[[20,80],[200,260],[380,440]]
 for start,end in events:
  ids=np.arange(start*SR,end*SR);local=ids-start*SR;n=len(ids)
  env=np.maximum(0,np.minimum(1,np.minimum(local/(8*SR),(n-1-local)/(12*SR))))
  stem[ids]=loop[ids%len(loop)]*env[:,None];active[ids]=True
 wet=dry+stem;assert np.array_equal(wet[~active],dry[~active]) and not stem[~active].any()
 assert np.isfinite(wet).all() and abs(wet).max()<1
 # Wind is zero at both ends, preserving the approved circular music boundary.
 assert np.array_equal(wet[:20*SR],dry[:20*SR]) and np.array_equal(wet[440*SR:],dry[440*SR:])
 outputs=[]
 for name,x in [('Below-the-Snowline-music-and-wind-9min-v1.flac',wet),('Below-the-Snowline-music-and-wind-9min-v1.mp3',wet),('Below-the-Snowline-wind-stem-9min-v1.flac',stem)]:
  p=audio(name,x);outputs.append(validate_audio(p,x));print('Verified',name,flush=True)
 master=H/'Below-the-Snowline-music-and-wind-9min-v1.flac'
 outputs.append(video('Below-the-Snowline-wind-in-scene-2min-v1.mp4',120,master,wet))
 outputs.append(video('Below-the-Snowline-music-and-wind-scene-9min-v1.mp4',540,master,wet))
 save('mix-recipe.json',{'date':'2026-11-02','user_request':'Add wind to Below the Snowline music to hear it in the scene','status':'Listening candidate; new wind balance not approved','music':{'path':str(M),'sha256':sha(M),'gain_db':0,'approval':'Existing nine-minute pair unchanged'},'wind':{'path':str(W),'sha256':sha(W),'source_seconds':30,'source_gain_db':4.85,'gain_basis':'Previously accepted Deepwell wind level; starting point only for this scene','source_trim_seconds':[1,29],'source_overlap_seconds':4,'source_cycle_seconds':24,'events_seconds':events,'event_duration_seconds':60,'quiet_gap_seconds':120,'fade_in_seconds':8,'fade_out_seconds':12,'phase':'Global frame clock modulo24s'},'video':{'path':str(V),'sha256':sha(V),'seconds':20,'repeat':'Existing20s V2 pictures repeated; no new animation or wind-synced visual change','review_status':'Existing V2 artistic review still pending'},'outputs':{'seconds':540,'sample_rate':SR,'channels':2,'opening_or_closing_fade_added':False,'loop_boundary':'Wind absent at both edges; approved music boundary retained'},'assistant_listening':False,'no_paid_generation':True,'originals_preserved':True})
 save('delivery-validation.json',{'status':'passed','outputs':outputs,'all_wind_off_samples_identical_to_approved_music':True,'approved_music_boundary_preserved':True,'wind_cycle_sample_step':step,'wind_cycle_step_p99_9':q,'all_audio_samples_compared':True,'full_video_decode_and_packet_comparison':True,'user_balance_review':'Pending','assistant_listening':False})
 print('PASS: nine-minute wind mix and scene previews ready.',flush=True)
if __name__=='__main__':main()
