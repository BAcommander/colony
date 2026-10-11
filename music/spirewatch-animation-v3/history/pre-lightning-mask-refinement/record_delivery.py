"""Update scene status only after successful encoded verification; preserve other work."""
from pathlib import Path
import json,hashlib
H=Path(__file__).parent;R=H.parents[1]
def read(p):return p.read_text(encoding='utf-8')
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def load(p):return json.loads(read(p))
def save(p,v):write(p,json.dumps(v,indent=2,ensure_ascii=False)+'\n')
delivery=load(H/'delivery-v3.json');analytic=load(H/'analytic-validation.json')
assert analytic['pass'] and delivery['preview_validation']['full_decode']
assert delivery['repeat_validation']['three_exact_decoded_repetitions']
assert load(H/'chunk-join-validation.json')['pass']
assert delivery['fingerprint']==analytic['fingerprint']
delivery.update(date='2026-10-11',feedback='User could not see v2 lightning/tower movement and found warm lighting static; requested more impact and light activity.',warm_apertures=157,warm_groups=36,lightning_first_peaks=[9.6,34.6,52.6],lightning_event_seconds=1.8,retained_validation='analytic-validation.json',chunk_join_validation='chunk-join-validation.json',encoded_inspection='encoded-inspection.json',assistant_continuous_playback=False,user_motion_approved=False,backup='V3 local only; v2 checkpoint remains backed up at 4f008e9')
save(H/'delivery-v3.json',delivery)
save(H/'visual-review.json',{'date':'2026-10-11','inspection':'Assistant inspected native/encoded full-composition samples and temporal details, plus isolated lighting samples; no continuous playback. First thick branch rejected internally and revised to partly obscured thin branches.','user_review':'Pending; previous positive v2 feedback followed by visibility criticism does not approve v3','user_motion_approved':False,'assistant_continuous_playback':False,'fingerprint':delivery['fingerprint']})
current=R/'music/digital-city-concepts-v1/current-direction.json';c=load(current)
c.update(status='V3 lighting revision delivered; user playback review pending',animation_record='music/spirewatch-animation-v3/delivery-v3.json',animation_preview='music/spirewatch-animation-v3/spirewatch-v3-preview-60s.mp4',latest_feedback=delivery['feedback'],user_motion_approved=False)
save(current,c)
p=R/'AGENTS.md';s=read(p);start=s.index('Current Spirewatch animation');end=s.index('\n\n',start)
paragraph='Current Spirewatch animation (2026-10-11): after the positive v2 checkpoint and verified backup 4f008e9, user could not see lightning/tower activity and found yellow lights static. V3 responds with broader double-pulse cloud illumination/afterglow at 9.6/34.6/52.6s, thin partially obscured branches, spatially related exterior/water response, higher-contrast up/down main-spire bands and six stronger cyan regions. 157 complete warm apertures in 36 local groups have independent holds/recovery and coupled spill; walkway/desk dips are stronger. Same source SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba, 1672x941; nine environment/transit/monitor layers match v2 exactly at five times. Silent genuine sixty-second 720p/30 fps preview and exact three-repeat review delivered in music/spirewatch-animation-v3/; see README.md and delivery-v3.json. First thick lightning branch rejected internally; preserved in history. Analytic source protection/periodicity, full 1800/5400-frame decode/timestamps/regional and quiet-neighbour seams, exact minute repetitions and all contiguous-render boundary pictures passed. Assistant inspected native/decoded stills, not continuous playback. User artistic review pending; 250% is ambition, not a measurement. V1/v2 and unrelated work preserved. No new music, 4K, long assembly, paid service, commit or push for v3; prior v2 remote backup does not include v3.'
write(p,s[:start]+paragraph+s[end:])
p=R/'PRODUCTION_PIPELINE.md';s=read(p);start=s.index('## Unnumbered city concept — Spirewatch');end=s.index('## Next concept exploration',start)
section='## Unnumbered city concept — Spirewatch\n\n2026-10-11: [V3 minute and repeat review](music/spirewatch-animation-v3/README.md) delivered after v2 visibility feedback. Stronger localized lightning and exterior response, higher-contrast tower/district travelling glows, 157 warm windows in 36 independent groups and stronger coupled lamp dips. Same source and retained v2 environment/transit/monitor; full technical checks passed. User playback review is next; assistant inspected sampled frames only. V2 checkpoint remains remotely verified at 4f008e9; v3 media/code/records are local. Unnumbered; 4K, long music and assembly remain separate.\n\n'
write(p,s[:start]+section+s[end:])
p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';s=read(p)
s=s.replace('**V1 needs substantial improvement; v2 is a positive progress checkpoint.**','**V1 needs substantial improvement; v2 was a positive checkpoint but failed lighting visibility; v3 awaits review.**')
marker='- V3 visibility correction (2026-10-11): '
assert marker not in s
s+='\n'+marker+'user missed lightning and tower motion and found yellow lighting static. Add-only cyan modulation can disappear against already bright source strips; v3 combines a dimmer emitter state with a wider travelling bright head/trail on existing mapped masks. Six other cyan regions use staggered travel. Sixteen tiny windows were inadequate city-wide coverage; 157 source apertures now form 36 independently timed groups with complete cores and local spill. Stronger cloud illumination uses two uneven pulses and an afterglow, spatially related exterior/water response, and the transported cloud brightness to retain dark cloud pockets. A first thick exposed zigzag looked graphic in sampled stills; current branches are thinner and partially obscured. Do not interpret “more impact” as thick neon bolts, synchronized whole facades or uniformly increasing every effect. Nine retained environment/transit/screen layers match at five times; full decode/loop/boundary checks passed. [V3 evidence](../music/spirewatch-animation-v3/delivery-v3.json). Assistant inspected stills, not continuous playback; new lighting remains a candidate until user review.\n'
write(p,s)
manifest=[]
for p in sorted(H.rglob('*')):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.mp4' and p.name!='package-manifest.json':
  manifest.append({'path':str(p.relative_to(H)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
save(H/'package-manifest.json',{'date':'2026-10-11','scope':'V3 authored source/config/masks/reports/stills; media hashes in delivery record, original source unchanged','files':manifest,'self_excluded':True})
print('V3 scene and shared production records updated')
