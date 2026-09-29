from pathlib import Path
import subprocess,json,hashlib,numpy as np
R=Path(__file__).resolve().parent
ROOT=Path('G:/AI/colony');D=ROOT/'exports/03-glacier-sanctuary'
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
source=D/'glacier.mp4';audio=D/'Glacier-Sanctuary-4-Hours-v2-Amber-Refuge.mp3';out=D/'glacier-v2-amber-refuge.mp4'
assert not out.exists()
audio_report=json.loads((R/'four-hour-render.json').read_text())
assert audio_report['full_decode_verified'] and audio_report['verified_decoded_seconds']==14400
with (R/'video-assembly.log').open('wb') as log:
 subprocess.run([FF,'-n','-hide_banner','-nostats','-i',str(source),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','14400','-map_metadata','-1','-metadata','title=Glacier Sanctuary - Amber Refuge - Four Hours','-movflags','+faststart',str(out)],stderr=log,check=True)
print('Video assembled; verifying original picture stream and full new audio.',flush=True)
def picture_hash(path):
 return subprocess.run([FF,'-v','error','-i',str(path),'-map','0:v:0','-c','copy','-f','streamhash','-hash','sha256','pipe:1'],capture_output=True,check=True).stdout.decode().strip()
old_hash=picture_hash(source);new_hash=picture_hash(out);assert old_hash==new_hash
with (R/'video-audio-loudness.txt').open('wb') as log:
 p=subprocess.Popen([FF,'-hide_banner','-nostats','-i',str(out),'-map','0:a:0','-af','ebur128=peak=true:framelog=verbose','-ar','48000','-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=log)
 count=0;peak=0.
 while True:
  b=p.stdout.read(48000*2*4)
  if not b:break
  x=np.frombuffer(b,np.float32);assert np.isfinite(x).all();count+=len(x);peak=max(peak,float(abs(x).max()))
 assert p.wait()==0
seconds=count/96000
assert abs(seconds-14400)<.025,seconds
report={'output':str(out),'source_video':str(source),'replacement_audio':str(audio),'video_stream_copy_verified':True,'video_stream_sha256':new_hash,'decoded_audio_seconds':seconds,'audio_full_decode_verified':True,'audio_peak_dbfs':float(20*np.log10(peak)),'video_decode':'Original encoded video stream preserved and hash-verified; no new full picture decode performed.','duration_target_seconds':14400,'original_video_and_audio_preserved':True,'user_join_feedback':'loop sounds fine','youtube_status':'User screenshot showed no notices on private nine-minute source; full replacement upload checks pending.','bytes':out.stat().st_size}
(R/'video-v2-validation.json').write_text(json.dumps(report,indent=2))
inv=ROOT/'final/local-export-inventory.json';data=json.loads(inv.read_text(encoding='utf-8-sig'))
for path in [audio,out]:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 rel=path.relative_to(ROOT).as_posix();data['files']=[v for v in data['files'] if v['path']!=rel]
 data['files'].append({'path':rel,'bytes':path.stat().st_size,'sha256':h.hexdigest(),'storage':'local ignored; separate backup required'})
inv.write_text(json.dumps(data,indent=2))
(R/'delivery-v2.md').write_text('''# Glacier replacement delivery v2

User approved the replacement join: "loop sounds fine". Four-hour MP3 and a ready-to-upload MP4 are saved separately under exports/03-glacier-sanctuary, with v2-Amber-Refuge / v2-amber-refuge filenames. Originals preserved.

Source Amber Refuge Beneath the Stone: 0:29-8:31, 15-second equal-power joins, 467-second repeat interval, gain -4.7 dB, 10-second initial fade and 20-second final fade. MP3 full decode verified exactly four hours. MP4 copies original video stream, including subscribe overlay, and replaces only audio with AAC 192 kb/s. Picture-stream identity and full new audio decode verified; see validation JSON and loudness logs.

User's private nine-minute test showed No notices. Upload this complete replacement privately and wait for YouTube checks before publishing. This screening result is not a guarantee against later claims. No YouTube action or support message was sent. No full-length artistic listening approval claimed. Files locally saved; no commit/push claimed, and ignored exports are not backed up by Git.
''')
with (ROOT/'creative/MUSIC_WORKFLOW.md').open('a',encoding='utf-8') as f:
 f.write('\n\nGlacier replacement delivered: user approved Amber Refuge join with "loop sounds fine" after private source upload showed No notices. Versioned four-hour MP3 and original-picture-stream MP4 completed. Source 0:29-8:31, 15-second equal-power overlap, -4.7 dB gain. See final/03-glacier-sanctuary/music/replacement-amber-refuge/delivery-v2.md. Full replacement YouTube checks pending; original claimed files preserved.\n')
print(json.dumps(report,indent=2),flush=True)
print((R/'video-audio-loudness.txt').read_text(errors='replace')[-650:])
