from pathlib import Path
import subprocess, json, numpy as np

R=Path(__file__).resolve().parent
OUT=R/'Lunar-Observatory-Night-Watch-1-Hour.mp3'
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'C:\Users\jazzs\Downloads\Lunar_Observatory_Night_Watch_2026-09-25T230455.mp4'
SR=48000
raw=subprocess.run([FF,'-v','error','-i',SRC,'-vn','-af','atrim=start=20:end=330,asetpts=PTS-STARTPTS','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert len(a)==310*SR
overlap=15*SR
phase=np.arange(overlap,dtype=np.float64)/overlap*np.pi/2
join=(a[-overlap:]*np.cos(phase)[:,None]+a[:overlap]*np.sin(phase)[:,None]).astype(np.float32)
total=3600*SR
encoder=subprocess.Popen([FF,'-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k','-metadata','title=Lunar Observatory Night Watch — One Hour','-metadata','comment=Listening version: 15-second equal-power crossfades; opening and closing fades.',str(OUT)],stdin=subprocess.PIPE)
written=0; peak=0.0
def write(segment):
 global written,peak
 for i in range(0,len(segment),SR):
  if written>=total:return
  chunk=segment[i:i+min(SR,total-written)].copy()
  positions=np.arange(written,written+len(chunk))
  gain=.7*np.minimum(np.minimum(positions/(10*SR),(total-1-positions)/(20*SR)),1)
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
report={'duration_seconds':3600,'sample_rate':SR,'channels':2,'mp3_bitrate_kbps':192,'source_excerpt_seconds':[20,330],'overlap_seconds':15,'crossfade':'equal-power sine/cosine','gain':.7,'fade_in_seconds':10,'fade_out_seconds':20,'preencode_peak_dbfs':float(20*np.log10(peak)),'output_bytes':OUT.stat().st_size}
(R/'one-hour-render.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
# Decode all audio to verify exact playable length and finite sample data.
p=subprocess.Popen([FF,'-v','error','-i',str(OUT),'-f','f32le','-acodec','pcm_f32le','pipe:1'],stdout=subprocess.PIPE)
count=0; decoded_peak=0.0
while True:
 data=p.stdout.read(SR*2*4)
 if not data:break
 x=np.frombuffer(data,np.float32)
 assert np.isfinite(x).all()
 count+=len(x);decoded_peak=max(decoded_peak,float(np.max(abs(x))))
assert p.wait()==0
assert count==total*2,(count,total*2)
report.update({'verified_decoded_seconds':count/(SR*2),'decoded_sample_peak_dbfs':float(20*np.log10(decoded_peak)),'full_decode_verified':True})
(R/'one-hour-render.json').write_text(json.dumps(report,indent=2))
print('Verified full one-hour decode:',OUT,flush=True)
