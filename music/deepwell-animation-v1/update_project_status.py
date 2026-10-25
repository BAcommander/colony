"""Apply narrowly scoped current-status documentation after delivery checks pass."""
from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[1]
assert R==Path(r'G:\AI\colony')
delivery=json.loads((H/'preview-validation.json').read_text());direct=json.loads((H/'direct-render-validation.json').read_text())
assert direct['all_selected_yuv_bytes_exact'] and len(delivery['clips'])==2
assert delivery['clips'][0]['validation']['decoded_frames']==600
assert delivery['clips'][1]['validation']['decoded_frames']==1800
assert delivery['clips'][1]['three_identical_encoded_packet_sequences']
status='Current Deepwell v1 candidate (2026-10-25): user requested an alien planet in the sky and the start of animation. music/deepwell-animation-v1/ contains a new 1672x941 plate (SHA-256 8c04e8fbf7af063d00cd05fb587c713f2e0a380b8274410016d072cdf9a25b9b), genuine twenty-second silent 720p/30fps preview and three exact repetitions. Built-in imagegen planet edit is confined to a colour-matched local sky patch; every original pixel outside the edit mask matches the approved v2 source. Source-specific filtered brine reflections and rightward planet-free cloud transport are primary; existing screen pressure/log/levels, four independent cliff-window groups and two coupled work-lamp/spill dips support them. Camera, terraces, structures, pipeline and planet stay fixed. Warm water reflections were initially overprotected by a colour gate, and rounded UI caused a seam spike; both corrected. Broad waves were too soft in assistant still review; finer brine-specific settings selected, without claiming user acceptance. Full 600/1800-frame decodes/timestamps, regional/composite and quiet-neighbour seams, encoded/decoded repeat identity and twelve direct-native-to-decoded-YUV comparisons passed. Assistant inspected source/masks/temporal/decoded stills, not continuous playback. New art and motion await user review; no music, opening, 4K or long assembly. Original artwork and approved thumbnail remain intact. New files are local, not committed/pushed. See music/deepwell-animation-v1/README.md and validation records.'
replacements={}
p=R/'AGENTS.md';old=p.read_text(encoding='utf-8');new=old
if 'Current Deepwell v1 candidate (2026-10-25):' not in old:new=old.replace('# Ambient Colony — working instructions\n\n','# Ambient Colony — working instructions\n\n'+status+'\n\n',1)
assert new!=old or status in old;replacements[p]=(old,new)
p=R/'PRODUCTION_PIPELINE.md';old=p.read_text(encoding='utf-8');rows=old.splitlines();found=0
for i,line in enumerate(rows):
 if line.startswith('| 12 | [Deepwell Station]'):
  rows[i]='| 12 | [Deepwell Station](final/12-deepwell-station/README.md) | V1 planet-edited 20-second 720p candidate and 60-second repeat review delivered; technical checks passed | Short/long prompts ready; no audio | Review [planet and motion candidate](music/deepwell-animation-v1/README.md); approved packaging retained; 4K after visual acceptance |';found+=1
assert found==1
new='\n'.join(rows)+'\n';new=re.sub(r'Last updated: \d{4}-\d{2}-\d{2}\.', 'Last updated: 2026-10-25.',new,count=1)
if 'Current Deepwell v1 candidate (2026-10-25):' not in new:new=new.replace('## Where we are\n\n','## Where we are\n\n'+status+'\n\n',1)
replacements[p]=(old,new)
p=R/'final'/'12-deepwell-station'/'README.md';old=p.read_text(encoding='utf-8');new=old.replace('No animation or audio exists for this package.','A first planet-edited animation candidate was produced on 2026-10-25; no audio exists. The new artwork and motion await user review.')
new=new.replace('- [Motion starting brief](motion-brief.md): proposed visible effects and source-specific checks, not an implemented animation.','- [Planet and first animation candidate](../../music/deepwell-animation-v1/README.md): twenty-second 720p loop and sixty-second repeat review, with source/configuration/masks and technical checks.\n- [Historical motion starting brief](motion-brief.md): the original 2026-09-29 proposal; current implementation is linked above.')
if 'The planet-edited plate lives in' not in new:new+='\nThe planet-edited plate lives in the versioned animation package. This approved artwork-v2.png and thumbnail-v1 remain unchanged; the new candidate is not an approved replacement for the release packaging. No 4K delivery or music assembly has been made for Deepwell.\n'
replacements[p]=(old,new)
p=R/'creative'/'ANIMATION_KNOWLEDGE_BANK.md';old=p.read_text(encoding='utf-8');new=old
lesson='## Deepwell brine and planet candidate — 2026-10-25\n\nThe first Deepwell implementation adds a built-in imagegen planet only through a colour-matched local sky patch, keeping original non-sky pixels exact. Advect the original planet-free sky; protecting the visible planet alone is insufficient. A water colour gate applied throughout the channel wrongly froze warm reflected buildings as islands. Use traced shorelines and confine material gating to their boundary, allowing warm reflections inside real water to move. Broad Glacier-scale waves softened this brine basin in assistant still review; smaller sampling-filtered waves retain finer reflection detail. These are source-specific candidate settings, not a new global accepted preset. Rounded monitor needles/bars produced an analytic seam spike; continuous needle/marker fields and fractional coverage removed it while retaining the gate. Full loop, quiet-neighbour, source-protection and direct colour-aware YUV checks passed. Assistant inspected temporal/decoded stills, not continuous playback; user artistic verdict remains pending. [Exact source, studies, code and checks](../music/deepwell-animation-v1/README.md).\n\n'
if '## Deepwell brine and planet candidate — 2026-10-25' not in old:
 pos=old.index('## Opening typography and pacing');new=old[:pos]+lesson+old[pos:]
new=re.sub(r'Updated \d{4}-\d{2}-\d{2}\.', 'Updated 2026-10-25.',new,count=1);replacements[p]=(old,new)
archive=H/'project-status-before';archive.mkdir(exist_ok=True);receipt=[]
for p,(old,new) in replacements.items():
 assert p.resolve().is_relative_to(R.resolve()) and p.suffix=='.md'
 backup=archive/(str(p.relative_to(R)).replace('\\','__').replace('/','__')+'.txt')
 if not backup.exists():backup.write_text(old,encoding='utf-8')
 if new!=old:p.write_text(new,encoding='utf-8')
 receipt.append({'path':str(p),'changed':new!=old,'sha256_before':hashlib.sha256(old.encode()).hexdigest(),'sha256_after':hashlib.sha256(new.encode()).hexdigest()})
(H/'project-status-update.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Updated only Deepwell current status, release row, package pointer and candidate lessons.')
