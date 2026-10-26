"""Extract the user's nominated five seconds without processing the original."""
from pathlib import Path
import subprocess,json,hashlib,wave
H=Path(__file__).resolve().parent
source=Path(r'C:\Users\jazzs\Downloads\TODO_-_Vast_Unfamiliar_World_2026-10-10T192538 (1).mp4')
target=H/'Vast-Unfamiliar-World-reference-00m24s-to-00m29s.wav'
assert not target.exists(),'Preserve existing extraction'
original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
common=['ffmpeg','-v','error','-i',str(source),'-map','0:a:0','-af','atrim=start=24:end=29,asetpts=PTS-STARTPTS','-c:a','pcm_s24le']
subprocess.run(common+['-n',str(target)],check=True)
expected=subprocess.run(common+['-f','s24le','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
with wave.open(str(target),'rb') as stream:
    metadata={'sample_rate':stream.getframerate(),'channels':stream.getnchannels(),'sample_width_bytes':stream.getsampwidth(),'sample_frames':stream.getnframes()}
    actual=stream.readframes(stream.getnframes())
assert actual==expected
assert metadata=={'sample_rate':48000,'channels':2,'sample_width_bytes':3,'sample_frames':240000}
assert hashlib.sha256(source.read_bytes()).hexdigest()==original_hash
record={'source':str(source),'source_sha256':original_hash,'requested_interval_seconds':[24,29],'output':target.name,'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'duration_seconds':5,'audio':metadata,'exact_decoded_source_segment_pcm24':True,'processing':'Decode AAC, select 24.000 <= t < 29.000 seconds, encode 24-bit PCM. No gain, fades, looping, stretching or resampling. Original unchanged.','selection':'User identifies this interval as the slower candidate. No assistant listening or musical acceptance claimed.','next_generation':'Manual 30-second instrumental trial with only this excerpt as reference. Influence is an untested choice, not measured optimum. No credits spent or generation submitted.','reference_docs':'https://elevenlabs.io/docs/help-center/product/core-capabilities/music/what-is-audio-reference','short_upload_caveat':'Current documentation does not establish a five-second minimum; a separate official References announcement states 10-second minimum. Try exact excerpt if uploader accepts it; do not include unwanted neighbouring music to meet a limit.'}
(H/'reference-manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
