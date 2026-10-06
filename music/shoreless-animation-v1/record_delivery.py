from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/09-offshore-night-office'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');p=read(H/'preview-validation.json')
assert a['fingerprint']==i['fingerprint']==p['fingerprint']
assert len(i['clips'])==4 and all(c['validation']['frames']==240 for c in i['clips'])
assert p['clips'][0]['validation']['frames']==600 and p['clips'][1]['validation']['frames']==1800
assert p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(v['pass'] for c in p['clips'] for v in c['validation']['encoded_seam'].values())
status='V1 silent twenty-second 720p draft delivered: moving sea/clouds, rotating existing turbines, independent cabin lights and room/monitor activity; review pending'
d={'date':'2026-10-06','status':status,'user_request':'ok based on everything likes do the next animation?','scene_selection':'Next catalog entry after Rainline: 09 The Shoreless Colony.','fingerprint':p['fingerprint'],'preview':p['clips'][0],'three_loop_review':p['clips'][1],'isolated_tests':i['clips'],'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],'silent':True,'user_motion_approved':False,'four_k_produced':False,'inspection':'Inspected source, coordinate crops, masks, temporal full-scene samples and decoded isolated/composite stills; no continuous playback claim.','knowledge_bank':'creative/ANIMATION_KNOWLEDGE_BANK.md','water_quantization':a['water_frequency_quantization_deviation_percent'],'limits':['Source-based water and optical blade extraction, not fluid or mechanical simulation.','Cloud transport uses local overlapping lifetimes; naturalness requires normal-speed review.','User approval of other scenes does not approve this new draft.'],'storage':'Local ignored draft media; no credits, commit or push. Existing artwork and prior scene files preserved.'}
save(H/'delivery-v1.json',d)
(H/'README.md').write_text('''# The Shoreless Colony animation v1

2026-10-06. First draft for catalog 09, built under the request to animate the next scene using accumulated feedback. Uses the clean artwork-v1.png, not the thumbnail adaptation. This is a review candidate.

- [Twenty-second silent 720p preview](shoreless-colony-v1-preview-20s.mp4)
- [Sixty-second review with three exact repetitions](shoreless-colony-v1-three-loops-60s.mp4)
- [Sea test](water-isolated-v1-8s.mp4)
- [Cloud test](sky-isolated-v1-8s.mp4)
- [Turbine test](turbines-isolated-v1-8s.mp4)
- [Room and monitors test](room-isolated-v1-8s.mp4)
- [Delivery record](delivery-v1.json)
- [Configuration](scene-plan-v1.json)
- [Mask review](mask-review.png)

## Visible actions

The original choppy sea moves through a filtered 24-wave perspective reflection surface. Displacement .40, contrast .045 and specular strength 3 retain the source water character at a restrained starting strength. Caissons, access platforms, connecting corridors and antenna masts are excluded from the output and sampled water texture. The treatment is a source-based 2D approximation; waves do not physically break around supports.

Upper and low cloud layers travel independently at 2.2 and 1.4 source pixels per second. Local overlapping lifetimes hide resets while preserving forward movement. Moons, island outlines, window frame and antenna silhouettes are excluded from the moving source and output. This can soften cloud texture; judge naturalness at normal speed.

The two existing turbine blade images are extracted over locally reconstructed sky and rotate once per twenty seconds. Fixed hubs and masts are restored over the blades. Small independently timed red hub lights support them. This optical reconstruction is new for Shoreless and awaits review, rather than inheriting acceptance from another scene.

Three small groups of cabin panes have independent dark holds of 5.4, 6.2 and 4.7 seconds; the last wraps across the join. Other windows and exterior practical lights remain steady. Source-space, supersampled masks preserve the visible frames and dividers. The foreground shelf light has a brief paired flicker near 4.2/4.8 seconds and a gentler dip near 14.1 seconds, with associated warm wall and desk illumination.

The left monitor has a moving marker along the existing platform diagram. An existing narrow log panel on the right monitor scrolls forward and its small status area carries changing segmented meters. Main monitor pictures, bezels, furniture and camera remain fixed.

## Reused lessons and checks

The configuration records the knowledge-bank choices: Glacier/Floodplain water and sampling protection, Cable cloud transport and monitor activity, Ringfall/Floodplain complete light apertures and local spill, and Saltline/Icebound circular light schedules. All coordinates are mapped afresh to this 1672x941 plate. Before rendering, sample inspection prompted additional protection for thin antenna masts in both sky and water regions.

Four eight-second isolated tests precede the complete draft. Analytic layer endpoints/seams, finite frames and protected source pixels passed. Every preview/review frame decoded with sequential timestamps; regional/composite encoded seam gates passed, with no duplicate endpoint. The sixty-second review has three identical decoded repetitions; it is not a unique one-minute animation. Water frequency quantization deviations are recorded in analytic-validation.json.

Assistant inspected source/crops/masks, temporal full-scene samples and decoded stills, not continuous playback. User review is pending, especially sea strength, turbine extraction, cloud travel, light masks and monitor readability. No 4K master, soundtrack or combined long video for scene 09 yet. Preview: 1280x720, 30 fps, silent. Future 4K will upscale the native 1672x941 source.

Use render_shoreless.py --stage samples, then isolated, then preview with the existing local Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. setup_scene.py refuses an existing config; renderer outputs refuse existing MP4 destinations. The shared Floodplain water/encoder and timing primitives are imported unchanged and fingerprinted. Draft videos remain local ignored files. No paid generation, new model, Git commit or push.
''',encoding='utf-8')
m=read(P/'manifest.json');old=m.get('animation_current')
if old and old.get('preview')!=d['preview']['path']:m.setdefault('animation_history',[]).append(old)
m['animation_current']={'status':status,'package':'../../music/shoreless-animation-v1/README.md','delivery':'../../music/shoreless-animation-v1/delivery-v1.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'user_motion_approved':False,'four_k_export_produced':False};save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8');old='No animation or soundtrack produced yet.';assert old in s
s=s.replace(old,'A [twenty-second v1 animation draft](../../music/shoreless-animation-v1/README.md) now includes sea/cloud movement, slow turbine rotation, independent windows and room/monitor activity. User motion review is pending; no soundtrack or 4K delivery yet.',1);rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8');lines=s.splitlines();line=next(x for x in lines if x.startswith('| 09 |'))
new='| 09 | [The Shoreless Colony](final/09-offshore-night-office/README.md) | V1 twenty-second 720p draft: sea/clouds, turbines, cabin lights and monitors; review pending | Short/long prompts ready; no audio | Review v1 sea strength, turbine edges, cloud travel and lighting before 4K |'
s=s.replace(line,new,1);rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');head,rest=s.split('\n\n',1)
note='Current Shoreless animation (2026-10-06): user requested the next animation using accumulated scene lessons. Catalog 09 now has a silent twenty-second 720p/30 fps v1 preview and sixty-second three-repeat review in music/shoreless-animation-v1/; see README.md and delivery-v1.json. Immutable clean artwork-v1.png SHA-256 f042d109358089f0e89b11c99a84505fba9a825dca3428ed7109055d29253f69, native 1672x941. Reuses filtered 24-wave water, source-cloud transport and deterministic light timing with newly mapped caissons, corridors, moons, thin masts and room masks. Two existing turbine blade images rotate optically around fixed hubs; independent red beacons, three cabin pane groups, shelf-light/wall/desk flickers, a diagram marker and scrolling log/meters support the sea/sky. Four isolated eight-second tests, analytic layer seams, protected source assertions, full 600/1800-frame decodes/timestamps, encoded regional/composite seams and three identical decoded repeats passed. Assistant inspected source/crops/masks/temporal/decoded stills, not continuous playback. New turbine extraction and the full look require user review; 4K, music and long assembly pending. Prior scenes untouched; no credits, commit or push. Knowledge bank includes the new candidate and its reuse limits.'
assert 'Current Shoreless animation (' not in s
rp.write_text(head+'\n\n'+note+'\n\n'+rest,encoding='utf-8')
rp=R/'final/catalog.json';cat=read(rp)
for e in cat:
 if e['folder']=='09-offshore-night-office':e.update(status=status,animation_preview='../../music/shoreless-animation-v1/README.md')
save(rp,cat)
rp=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';s=rp.read_text(encoding='utf-8');anchor='## Render and delivery improvements to retain';assert anchor in s
entry='''### 09 The Shoreless Colony

**Current candidate:** first twenty-second v1 draft, user review pending. [Scene record](../music/shoreless-animation-v1/README.md), [configuration](../music/shoreless-animation-v1/scene-plan-v1.json), [renderer](../music/shoreless-animation-v1/render_shoreless.py).

- Starts with the prior lessons: filtered perspective water with protected caissons, independently moving cloud depths, complete cabin panes, coupled room-light spill and readable actions inside original monitors. These mapped effects are technically checked, not yet artistically accepted for Shoreless.
- Thin antenna masts intersect both the sea and sky regions. Source/mask inspection caught these before the motion tests; protect them in both texture sampling and output, including the short section above a platform roof.
- Slow rotation uses the existing turbine blade image over a locally reconstructed background and restores the fixed hub/mast. This is a new candidate optical method; inspect blade remnants, extraction edges and background consistency before reusing it elsewhere.
- The source sea is choppy. Preserve its texture and tune movement strength independently; do not flatten it to match a different scene's calm-water setting or claim physical waves around the supports.

'''
s=s.replace(anchor,entry+anchor,1).replace('lessons from videos 01–08','lessons from videos 01–09',1)
s=s.replace('For videos 09–14,','For videos 10–14,');rp.write_text(s,encoding='utf-8')
for rel in ['AGENTS.md','PRODUCTION_PIPELINE.md','creative/ANIMATION_WORKFLOW.md']:
 rp=R/rel;s=rp.read_text(encoding='utf-8')
 s=s.replace('It consolidates videos 01–08:','It consolidates videos 01–09:').replace('links lessons from videos 01–08','links lessons from videos 01–09').replace('The bank covers videos 01–08','The bank covers videos 01–09')
 rp.write_text(s,encoding='utf-8')
print('Shoreless v1 delivery, scene status and knowledge-bank candidate recorded')
