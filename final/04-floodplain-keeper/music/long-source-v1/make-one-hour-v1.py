"""Render one hour using the user-approved Shelter Recovery join recipe."""
from pathlib import Path
import hashlib,json,subprocess,re
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
REPORT=Path(__file__).resolve().parent
FF=r'C:/Program Files/ShareX/ffmpeg.exe'
config=json.loads((REPORT/'audition-v1.json').read_text())
SRC=ROOT/config['source']
DEST=ROOT/'exports/04-floodplain-keeper/Floodplain-Keeper-Shelter-Recovery-1-Hour-v1.mp3'
assert not DEST.exists(),f'Preserve existing export: {DEST}'
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()
assert source_hash=='58306a7d75ecfc3c0fc829f7ed7c611c69421790e06940f4e0f50c6260aa3d78'
SR=48000;TOTAL=3600*SR;FADE_IN=10;FADE_OUT=20
start,end=config['start_seconds'],config['end_seconds']
raw=subprocess.run([FF,'-v','error','-i',str(SRC),'-map','0:a:0','-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert len(a)==(end-start)*SR and np.isfinite(a).all()
n=config['overlap_seconds']*SR
phase=np.linspace(0,np.pi/2,n,dtype=np.float64)
blend=(a[-n:]*np.cos(phase)[:,None]+a[:n]*np.sin(phase)[:,None]).astype(np.float32)
p=subprocess.Popen([FF,'-n','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k','-metadata','title=Floodplain Keeper - Shelter Recovery - One Hour','-metadata','comment=Approved eight-second equal-power joins; single opening and closing fades.',str(DEST)],stdin=subprocess.PIPE)
written=0;prepeak=0.;joins=[]
def write(part):
 global written,prepeak
 for offset in range(0,len(part),SR):
  if written==TOTAL:return
  b=part[offset:offset+min(SR,TOTAL-written)].copy()
  positions=np.arange(written,written+len(b))
  env=np.minimum(np.minimum(positions/(FADE_IN*SR),(TOTAL-1-positions)/(FADE_OUT*SR)),1).clip(0,1)
  b*=(10**(config['gain_db']/20)*env[:,None]).astype(np.float32)
  assert np.isfinite(b).all()
  prepeak=max(prepeak,float(abs(b).max()))
  p.stdin.write(b.astype('<f4').tobytes());written+=len(b)
write(a[:-n])
while written<TOTAL:
 joins.append([written/SR,min(written+n,TOTAL)/SR])
 write(blend)
 write(a[n:-n])
p.stdin.close();assert p.wait()==0 and written==TOTAL
print('Encoded one hour. Full decode and loudness verification starting.',flush=True)
# Count decoded samples and inspect every sample without retaining the full hour in RAM.
dec=subprocess.Popen([FF,'-v','error','-i',str(DEST),'-map','0:a:0','-ac','2','-ar',str(SR),'-f','f32le','pipe:1'],stdout=subprocess.PIPE)
bytecount=0;decoded_peak=0.
while True:
 chunk=dec.stdout.read(SR*8)
 if not chunk:break
 assert len(chunk)%8==0
 data=np.frombuffer(chunk,np.float32)
 assert np.isfinite(data).all()
 decoded_peak=max(decoded_peak,float(abs(data).max()));bytecount+=len(chunk)
assert dec.wait()==0 and bytecount==TOTAL*8,(bytecount,TOTAL*8)
assert decoded_peak<1,'Clipping detected'
loud=subprocess.run([FF,'-hide_banner','-nostats','-i',str(DEST),'-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True,check=True)
log=loud.stderr.decode(errors='replace')
(REPORT/'one-hour-loudness.txt').write_text('\n'.join(line.rstrip() for line in log.splitlines())+'\n')
summary=log.rsplit('Summary:',1)[-1]
integrated=float(re.search(r'I:\s+(-?[\d.]+) LUFS',summary).group(1))
truepeak=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS',summary).group(1))
assert truepeak<0
report={'date':'2026-09-29','file':DEST.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'bytes':DEST.stat().st_size,'source':config['source'],'source_sha256':source_hash,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_start_seconds':start,'source_end_seconds':end,'overlap_seconds':config['overlap_seconds'],'repeat_interval_seconds':config['repeat_interval_seconds'],'curve':config['curve'],'gain_db':config['gain_db'],'opening_fade_seconds':FADE_IN,'closing_fade_seconds':FADE_OUT,'encoded_format':'MP3 192 kb/s, stereo 48 kHz','decoded_samples_per_channel':bytecount//8,'decoded_seconds':bytecount/8/SR,'full_decode':'passed; every sample finite; exact one-hour sample count','integrated_lufs':integrated,'true_peak_dbtp':truepeak,'decoded_sample_peak_dbfs':20*np.log10(decoded_peak),'preencode_peak_dbfs':20*np.log10(prepeak),'join_windows_seconds':joins,'user_feedback':'transition sounds totally fine, make the hour long version?','approval_scope':'Short join approved and one-hour assembly requested. No full-hour listening review claimed.','assistant_listening':False,'storage':'Local ignored export; not backed up by Git.'}
(REPORT/'one-hour-delivery-v1.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
