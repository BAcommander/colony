from pathlib import Path
import sys, json, math, hashlib, subprocess
from dataclasses import asdict
import numpy as np
sys.path.insert(0, 'C:/dev/SpeedySlideShow')
from colony import render as R

ROOT=Path('G:/AI/colony'); M=ROOT/'final/09-offshore-night-office/music'
D=M/'water-mix-v2'; D.mkdir(exist_ok=True)
previous=json.loads((M/'water-mix-v1/delivery-v1.json').read_text())
c=json.loads((M/'long-source-v1/audition-v1.json').read_text())
settings=R.SfxSettings(**{**previous['settings'], 'gain_db': previous['settings']['gain_db']+20*math.log10(.85)})
FF=R.get_ffmpeg_path(); SR=48000
def run(args, **kw): return subprocess.run([FF,'-v','error',*args],check=True,**kw)
def decode(p):
    return np.frombuffer(run(['-i',str(p),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True).stdout,np.float32).reshape(-1,2)
src=ROOT/c['source']; assert hashlib.sha256(src.read_bytes()).hexdigest()==c['source_sha256']
a=decode(src)[c['source_start_seconds']*SR:c['source_end_seconds']*SR]
a=a*10**(c['gain_db']/20)
n=c['overlap_seconds']*SR; interval=c['repeat_interval_seconds']; total=440
phase=np.linspace(0,np.pi/2,n)
blend=a[-n:]*np.cos(phase)[:,None]+a[:n]*np.sin(phase)[:,None]
b=np.concatenate([a[:-n],blend,a[n:(total-interval)*SR]]).astype(np.float32)
assert len(b)==total*SR and np.isfinite(b).all() and abs(b).max()<1
dry=D/'music-loop-review-source-v2.flac'
run(['-n','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','flac',str(dry)],input=b.tobytes())
loop=D/'water-source-loop-v2.wav'
R.prepare_loop(FF,settings,str(loop),previous['source_seconds'])
graph=R.mix_graph(R.build_audio_graph([0],0,first_input=0),settings,total,1)
full=D/'Shoreless-water-and-music-loop-review-7m20s-v2.mp3'
run(['-n','-i',str(dry),'-stream_loop','-1','-i',str(loop),'-filter_complex',graph,'-map','[aout]','-t',str(total),'-c:a','libmp3lame','-b:a','192k',str(full)])
short=D/'Shoreless-water-short-preview-v2.mp3'
join=D/'Shoreless-music-loop-join-review-60s-v2.mp3'
for p,start,duration in [(short,0,120),(join,368,60)]:
    run(['-n','-i',str(full),'-ss',str(start),'-t',str(duration),'-c:a','libmp3lame','-b:a','192k',str(p)])
checks=[]
for p,duration in [(full,total),(short,120),(join,60)]:
    x=decode(p); assert len(x)==duration*SR and np.isfinite(x).all() and abs(x).max()<1
    checks.append(dict(path=p.relative_to(ROOT).as_posix(),seconds=duration,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),full_decode_passed=True,all_samples_finite=True,sample_peak_dbfs=float(20*np.log10(abs(x).max()))))
def save(p,v): p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
record={**previous,'user_feedback':"at it's loudest reduce it by 15%",'followup':'then let me listen to the loop so we can make a 2 hour version etc','settings':asdict(settings),'amplitude_multiplier_relative_to_v1':.85,'amplitude_fraction_of_supplied_sfx':10**(settings.gain_db/20),'files':checks,'music_loop_join_full_seconds':[392,404],'music_loop_join_short_seconds':[24,36],'target_final_duration_seconds':7200,'status':'V2 water reduced 15% in amplitude at unchanged timings. Full audition includes one exact candidate music overlap. User listening approval pending before two-hour extension.','previous_record':'music/water-mix-v1/delivery-v1.json'}
save(D/'delivery-v2.json',record)
p=M/'generation-record.json'; g=json.loads(p.read_text(encoding='utf-8')); g.update(status=record['status'],water_mix_record='music/water-mix-v2/delivery-v2.json',water_settings=asdict(settings),water_feedback=record['user_feedback'],target_final_duration_seconds=7200,water_mix_approved=False,local_join_approved=False);save(p,g)
p=M.parent/'manifest.json';g=json.loads(p.read_text(encoding='utf-8'));g['music_current'].update(status=record['status'],water_mix_record='music/water-mix-v2/delivery-v2.json',target_final_duration_seconds=7200);save(p,g)
p=ROOT/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8').replace('Eight-minute music source supplied; join and quiet sparse water auditions awaiting review','Two-hour target requested; music join and water v2 (15% quieter) auditions awaiting review');p.write_text(s,encoding='utf-8')
p=ROOT/'AGENTS.md';s=p.read_text(encoding='utf-8');i=s.index('Current Shoreless music (');j=s.index('\n\n',i);part=s[i:j].replace('final duration unset','two-hour target requested').replace('Water-mix-v1 auditions use -18 dB source gain','Water-mix-v1 auditions used -18 dB source gain');part+=' Latest: user requested another 15% reduction at peak and a loop audition before a two-hour version. V2 gain is -19.41162149 dB with all timings unchanged. Fully decoded 7:20 mixed audition includes music crossfade at 6:32–6:44; short join review at 0:24–0:36. See music/water-mix-v2/delivery-v2.json. Mix and join approval remain pending.';p.write_text(s[:i]+part+s[j:],encoding='utf-8')
p=ROOT/'creative/MUSIC_WORKFLOW.md';s=p.read_text(encoding='utf-8');old='This is a pending trial, not an approved default;';new='The user then requested another 15% reduction at peak: v2 multiplies the entire water envelope by 0.85 (-1.41162149 dB), yielding -19.41162149 dB source gain while preserving timings. See [v2 audition evidence](../final/09-offshore-night-office/music/water-mix-v2/delivery-v2.json). This is a pending trial, not an approved default;';assert old in s;s=s.replace(old,new,1);p.write_text(s,encoding='utf-8')
print(json.dumps({'settings':asdict(settings),'files':checks,'join_seconds':[24,36]},indent=2))
