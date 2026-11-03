"""Reconcile the production and November3 sound-design branches without media edits."""
from pathlib import Path
import subprocess,re,json
H=Path(__file__).resolve().parent;R=H.parents[1];C=H/'cache';C.mkdir(exist_ok=True)
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def stage(n,path):return git('show',f':{n}:{path}')
conflicts=git('diff','--name-only','--diff-filter=U').decode().splitlines()
for p in conflicts:
 for n in [1,2,3]:
  try:(C/(p.replace('/','__')+f'.stage{n}')).write_bytes(stage(n,p))
  except subprocess.CalledProcessError:pass
ours=stage(2,'.gitattributes').decode();theirs=stage(3,'.gitattributes').decode()
existing=set(ours.splitlines());extra=[line for line in theirs.splitlines() if line and line not in existing]
(R/'.gitattributes').write_text(ours+'\n# Imported Snowline sound-design/media rules,2026-11-03.\n'+'\n'.join(extra)+'\n',encoding='utf-8',newline='')
for name in ['README.md','build_library.py','catalog.json','index.html','validation.json']:
 path='music/sfx-library/'+name;(R/path).write_bytes(stage(3,path))
pattern=r'<<<<<<< HEAD\r?\n(.*?)=======\r?\n(.*?)>>>>>>>[^\r\n]*(?:\r?\n|$)'
for path in ['PRODUCTION_PIPELINE.md','creative/MUSIC_WORKFLOW.md','creative/music/november-2026/README.md','final/13-below-the-snowline/music/README.md']:
 p=R/path;s=p.read_text(encoding='utf-8')
 if path=='creative/MUSIC_WORKFLOW.md':
  s=re.sub(pattern,lambda m:m.group(2)+'\n'+m.group(1),s,flags=re.S)
 else:s=re.sub(pattern,lambda m:m.group(1),s,flags=re.S)
 if path=='PRODUCTION_PIPELINE.md':
  s=re.sub(r'^\| 13 \|.*$', '| 13 | [Below the Snowline](final/13-below-the-snowline/README.md) | Existing20s720p V2 animation preserved; artistic review pending | Current2h V6 with radio, wind, creaks, ventilation and both snow takes; full listening pending | [Latest handoff](music/snowline-snow-2026-11-03/RESUME.md); restore media, review animation, then4K assembly |',s,flags=re.M)
 prefix=''
 if path=='creative/music/november-2026/README.md':prefix='Merged production update(2026-11-03): current Snowline audio is the [two-hour V6 with both snow takes](../../../music/snowline-snow-2026-11-03/RESUME.md). November1/2 production records and existing V2 animation are now present in the same checkout. Historical preparation and earlier audition notes below are retained; do not restart accepted music or add SFX twice.'
 if path=='final/13-below-the-snowline/music/README.md':
  prefix='**Current soundtrack,2026-11-03:** [two-hour V6 with both snow takes](../../../music/snowline-snow-2026-11-03/RESUME.md), based on the approved dry pair below, now includes music,47radio calls,80wind passages,24creaks,ventilation and24snow events. Full-session/new-take review remains pending. Use the unity unfaded V6 master for assembly; apply+0.4dB playback gain and the intro/closing once. All SFX are already present. The nine-minute pair below is the preserved dry-music source, not the latest finished sound design.'
  s=s.replace('SFX remain separate and unapproved for this scene. Reuse suitable originals from the SFX library for future in-composition auditions. Animation/thumbnail and final runtime decisions remain in the scene README.','The earlier separate-SFX preparation is superseded by the current V6 sound design linked above. Existing source files and earlier auditions remain history. Animation/thumbnail review and final video assembly remain pending.')
 if prefix:
  i=s.index('\n');s=s[:i+1]+'\n'+prefix+'\n\n'+s[i+1:]
 p.write_text(s,encoding='utf-8',newline='')
(R/'final/13-below-the-snowline/README.md').write_text('''# 13 — Below the Snowline

## Current production —2026-11-03

The November3 sound-design branch is now merged with the existing production work in this checkout. The current soundtrack is **two-hour V6 with both snow takes**; the current animation remains **V2**, a20-second720p loop. No4K/two-hour video has been assembled.

- [Latest audio and restore instructions](../../music/snowline-snow-2026-11-03/RESUME.md): music,47radio calls,80wind passages,24creaks,ventilation and24snow passages alternating two takes. Requested snow level reduction is already applied. Full-session/new-take listening remains pending.
- [Current working sound settings](../../creative/music/sound-design/receiver-2026-11-02/snowline-working-mix-current.json) and [cue sheet](../../creative/music/sound-design/receiver-2026-11-02/cue-sheet-snow-two-hour-v6-2026-11-03.txt).
- [Current V2 animation](../../music/below-the-snowline-animation-v2/README.md): corrected dish masking and equipment/base activity, awaiting user review. Existing native1672×941 [artwork v5](ice-planet-retheme-v3/artwork-v5.png) remains selected.
- [Latest thumbnail candidate](../../music/below-the-snowline-animation-v2/thumbnail-v2.jpg) awaits selection; [earlier approved branded thumbnail](thumbnail-v1.jpg) remains intact. See current packaging learnings before another thumbnail pass.
- [Approved nine-minute dry music pair](../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/README.md) and [earlier wind-only scene audition](../../music/below-the-snowline-wind-review-2026-11-02/README.md) are preserved history, not the current full sound-design mix.

## Next

Review the restored V6 audio and current animation. Assemble the requested full video only after the scene is ready. The V6 unfaded FLAC master already contains all six layers; apply+0.4dB playback gain once and the current Colony intro/closing once. Do not stack the old wind audition onto V6 or reapply historical gain adjustments.

Publication [title](youtube-title.txt),[description](description.txt) and[tags](youtube-tags.txt) remain drafts. Add verified final runtime,resolution and sound-layer details after assembly. Catalog13 maps to creative concept19. Earlier art,prompts,sources and approvals are preserved; exact original30s seed and generation settings remain unverified. No new generation or upload performed by this merge.
''',encoding='utf-8')
p=R/'AGENTS.md';s=p.read_bytes().decode('utf-8');i=s.index('\n');s=s[:i+1]+'\nCheckout synchronization(2026-11-03): merged origin/codex/concept-brainstorms-2026-10-27 at2829fd6 into the existing production branch after user requested pull and identified missing snow work. Latest two-hour Snowline V6 sound design and nine-source library now coexist with local V2 animation and current Deepwell/Junction deliveries. Earlier notes saying the production tree is not merged are historical. Preserve original assets; do not reapply prior wind/radio/creak/snow gain steps. Media restoration evidence belongs in music/repo-sync-2026-11-03/restore-results.json. Local integration only; no push requested.\n\n'+s[i+1:];p.write_bytes(s.encode('utf-8'))
for p in conflicts:
 assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)',(R/p).read_text(encoding='utf-8'),re.M),p
subprocess.run(['git','add','--',*conflicts,'AGENTS.md'],cwd=R,check=True)
(H/'merge-record.json').write_text(json.dumps({'date':'2026-11-03','old_head':git('rev-parse','HEAD').decode().strip(),'incoming':git('rev-parse','MERGE_HEAD').decode().strip(),'conflicts_resolved':conflicts,'resolution':'Keep production visuals/deliveries; use latest remote SFX catalog and V6 audio; combine workflow learnings; retain both media-rule sets','push_authorized':False},indent=2)+'\n',encoding='utf-8')
print('Resolved',len(conflicts),'shared-record/library conflicts; original media not edited.')
