"""Use the existing Colony application's export engine for Floodplain."""
from pathlib import Path
import os, sys, json, hashlib, subprocess, shutil, time
APP=Path('C:/dev/SpeedySlideShow');R=Path('G:/AI/colony')
sys.path.insert(0,str(APP));os.environ['PATH']='C:/Program Files/ShareX;'+os.environ.get('PATH','')
from colony import render
P=R/'final/04-floodplain-keeper/assembly-v1';P.mkdir(exist_ok=True)
E=R/'exports/04-floodplain-keeper';CACHE=E/'assembly-v1';CACHE.mkdir(exist_ok=True)
video=R/'final/04-floodplain-keeper/video-4k-v2.mp4';audio=E/'Floodplain-Keeper-Shelter-Recovery-1-Hour-v1.mp3'
output=E/'Floodplain-Keeper-1-Hour-4K-v1.mp4'
resume='--verify-only' in sys.argv
assert resume or not output.exists(),'Preserve existing output'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
delivery=json.loads((R/'final/04-floodplain-keeper/delivery-v2/delivery-validation.json').read_text())
assert sha(video)==delivery['master']['sha256']
assert sha(audio)=='611a755059906d3bd5cc598c693dc35840664d76d900ff9cf028ab6350aaa109'
ffmpeg=render.get_ffmpeg_path()
progress_state=[-1,0]
def status(s):print(s,flush=True);progress_state[0]=-1
def progress(f,eta):
 pct=int(f*100);now=time.monotonic()
 if pct>=progress_state[0]+5 or now-progress_state[1]>30:
  print(f'Progress {pct}%'+(f'; stage ETA {round(eta)}s' if eta else ''),flush=True);progress_state[:]=[pct,now]
# Colony already supports reusing a prepared loop. Its scaler altered untagged
# source colour values even at CRF0, so seed that cache with the verified master.
# The real render(), audio chain, concat assembly and full decode checks are used.
# No application code or GUI setting is changed; no overlay is requested.
source=render.probe_video(ffmpeg,str(video))
loop=CACHE/'colony-loop-preserved-4k.mp4'
if not resume:
 assert not loop.exists();shutil.copy2(video,loop)
assert sha(loop)==sha(video)
render._prepared=render.Prepared(str(CACHE),render._file_key(str(video)),source,
 render.ColorTags(source.color_space,source.color_primaries,source.color_trc,source.color_range),
 str(loop),20.0,render.probe_video(ffmpeg,str(loop)))
def frame_hashes(path):
 result=subprocess.run([ffmpeg,'-v','error','-i',str(path),'-t','20','-map','0:v:0','-an','-f','framemd5','-'],capture_output=True,check=True,text=True)
 return [line.rsplit(',',1)[-1].strip() for line in result.stdout.splitlines() if line and not line.startswith('#')]
if not resume:
 result=render.render(str(video),[str(audio)],str(output),crossfade=0,overlay_mode=render.OVERLAY_OFF,match_loudness=False,full_decode=True,overwrite=False,on_status=status,on_progress=progress)
 assert result.verified and all(c.ok for c in result.checks),result.checks
 assert result.duration==3600 and result.width==3840 and result.height==2160 and result.fps==30
 assert result.gains_db==[0.0] and result.crossfade==0
 shutil.copy2(result.manifest,P/'colony-export.json')
manifest=json.loads((P/'colony-export.json').read_text())
assert manifest['verification']['passed'] and manifest['verification']['full_decode']
status('Checking decoded first-loop pictures against the accepted master...')
original=frame_hashes(video);encoded=frame_hashes(output)
assert len(original)==600 and original==encoded,'Assembled picture differs from accepted master'
print('All 600 decoded YUV frames preserved exactly',flush=True)
status('Checking every copied video packet and timestamp...')
def packet_rows(path,target):
 with target.open('wb') as stream:
  subprocess.run([ffmpeg,'-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','framehash','-hash','sha256','-'],stdout=stream,check=True)
 lines=target.read_text().splitlines();tb=next(x for x in lines if x.startswith('#tb 0:')).split(':',1)[1].strip();n,d=map(int,tb.split('/'))
 return [(int(a[1])*n/d,int(a[2])*n/d,a[5].strip()) for x in lines if x and not x.startswith('#') for a in [x.split(',')]]
base=packet_rows(loop,CACHE/'loop-packets.txt');full=packet_rows(output,CACHE/'one-hour-packets.txt')
assert len(base)==600 and len(full)==108000,(len(base),len(full))
for i,(dts,pts,h) in enumerate(full):
 assert abs(pts-i/30)<.0001 and abs(dts-i/30)<.0001,(i,dts,pts)
 # MP4 concat inserts 38 bytes of SPS/PPS into the three IDR packets per loop.
 # Compare repeats with the first assembled loop, whose decoded pixels match
 # the master exactly above; do not mistake parameter-set framing for an edit.
 assert h==full[i%600][2],i
record={'date':'2026-09-29','tool':'Colony application export engine','tool_path':str(APP/'colony/render.py'),'tool_sha256':sha(APP/'colony/render.py'),'exporter_sha256':sha(APP/'app/exporter.py'),'runner_sha256':sha(__file__),'output':str(output),'bytes':output.stat().st_size,'sha256':sha(output),'duration_seconds':3600,'dimensions':[3840,2160],'fps':30,'audio':'AAC 192k stereo 48000 Hz','settings':{'crossfade':0,'match_loudness':False,'gain_db':0,'overlay':'off','full_decode':True,'loop_preparation':'Verified short master reused through Colony prepared-loop cache; no re-encode'},'source_video_sha256':sha(video),'source_audio_sha256':sha(audio),'colony_loop':{'path':str(loop),'sha256':sha(loop),'decoded_yuv_frames_exactly_match_accepted_master':True},'validation':{'full_video_audio_decode':True,'video_packet_count':len(full),'sequential_pts_dts':True,'all_180_encoded_loop_payloads_identical':True,'seam':'Exact decoded YUV frames retained from approved, seam-verified short master; every repeated payload identical.'},'review':'Technical validation and decoded still checks only; no full-hour artistic playback/listening or upload check claimed.','storage':'Finished one-hour video/audio and cached loop remain local ignored exports.'}
(P/'delivery-validation.json').write_text(json.dumps(record,indent=2)+'\n')
status('Colony one-hour export and packet validation complete')
