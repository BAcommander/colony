"""Versioned Rainline music-only hour and optional rain mix through Colony's SFX graph."""
from pathlib import Path
import sys, subprocess, hashlib, json, shutil, re
import numpy as np
sys.path.insert(0, 'C:/dev/SpeedySlideShow')
from colony import render as R
from colony.sfx import SfxSettings, prepare_loop, mix_graph
from dataclasses import asdict

ROOT=Path('G:/AI/colony')
REPORT=ROOT/'final/08-rainline-relay/music/long-source-v1'
OUT=ROOT/'exports/08-rainline-relay'
RAIN=ROOT/'music/shared-rain-overlay'
for d in (REPORT,OUT,RAIN): d.mkdir(parents=True,exist_ok=True)
FF=R.get_ffmpeg_path()
def preserve(src,d):
    src=Path(src); dst=d/src.name
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if dst.exists(): assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
    else: shutil.copy2(src,dst)
    return dst,digest
src,src_hash=preserve('C:/Users/jazzs/Downloads/Above_the_Flooded_Canopy_2026-10-10T120411.mp4',REPORT)
rain,rain_hash=preserve('C:/Users/jazzs/Downloads/Gentle_continuous_ra_#2-1791634292024.mp3',RAIN)
SR=48000; TOTAL=3600*SR; START=20; END=408; OVERLAP=12; GAIN=-6
dry=OUT/'Rainline-Relay-Above-the-Flooded-Canopy-1-Hour-v1.mp3'
wet=OUT/'Rainline-Relay-1-Hour-with-Rain-v1.mp3'
audition=REPORT/'Rainline-music-join-review-60s-v1.mp3'
preview=REPORT/'Rainline-rain-mix-preview-v1.mp3'
settings=SfxSettings(str(rain),gain_db=-4,start_s=20,on_s=120,off_s=90,fade_in_s=20,fade_out_s=30)
assert not any(p.exists() for p in (dry,wet,audition,preview)), 'Preserve existing exports; make a new version.'
raw=subprocess.run([FF,'-v','error','-i',str(src),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
original=np.frombuffer(raw,np.float32).reshape(-1,2)
assert np.isfinite(original).all()
a=original[START*SR:END*SR]; n=OVERLAP*SR
phase=np.linspace(0,np.pi/2,n)
blend=(a[-n:]*np.cos(phase)[:,None]+a[:n]*np.sin(phase)[:,None]).astype(np.float32)
p=subprocess.Popen([FF,'-n','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0',
 '-c:a','libmp3lame','-b:a','192k','-metadata','title=Rainline Relay - Above the Flooded Canopy - One Hour',str(dry)],stdin=subprocess.PIPE)
written=0; joins=[]; peak=0
def write(part):
    global written,peak
    for offset in range(0,len(part),SR):
        if written==TOTAL:return
        b=part[offset:offset+min(SR,TOTAL-written)].copy()
        pos=np.arange(written,written+len(b))
        env=np.minimum(np.minimum(pos/(10*SR),(TOTAL-1-pos)/(20*SR)),1).clip(0,1)
        b*=(10**(GAIN/20)*env[:,None]).astype(np.float32)
        peak=max(peak,float(abs(b).max()))
        p.stdin.write(b.astype('<f4').tobytes()); written+=len(b)
write(a[:-n])
while written<TOTAL:
    joins.append([written/SR,min(written+n,TOTAL)/SR]);write(blend);write(a[n:-n])
p.stdin.close(); assert p.wait()==0 and written==TOTAL
print('Music-only hour encoded.',flush=True)
subprocess.run([FF,'-n','-v','error','-ss','352','-i',str(dry),'-t','60','-c:a','libmp3lame','-b:a','192k',str(audition)],check=True)
loop=REPORT/'rain-loop-28s-v1.wav'
rain_info=R.measure_track(FF,str(rain))
actual_x=prepare_loop(FF,settings,str(loop),rain_info.duration)
graph=mix_graph(R.build_audio_graph([0],0,first_input=0),settings,3600,1)
subprocess.run([FF,'-n','-v','error','-i',str(dry),'-stream_loop','-1','-i',str(loop),
 '-filter_complex',graph,'-map','[aout]','-t','3600','-c:a','libmp3lame','-b:a','192k',str(wet)],check=True)
print('Rain hour encoded; generating tool mix preview.',flush=True)
R.preview_audio([str(dry)],str(preview),sfx=settings)
def validate(path,seconds):
    d=subprocess.Popen([FF,'-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
    count=0; mx=0
    while True:
        chunk=d.stdout.read(SR*8)
        if not chunk:break
        v=np.frombuffer(chunk,np.float32); assert np.isfinite(v).all()
        mx=max(mx,float(abs(v).max()));count+=len(chunk)
    assert d.wait()==0 and count==seconds*SR*8 and mx<1,(count,seconds*SR*8,mx)
    r=subprocess.run([FF,'-hide_banner','-nostats','-i',str(path),'-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True,check=True)
    summary=r.stderr.decode(errors='replace').rsplit('Summary:',1)[-1]
    lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS',summary)[1]);tp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS',summary)[1]);assert tp<0
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,
      decoded_seconds=count/SR/8,decoded_samples_per_channel=count//8,all_samples_finite=True,
      integrated_lufs=lufs,true_peak_dbtp=tp,decoded_peak_dbfs=20*np.log10(mx),full_decode_passed=True)
checks=[]
for path,seconds in ((dry,3600),(wet,3600),(audition,60),(preview,260)):
    checks.append(validate(path,seconds));print('Verified',path.name,checks[-1]['integrated_lufs'],flush=True)
record=dict(date='2026-10-10',source=str(src),source_sha256=src_hash,source_decoded_seconds=len(original)/SR,
 rain_source=str(rain),rain_sha256=rain_hash,rain_source_seconds=rain_info.duration,rain_source_lufs=rain_info.loudness,
 start_seconds=START,end_seconds=END,overlap_seconds=OVERLAP,repeat_interval_seconds=END-START-OVERLAP,
 curve='equal-power sine/cosine',gain_db=GAIN,opening_fade_seconds=10,closing_fade_seconds=20,
 rationale='Trim generated opening/closing fades; match measured ambient listening levels near -20 LUFS. Join is a candidate, not a harmonic/listening verdict.',
 join_windows_seconds=joins,audition_join_window_seconds=[24,36],sfx=asdict(settings),actual_rain_loop_overlap_seconds=actual_x,
 rain_windows_seconds=[[t,min(t+settings.on_s,3600)] for t in range(20,3600,210)],
 files=checks,assistant_listening=False,user_join_approved=False,user_rain_mix_approved=False,
 approval_scope='User selected supplied final seven-minute piece and requested one hour plus configurable rain. New join, mix and full-hour listening remain for review.',
 format='MP3 192 kb/s, stereo 48 kHz',storage='Local media; no commit, push or remote backup claimed.')
(REPORT/'one-hour-delivery-v1.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(RAIN/'rain-source-v1.json').write_text(json.dumps(dict(source=str(rain),sha256=rain_hash,seconds=rain_info.duration,lufs=rain_info.loudness,
 supplied_by_user=True,assistant_listening=False,reusable_loop=str(loop),loop_crossfade_seconds=actual_x),indent=2)+'\n',encoding='utf-8')
shutil.copy2(__file__,REPORT/Path(__file__).name)
print(json.dumps(checks,indent=2),flush=True)
