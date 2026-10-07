"""Publish accurate local delivery records after the complete preview passes validation."""
import json
from pathlib import Path
from render_junction import H,R,Junction,save,digest
def read(p):return p.read_text(encoding='utf-8')
def write(p,t):p.write_text(t,encoding='utf-8')

def main():
 s=Junction();fp=s.fingerprint();names=['analytic-validation.json','isolated-validation.json','preview-validation.json','coverage-delivery-validation.json']
 checks={n:json.loads(read(H/n)) for n in names}
 assert all(x['fingerprint']==fp for x in checks.values())
 clips=checks['preview-validation.json']['clips']
 assert clips[0]['validation']['frames']==1800 and clips[1]['validation']['frames']==5400
 assert clips[1]['exact_three_decoded_repetitions']
 for c in clips:assert digest(R/c['path'])==c['sha256']
 inspection='Native source/crops, weather and light masks, forced-dim states, normal-size temporal samples and decoded stills inspected. Continuous playback unavailable. Full-preview user verdict pending.'
 save('delivery-v1.json',{'scene':'The Empty Junction','catalog':11,'version':'v1','date':'2026-10-07','status':'Complete minute candidate delivered; user playback review pending','request':'execute the prompt','production_prompt':'final/11-empty-junction/animation-production-prompt-v1.txt','production_prompt_sha256':digest(R/'final/11-empty-junction/animation-production-prompt-v1.txt'),'fingerprint':fp,'preview':clips[0],'repeat_review':clips[1],'validation_records':names,'changes':['Rightward transport of source cloud material above the mineral pass','Independent far and side-cutting mist with continuous arrivals','Independent existing window holds and lamp/core/spill schedules'],'geometry':'Camera, mineral silhouettes, railway points, wagons and buildings fixed; fine turnout mechanics preserved from approved source without engineering claims','omitted':s.config['omitted'],'inspection':inspection,'user_approved':False,'source_size':[1672,941],'preview_size':[1280,720],'fps':30,'duration':60,'silent':True,'master_4k':None,'music':None,'assembly':None,'remote_backup':None,'credits_spent':0})
 save('visual-review.json',{'status':'pending_user_playback','preview_sha256':clips[0]['sha256'],'inspection':inspection,'observations':['Source cloud bank crosses rightward over the central pass','Pale far mist crosses the valley and broken side wisps pass behind protected structures','Selected window groups hold independent dim states while other rooms stay lit','Door/yard/roof lamps retain attached emitters and local spill; trackside amber stays steady'],'pre_delivery_fixes':['Coarse sky extraction carried rock-tip fragments; restricted source/destination near the skyline','Global spectral rejection froze dark cloud cores; limited rejection to a 20-pixel skyline neighborhood','Extrapolated only atmospheric residual across sampling gaps to avoid moving occluder-shaped cutouts','Separated mist from original valley haze through paler colour and clearer optical density','Expanded lamp apertures and near-core glow after forced-dim bright-remnant review'],'limitations':['Sky background and atmosphere are 2D optical approximations','Local renewals may still need adjustment after playback review','Numeric coverage, tracking and seam gates do not establish artistic acceptance']})
 p=R/'final/11-empty-junction/manifest.json';m=json.loads(read(p))
 m['motion_preparation']['status']='Implemented v1 complete preview; user playback review pending'
 m['animation']={'version':'v1','date':'2026-10-07','status':'Complete minute candidate; user review pending','record':'music/empty-junction-animation-v1/delivery-v1.json','preview':clips[0]['path'],'preview_sha256':clips[0]['sha256'],'repeat_review':clips[1]['path'],'repeat_review_sha256':clips[1]['sha256'],'duration_seconds':60,'fps':30,'dimensions':[1280,720],'silent':True,'seam_checks_passed':True,'user_approved':False,'master_4k':None}
 m['resolution_note']='Native artwork 1672x941; v1 preview 1280x720; 4K awaits complete-preview acceptance.'
 write(p,json.dumps(m,indent=2)+'\n')
 p=R/'final/11-empty-junction/README.md';t=read(p)
 t=t.replace('No animation or audio exists for this package.','A complete v1 minute animation candidate is now delivered; no audio exists for this package.')
 t=t.replace('- [Complete animation production prompt](animation-production-prompt-v1.txt), prepared 2026-10-07: proposed genuine sixty-second loop, readable sky/pass weather, source-mapped habitation lights, complete preview/repeat validation and 4K after preview acceptance. Prompt only; no animation rendered.','- [Executed animation production prompt](animation-production-prompt-v1.txt), 2026-10-07: sixty-second sky/pass weather and source-mapped habitation lights. The prompt remains historical instructions; the scene record below owns actual implementation status.')
 t+='\nCurrent animation (2026-10-07): [v1 complete minute](../../music/empty-junction-animation-v1/empty-junction-v1-preview-60s.mp4), [three-minute join review](../../music/empty-junction-animation-v1/empty-junction-v1-three-loops-180s.mp4), and [scene record/reproduction](../../music/empty-junction-animation-v1/README.md). Silent 720p/30 fps, unchanged source artwork. Full decoding, timestamps, protected pixels, individual/encoded seams and exact three-cycle identity passed. Assistant inspected temporal/decoded stills, not continuous playback. User review pending; 4K follows full-preview acceptance with identical settings and disclosed upscaling. No music, assembly or remote backup in this pass.\n'
 write(p,t)
 p=R/'AGENTS.md';t=read(p);a=t.index('Current Empty Junction planning');b=t.index('\n\n',a)
 current="Current Empty Junction animation (2026-10-07): user invoked the saved production prompt. V1 genuine sixty-second silent 720p/30 fps preview and exact three-repeat 180-second review are delivered in music/empty-junction-animation-v1/; see README.md and delivery-v1.json. Same approved artwork-v2.png SHA-256 ed7b02777c1dcc35504bc0628739688b56515f09ece89d58f299f2dd6013a4be, native 1672x941. Source cloud material travels right at 3.4/2.1 native px/sec over a stationary reconstructed sky gradient; far mist at 2.6 and side-cutting wisps at 4.0 use remapped Saltline optical density and locally staggered minute lifetimes. Independent existing hall/gallery/upper-room window holds, mild cabin glazing change, doorway/yard/path light events and roof amber acknowledgements include cores/local spill; trackside amber remains steady. Rails, wagons, camera and mineral geometry fixed. No invented monitor/hardware, aurora, stars, foreground precipitation or capped-pipe plume. Initial rock fragments in cloud extraction were corrected by refining source/output near the skyline; an overbroad colour gate froze dark cloud cores, corrected by restricting it to boundary neighborhoods. Atmospheric residual is extrapolated across sampling gaps. First mist lacked contrast; paler defined wisps replaced it. Forced-dim bright lamp remnants were corrected. Three isolated clips, finite/protected pixels, analytic states/velocity diagnostics, five-region minute coverage, encoded transport/lights, full 1800/5400 decodes/timestamps, encoded regional/composite seams and exact three repeats passed. Assistant inspected normal-size temporal/decoded stills, not continuous playback. Full-preview user review pending; artwork approval is separate from motion acceptance. 4K follows acceptance with identical settings and disclosed source upscaling. Music/assembly separate; no paid tools, model installation, commit/push or remote backup in this production pass."
 write(p,t[:a]+current+t[b:])
 p=R/'PRODUCTION_PIPELINE.md';t=read(p);line=next(x for x in t.splitlines() if x.startswith('| 11 |'))
 t=t.replace(line,'| 11 | [The Empty Junction](final/11-empty-junction/README.md) | V1 complete minute and 180-second review delivered: sky/pass weather and independent practical lights; technical checks passed | Short/long prompts ready; no audio | Review [v1 complete preview](music/empty-junction-animation-v1/README.md); 4K after acceptance |')
 t=t.replace('## Proposed motion direction for scenes 04–10','## Motion direction for scenes 04–11')
 at=t.index('\n',t.index('| 10 Farpoint |'))
 t=t[:at]+ '\n| 11 Empty Junction | Source clouds travel rightward; far pass and side-cutting mist have separate rates and continuous arrivals | Existing windows, doorway/yard/path lights and roof amber have independent schedules; trackside signal steady. V1 minute awaits playback review. |'+t[at:]
 write(p,t)
 p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';t=read(p)
 t=t.replace('lessons from videos 01–10','lessons from videos 01–11')
 at=t.index('## Render and delivery improvements to retain')
 section="""### 11 The Empty Junction

**Current candidate:** [V1](../music/empty-junction-animation-v1/README.md) complete sixty-second silent preview and exact 180-second review delivered after the user invoked the production prompt. Artwork package approval remains separate; animation playback review and 4K are pending. Technical gates passed; assistant inspected stills, not continuous playback.

- Adapted source-cloud transport and Saltline's locally renewed optical mist to the mineral pass. Far and side-cutting masks have different speeds and shapes; the foreground railway remains clear. Check five named regions through the final third rather than relying on the opening gust.
- Coarse skyline masks admitted rock fragments into moving cloud texture. Refine BOTH sampling and output near the silhouette. A global dark-pixel rejection then froze genuine dark cloud cores: restrict that test to the skyline neighborhood, preserving dark clouds in open sky. Encoded rightward transport confirms implementation, not artistic acceptance.
- Even an object-free source cutout can carry its former occluder's silhouette as a hard atmospheric edge. Extend only atmospheric residual through sampling gaps; do not copy the protected object's RGB. Reconstructed sky remains an approximation requiring playback review.
- Complete lamp apertures initially needed expansion to include bright edge strips; near-core glow needed stronger coupling. Forced-dim inspection caught these defects before full delivery. Preserve steady lamps/windows as well as independent held activity.
- The source has no readable display and its roof pipe appears capped. Omit an invented monitor or unanchored plume instead of applying every previous effect. Fixed turnout details remain visually ambiguous; preserve the approved plate without claiming mechanical accuracy.
- Three short isolated tests are diagnostics. The delivery includes the full minute and repeat review, finite/protected pixels, analytical/encoded seams, full decodes/timestamps, exact repetition and fingerprints. This first implementation is not an accepted preset.

"""
 t=t[:at]+section+t[at:]
 t=t.replace('For videos 11–14, the current artwork and motion proposals are starting material, not implemented animation evidence.','For videos 12–14, current artwork and motion proposals are starting material, not implemented animation evidence. Empty Junction 11 now has a technically checked v1 full-minute candidate awaiting user review.')
 write(p,t)
 print('Empty Junction delivery and current records saved',flush=True)
if __name__=='__main__':main()

