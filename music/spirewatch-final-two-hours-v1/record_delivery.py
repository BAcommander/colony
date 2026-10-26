"""Save the verified Spirewatch final delivery and narrowly update project records."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,shutil
H=Path(__file__).resolve().parent;R=H.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=read(H/'delivery-validation.json');assert d['status']=='passed' and d['frames']==216000 and d['colony_full_video_audio_decode']
visual=read(H/'visual-review.json');assert visual.get('assistant_inspected') is True,'Inspect final contact sheet first'
settings=read(H/'assembly-settings.json');audio=read(R/'music/illuminated-horizon-stillness-two-hours-v1/delivery-paths.json')
output=Path(d['output']);assert output.stat().st_size==d['bytes']
snapshot=H/'tool-source-snapshot';snapshot.mkdir(exist_ok=True)
base=R/'creative/brand/intro-v3/tool-source-snapshot'
app=Path('C:/dev/SpeedySlideShow')
frozen={}
for name,expected in {**settings['intro_verified_files'],**settings['dependencies']}.items():
    source=Path(name);assert digest(source)==expected,source
    rel=source.relative_to(base) if source.is_relative_to(base) else source.relative_to(app)
    target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target);assert digest(target)==expected
    frozen[rel.as_posix()]=expected
for rel in ['colony/__init__.py','app/__init__.py','app/trims.py']:
    source=app/rel;target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target);frozen[rel]=digest(target)
save(H/'tool-source-snapshot-manifest.json',{'sources':frozen,'scope':'Verified saved Colony v3 engine/fonts plus the recorded local exporter/SFX dependencies. Minimal package init/trims also retained for reproduction; no installed tool files modified.'})
failure=output.with_suffix('.error.log')
if failure.exists():
    archive=H/'history/initial-color-tag-setup'/failure.name
    assert archive.exists() and digest(failure)==digest(archive)
    assert failure.resolve().parent==(R/'exports/spirewatch').resolve()
    failure.unlink()
date=datetime.now(timezone.utc).date().isoformat()
status=f'Current Spirewatch final production ({date}): user requested the final two-hour 4K video through Colony with the approved alternating Horizon/Stillness music and current intro. Delivered exports/spirewatch/Spirewatch-2-Hours-4K-v1.mp4, exact 7200s/3840x2160/30fps/216000 frames, H.264 BT.709 with AAC 192k stereo 48kHz. Verified v8 sixty-second master retained; native artwork is 1672x941, previously Lanczos upscaled. Current v3 AMBIENT COLONY/orbital logo/PRESENTS, SPIREWATCH title and lower Stay a while and listen appear once; graphics clear by 22s, audio silent to5 then fades to20. Existing two-hour gains, eight-second A/B joins and closing fade retained. The local installed Colony copy predates the intro, so the hash-verified saved v3 real renderer/fonts were loaded with existing exporter/SFX dependencies; no installed app source changed. Job-local CRF0 opening unit preserves all first-minute pictures after22s exactly; subsequent119 minute units have identical copied packets and match source decoded YUV. Full Colony video/audio decode, every video timestamp, entire AAC-to-expected-mix comparison, source hashes and output hash passed. Assistant inspected final decoded temporal stills, not continuous playback/full listening. Latest scene authorized for assembly; no separate detailed artistic verdict inferred. Full combined user review/upload checks pending. See music/spirewatch-final-two-hours-v1/README.md and delivery-validation.json. Originals preserved; no paid generation, upload, commit/push or remote media backup.'
changes={}
for relative in ['AGENTS.md','PRODUCTION_PIPELINE.md','creative/MUSIC_WORKFLOW.md']:
    path=R/relative;before=path.read_bytes();after=before
    if relative=='AGENTS.md':
        pattern=rb'^Current Spirewatch v8 4K delivery \(2026-10-21\):[^\r\n]*'
        m=re.search(pattern,after,re.M);assert m
        historical=m.group().replace(b'Current Spirewatch',b'Historical Spirewatch',1)
        after=after[:m.start()]+status.encode()+b'\n\n'+historical+after[m.end():]
    elif relative=='PRODUCTION_PIPELINE.md':
        pattern=rb'^Spirewatch v8 now has a verified clean sixty-second [^\r\n]*'
        m=re.search(pattern,after,re.M);assert m
        after=after[:m.start()]+status.encode()+b'\n\nHistorical source-master record: '+m.group()+after[m.end():]
    else:
        m=re.search(rb'^Current Illuminated Horizon / Stillness soundtrack [^\r\n]*',after,re.M);assert m
        old=m.group();new=old.replace(b'full two-hour listening/video assembly remain separate',b'full combined listening/playback review remains pending; the final two-hour Spirewatch video with intro is now delivered')
        assert new!=old;after=after[:m.start()]+new+after[m.end():]
        after+=f'\n\nSpirewatch final assembly ({date}): the verified two-hour FLAC was supplied once to Colony with no additional gain, joins, loudness matching or SFX. Only the current once-only 0:05–0:20 entrance was added; the closing fade remains supplied. Final video and complete audio/visual verification: ../music/spirewatch-final-two-hours-v1/README.md. Full combined user listening remains pending.\n'.encode()
    if relative!='creative/MUSIC_WORKFLOW.md':
        music=re.search(rb'^Current Illuminated Horizon / Stillness soundtrack [^\r\n]*',after,re.M)
        assert music
        old=music.group();new=old.replace(b'full two-hour listening/video assembly remain separate',b'full combined listening/playback review remains pending; the final two-hour Spirewatch video with intro is now delivered')
        assert new!=old
        after=after[:music.start()]+new+after[music.end():]
    changes[path]=(before,after)
path=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';before=path.read_bytes()
lesson=f'\n\n## Spirewatch final assembly and preserved intro — {date}\n\nThe local installed Colony source/executable predates the already saved v3 intro. Verify the saved release renderer/fonts against its implementation manifest and use that real export engine with recorded local dependencies rather than silently omitting the intro or editing the installation. Seed Prepared with the exact verified master; use color_tags_for(source) to fill omitted redundant colour fields before an opening encode. Directly constructing ColorTags from sparse probe fields passed None into encoder arguments; the first job stopped before encoding and is retained as history. The corrected job uses lossless opening encoding; all pictures after22s equal the source, and119 later clean minute packets are identical. Verify source phase across the first/second-minute boundary, all216000 timestamps, complete video/audio decoding and the entire AAC signal against the source passed through the actual opening graph. Inspect final branded stills and preserve the clean master. This validates production integrity, not continuous playback or artistic approval. See ../music/spirewatch-final-two-hours-v1/README.md.\n'
assert b'## Spirewatch final assembly and preserved intro' not in before
changes[path]=(before,before+lesson.encode())
path=R/'music/spirewatch-animation-v8/README.md';before=path.read_bytes()
addition=f'\n\n## Final two-hour assembly — {date}\n\nUser requested the latest Spirewatch with the approved two-track soundtrack and current intro. [Final video]({output.as_posix()}) is delivered and technically verified. See [assembly evidence](../spirewatch-final-two-hours-v1/README.md). This does not overwrite the clean minute master or historical preview. Full combined user review remains pending; no upload or remote backup.\n'
changes[path]=(before,before+addition.encode())
receipt=[]
for path,(before,after) in changes.items():
    assert path.read_bytes()==before,'Concurrent change; reread before saving'
    path.write_bytes(after)
    receipt.append({'path':str(path),'sha256_before':hashlib.sha256(before).hexdigest(),'sha256_after':hashlib.sha256(after).hexdigest(),'scope':'Spirewatch final status, explicit history label, scoped production lesson or final link only; unrelated bytes retained.'})
inventory=R/'final/local-export-inventory.json';raw=inventory.read_bytes();inv=json.loads(raw)
items=[{'path':output.relative_to(R).as_posix(),'bytes':d['bytes'],'sha256':d['sha256'],'storage':'local ignored; no remote backup','record':'music/spirewatch-final-two-hours-v1/delivery-validation.json'}]
for entry in audio['outputs']:
    items.append({'path':Path(entry['path']).relative_to(R).as_posix(),'bytes':entry['bytes'],'sha256':entry['sha256'],'storage':'local ignored; no remote backup','record':'music/illuminated-horizon-stillness-two-hours-v1/delivery-validation.json'})
for entry in items:
    existing=[v for v in inv['files'] if v['path']==entry['path']]
    if existing:assert len(existing)==1 and existing[0]['sha256']==entry['sha256']
    else:inv['files'].append(entry)
inv['date']=date;assert inventory.read_bytes()==raw;save(inventory,inv)
receipt.append({'path':str(inventory),'scope':'Added the three verified Spirewatch final audio/video exports; existing inventory entries retained'})
save(H/'project-status-update.json',receipt)
summary=f'''# Spirewatch — final two-hour 4K video

Delivered {date} through the actual Colony export engine, with the current once-only v3 intro and the user-approved Horizon/Stillness transitions.

[Open final video]({output.as_posix()})

Exact runtime 2:00:00; 3840×2160, 30 fps, 216,000 frames. H.264 YUV420p BT.709 with stereo 48 kHz AAC at 192 kb/s. Size {d['bytes']:,} bytes. Native artwork detail remains 1672×941, previously Lanczos upscaled in the verified clean master. SHA-256: `{d['sha256']}`.

Opening: AMBIENT COLONY with orbital logo, closer PRESENTS, SPIREWATCH, then the lower “Stay a while and listen”. The current timings, 88% initial darkening and 22-second graphics budget are retained. Sound is silent until 0:05 and rises gently to the approved level at 0:20. Runtime and animation phase are unchanged. No repeated intro or extra subscribe overlay/SFX.

Soundtrack: the existing two-hour FLAC supplied once, gain0, no loudness matching or new playlist joins. Complete original Horizon and long Stillness alternate with the accepted eight-second overlaps, original -7.74/-7.08 dB source gains, and one existing twenty-second closing fade. Source pitch/tempo remain unchanged. The user approved both short transition auditions and requested the final duration; full combined playback review remains pending.

The installed local Colony copy predates the saved intro release. The saved v3 renderer/fonts were checked against their recorded SHA-256 and used via the package search path with recorded local exporter/SFX dependencies. No installed source or executable was changed. The first setup stopped before encoding because sparse source colour fields were passed directly; built-in colour completion fixes this, with the initial attempt preserved in history. The exact verified clean sixty-second loop is reused through Colony Prepared. The opening minute is rendered losslessly with job-local CRF0/veryfast settings; all pixels after22s match the source. Later119 clean minutes remain copied, with identical packet sequences and exact decoded source controls.

Validation: complete Colony video/audio decode without error; all216000 video timestamps and packet sequences checked; all1800 frames of the first clean minute equal the master; first-minute frames after22s equal the master. Every AAC sample over7200 seconds is finite/unclipped and compared with the expected full FLAC passed through Colony's actual intro/limiter graph. Levels, silence, fade and source hashes passed. See assembly-settings.json, colony-export.json, video-validation.json, audio-validation.json and delivery-validation.json. Assistant inspected final decoded opening/scene temporal stills, not continuous playback or full listening.

Sources, clean masters, older attempts and standalone soundtrack are preserved. The final file/cache are local under ignored exports/spirewatch; Git backup does not cover them. No new generation, paid service, upload, commit or push. Reproduction: assemble_with_colony.py, verify_final.py, then record_delivery.py after visual inspection. Scripts preserve existing output. The retained rendering cache is not needed to play the final MP4.
'''
(H/'README.md').write_text(summary,encoding='utf-8')
save(H/'production-manifest.json',{'final_video':{'path':str(output),'bytes':d['bytes'],'sha256':d['sha256']},'settings':'assembly-settings.json','checks':'delivery-validation.json','records':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(H.iterdir()) if p.is_file() and p.name!='production-manifest.json'},'assistant_visual_inspection':visual,'remote_backup':False})
print('Spirewatch final delivery, source/intro/audio records, inventory and scoped status saved.',flush=True)
