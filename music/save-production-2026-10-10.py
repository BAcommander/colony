from pathlib import Path
import json,hashlib,subprocess,re
R=Path('G:/AI/colony');P=R/'final/09-offshore-night-office';B=R/'music/production-backup-2026-10-10';B.mkdir(exist_ok=True)
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
tags='ambient music, relaxing ambient music, sci fi ambient music, space ambient music, ocean ambience, ambient music with ocean sounds, ocean sounds with music, sci fi ambience, cozy ambience, focus music, music for studying, background music for work, music for reading, sleep music, atmospheric music, 2 hour ambient music, Ambient Colony, The Shoreless Colony'
assert len(tags)+2*len(tags.split(', '))<500
old=P/'youtube-tags.txt';hist=P/'metadata-history';hist.mkdir(exist_ok=True);snapshot=hist/'youtube-tags-before-listener-revision-2026-10-10.txt'
assert not snapshot.exists();snapshot.write_bytes(old.read_bytes());old.write_text(tags+'\n',encoding='utf-8')
m=json.loads((P/'manifest.json').read_text(encoding='utf-8'));m['youtube_metadata'].update(tags_sha256=sha(old),tags_characters_including_separators=len(tags),tags_characters_including_file_newline=len(tags)+1,tags_count=len(tags.split(', ')),tags_revision={'date':'2026-10-10','reason':'User requested more useful listener-oriented tags; music, sea ambience, listening uses and verified two-hour duration.','previous_file':snapshot.relative_to(P).as_posix(),'search_volume_verified':False});save(P/'manifest.json',m)
p=P/'README.md';s=p.read_text(encoding='utf-8');s=re.sub(r'Tag count: \d+ characters',f'Tag count: {len(tags)} characters',s);p.write_text(s,encoding='utf-8')
p=R/'creative/MUSIC_WORKFLOW.md';s=p.read_text(encoding='utf-8').replace('Updated 2026-09-26.','Updated 2026-10-10.').replace('## Water ambience — Shoreless trial,','## Water ambience — Shoreless accepted mix,')
s=s.replace('## Evidence and analysis discipline','''## Long-form delivery and metadata lessons — 2026-10-10

- Review the music join before extending, and review the SFX plateau separately. A request to lower water by 15% was implemented as an amplitude multiplier of 0.85, or -1.41162149 dB; preserve event timings while changing level. Do not describe this as a 15% change in perceived loudness.
- Keep source recordings and accepted cut/gain/crossfade recipes. Make a long soundtrack with one opening and closing fade, then assemble from the verified short animation with no extra normalization or second SFX layer. The long soundtrack and animation have independent repeat periods.
- Generate clear water detail first; sheltered or muffled prompt wording made the first water result too indistinct. Mix clear water quietly and sparsely afterward. Rainline rain and Shoreless water are different accepted presets, not global defaults. Use the source hashes when reusing them.
- For tags, describe the actual listening experience and likely use: ambient music, focus/study/reading/sleep, sci-fi atmosphere and the audible environment. Retain a couple of channel/title tags. Avoid filling the field with fictional geography or scenery details. This is an editorial relevance decision, not measured search-volume evidence. Do not describe intermittent quiet waves as continuous ocean noise.
- Keep the very large combined exports local under exports/; back up code, sources selected for Git, short masters, prompts, settings and validation records. A Git push of records does not back up a 50 GB combined video. Preserve exact byte hashes for configs/renderers used in fingerprints.

## Evidence and analysis discipline''',1);p.write_text(s,encoding='utf-8')
p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';s=p.read_text(encoding='utf-8');s=s.replace('Updated 2026-10-08.','Updated 2026-10-10.');s+='''
## Verified long-form delivery — Rainline and Shoreless, 2026-10-10

Render 4K from immutable native scene layers and the same preview fingerprint; do not upscale an already compressed 720p preview. These sources are 1672x941, so disclose Lanczos upscaling. Explicit BT.709 conversion and tags, H.264 QP0 yuv420p and no B frames retained the verified scene pictures. Check every encoded short-master frame, regional and composite seam, and minute-wide distinct states before assembly.

Colony's normal preparation scaler previously changed source colour values. Its existing Prepared cache accepts a verified short master, allowing the actual export engine to copy its frames without changing the app or scene. Compare the decoded first minute to the master, then all repeated packet sequences and timestamps. MP4 concat can inject SPS/PPS into IDR packets; compare later encoded loops with the first assembled loop after decoded identity is established, rather than assuming differently framed packets imply altered pixels.

QP0 long exports are large: Rainline one hour is 59.3 GB; Shoreless two hours is 50.7 GB. MP4 faststart reorganization can leave timeline progress unchanged for minutes while disk I/O continues. Check process/disk activity before calling it stalled. Full decode and hashing also take time. Technical verification and decoded-still inspection do not imply full user playback approval.

Evidence: [Rainline delivery](../final/08-rainline-relay/assembly-v1/delivery-validation.json), [Shoreless delivery](../final/09-offshore-night-office/assembly-v1/delivery-validation.json). User approved both music joins and the final SFX balances and authorized latest-scene final assembly. Preserve the scope of earlier visual feedback.
''';p.write_text(s,encoding='utf-8')
masters=['final/06-last-cable-station/video-4k-v3.mp4','final/07-icebound-weather-post/video-4k-v3-60s.mp4','final/08-rainline-relay/video-4k-v5-20s.mp4','final/09-offshore-night-office/video-4k-v3-60s.mp4']
p=R/'.gitattributes';s=p.read_text();s+='\n# 2026-10-10 production backup: exact masters and hash-bound records.\n'
for rel in masters:s+=rel+' filter=lfs diff=lfs merge=lfs -text\n'
for pattern in ['music/cable-animation-v*/**','music/icebound-animation-v*/**','music/colony-sfx-update/**','music/rainline-final-v1/**','music/shoreless-final-v1/**','music/shoreless-music-v1/**','music/production-backup-2026-10-10/**','final/0[5-9]-*/**/*.py','final/0[5-9]-*/**/*.json']:s+=pattern+' -text\n'
p.write_text(s,encoding='utf-8')
p=R/'.gitignore';s=p.read_text();s+='\n# Requested short-master backup; large combined exports stay local.\n'+''.join('!'+rel+'\n' for rel in masters);p.write_text(s,encoding='utf-8')
save(B/'scope.json',{'date':'2026-10-10','request':'commit, ppush and save all our learnings','includes':'Production records, scene code/config/masks and diagnostics for recent work through 09; shared music/animation lessons; selected short 4K masters via exact-path LFS; original reusable rain/water SFX; separate Colony-tool commit.','excludes':'Long exports, original full generated music exports, render/environment caches, intermediate PCM, redundant review media and executables remain local.','masters':[{'path':x,'bytes':(R/x).stat().st_size,'sha256':sha(R/x)} for x in masters],'final_video':{'path':'exports/09-offshore-night-office/Shoreless-Colony-2-Hours-4K-v1.mp4','sha256':'7fddb9e35e7cac4cd0f19d367e542402f2733412164d60f3ae3f1f4698677325','remote_media_backup':False},'remote_verification':'See subsequent local verification receipt; this manifest alone does not prove push.'})
print(json.dumps({'tags':tags,'characters':len(tags),'count':len(tags.split(', ')),'masters':masters},indent=2))
