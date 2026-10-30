from pathlib import Path
import sys,json,subprocess,hashlib,re
import numpy as np
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render
R=Path('G:/AI/colony');M=R/'final/10-nightward-station/music';D=M/'one-hour-v1';D.mkdir(exist_ok=True)
E=R/'exports/10-nightward-station';E.mkdir(exist_ok=True)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
c=json.loads((M/'long-a-unfolding-warmth-v1/audition-v1.json').read_text(encoding='utf-8'))
assert c['user_join_approved']
FF=render.get_ffmpeg_path();SR=48000;total=3600;src=R/c['source']
assert sha(src)==c['source_sha256']
raw=subprocess.run([FF,'-v','error','-i',str(src),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)[c['source_start_seconds']*SR:c['source_end_seconds']*SR].copy()
assert np.isfinite(a).all()
n=c['overlap_seconds']*SR;phase=np.linspace(0,np.pi/2,n)
blend=(a[-n:]*np.cos(phase)[:,None]+a[:n]*np.sin(phase)[:,None]).astype(np.float32)
cycle=np.concatenate([blend,a[n:-n]]);gain=10**(c['gain_db']/20)
out=E/'Farpoint-Station-Unfolding-Warmth-1-Hour-v1.mp3'
assert not out.exists(),'Preserve existing media'
p=subprocess.Popen([FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-af','afade=t=in:st=0:d=10,afade=t=out:st=3580:d=20','-c:a','libmp3lame','-b:a','192k',str(out)],stdin=subprocess.PIPE)
sent=0;index=0
try:
 while sent<total*SR:
  block=(a[:-n] if index==0 else cycle)[:total*SR-sent]*gain
  p.stdin.write(block.astype(np.float32).tobytes());sent+=len(block);index+=1
  print(f'Music {sent/SR:.0f}/{total}s',flush=True)
finally:p.stdin.close()
assert p.wait()==0
print('Checking all decoded audio samples',flush=True)
p=subprocess.Popen([FF,'-v','error','-i',str(out),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
count=0;peak=0
while True:
 block=p.stdout.read(SR*8)
 if not block:break
 x=np.frombuffer(block,np.float32);assert np.isfinite(x).all();peak=max(peak,float(abs(x).max()));count+=len(x)
assert p.wait()==0 and count==total*SR*2 and peak<1
print('Measuring soundtrack loudness',flush=True)
v=subprocess.run([FF,'-hide_banner','-i',str(out),'-af','loudnorm=I=-20.5:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
measure=json.loads(re.findall(r'\{[^{}]+\}',v.stderr)[-1])
record={'date':'2026-10-10','file':out.relative_to(R).as_posix(),'sha256':sha(out),'bytes':out.stat().st_size,'duration_seconds':total,'sample_rate':SR,'channels':2,'bitrate':192000,'source':c['source'],'source_sha256':c['source_sha256'],'source_cut_seconds':[42,284],'music_gain_db':-7,'overlap_seconds':12,'repeat_interval_seconds':230,'curve':c['curve'],'sfx':None,'opening_fade_seconds':10,'closing_fade_seconds':20,'validation':{'full_decode':True,'finite_samples':True,'sample_count_per_channel':count//2,'sample_peak_dbfs':20*np.log10(peak),'integrated_lufs':float(measure['input_i']),'true_peak_dbtp':float(measure['input_tp'])},'approval':{'join_quote':'i think it works fine,','assembly_quote':'i think for now lets just build out the full farpoint with this. since the track was only 5 minutes do you recommend 1 hour?','duration_decision':'One hour recommended and used for requested full Farpoint assembly.'},'review':'User approved join; full-hour listening not claimed.','runner_sha256':sha(__file__)}
save(D/'delivery.json',record);print(json.dumps(record,indent=2),flush=True)
