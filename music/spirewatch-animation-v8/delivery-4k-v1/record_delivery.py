"""Record a verified 4K delivery without changing earlier render evidence."""
from pathlib import Path
import json, hashlib
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
v=json.loads((D/'delivery-validation.json').read_text())
assert v['full_decode'] and v['frames']==1800 and v['all_timestamps_checked']
assert all(r['pass'] for r in v['regional_and_composite_seams'].values())
master=D/v['master']
with master.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==v['sha256']
summary=('Spirewatch v8 now has a verified clean sixty-second 3840x2160/30fps silent master at '
    'music/spirewatch-animation-v8/delivery-4k-v1/Spirewatch-v8-60s-4K-loop.mp4, requested with '
    '"sure make a 60s 4k loop". Exact saved source/config/renderer/dependency/mask/runtime fingerprint retained. '
    'Native 1672x941 frames upscaled directly with Lanczos; no 720p video enlargement or effect changes. '
    'All 1800 frames/timestamps, regional/composite and quiet-neighbour loop seams passed; ten decoded '
    '4K pictures including chunk boundaries match direct native-to-YUV renders exactly. '
    'Assistant inspected decoded stills, not continuous playback. No audio or opening baked into the loop; '
    'apply the current opening once during later Colony assembly. User authorized 4K delivery; full combined '
    'playback remains separate. New master and delivery records are local, not committed/pushed. '
    'The prior v8 preview/source backup remains verified at b456b82. See delivery-4k-v1/delivery-validation.json.')
(D/'README.md').write_text('# Spirewatch v8 — 60-second 4K loop\n\n'
    '[Open the clean 4K loop](Spirewatch-v8-60s-4K-loop.mp4)\n\n'+summary+'\n\n'
    f'Master size: {v["bytes"]:,} bytes. SHA-256: `{v["sha256"]}`. H.264 QP0, YUV420p, BT.709. '
    'The lossless encoded master is intended for reuse during final assembly. Native source detail remains 1672x941.\n\n'
    'Checks: source-verification.json, render.json, delivery-validation.json. Reproduce with render_delivery.py; '
    'use --verify-only to recheck an existing master. Existing preview, older renders and intermediates are preserved.\n\n'
    'Two exploratory storm PNGs in the parent directory differ from the delivered preview; do not treat them '
    'as final source states. Their corresponding delivered preview frames (552 and 1296) match the current '
    'native renderer exactly. Six other saved native stills also match. This finding did not change any effects.\n',encoding='utf-8')
p=ROOT/'AGENTS.md';s=p.read_text(encoding='utf-8');lines=s.split('\n\n')
idx=next(i for i,l in enumerate(lines) if l.startswith('Current Spirewatch v8 (2026-10-21):'))
lines[idx]='Current Spirewatch v8 4K delivery (2026-10-21): '+summary+' Earlier v8 finishing details and backup scope remain in music/spirewatch-animation-v8/README.md.'
p.write_text('\n\n'.join(lines),encoding='utf-8')
p=ROOT/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8');start=s.index('## Unnumbered city concept — Spirewatch');end=s.index('\n## ',start+4)
s=s[:start]+'## Unnumbered city concept — Spirewatch\n\n'+summary+'\n'+s[end:];p.write_text(s,encoding='utf-8')
p=ROOT/'music/digital-city-concepts-v1/current-direction.json';d=json.loads(p.read_text())
d['status']='V8 clean 60-second 4K loop delivered and technically verified; final music assembly separate'
d['animation_4k_master']=master.relative_to(ROOT).as_posix()
d['animation_4k_validation']=(D/'delivery-validation.json').relative_to(ROOT).as_posix()
d['animation_4k_backed_up']=False
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('Recorded 4K delivery; prior shared-document changes preserved')
