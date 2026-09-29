"""Reproduce Floodplain candidate auditions without overwriting existing media."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
REPORT=Path(__file__).resolve().parent
OUT=ROOT/'exports/04-floodplain-keeper'
FF=r'C:/Program Files/ShareX/ffmpeg.exe'
SRC=OUT/'source/Shelter_Recovery_2026-09-29T165637.mp4'
SR=48000
START,END,OVERLAP=11,410,8
GAIN_DB=-4.7
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='58306a7d75ecfc3c0fc829f7ed7c611c69421790e06940f4e0f50c6260aa3d78'
raw=subprocess.run([FF,'-v','error','-i',str(SRC),'-map','0:a:0','-af',f'atrim=start={START}:end={END},asetpts=PTS-STARTPTS','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert len(a)==(END-START)*SR
n=OVERLAP*SR
phase=np.linspace(0,np.pi/2,n,dtype=np.float64)
blend=(a[-n:]*np.cos(phase)[:,None]+a[:n]*np.sin(phase)[:,None]).astype(np.float32)
join=np.concatenate([a[-(25+OVERLAP)*SR:-n],blend,a[n:(OVERLAP+25)*SR]])
reports=[]
def encode(parts,name,total,fadein,fadeout):
 path=OUT/name
 assert not path.exists(),f'Preserve existing export: {path}'
 p=subprocess.Popen([FF,'-n','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k',str(path)],stdin=subprocess.PIPE)
 written=0;peak=0
 for part in parts:
  for pos in range(0,len(part),SR):
   b=part[pos:pos+SR].copy()
   absolute=np.arange(written,written+len(b))
   envelope=np.minimum(np.minimum(absolute/(fadein*SR),(total-1-absolute)/(fadeout*SR)),1).clip(0,1)
   b*= (10**(GAIN_DB/20)*envelope[:,None]).astype(np.float32)
   peak=max(peak,float(abs(b).max()))
   p.stdin.write(b.astype('<f4').tobytes());written+=len(b)
 p.stdin.close()
 assert p.wait()==0 and written==total
 # Fully decode MP3 and count exact samples; then independently measure loudness/true peak.
 dec=subprocess.Popen([FF,'-v','error','-i',str(path),'-map','0:a:0','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
 bytecount=0
 while True:
  chunk=dec.stdout.read(1024*1024)
  if not chunk:break
  bytecount+=len(chunk)
 assert dec.wait()==0 and bytecount==total*8,(bytecount,total*8)
 loud=subprocess.run([FF,'-hide_banner','-nostats','-i',str(path),'-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True,check=True)
 summary=loud.stderr.decode(errors='replace').rsplit('Summary:',1)[-1].strip()
 (REPORT/(path.stem+'-loudness.txt')).write_text(loud.stderr.decode(errors='replace'))
 item={'path':path.relative_to(ROOT).as_posix(),'seconds':written/SR,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'full_decode':'passed; exact sample count','preencode_peak_dbfs':20*np.log10(peak),'loudness_summary':summary}
 reports.append(item);print(json.dumps(item,indent=2),flush=True)
encode([join],'Floodplain-Keeper-Shelter-Recovery-join-v1.mp3',len(join),.15,.3)
encode([a[:-n],blend,a[n:-n],blend,a[n:]],'Floodplain-Keeper-Shelter-Recovery-three-repeats-v1.mp3',(3*(END-START)-2*OVERLAP)*SR,5,10)
report={'status':'candidate auditions; user listening pending','source':SRC.relative_to(ROOT).as_posix(),'start_seconds':START,'end_seconds':END,'overlap_seconds':OVERLAP,'repeat_interval_seconds':END-START-OVERLAP,'curve':'equal-power sine/cosine','gain_db':GAIN_DB,'selection_reason':'Near-full-length candidate with 0.073 dB overlap mean-level difference and 0.765 dB coarse normalized spectral distance. Retains 399 seconds; stronger numerical 16-second candidate retains 340 seconds. No harmonic compatibility or listening claim.','short_audition_crossfade_seconds':[25,33],'three_repeat_crossfades_seconds':[[391,399],[782,790]],'assistant_listening':False,'files':reports}
(REPORT/'audition-v1.json').write_text(json.dumps(report,indent=2)+'\n')
