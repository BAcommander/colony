"""Record approved soundtrack and reconcile this scene's catalog entries."""
from pathlib import Path
import json,shutil,hashlib
H=Path(__file__).resolve().parent; R=H.parents[1]; P=H/'paired-loop-v1'; F=R/'final/13-below-the-snowline'; HISTORY=H/'history/before-approved-soundtrack'
QUOTE="ok i think we're good push the track into the repo. and maybe update everything else about the iceline one?"
def read(p):return Path(p).read_bytes().decode('utf-8-sig')
def write(p,s):Path(p).write_bytes(s.encode('utf-8'))
def save(p,d):write(p,json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def archive(p):
    dst=HISTORY/Path(p).relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(p,dst)
def amend(p,old,new):
    archive(p);s=read(p);assert old in s,(p,old);write(p,s.replace(old,new,1))
def prepend(p,paragraph):
    archive(p);s=read(p);i=s.index('\n');write(p,s[:i+1]+'\n'+paragraph+'\n\n'+s[i+1:])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

approval={'date':'2026-11-01','verbatim':QUOTE,'scope':'Accepts delivered nine-minute paired music loop and authorizes repository commit/push and related scene record updates. Does not approve pending animation/thumbnail or imply a full-hour delivery.','master_path':str(P/'Below-the-Snowline-paired-loop-9min-v1.flac'),'master_sha256':sha(P/'Below-the-Snowline-paired-loop-9min-v1.flac'),'duration_seconds':540,'assistant_listening':False}
save(P/'user-approval.json',approval)
recipe=json.loads(read(P/'mix-recipe.json'));recipe.update(status='User-approved paired music loop',user_join_approval=True,approval_record='user-approval.json');save(P/'mix-recipe.json',recipe)
validation=json.loads(read(P/'delivery-validation.json'));validation['musical_approval']='User accepts delivered pair; see user-approval.json. Technical checks do not imply assistant listening.';save(P/'delivery-validation.json',validation)
(P/'analysis').mkdir(exist_ok=True)
for label in ['shelter-full','shelter-body','outpost-full','outpost-body']:
    shutil.copy2(H/'cache'/label/'analysis.json',P/'analysis'/(label+'.json'))
build=read(P/'build.py');build=build.replace("all(sha(r['original_path'])==sha(r['copy_path'])==r['source_sha256'] for r in records)","all(sha(r['copy_path'])==r['source_sha256'] and (not Path(r['original_path']).exists() or sha(r['original_path'])==r['source_sha256']) for r in records)")
write(P/'build.py',build)
prepend(P/'README.md','**Approved 2026-11-01:** user accepts this delivered nine-minute soundtrack and requests commit/push. [Exact approval and master hash](user-approval.json). Earlier pending-review statements below describe delivery-time status. Reproduction now reads archived `analysis/*.json`; Downloads originals are optional when restored source copies are available. Use a fresh output directory for reproduction; newly rendered files require comparison with the approved hash/recipe.')
prepend(H/'README.md','**Current approval, 2026-11-01:** the nine-minute Shelter on the Ice Plain / Outpost on the Ice pair is accepted for Below the Snowline. See [approval](paired-loop-v1/user-approval.json). Repository backup requested; actual remote evidence will be recorded in `backup/remote-backup-verification.json`. SFX, latest animation/thumbnail review, 4K and full-length assembly remain pending.')

for name in ['README.md','description.txt','youtube-title.txt','youtube-tags.txt','music/README.md','music/generation-record.json']:archive(F/name)
write(F/'README.md', '''# 13 — Below the Snowline

## Current production — 2026-11-01

The user has accepted the nine-minute paired soundtrack, **Shelter on the Ice Plain / Outpost on the Ice**, and requested commit/push and updated scene records. The public scene name remains Below the Snowline; “iceline” in the request refers to this project.

- [Approved soundtrack and listening checks](../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/README.md): exact9:00 circular music loop, lossless24-bit48kHz stereo FLAC and MP3. Fixed gains and20s joins in both directions. No SFX or baked opening/closing fade.
- [Current clean artwork v5](ice-planet-retheme-v3/artwork-v5.png): snowy exterior outpost, warm monitoring room, enclosed bridge, communications dish and ion-cannon silhouette. Earlier underground ice-vault artwork is history.
- [Latest animation v2](../../music/below-the-snowline-animation-v2/README.md):20s720p silent loop, corrected dish ghost and richer equipment/base lighting. User review remains pending; no4K or long combined video yet.
- [Latest thumbnail candidate](../../music/below-the-snowline-animation-v2/thumbnail-v2.jpg): Hoth-inspired candidate, not selected by this audio approval. [Earlier approved branded thumbnail](thumbnail-v1.jpg) preserved. Scene-only / sparse-text treatment is a proposed next comparison, not created or approved here.
- Publication drafts: [title](youtube-title.txt), [description](description.txt), [tags](youtube-tags.txt). Updated to the actual snowy outpost and received music. Runtime/resolution/SFX claims must wait for the final export.

## Next production steps

Review the current animation and thumbnail; audition existing wind in the accepted music if desired; decide on any additional sheltered-room ambience; then assemble the agreed full runtime with the current Colony opening once. No additional music generation is needed to proceed. Soundtrack acceptance does not establish a full-hour listening verdict.

## Provenance

[Music status and generation provenance](music/README.md). The user reports extending a liked30s seed, but that exact file, generation prompt/model/settings/cost remain unverified. Hoth reference analysis was signal analysis, not assistant listening. Earlier V1–V3 prompts and artwork/thumbnail versions remain intact. Previous catalog copy is archived under music/below-the-snowline-production-2026-11-01/history/before-approved-soundtrack/.

Catalog13 maps to creative concept19. Native artwork is1672×941. No upload or publication was performed.
''')
write(F/'music/README.md','''# Below the Snowline — approved music

Approved2026-11-01: **Shelter on the Ice Plain** and **Outpost on the Ice**, each300s, combined into an exact540s circular loop. [Production package](../../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/README.md) · [FLAC master](../../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/Below-the-Snowline-paired-loop-9min-v1.flac) · [MP3 review](../../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/Below-the-Snowline-paired-loop-9min-v1.mp3).

Source gains−8.5/−8.0dB; retain4–294s of each source, with20s equal-power joins. File begins at Shelter24s, with its preceding selected head mixed across the closing overlap. No stretch, pitch change, EQ, compression, SFX or added opening/closing fade. Use lossless decoded repetition for later assembly and apply the current Colony intro once.

User accepts the delivered pair and authorizes backup. [Exact approval](../../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/user-approval.json). Full-hour listening and combined video are not yet evaluated. Analysis/recipe/full-decode and boundary checks are recorded; the assistant has not listened.

## Generation provenance and prompts

User says the five-minute sources were made from a liked30s version. That seed was not supplied; model, exact prompt, settings and cost are unverified. Initial Frozen Outpost/Frozen Expanse downloads were actually60s, preserved as earlier intake history.

The user requested the overall atmosphere of SWTOR's Hoth, The Frozen Wastes. [Reference measurements and creative test prompt](../../../music/hoth-reference-analysis-2026-11-01/README.md) are saved. The official third-party recording remains ignored local reference material and is not part of the soundtrack or backup.

Existing V1/V2/V3 prompt files are historical prepared proposals. Do not identify any as the confirmed generation prompt or regenerate the accepted music automatically. The old120s pilot/eight-minute proposal is superseded by the received300s sources and approved540s loop. [Structured record](generation-record.json).

SFX remain separate and unapproved for this scene. Reuse suitable originals from the SFX library for future in-composition auditions. Animation/thumbnail and final runtime decisions remain in the scene README.
''')
write(F/'youtube-title.txt','Below the Snowline — Shelter on an Ice Planet | Sci-Fi Ambient\n')
write(F/'description.txt','''Beyond the warm windows, the frozen world stretches to the horizon.

Take shelter in the monitoring room at a remote ice-planet outpost. An enclosed bridge links the illuminated buildings across a snowy ravine, while a communications dish stands above the base and jagged mountains disappear into the distance.

Featuring Shelter on the Ice Plain and Outpost on the Ice, paired into a continuous sci-fi ambient soundtrack for Ambient Colony.

Music and artwork were created using AI tools. Animation and the final music arrangement were assembled for Ambient Colony.

Welcome to Ambient Colony. Stay a while and listen.

#SciFiAmbience #IcePlanet #AmbientColony
''')
write(F/'youtube-tags.txt','Below the Snowline, Below the Snow Line, Ambient Colony, sci fi ambience, sci fi ambiance, ice planet, frozen outpost, snowy mountains, space colony, winter sci fi, warm control room, remote station, science fiction scenery, cinematic ambience, distant world, sheltered outpost\n')
old=json.loads(read(F/'music/generation-record.json'))
sources=[]
for s in recipe['sources']:
    sources.append({'title':'Shelter on the Ice Plain' if s['title']=='shelter' else 'Outpost on the Ice','path':str(Path(s['copy_path']).relative_to(R)).replace('\\','/'),'sha256':s['source_sha256'],'duration_seconds':300})
old.update(status='User-approved nine-minute paired loop delivered',updated='2026-11-01',actual_generated_files=sources,short_test_files=[],selected_test={'user_report':'Liked30s seed; exact file not supplied'},long_export=str((P/'Below-the-Snowline-paired-loop-9min-v1.flac').relative_to(R)).replace('\\','/'),user_feedback=approval,audio_approval=True,local_join_review=str(P/'README.md'),delivery_duration_seconds=540,current_prompt_version='Exact generation prompt unverified; earlier V3 proposal and later Hoth test draft retained',generation_settings_verified=False,sfx_status='Not added or approved',video_status='V2 preview remains awaiting review; no final combined video')
save(F/'music/generation-record.json',old)
planpath=R/'creative/music/november-2026/month-plan.json';archive(planpath);plan=json.loads(read(planpath));item=next(x for x in plan['items'] if x['catalog_id']=='13')
item.update(status='Nine-minute paired music loop approved; animation/thumbnail review, SFX and full-length assembly pending',generated_files=sources,actual_source_durations_seconds=[300,300],selected_pilot='User-reported liked30s seed; exact file unknown',audio_delivery=old['long_export'],audio_approval=approval,generation_provenance_note='Exact model, prompt, settings, seed and cost unverified; prepared V3 durations are historical proposals',actual_loop_seconds=540)
save(planpath,plan)
amend(R/'PRODUCTION_PIPELINE.md','| 13 | [Below the Snowline](music/below-the-snowline-animation-v2/README.md) | V2: dish ghost fixed; colored console/base lighting and activity; 20s720p checked | Retheme prompts pending; no audio | Review v2 animation and new Hoth thumbnail; 4K pending |','| 13 | [Below the Snowline](final/13-below-the-snowline/README.md) | V2: dish ghost fixed; equipment/base lighting;20s720p review pending | Approved9:00 Shelter/Outpost circular music loop; SFX pending | Review animation/thumbnail, audition SFX, then full-length4K assembly |')
amend(R/'final/README.md','| [13 - Below the Snowline](13-below-the-snowline/) | [Selected v2 artwork](13-below-the-snowline/artwork-v2.png); no video yet | [JPEG](13-below-the-snowline/thumbnail-v1.jpg) |','| [13 - Below the Snowline](13-below-the-snowline/) | [Current v5 artwork](13-below-the-snowline/ice-planet-retheme-v3/artwork-v5.png); [v2 animation](../music/below-the-snowline-animation-v2/README.md); [approved9min music](../music/below-the-snowline-production-2026-11-01/paired-loop-v1/README.md) | [Latest candidate](../music/below-the-snowline-animation-v2/thumbnail-v2.jpg), review pending; [earlier approved JPEG](13-below-the-snowline/thumbnail-v1.jpg) |')
prepend(R/'creative/music/november-2026/README.md','Below the Snowline update(2026-11-01): [nine-minute paired soundtrack approved](../../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/README.md), from two supplied five-minute extensions. The user prefers the overall Hoth/SWTOR atmosphere. Exact generation wording remains unverified. Earlier proposed pilot durations below are historical; animation/thumbnail/SFX and full-length assembly remain pending.')
prepend(R/'AGENTS.md','Below the Snowline approved music(2026-11-01): user accepts the9min Shelter on the Ice Plain/Outpost on the Ice loop and explicitly requests commit/push plus related scene updates. music/below-the-snowline-production-2026-11-01/paired-loop-v1/ holds24-bit48kHz FLAC, MP3, two60s join checks, source analysis and reproducible recipe. Each original is300s; gains−8.5/−8.0dB, retained4–294s,20s equal-power joins in both directions; exact540s. No stretch/EQ/compression/SFX or added opening/closing fade. Full decode/all-sample recipe and boundary checks passed; user acceptance recorded, assistant has not listened. Catalog/metadata/month tracker now match snowy v5 art and approved audio; old underground copy archived. Animation v2 and thumbnail candidate remain pending user review, no4K/hour combined export. Exact30s seed/prompt/model/cost unverified. Hoth reference recording stays ignored; only measurements/brief backed up. Actual push evidence: music/below-the-snowline-production-2026-11-01/backup/remote-backup-verification.json. Preserve unrelated work and shared main.')
print('Updated approval, catalog, metadata, music provenance and production trackers.')
