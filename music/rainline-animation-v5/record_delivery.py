from pathlib import Path
import json, hashlib

H=Path(__file__).resolve().parent
R=H.parents[1]
P=R/'final/08-rainline-relay'
V4=H.parent/'rainline-animation-v4'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,d): p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')

a=read(H/'analytic-validation.json')
i=read(H/'isolated-validation.json')
p=read(H/'preview-validation.json')
retained=read(H/'v4-retained-layer-check.json')
assert a['fingerprint']==i['fingerprint']==p['fingerprint']==retained['v5_fingerprint']
assert all(retained['isolated_source_frames_byte_identical'].values())
assert len(i['clips'])==2 and p['clips'][0]['validation']['frames']==600
assert p['clips'][1]['validation']['frames']==1800
assert p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(e['pass'] for clip in p['clips'] for e in clip['validation']['encoded_seam'].values())
snapshot=V4/'renderer-v4-snapshot.py'
assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==read(V4/'delivery-v4.json')['fingerprint']['renderer_sha256']
status='V5 twenty-second silent 720p draft delivered: brief foreground lamp blinks and sliding rain beads on window glass; review pending'
d={
 'date':'2026-10-05','version':'v5','status':status,
 'feedback':(H/'feedback-v4.txt').read_text(encoding='utf-8'),
 'fingerprint':p['fingerprint'],'preview':p['clips'][0],
 'three_loop_review':p['clips'][1],'isolated_tests':i['clips'],
 'retained_v4_layers':retained,'silent':True,
 'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],
 'user_motion_approved':False,'four_k_produced':False,
 'inspection':'Inspected masks, temporal full-scene samples and decoded isolated/composite stills. No continuous playback claim.',
 'changes':[
  'Two brief lamp blinks at approximately 4 and 14 seconds, coupled to warm desk spill and nearby lamp halo.',
  'Twelve sparse sliding rain beads/trails with local refraction and highlights, constrained to window glass.',
  'V4 water, rain, building lights, screen, radio, beacons and mist retained; sampled isolated frames at 0 and 7 seconds match v4 exactly.'
 ],
 'approval_scope':'User said v4 was about there and requested this refinement. V5 appearance and timing await user review.',
 'v4_renderer_snapshot':snapshot.relative_to(R).as_posix(),
 'storage':'Local ignored draft media; earlier art/media/config retained. No credits, commit, push or remote media backup.'
}
save(H/'delivery-v5.json',d)
(H/'README.md').write_text('''# Rainline Relay — animation v5

2026-10-05. User felt v4 was nearly there and requested a foreground light blink and rain on the windows. V5 is a review candidate; this request does not establish final visual approval.

- [20-second silent 720p/30 fps preview](rainline-relay-v5-preview-20s.mp4)
- [60-second review: three exact repetitions](rainline-relay-v5-three-loops-60s.mp4)
- [Glass-rain isolated test](glass-isolated-v5-8s.mp4)
- [Foreground-room isolated test](room-isolated-v5-8s.mp4)
- [Delivery record](delivery-v5.json)

## Changes

The desk lamp has two brief, clearly dark blinks at approximately four and fourteen seconds. The existing white emitter, warm desk light and nearby halo dim together. Remaining slow lamp variation is reduced. Furniture, shade and camera remain fixed.

Twelve sparse rain beads slide along the foreground window glass, leaving narrow wet trails. Each has a locally refracted view and restrained cool highlights. Motion is clipped to the existing glass mask, protecting frames and foreground equipment. Ten- and twenty-second lifetimes divide the loop; local fade-in/out hides particle resets. This is a procedural optical approximation, not a fluid simulation.

V4 water strength/speed, radio and screen activity, corrected building panes, red/green antenna cycles, exterior rain and mist are retained. Separate frames for eight retained layers match v4 byte-for-byte at 0 and 7 seconds; this sampled regression does not claim full playback review.

## Checks and status

Two eight-second isolated tests preceded the complete draft. Analytic layer endpoints/seams, finite source frames and unchanged protected pixels passed. All 600 preview and 1800 repeated-review frames decoded with sequential timestamps. Regional/composite encoded seam gates passed, and the review contains three exact decoded copies without duplicate endpoints. Reports bind source/config/code/dependency/mask hashes.

Assistant inspected masks, temporal samples and decoded isolated/composite stills, not continuous playback. User normal-speed review is pending. The source is 1672x941; this preview is 1280x720. No 4K, music or long assembly for scene 08 yet. Earlier versions remain preserved. The exact v4 renderer is saved as ../rainline-animation-v4/renderer-v4-snapshot.py and verified against its delivery hash. Draft media remain local and ignored by Git. No credits, commit or push.

Run ../rainline-renderer/render_rainline.py with --config pointing to scene-plan-v5.json and --stage samples, isolated, then preview. Existing MP4 destinations are protected. Use the existing Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. prepare_v5.py records the initial configuration changes and snapshot step; it is not intended to overwrite a later renderer. The final scene-plan-v5.json is authoritative, including subsequent bead visibility and lamp-halo refinements.
''',encoding='utf-8')

m=read(P/'manifest.json')
old=m.get('animation_current',{})
if old and old.get('preview')!=d['preview']['path']:
 m.setdefault('animation_history',[]).append(old)
m['animation_current']={
 'status':status,'package':'../../music/rainline-animation-v5/README.md',
 'delivery':'../../music/rainline-animation-v5/delivery-v5.json',
 'preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],
 'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':20,
 'preview_dimensions':[1280,720],'fps':30,'four_k_export_produced':False,
 'user_motion_approved':False,'feedback_on_v4':d['feedback']
}
save(P/'manifest.json',m)
rp=P/'README.md'
s=rp.read_text(encoding='utf-8')
start=s.index('The [revised 20-second v4')
end=s.index(' User motion review pending',start)
s=s[:start]+'The [revised 20-second v5 animation draft](../../music/rainline-animation-v5/README.md) adds brief foreground lamp blinks with coupled desk spill/halo and sparse sliding rain beads on the window glass. V4 water, instruments, building lights and red/green beacons are retained. Earlier versions are preserved.'+s[end:]
rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md'
s=rp.read_text(encoding='utf-8').replace('Last updated: 2026-10-04.','Last updated: 2026-10-05.',1)
s=s.replace('V4 twenty-second 720p draft: readable foreground/radio, refined rear panes, water reduced 25%; review pending','V5 twenty-second 720p draft: foreground lamp blinks and sliding window rain; v4 background retained; review pending')
s=s.replace('Review v4 foreground readability, rear window edges and gentler water before 4K; music remains separate','Review v5 lamp timing and glass rain before 4K; music remains separate')
rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md'
s=rp.read_text(encoding='utf-8');start=s.index('Current Rainline animation (');end=s.index('\n\n',start)
s=s[:start]+'''Current Rainline animation (2026-10-05): user said v4 was "about there" and requested foreground lamp blinking plus rain on the windows. V5 silent twenty-second 720p/30 fps preview and three-loop sixty-second review are delivered in music/rainline-animation-v5/; see README.md and delivery-v5.json. Same immutable artwork-v1.png SHA-256 2a159c964df74dc56ecec50bee9fdf66ebf48899c5b77050616863092cc365f8, native 1672x941. Two brief lamp blinks dim its emitter, warm desk spill and nearby halo together. Twelve sparse glass rain beads/trails use local refraction/highlights and the protected window mask; 10/20-second lifetimes close on the loop. V4 water displacement .3375/speed .12, corrected habitat panes, readable radio/screen, exterior rain/mist and red/green antennas retained. Eight isolated retained layers match v4 exactly at sampled times 0 and 7 seconds. Shared renderer music/rainline-renderer/render_rainline.py; exact hash-verified v4 snapshot in music/rainline-animation-v4/renderer-v4-snapshot.py. Two isolated eight-second tests, analytic seams/protected pixels, full 600/1800-frame decodes/timestamps, encoded regional/composite seams and three identical decoded repetitions passed. Assistant inspected masks/temporal/decoded stills, not continuous playback. V4 positive feedback does not approve v5 timing/look; user review, music, 4K and assembly pending. Earlier versions preserved; no credits, commit, push or new remote media backup.'''+s[end:]
rp.write_text(s,encoding='utf-8')
rp=R/'final/catalog.json'
cat=read(rp)
for e in cat:
 if e['folder']=='08-rainline-relay':
  e.update(status='V5 preview: brief lamp blinks and sliding glass rain; v4 water and background retained; user review pending',animation_preview='../../music/rainline-animation-v5/README.md')
save(rp,cat)
print('Rainline v5 delivery and current status recorded')
