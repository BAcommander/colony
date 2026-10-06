from pathlib import Path
import json
import re
import hashlib

H = Path(__file__).resolve().parent
R = H.parents[1]
P = R / 'final/09-offshore-night-office'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

a = read(H / 'analytic-validation.json')
i = read(H / 'isolated-validation.json')
p = read(H / 'preview-validation.json')
assert a['fingerprint'] == i['fingerprint'] == p['fingerprint']
assert len(i['clips']) == 5 and all(c['validation']['frames'] == 240 for c in i['clips'])
assert p['clips'][0]['validation']['frames'] == 600
assert p['clips'][1]['validation']['frames'] == 1800
assert p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(v['pass'] for c in p['clips'] for v in c['validation']['encoded_seam'].values())
assert all(a['v1_retained_layers_exact_at_0_and_7'].values())
v1 = read(H.parent / 'shoreless-animation-v1/delivery-v1.json')
preserved = {
    R / 'final/09-offshore-night-office/artwork-v1.png': v1['fingerprint']['source_sha256'],
    H.parent / 'shoreless-animation-v1/scene-plan-v1.json': v1['fingerprint']['config_sha256'],
    H.parent / 'shoreless-animation-v1/render_shoreless.py': v1['fingerprint']['renderer_sha256'],
    R / v1['preview']['path']: v1['preview']['sha256'],
    R / v1['three_loop_review']['path']: v1['three_loop_review']['sha256']
}
for path, expected in preserved.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
status = 'V2 silent twenty-second 720p draft: corrected window masks, sea foam, red/green antennas, readable monitor telemetry, extra local flickers and sunlight; review pending'
d = {
    'date': '2026-10-06', 'status': status,
    'user_request': (H / 'feedback-v1.txt').read_text(encoding='utf-8').strip(),
    'fingerprint': p['fingerprint'], 'preview': p['clips'][0],
    'three_loop_review': p['clips'][1], 'isolated_tests': i['clips'],
    'native_source_dimensions': [1672, 941], 'preview_dimensions': [1280, 720],
    'silent': True, 'user_motion_approved': False, 'four_k_produced': False,
    'retained_v1_layers_exact_at_sampled_times': a['v1_retained_layers_exact_at_0_and_7'],
    'v1_artwork_config_renderer_and_videos_hash_preserved': {path.relative_to(R).as_posix(): digest for path, digest in preserved.items()},
    'inspection': 'Inspected corrected dim-mask crops, full-scene temporal samples and decoded isolated/composite stills; no continuous playback claim.',
    'knowledge_bank': 'creative/ANIMATION_KNOWLEDGE_BANK.md',
    'limits': ['Source-derived crest foam and local sun shafts are optical approximations, not fluid or volumetric simulation.',
               'New effects and retained v1 turbine treatment need user visual review.',
               'The sixty-second review is three identical twenty-second repetitions.'],
    'storage': 'Local ignored draft media. No paid generation, Git commit or push. Original artwork, v1 source/config/code/media and prior scenes preserved.'
}
save(H / 'delivery-v2.json', d)
(H / 'README.md').write_text('''# The Shoreless Colony animation v2

2026-10-06. Requested revision to the first catalog 09 draft. User visual review is pending.

- [Twenty-second silent 720p preview](shoreless-colony-v2-preview-20s.mp4)
- [Sixty-second review: three identical repetitions](shoreless-colony-v2-three-loops-60s.mp4)
- [Delivery evidence](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Renderer](render_shoreless_v2.py)
- [Mask review](mask-review.png)

## Changes from v1

Complete source-space aperture masks replace the three selected cabin-pane masks. Close-up forced dim checks revealed a few-pixel error on the middle and far cabins; the final masks remove the remaining bright strips while retaining dark frames and neighboring windows. The initial v2 mask review is retained under initial-mask-review/ as diagnostic history. Whole-aperture coverage includes bright cores and warm internal reflections; color gating alone is insufficient.

Sea foam follows bright photographed moving crests with advecting broken coverage and stronger wash near the three caisson bases. The underlying v1 sea displacement and speed are unchanged. It is a restrained photographic approximation, not physical wave breaking or foam simulation.

Three actual rooftop antenna tips now pulse independently and alternate red/green. A five-second pulse interval gives a ten-second complete color cycle within the twenty-second loop. The two original red turbine-hub beacons remain independent.

The left monitor has brighter route highlights, a moving marker and staggered node pulses. The right monitor has a cyan telemetry trace and meters inside its existing lower panel. Existing main imagery, screen perspective, bezels and room geometry remain fixed.

Additional brief window, exterior-practical and foreground shelf-light flickers are staggered. The shelf light dims its nearby warm wall and desk spill together. Other lighting stays steady.

A slow cloud opening introduces soft localized sun shafts and a warm reflection across the moving sea. The effect avoids buildings, islands and the room. It is a composited lighting approximation; it does not change global exposure.

## Preservation and verification

The immutable clean artwork-v1.png remains native 1672x941, SHA-256 f042d109358089f0e89b11c99a84505fba9a825dca3428ed7109055d29253f69. The v2 adapter imports the unchanged hash-bound v1 renderer. Water, sky, turbine rotation and original beacons match v1 exactly in isolated source frames at 0 and 7 seconds. V1 files and prior scenes remain preserved.

Five eight-second isolated tests cover lights, foam, antennas, room and sunlight. Analytic layer endpoints/seams and protected pixels passed. Full 600/1800-frame decodes and sequential timestamps passed, as did regional/composite encoded seams and three identical decoded repetitions. No duplicate endpoint is added. See analytic-validation.json, isolated-validation.json and preview-validation.json.

Assistant inspected mask crops, full-scene temporal samples and decoded stills, not continuous playback. Technical verification does not establish artistic approval. Review window edges, foam strength, antenna visibility, monitor readability and sunlight timing at normal speed. No soundtrack, 4K master or long assembly produced. Future 4K would upscale the 1672x941 artwork.

Reproduce with render_shoreless_v2.py --stage samples, then isolated, then preview, using the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. prepare_v2.py refuses an existing config and the renderer refuses existing MP4 outputs. Draft media remain local and ignored; no credits, commit or push.
''', encoding='utf-8')

m = read(P / 'manifest.json')
old = m.get('animation_current')
if old and old.get('preview') != d['preview']['path']:
    m.setdefault('animation_history', []).append(old)
m['animation_current'] = {
    'status': status, 'package': '../../music/shoreless-animation-v2/README.md',
    'delivery': '../../music/shoreless-animation-v2/delivery-v2.json',
    'preview': d['preview']['path'], 'preview_sha256': d['preview']['sha256'],
    'source_sha256': d['fingerprint']['source_sha256'], 'preview_seconds': 20,
    'preview_dimensions': [1280, 720], 'fps': 30, 'user_motion_approved': False,
    'four_k_export_produced': False
}
save(P / 'manifest.json', m)

rp = P / 'README.md'
s = rp.read_text(encoding='utf-8')
old = 'A [twenty-second v1 animation draft](../../music/shoreless-animation-v1/README.md) now includes sea/cloud movement, slow turbine rotation, independent windows and room/monitor activity. User motion review is pending; no soundtrack or 4K delivery yet.'
new = 'A [twenty-second v2 animation draft](../../music/shoreless-animation-v2/README.md) adds corrected window masks, sea foam, red/green rooftop antennas, clearer monitors, local flickers and sunlight. The v1 sea/cloud movement and turbine rotation are retained. User motion review is pending; no soundtrack or 4K delivery yet.'
assert old in s or new in s
rp.write_text(s.replace(old, new, 1), encoding='utf-8')

rp = R / 'PRODUCTION_PIPELINE.md'
s = rp.read_text(encoding='utf-8')
line = next(x for x in s.splitlines() if x.startswith('| 09 |'))
new = '| 09 | [The Shoreless Colony](final/09-offshore-night-office/README.md) | V2 twenty-second 720p draft: improved panes, foam, red/green antennas, monitors, flickers and sunlight; review pending | Short/long prompts ready; no audio | Review v2 masks, foam, monitor readability and sunlight timing before 4K |'
rp.write_text(s.replace(line, new, 1), encoding='utf-8')

rp = R / 'AGENTS.md'
s = rp.read_text(encoding='utf-8')
note = 'Current Shoreless animation (2026-10-06): user requested improved window masks, sea froth, standard antennas, active monitors, more flicker and sunlight through clouds. Silent twenty-second 720p/30 fps v2 preview and sixty-second three-repeat review are delivered in music/shoreless-animation-v2/; see README.md and delivery-v2.json. Same immutable artwork-v1.png SHA-256 f042d109358089f0e89b11c99a84505fba9a825dca3428ed7109055d29253f69, native 1672x941. Complete corrected cabin apertures, source-crest foam/wash, three staggered red/green antenna tips, clearer route/telemetry monitors, extra coupled local flickers and a soft localized sunlight/reflection pass. V1 water, sky, turbine rotation and red turbine beacons retained exactly in isolated comparisons at 0 and 7 seconds; v1 assets preserved. Five isolated eight-second tests, analytical seams/protected pixels, full 600/1800-frame decodes/timestamps, encoded regional/composite seams and three identical decoded repeats passed. Assistant inspected mask/temporal/decoded stills, not continuous playback. User visual review, music, 4K and long assembly pending. Prior scenes untouched; no credits, commit or push. Knowledge bank records the pane-coordinate correction and new candidate effects.'
s, n = re.subn(r'Current Shoreless animation \([^\n]+', note, s, count=1)
assert n == 1
rp.write_text(s, encoding='utf-8')

rp = R / 'final/catalog.json'
cat = read(rp)
for e in cat:
    if e['folder'] == '09-offshore-night-office':
        e.update(status=status, animation_preview='../../music/shoreless-animation-v2/README.md')
save(rp, cat)

rp = R / 'creative/ANIMATION_KNOWLEDGE_BANK.md'
s = rp.read_text(encoding='utf-8')
start = s.index('### 09 The Shoreless Colony')
end = s.index('## Render and delivery improvements to retain', start)
entry = '''### 09 The Shoreless Colony

**Current candidate:** twenty-second v2 revision, user review pending. [Scene record](../music/shoreless-animation-v2/README.md), [configuration](../music/shoreless-animation-v2/scene-plan-v2.json), [adapter](../music/shoreless-animation-v2/render_shoreless_v2.py). V1 remains preserved.

- User requested better pane masking, foam, standard antenna activity, readable monitors, more local flickers and sunlight. These are implemented candidates, not accepted defaults for strength/timing.
- Complete pane shapes still need a forced-dim crop review: a few-pixel coordinate error left bright strips on the middle/far cabins despite plausible masks. Correct against actual pixels, include bright cores and warm dividers/reflections, and preserve neighboring frames. Do not depend on warm-color gating alone.
- Foam follows existing bright moving crests with broken advecting coverage and local caisson wash. Retain the accepted or previous sea motion while tuning foam separately. This is an optical approximation, not physical breaking waves.
- Put beacons on actual mast tips. For alternating colors, the entire color cycle must divide the loop duration, not just the pulse interval. Here five-second pulses alternate red/green over a ten-second cycle.
- Small numerical UI changes were insufficient in v1. V2 uses readable route highlights/node pulses and a larger cyan telemetry graph inside an existing screen panel. Inspect full composition at delivery size as well as crops.
- A localized cloud opening and softly masked shafts have a related warm water reflection. Protect fixed islands/platforms and avoid global exposure pumping. Extra lamp flickers include nearby spill, not just the emitter.
- Thin antenna masts intersect sky and sea: protect them in both sampled textures and output. V1 water, sky, turbine rotation and turbine beacons remain byte-identical in isolated source frames sampled at 0 and 7 seconds.
- Existing turbine blades rotate optically over locally reconstructed sky with fixed hub/mast restored. This remains a new unapproved method; review extraction edges/background before reuse.

'''
rp.write_text(s[:start] + entry + s[end:], encoding='utf-8')
print('Shoreless v2 delivery, scene status and knowledge bank recorded')
