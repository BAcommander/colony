"""Quiet, sparse water audition through Colony; no long-form delivery yet."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil,re
import numpy as np
from dataclasses import asdict
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render as R
ROOT=Path('G:/AI/colony');M=ROOT/'final/09-offshore-night-office/music';D=M/'water-mix-v1';D.mkdir(exist_ok=True)
source=Path('C:/Users/jazzs/Downloads/Clear_ocean_water_re_#1-1791650516724.mp3');water=D/source.name
if water.exists():assert water.read_bytes()==source.read_bytes()
else:shutil.copy2(source,water)
c=json.loads((M/'long-source-v1/audition-v1.json').read_text());music=ROOT/c['source']
assert hashlib.sha256(music.read_bytes()).hexdigest()==c['source_sha256']
FF=R.get_ffmpeg_path();SR=48000
dry=D/'music-excerpt-level-matched-v1.flac';preview=D/'Shoreless-water-sparse-preview-v1.mp3';short=D/'Shoreless-water-short-preview-v1.mp3'
assert not any(p.exists() for p in (dry,preview,short))
subprocess.run([FF,'-n','-v','error','-i',str(music),'-vn','-af',
 f"atrim=start={c['source_start_seconds']}:end={c['source_end_seconds']},asetpts=PTS-STARTPTS,volume={c['gain_db']}dB",
 '-ar','48000','-ac','2','-c:a','flac',str(dry)],check=True)
settings=R.SfxSettings(str(water),gain_db=-18,start_s=45,on_s=35,off_s=265,fade_in_s=12,fade_out_s=18,loop_crossfade_s=2)
R.preview_audio([str(dry)],str(preview),sfx=settings)
subprocess.run([FF,'-n','-v','error','-i',str(preview),'-t','120','-c:a','libmp3lame','-b:a','192k',str(short)],check=True)
def check(path,seconds):
 raw=subprocess.run([FF,'-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
 a=np.frombuffer(raw,np.float32);assert len(a)==seconds*SR*2 and np.isfinite(a).all() and abs(a).max()<1
 return {'path':path.relative_to(ROOT).as_posix(),'seconds':seconds,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'full_decode_passed':True,'all_samples_finite':True,'sample_peak_dbfs':float(20*np.log10(abs(a).max()))}
checks=[check(short,120),check(preview,367)]
info=R.measure_track(FF,str(water))
record={'date':'2026-10-10','user_feedback':"to mix this in we'd have to use it at much lower volume and way more sparingly",'source':water.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(water.read_bytes()).hexdigest(),'source_seconds':info.duration,'source_integrated_lufs':info.loudness,'settings':asdict(settings),'amplitude_fraction_of_supplied_sfx':10**(-18/20),'music_source':c['source'],'music_source_sha256':c['source_sha256'],'music_gain_db':c['gain_db'],'music_excerpt_source_seconds':[c['source_start_seconds'],c['source_end_seconds']],'water_events_preview_seconds':[[45,80],[345,380]],'first_event_peak_plateau_seconds':[57,62],'files':checks,'user_water_mix_approved':False,'user_join_approved':False,'assistant_listening':False,'status':'Quiet sparse audition; level and schedule proposed from user feedback, not yet approved. No long loop or final runtime selected.'}
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
save(D/'delivery-v1.json',record)
p=M/'generation-record.json';g=json.loads(p.read_text(encoding='utf-8'));g.update(status='Long source and join audition ready; quiet sparse water mix preview awaiting review',water_source=record['source'],water_mix_record='music/water-mix-v1/delivery-v1.json',water_settings=asdict(settings),water_feedback=record['user_feedback'],water_mix_approved=False);save(p,g)
p=M.parent/'manifest.json';g=json.loads(p.read_text(encoding='utf-8'));g['music_current'].update(status='Music join and sparse water mix awaiting review',water_sfx_status='Supplied; quiet sparse audition rendered',water_mix_record='music/water-mix-v1/delivery-v1.json');save(p,g)
# Preserve revised prompt as provenance; muffled first prompt stays intact.
(M/'water-sfx-prompt-v2-clear.txt').write_text('Clear ocean water recorded close to the surface. Gentle rolling swells, overlapping ripples and small waves washing against offshore platform supports. Detailed liquid movement, soft splashes and brief fizzing foam, with natural variation and stereo depth. Seamless continuous loop, no fade. No music, voices, birds, wind, machinery or crashing surf.\n',encoding='utf-8')
p=ROOT/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8').replace('Alien Sea Viewport eight-minute source supplied; music join audition ready; water prompt prepared','Eight-minute music source supplied; join and quiet sparse water auditions awaiting review');p.write_text(s,encoding='utf-8')
p=ROOT/'AGENTS.md';s=p.read_text(encoding='utf-8');i=s.index('Current Shoreless music (');j=s.index('\n\n',i);part=s[i:j];part=part.replace('Water prompt saved as music/water-sfx-prompt-v1.txt: gentle distant platform swells from shelter, no generated/supplied water SFX yet.', 'User found sheltered/muffled water prompt too subdued; revised clear-water prompt saved as water-sfx-prompt-v2-clear.txt. Supplied Clear_ocean_water_re_#1-1791650516724.mp3 and requested much lower/sparser mixing. Water-mix-v1 auditions use -18 dB source gain, first at 45 seconds, 35 seconds on including 12/18-second fades, 265 seconds off (five-minute onset spacing). Two-minute and 367-second previews fully decoded; exact settings/hashes in music/water-mix-v1/delivery-v1.json. Water balance/schedule and music join remain unapproved; no long loop produced.')
s=s[:i]+part+s[j:];p.write_text(s,encoding='utf-8')
p=ROOT/'creative/MUSIC_WORKFLOW.md';s=p.read_text(encoding='utf-8');heading='## Water ambience — Shoreless trial, 2026-10-10\n\n';lesson=heading+'The sheltered-room/lightly-muffled prompt lost too much audible water detail for the user. Generate clear liquid movement first, then control its gain and frequency of appearance in the local mix. The user subsequently said the clear water must be much quieter and used far more sparingly. Initial audition: -18 dB on this specific source (about 12.6% amplitude), 35 seconds including 12/18-second fades, followed by 265 seconds fully off. First onset 45 seconds. This is a pending trial, not an approved default; separate per-source settings from the accepted Rainline rain preset. Check isolated splash peaks as well as average level. Source measured -27.1 LUFS with -7.5 dBTP, so average loudness alone understates its transient peaks. See [audition evidence](../final/09-offshore-night-office/music/water-mix-v1/delivery-v1.json). Music join approval remains separate.\n\n'
assert heading not in s;s=s.replace('## Evidence and analysis discipline',lesson+'## Evidence and analysis discipline',1);p.write_text(s,encoding='utf-8')
print(json.dumps(record,indent=2),flush=True)
