"""Place verified long media in standard ignored exports and save scoped status."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,sys,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1]
assert R==Path('G:/AI/colony')
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
validation=json.loads((H/'delivery-validation.json').read_text());assert validation['status']=='passed'
destination=R/'exports'/'spirewatch'
assert destination.resolve().is_relative_to((R/'exports').resolve())
destination.mkdir(parents=True,exist_ok=True)
outputs=[]
for record in validation['outputs']:
    source=H/record['file'];target=destination/record['file']
    assert source.parent==H and target.parent.resolve()==destination.resolve()
    if target.exists():assert not source.exists() and digest(target)==record['sha256']
    else:
        assert source.exists() and digest(source)==record['sha256']
        source.replace(target)
    assert digest(target)==record['sha256']
    outputs.append({'path':str(target),'bytes':target.stat().st_size,'sha256':record['sha256']})
save('delivery-paths.json',{'finalized_utc':datetime.now(timezone.utc).isoformat(),'outputs':outputs,'long_media_location':'Standard Git-ignored exports/spirewatch/','remote_backup':False})
status='Current Illuminated Horizon / Stillness soundtrack (2026-10-25): user accepted both long-Stillness transition previews with "yeah those transitions sound good" and requested a two-hour alternating version. Delivered exports/spirewatch/Illuminated-Horizon-and-Stillness-2-Hours-v1.mp3 and matching stereo 48 kHz/24-bit FLAC. Original Horizon is 8:30, long Stillness 3:00; complete sources alternate with approved eight-second equal-power overlaps and fixed -7.74/-7.08 dB gains. Cycle interval 11:14; eleven Horizon occurrences (final 7:40) and ten complete Stillness occurrences, twenty handovers, exact 2:00:00. One twenty-second closing fade; no extra opening fade, SFX, stretch, pitch shift, EQ or dynamic normalization. Apply the current opening once during later Colony video assembly. All 345,600,000 stereo frames of each file decoded with finite samples/no clipping; full FLAC samples match the complete recipe within 24-bit tolerance. Integrated loudness/true peaks and source hashes verified. User approval covers short joins and extension request; assistant performed technical checks, not listening, and full two-hour listening/video assembly remain separate. See music/illuminated-horizon-stillness-two-hours-v1/README.md, mix-recipe.json, delivery-validation.json and delivery-paths.json. Earlier failed experiments and source files preserved. No new credit spend, video render, commit/push or remote backup of this delivery.'
receipts=[]
for relative in ['AGENTS.md','PRODUCTION_PIPELINE.md','creative/MUSIC_WORKFLOW.md']:
    path=R/relative;before=path.read_bytes()
    pattern=rb'^(?:Current )?Illuminated Horizon / ambient-middle experiment \(2026-10-21\):[^\r\n]*'
    match=re.search(pattern,before,re.M);assert match,relative
    historical=re.sub(rb'^(?:Current )?Illuminated Horizon',b'Historical Illuminated Horizon',match.group())
    replacement=status.encode()+b'\n\n'+historical
    after=before[:match.start()]+replacement+before[match.end():]
    assert after[:match.start()]==before[:match.start()] and after[match.start()+len(replacement):]==before[match.end():]
    if relative=='creative/MUSIC_WORKFLOW.md':
        lesson='\n\n## Separate companion-track arrangement — 2026-10-25\n\nMinimum-influence reference tests retained the unwanted pulse; user reports the five-second slow-phrase reference and its repeated upload-length workaround also did not work. A standalone reference-free thirty-second Illuminated Stillness had potential. User generated a three-minute companion and accepted both eight-second, level-matched handovers to/from original Illuminated Horizon, then requested two-hour A/B alternation. This solved the immediate arrangement direction through a new composition, not a successful removal of the old synth. Preserve full sources, exact gains/joins and the accepted audition records. Match loudness using fixed gains rather than changing tempo; audition both directions before extending. The current two-hour master has no added opening fade so Colony can apply the current opening once. Full technical validation and short-join approval do not imply full-length listening. See ../music/illuminated-horizon-stillness-two-hours-v1/README.md.\n'
        assert b'## Separate companion-track arrangement' not in after
        after+=lesson.encode()
    assert path.read_bytes()==before,'Concurrent edit; reread before replacing'
    path.write_bytes(after)
    receipts.append({'path':str(path),'sha256_before':hashlib.sha256(before).hexdigest(),'sha256_after':hashlib.sha256(after).hexdigest(),'previous_status':match.group().decode(),'scope':'Only new soundtrack current status, historical label on prior experiment; Music Workflow also appends scoped companion-track lesson. Other bytes retained.'})
save('project-status-update.json',receipts)
with (H/'README.md').open('a',encoding='utf-8') as f:
    f.write('\n## Verified final locations\n\n'+''.join('- ['+Path(r['path']).name+']('+Path(r['path']).as_posix()+')\n' for r in outputs)+'\nLong media are stored in the standard Git-ignored exports/spirewatch/ directory. delivery-paths.json records exact hashes and locations. Build script output paths describe the temporary encode staging; finalize_delivery.py moves only the two fully verified files. No remote backup is implied.\n')
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import numpy as np
save('production-manifest.json',{'status':'verified two-hour local audio delivery','source_recipe':'mix-recipe.json','verification':'delivery-validation.json','media':outputs,'records':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(H.iterdir()) if p.is_file() and p.name!='production-manifest.json'},'runtime':{'python':sys.version,'numpy':np.__version__,'ffmpeg':subprocess.run(['ffmpeg','-version'],stdout=subprocess.PIPE,check=True).stdout.decode().splitlines()[0]},'approval_scope':'User accepted both short joins and requested two hours; full-length listening/video assembly separate.','remote_backup':False})
print(json.dumps({'final_media':outputs,'updated_records':len(receipts)},indent=2))
