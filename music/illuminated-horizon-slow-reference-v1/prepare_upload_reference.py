"""Meet the confirmed UI minimum using only the nominated five-second excerpt."""
from pathlib import Path
import subprocess,json,hashlib,wave
H=Path(__file__).resolve().parent
source=H/'Vast-Unfamiliar-World-reference-00m24s-to-00m29s.wav'
target=H/'Vast-Unfamiliar-World-slow-reference-12s-crossfaded.wav'
assert not target.exists(),'Preserve previous output'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
graph='[0:a]asplit=3[a][b][c];[a][b]acrossfade=d=0.15:c1=tri:c2=tri[ab];[ab][c]acrossfade=d=0.15:c1=tri:c2=tri,atrim=duration=12,asetpts=PTS-STARTPTS[out]'
subprocess.run(['ffmpeg','-v','error','-n','-i',str(source),'-filter_complex',graph,'-map','[out]','-c:a','pcm_s24le',str(target)],check=True)
with wave.open(str(target),'rb') as w:
    meta={'sample_rate':w.getframerate(),'channels':w.getnchannels(),'sample_frames':w.getnframes(),'sample_width_bytes':w.getsampwidth()}
assert meta=={'sample_rate':48000,'channels':2,'sample_frames':576000,'sample_width_bytes':3}
subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
record={'reason':'User screenshot confirms upload requires 10 seconds to 5 minutes.','output':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'duration_seconds':12,'audio':meta,'source_excerpt':source.name,'source_sha256':source_hash,'source_interval_in_original_seconds':[24,29],'recipe':'Three copies of the five-second excerpt, 150ms linear amplitude crossfades, trim to 12 seconds. No time stretching, pitch shift, resampling or music from neighbouring intervals.','overlap_start_seconds':[4.85,9.7],'limitation':'Phrase repeats are introduced solely to meet the upload limit. They may condition repetition; this is a reference-only workaround, not a genuine twelve-second original passage or new composed interlude. Crossfades have not been auditioned by assistant.','generation':'Use existing 30-second prompt as one manual trial. No generation submitted or credits spent.'}
(H/'upload-reference-manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
with (H/'README.md').open('a',encoding='utf-8') as f:
    f.write('\n## Confirmed upload minimum and reference-only workaround\n\nUser screenshot confirms a ten-second minimum and five-minute maximum. The 12-second WAV reuses only the original selected five seconds, with 150ms linear crossfades at 4.85 and 9.70 seconds. This introduces repeated phrases rather than extending the composition. The unchanged 30-second prompt asks the model to develop the idea. Repetition may carry into generation, so this remains an experiment; the assistant has not auditioned joins. Full decode, exact 576,000-frame stereo/48kHz duration and unchanged source hash passed. See upload-reference-manifest.json. No credits spent.\n')
print(json.dumps(record,indent=2))
