from pathlib import Path
import subprocess,json,numpy as np
R=Path(__file__).resolve().parent
ROOT=Path('G:/AI/colony')
OUT=ROOT/'exports/03-glacier-sanctuary/Glacier-Sanctuary-4-Hours-v2-Amber-Refuge.mp3'
SRC=OUT.parent/'source/Amber_Refuge_Beneath_the_Stone_2026-09-27T204853.mp4'
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SR=48000
assert not OUT.exists(), 'Preserve existing output'
raw=subprocess.run([FF,'-v','error','-i',str(SRC),'-vn','-af','atrim=start=29:end=511,asetpts=PTS-STARTPTS','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert len(a)==482*SR
overlap=15*SR
phase=np.arange(overlap,dtype=np.float64)/overlap*np.pi/2
join=(a[-overlap:]*np.cos(phase)[:,None]+a[:overlap]*np.sin(phase)[:,None]).astype(np.float32)
total=14400*SR
enc=subprocess.Popen([FF,'-n','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k','-metadata','title=Glacier Sanctuary - Four Hours',str(OUT)],stdin=subprocess.PIPE)
written=0
peak=0.
def write(segment):
 global written,peak
 for i in range(0,len(segment),SR):
  if written>=total:return
  chunk=segment[i:i+min(SR,total-written)].copy()
  positions=np.arange(written,written+len(chunk))
  gain=10**(-4.7/20)*np.minimum(np.minimum(positions/(10*SR),(total-1-positions)/(20*SR)),1)
  chunk*=gain[:,None]
  peak=max(peak,float(abs(chunk).max()))
  enc.stdin.write(chunk.astype('<f4').tobytes())
  written+=len(chunk)
write(a[:-overlap])
while written<total:
 write(join)
 write(a[overlap:-overlap])
enc.stdin.close()
assert enc.wait()==0
print('Encoded four hours; checking full decode and loudness.',flush=True)
log=(R/'four-hour-loudness.txt').open('wb')
p=subprocess.Popen([FF,'-hide_banner','-nostats','-i',str(OUT),'-af','ebur128=peak=true:framelog=verbose','-f','f32le','-acodec','pcm_f32le','pipe:1'],stdout=subprocess.PIPE,stderr=log)
count=0; decoded_peak=0.
while True:
 data=p.stdout.read(SR*2*4)
 if not data:break
 x=np.frombuffer(data,np.float32)
 assert np.isfinite(x).all()
 count+=len(x);decoded_peak=max(decoded_peak,float(abs(x).max()))
assert p.wait()==0
log.close()
assert count==total*2,(count,total*2)
report={'output':str(OUT),'source':str(SRC),'duration_seconds':14400,'verified_decoded_seconds':count/(SR*2),'full_decode_verified':True,'source_excerpt_seconds':[29,511],'repeat_interval_seconds':467,'crossfade_seconds':15,'crossfade':'equal-power sine/cosine','gain_db':-4.7,'opening_fade_seconds':10,'closing_fade_seconds':20,'sample_rate':SR,'channels':2,'bitrate_kbps':192,'decoded_sample_peak_dbfs':float(20*np.log10(decoded_peak)),'output_bytes':OUT.stat().st_size,'listening_status':'User said loop sounds fine; join approved. Full-length listening not claimed.'}
(R/'four-hour-render.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
print((R/'four-hour-loudness.txt').read_text(errors='replace')[-750:])
