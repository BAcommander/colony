from pathlib import Path
import subprocess, json, numpy as np

R=Path(__file__).resolve().parent
OUT=R.parents[2]/'exports/02-basalt-transmission/Basalt-Transmission-2-Hours.mp3'
assert not OUT.exists(), 'Preserve existing delivery; choose a versioned output'
OUT.parent.mkdir(parents=True,exist_ok=True)
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=str(R.parents[2]/'exports/02-basalt-transmission/source/Copper_Dusk_Transmission_2026-09-26T155535.mp4')
SR=48000
raw=subprocess.run([FF,'-v','error','-i',SRC,'-vn','-af',"volume='if(lt(t,345),1,if(lt(t,375),pow(10,-6*(t-345)/600),pow(10,-6/20)))':eval=frame,atrim=start=39:end=596,asetpts=PTS-STARTPTS",'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert len(a)==557*SR
overlap=15*SR
phase=np.arange(overlap,dtype=np.float64)/overlap*np.pi/2
join=(a[-overlap:]*np.cos(phase)[:,None]+a[:overlap]*np.sin(phase)[:,None]).astype(np.float32)
total=7200*SR
encoder=subprocess.Popen([FF,'-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k','-metadata','title=Basalt Transmission - Two Hours','-metadata','comment=Listening version: 15-second equal-power crossfades; opening and closing fades.',str(OUT)],stdin=subprocess.PIPE)
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
report={'duration_seconds':7200,'sample_rate':SR,'channels':2,'mp3_bitrate_kbps':192,'source_excerpt_seconds':[39,596],'overlap_seconds':15,'crossfade':'equal-power sine/cosine','gain':.7*10**(3.5/20),'gain_vs_accepted_preview_db':3.5,'level_adjustment':'0 dB until source 5:45, ramp to -6 dB at 6:15, held afterward','target_lufs':-17.7,'fade_in_seconds':10,'fade_out_seconds':20,'preencode_peak_dbfs':float(20*np.log10(peak)),'output_bytes':OUT.stat().st_size}
(R/'two-hour-render.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
# Decode all audio to verify exact playable length and finite sample data.
log=(R/'two-hour-loudness.txt').open('wb')
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
(R/'two-hour-render.json').write_text(json.dumps(report,indent=2))
print('Verified full two-hour decode:',OUT,flush=True)

print((R/'two-hour-loudness.txt').read_text(errors='replace')[-900:])
