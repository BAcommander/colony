"""Build the local review page and record the delivered scene, without Git actions."""
from pathlib import Path
from html import escape
import hashlib,json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REL=HERE.relative_to(ROOT).as_posix()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,value):path.write_bytes(value.encode('utf-8'))
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def prepend(path,value):
    first,sep,body=path.read_bytes().partition(b'\n');anchor=value.splitlines()[0].encode()
    if anchor not in body:path.write_bytes(first+sep+b'\n'+value.encode()+b'\n'+body)
def main():
    delivery=load(HERE/'delivery-validation.json');details=load(HERE/'detail-review-validation.json');cfg=load(HERE/'settings.json');continuation=load(HERE/'continuation-checkpoint.json')
    assert delivery['status']=='technical_checks_passed_user_visual_review_pending' and details['source_sha256']==delivery['sha256']
    assert continuation['review_media']['sha256']==delivery['sha256'];media=ROOT/delivery['path'];assert digest(media)==delivery['sha256']
    for item in details['reviews']:assert digest(HERE/item['path'])==item['sha256']
    chapters=[(0,'Start'),(12,'Cabin displays'),(27.2,'Work lamp and bonnet'),(57.1,'Passing car'),(65,'Rain gust'),(78,'Diagnostic sweep'),(94,'Second lamp dip'),(115,'Approach the join')]
    buttons=''.join(f'<button type="button" data-t="{t}">{int(t)//60}:{int(t)%60:02d} · {escape(label)}</button>' for t,label in chapters)
    detail_html=''.join(f'<details><summary>{escape(x["path"].removeprefix("Back-Before-Dawn-").removesuffix(".mp4").replace("-"," "))} · {x["seconds"]} s</summary><video controls playsinline preload="none" src="{escape(x["path"],quote=True)}"></video></details>' for x in details['reviews'])
    poster='evidence/combined-60.00s.png';assert (HERE/poster).is_file()
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Back Before Dawn — visual review</title><style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#12161a;color:#f2ece1;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1340px;margin:auto;padding:2rem 1.5rem 4rem}}h1{{font-size:2.25rem;line-height:1.14;margin:.25rem 0 1rem}}a{{color:#91d0e3}}.meta{{color:#e6b978;font-size:.8rem;letter-spacing:.1em}}.note{{color:#babfc1;max-width:78ch}}video{{display:block;width:100%;max-height:82vh;height:auto;background:#080a0d}}.chapters{{display:flex;flex-wrap:wrap;gap:.55rem;margin:1rem 0}}button{{font:inherit;font-size:.9rem;background:#252c33;color:#eeeae1;border:1px solid #55616a;padding:.48rem .75rem;cursor:pointer}}button:hover,button:focus{{border-color:#e6b978}}details{{border:1px solid #38424b;margin:.65rem 0;padding:.65rem .9rem}}summary{{cursor:pointer}}details video{{margin-top:.75rem}}footer{{margin-top:2rem;color:#babfc1;font-size:.9rem}}
</style></head><body><main><p class="meta">AMBIENT COLONY · SCENE 18 · VISUAL DRAFT</p><h1>Back Before Dawn</h1><p class="note">A quiet workshop after dark. Two minutes at 720p/30fps, with exterior rain, warm practical light and a time machine left in the garage. Silent review.</p><video id="main-video" controls loop playsinline preload="metadata" poster="{poster}" src="{media.name}"></video><div class="chapters">{buttons}</div><p class="note">Watch the full composition first. The car pass spans the one-minute boundary; the ten-minute production schedule uses the same physical weather speed and wider gaps between rare events.</p><h2>Closer views and loop join</h2>{detail_html}<p class="note">Detail crops come from the encoded draft at the same speed and strength. The join clip shows 1:55–2:00 followed by 0:00–0:05.</p><p><a href="CONTINUE.md">Continuation recipe</a> · <a href="documentation/LEARNINGS.md">Saved lessons</a> · <a href="delivery-validation.json">Technical checks</a></p><footer>User visual review, full ten-minute audition, sound and 4K remain pending.</footer></main><script>const mainVideo=document.getElementById('main-video');document.querySelectorAll('button[data-t]').forEach(button=>button.addEventListener('click',()=>{{mainVideo.currentTime=Number(button.dataset.t);mainVideo.play()}}));document.querySelectorAll('video').forEach(video=>video.addEventListener('play',()=>document.querySelectorAll('video').forEach(other=>{{if(other!==video)other.pause()}})));</script></body></html>'''
    write(HERE/'review.html',page)
    links='\n'.join(f'- [{x["path"]}]({x["path"]})' for x in details['reviews'])
    write(HERE/'README.md',f'''# Back Before Dawn — complete visual draft

[Watch the two-minute scene]({media.name}) · [Review with chapter controls](review.html) · [Scene18 package](../../final/18-back-before-dawn/README.md).

Silent1280×720 at30fps, rendered native-first from the unchanged1672×941 H1 artwork. The locked camera holds the parked DeLorean while rain, wet-street reflections, eave drips, restrained foliage, cabin electronics, a perspective-mapped scope, coupled work-lamp/bonnet light, faint dust and one grounded sedan pass carry the motion. The source closed vessel has no added steam.

Watch 0:12 for a cabin hold, 0:27 for the lamp/bonnet dip, 0:57–1:11 for the passing sedan, 1:05 for the next gust and 1:18–1:30 for the upper display sweep. Rare cues are closer in this review than in the implemented ten-minute production schedule.

## Actual-video details

{links}

## What was corrected

The first cutout version had an internal blue chord where a moving canopy cut revealed generated sky, and the original rain mask touched a small raised-door fin. Preserve the [first-cutout record](history/first-cutout/disposition.json). The final uses bounded original-source foliage motion with fixed boundaries, and a dedicated fin exclusion. [Independent correction checks](source-audit/correction-validation.json) test local palette provenance and the fin across weather states. The generated sky is archived as a rejected experiment; the generated sedan remains in use with measured source headlamps.

## Verification and handoff

Full decode: {delivery['decoded_frames']} sequential frames, {delivery['unique_decoded_frame_hashes']} distinct picture hashes, no audio. Native-to-YUV controls, source protection, source-tap/warp checks and actual regional encoded steps pass at the one-minute boundary and the end-to-start join. Some quiet environment phases repeat while the attention timeline carries different actions. All detail videos are from the encoded master. Native and colour-aware decoded stills inspected; no assistant continuous-playback or user artistic verdict inferred.

[Continue later](CONTINUE.md) · [Settings](settings.json) · [Asset hashes](assets/asset-manifest.json) · [Sound cues](documentation/cue-sheet.json) · [Today's lessons](documentation/LEARNINGS.md). Production600 is implemented and native-checked; full playback, audio and4K remain pending. Save these files locally; a new commit/push was not requested.
''')
    catalog_path=ROOT/'final/catalog.json';catalog=load(catalog_path);source='../../'+cfg['source'];thumb='../../creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/thumbnail-v1.jpg'
    entry={'folder':'18-back-before-dawn','title':'Back Before Dawn','catalog_number':'18','title_status':'working title','status':'Complete120s silent720p30 visual draft technically verified; user visual review pending. Sparse600s attention mode implemented/native-audited; full playback, audio and4K pending.','artwork':source,'animation_source':source,'thumbnail':thumb,'thumbnail_status':'existing H1 draft','video':None,'audio':None,'duration_seconds':None,'animation_preview':{'folder':'../../'+REL,'video':media.name,'duration_seconds':120,'fps':30,'user_approved':False},'animation_review':'../../'+REL+'/review.html','manifest':'manifest.json','production_brief':'README.md'}
    catalog=[item for item in catalog if str(item.get('catalog_number',''))!='18']+[entry];catalog_path.write_bytes((json.dumps(catalog,indent=2)+'\n').replace('\n','\r\n').encode())
    tracker=ROOT/'PRODUCTION_PIPELINE.md';raw=tracker.read_bytes();row=b'| 18 | [Back Before Dawn](final/18-back-before-dawn/README.md) | [120s720p30 visual draft](music/back-before-dawn-animation-v1/README.md), source-safe corrections and full technical checks passed | Gust/vehicle/practical cue sheet; no soundtrack or SFX mix yet | Review full motion and details, then audition implemented600s schedule, audio and 4K |';lines=raw.splitlines(keepends=True)
    if not any(line.startswith(b'| 18 |') for line in lines):
        pos=next(i for i,line in enumerate(lines) if line.startswith(b'| 17 |'));lines.insert(pos+1,row+b'\n');tracker.write_bytes(b''.join(lines))
    index=ROOT/'final/README.md';lines=index.read_bytes().splitlines(keepends=True)
    if not any(line.startswith(b'| [18 -') for line in lines):
        pos=next(i for i,line in enumerate(lines) if line.startswith(b'| [17 -'));lines.insert(pos+1,b'| [18 - Back Before Dawn](18-back-before-dawn/) | [120-second 720p/30fps first draft](../music/back-before-dawn-animation-v1/README.md), visual review pending | [Back Before Dawn draft](../creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/thumbnail-v1.jpg) |\n');index.write_bytes(b''.join(lines))
    prepend(ROOT/'creative/ANIMATION_KNOWLEDGE_BANK.md','''## Back Before Dawn scene18 — 2026-11-05

[The complete workshop draft](../music/back-before-dawn-animation-v1/README.md) uses the H1 DeLorean art unchanged, with nine effect groups over a two-minute review. Its independent visual audit caught two defects after the first broad numeric checks passed. A tree cutout boundary through a solid crown exposed inferred blue sky, and the broad car exclusion missed a small upper door fin. Preserve the failed setup as a lesson: masks can be numerically respected yet semantically wrong. Fix the actual small feature, not the whole scene.

When a motion region cuts through solid foliage, keep that internal boundary fixed and use bounded original-source deformation, or prepare a genuinely complete isolated silhouette. Generated cleanup can change pixels underneath and should never become an accidental whole-plate replacement. Verify the original local source palette for a source-only warp and inspect native crops. Name small fixed geometry such as fins independently in the protection audit; the corrected workshop fin passes all240 targeted weather states. First-cutout settings/reports and generated sky are retained as rejected history.

The moving sedan keeps its body, headlamps, shadow and wet-road response attached. Determine reflection anchors from real emissive lenses on the RGBA source rather than guessed floating glows. Include a tall enough visible vehicle volume above the road, then subtract the hero occluder. Workshop electronics alter source emitters and nearby material receivers, while a complete white work-lamp core and bonnet reflection share one linear-light dip. A lidded bench vessel supplies no steam.

Scene18 turns the separate clock proposal into executable settings:60s physical fields,120s review attention and sparse600s production attention. Carry absolute cue time through minute and later render boundaries; the review sedan crosses t60 without restarting. Both clocks have native controls, but native passes are not full production playback. Retain exact review clips, input hashes, settings and a short continuation check. Do not reuse scene-specific Snowline gain or frequency choices. [Detailed saved lessons and cue sheet](../music/back-before-dawn-animation-v1/documentation/LEARNINGS.md).
''')
    prepend(ROOT/'AGENTS.md','''Back Before Dawn scene18 first draft (2026-11-05): user selects the recommended H1 DeLorean workshop by requesting the complete animation for18 and saving today's lessons. music/back-before-dawn-animation-v1/ delivers a silent120s720p30 visual draft, four actual-video detail crops and an exact10s tail/head review. Native1672x941 source unchanged; parked body/door/wheels and camera fixed. Nine groups: bounded foliage, exterior rain, wet road, eave drips, cabin banks/receivers, CRT, coupled lamp/bonnet dips, dust and one distant RGBA sedan with measured headlamps and occlusion. The first technically passing cutout version revealed a blue chord inside a crown and rain on a tiny door fin; source-only bounded foliage and a dedicated fin mask corrected them. Generated clean sky retained as rejected history, sedan retained in use. Full3600-frame decode/timestamps, native/YUV controls, actual t60/end joins and independent fin/palette/source checks passed. Two-minute attention over60s physical weather; executable sparse600s attention mode native-audited, full playback unreviewed. See review.html, delivery-validation.json, continuation-checkpoint.json, CONTINUE.md and documentation/. Native/decoded stills inspected, not continuous playback. Artistic verdict, soundtrack, 4K and final runtime pending. Catalog18 is Back Before Dawn working title; existing H1 thumbnail is a draft. Work saved on main locally; no new commit/push/upload or paid API. Prior16/17 backup scope is separate.
''')
    scene_readme=ROOT/'final/18-back-before-dawn/README.md';old=scene_readme.read_text(encoding='utf-8');marker='[Review page and chapter controls]';
    if marker not in old:write(scene_readme,old+'\n[Review page and chapter controls](../../'+REL+'/review.html) · [Continuation recipe](../../'+REL+'/CONTINUE.md)\n')
    print('Saved verified local review, scene18 index and reusable lessons')
if __name__=='__main__':main()
