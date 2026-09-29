from pathlib import Path
import subprocess, json, numpy as np

R=Path(__file__).resolve().parent
OUT=Path('G:/AI/colony/exports/02-basalt-transmission/Basalt-Transmission-2-Hours-v2-section-removed.mp3')
assert not OUT.exists(), 'Preserve existing revision'
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'G:\AI\colony\exports\02-basalt-transmission\source\Copper_Dusk_Transmission_2026-09-26T155535.mp4'
SR=48000
raw=subprocess.run([FF,'-v','error','-i',SRC,'-vn','-af',"volume='if(lt(t,345),1,if(lt(t,375),pow(10,-6*(t-345)/600),pow(10,-6/20)))':eval=frame,atrim=start=39:end=596,asetpts=PTS-STARTPTS",'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert len(a)==557*SR
# Exclude source [4:17,4:48), including ten seconds either side of 4:27-4:38.
# Crossfade only retained samples: source 4:05-4:17 and 4:48-5:00.
left=a[:(257-39)*SR];right=a[(288-39)*SR:]
inner=12*SR
phase_inner=np.arange(inner,dtype=np.float64)/inner*np.pi/2
blend=(left[-inner:]*np.cos(phase_inner)[:,None]+right[:inner]*np.sin(phase_inner)[:,None]).astype(np.float32)
a=np.concatenate([left[:-inner],blend,right[inner:]])
assert len(a)==514*SR
preview_gain=.7*10**(3.5/20)
def preview(data,name):
 p=subprocess.run([FF,'-n','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k',str(OUT.parent/name)],input=(data*preview_gain).astype('<f4').tobytes(),capture_output=True,check=True)
preview(a[181*SR:243*SR],'Basalt-v2-new-edit-audition.mp3')
print('New edit audition ready; crossfade at 0:25-0:37.',flush=True)
overlap=15*SR
phase=np.arange(overlap,dtype=np.float64)/overlap*np.pi/2
join=(a[-overlap:]*np.cos(phase)[:,None]+a[:overlap]*np.sin(phase)[:,None]).astype(np.float32)
preview(np.concatenate([a[-40*SR:-overlap],join,a[overlap:40*SR]]),'Basalt-v2-loop-join-audition.mp3')
total=7200*SR
encoder=subprocess.Popen([FF,'-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k','-metadata','title=Basalt Transmission - Two Hours - Revised Section','-metadata','comment=Listening version: 15-second equal-power crossfades; opening and closing fades.',str(OUT)],stdin=subprocess.PIPE)
written=0; peak=0.0
def write(segment):
 global written,peak
 for i in range(0,len(segment),SR):
  if written>=total:return
  chunk=segment[i:i+min(SR,total-written)].copy()
  positions=np.arange(written,written+len(chunk))
  gain=(.7*10**(3.5/20))*np.minimum(np.minimum(positions/(10*SR),(total-1-positions)/(20*SR)),1)
  chunk*=gain[:,None]
  peak=max(peak,float(np.max(abs(chunk))))
  encoder.stdin.write(chunk.astype('<f4').tobytes());written+=len(chunk)
write(a[:-overlap])
while written<total:
 write(join)
 write(a[overlap:-overlap])
encoder.stdin.close()
assert encoder.wait()==0
assert written==total
report={'duration_seconds':7200,'sample_rate':SR,'channels':2,'mp3_bitrate_kbps':192,'source_excerpt_seconds':[39,596],'excluded_source_seconds':[257,288],'original_claim_source_seconds':[267,278],'internal_crossfade_seconds':12,'internal_crossfade_retained_source_windows':[[245,257],[288,300]],'edited_section_seconds':514,'repeat_interval_seconds':499,'internal_edit_output_first_seconds':[206,218],'overlap_seconds':15,'crossfade':'equal-power sine/cosine','gain':.7*10**(3.5/20),'gain_vs_accepted_preview_db':3.5,'level_adjustment':'0 dB until source 5:45, ramp to -6 dB at 6:15, held afterward','target_lufs':-17.7,'fade_in_seconds':10,'fade_out_seconds':20,'preencode_peak_dbfs':float(20*np.log10(peak)),'output_bytes':OUT.stat().st_size}
(R/'two-hour-v2-render.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
# Decode all audio to verify exact playable length and finite sample data.
log=(R/'two-hour-v2-loudness.txt').open('wb')
p=subprocess.Popen([FF,'-hide_banner','-nostats','-i',str(OUT),'-af','ebur128=peak=true:framelog=verbose','-f','f32le','-acodec','pcm_f32le','pipe:1'],stdout=subprocess.PIPE,stderr=log)
count=0; decoded_peak=0.0
while True:
 data=p.stdout.read(SR*2*4)
 if not data:break
 x=np.frombuffer(data,np.float32)
 assert np.isfinite(x).all()
 count+=len(x);decoded_peak=max(decoded_peak,float(np.max(abs(x))))
assert p.wait()==0
log.close()
assert count==total*2,(count,total*2)
report.update({'verified_decoded_seconds':count/(SR*2),'decoded_sample_peak_dbfs':float(20*np.log10(decoded_peak)),'full_decode_verified':True})
(R/'two-hour-v2-render.json').write_text(json.dumps(report,indent=2))
print('Verified full two-hour decode:',OUT,flush=True)

print((R/'two-hour-v2-loudness.txt').read_text(errors='replace')[-900:])
