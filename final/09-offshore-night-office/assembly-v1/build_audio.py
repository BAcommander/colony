from pathlib import Path
import sys,json,subprocess,hashlib,re,time
import numpy as np
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render as R
ROOT=Path('G:/AI/colony'); M=ROOT/'final/09-offshore-night-office/music'; D=M/'two-hour-v1';D.mkdir(exist_ok=True)
E=ROOT/'exports/09-offshore-night-office';E.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
c=read(M/'long-source-v1/audition-v1.json'); w=read(M/'water-mix-v2/delivery-v2.json')
approval={'date':'2026-10-10','quote':'transition is fine , water is fine, make the 2 hour loop, scale up the video quality etc etc?','music_join_approved':True,'water_mix_v2_approved':True,'duration_seconds':7200,'animation_authorization':'Use current v3 for 4K and final assembly; no separate detailed motion verdict inferred.'}
save(D/'approval.json',approval)
FF=R.get_ffmpeg_path(); SR=48000; total=7200
src=ROOT/c['source']; assert sha(src)==c['source_sha256']
raw=subprocess.run([FF,'-v','error','-i',str(src),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)[c['source_start_seconds']*SR:c['source_end_seconds']*SR].copy()*10**(c['gain_db']/20)
assert np.isfinite(a).all()
n=c['overlap_seconds']*SR; phase=np.linspace(0,np.pi/2,n)
blend=(a[-n:]*np.cos(phase)[:,None]+a[:n]*np.sin(phase)[:,None]).astype(np.float32)
cycle=np.concatenate([blend,a[n:-n]])
dry=D/'music-two-hour-pre-fades.flac'
if not dry.exists():
 proc=subprocess.Popen([FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','flac',str(dry)],stdin=subprocess.PIPE)
 sent=0
 for index in range(20):
  block=(a[:-n] if index==0 else cycle)[:total*SR-sent]
  if len(block)==0:break
  proc.stdin.write(block.tobytes());sent+=len(block);print(f'Music {sent/SR:.0f}/{total}s',flush=True)
 proc.stdin.close();assert proc.wait()==0 and sent==total*SR
settings=R.SfxSettings(**w['settings']); loop=M/'water-mix-v2/water-source-loop-v2.wav'
assert sha(Path(settings.path))==w['source_sha256']
out=E/'Shoreless-Colony-Alien-Sea-Viewport-with-Water-2-Hours-v1.mp3'
graph=R.mix_graph(R.build_audio_graph([0],0,first_input=0),settings,total,1)
graph+=';[aout]afade=t=in:st=0:d=10,afade=t=out:st=7180:d=20[final]'
if not out.exists():
 subprocess.run([FF,'-v','error','-n','-i',str(dry),'-stream_loop','-1','-i',str(loop),'-filter_complex',graph,'-map','[final]','-t',str(total),'-c:a','libmp3lame','-b:a','192k',str(out)],check=True)
print('Checking every decoded audio sample',flush=True)
proc=subprocess.Popen([FF,'-v','error','-i',str(out),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
count=0;peak=0
while True:
 block=proc.stdout.read(48000*8)
 if not block:break
 x=np.frombuffer(block,np.float32);assert np.isfinite(x).all();peak=max(peak,float(abs(x).max()));count+=len(x)
assert proc.wait()==0 and count==total*SR*2 and peak<1
print('Measuring final soundtrack loudness',flush=True)
result=subprocess.run([FF,'-hide_banner','-i',str(out),'-af','loudnorm=I=-20.5:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
measure=json.loads(re.findall(r'\{[^{}]+\}',result.stderr)[-1])
record={'approval':approval,'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'bytes':out.stat().st_size,'duration_seconds':total,'sample_rate':SR,'channels':2,'bitrate':192000,'source':c['source'],'source_sha256':c['source_sha256'],'source_cut_seconds':[40,444],'music_gain_db':c['gain_db'],'overlap_seconds':12,'repeat_interval_seconds':392,'curve':c['curve'],'water_settings':w['settings'],'opening_fade_seconds':10,'closing_fade_seconds':20,'validation':{'full_decode':True,'finite_samples':True,'sample_count_per_channel':count//2,'sample_peak_dbfs':20*np.log10(peak),'integrated_lufs':float(measure['input_i']),'true_peak_dbtp':float(measure['input_tp'])},'review':'User approved join and water v2; full two-hour listening not claimed.','runner_sha256':sha(__file__)}
save(D/'delivery.json',record)
p=M/'generation-record.json';g=read(p);g.update(status='Approved music join and water v2 extended to two hours; 4K assembly in progress',local_join_approved=True,water_mix_approved=True,final_duration_seconds=7200,two_hour_record='music/two-hour-v1/delivery.json');save(p,g)
print(json.dumps(record,indent=2),flush=True)
