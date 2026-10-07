"""Bind the completed delivery to validation and update current scene status in place."""
import json
from pathlib import Path
from render_junction_v2 import H,R,Junction,save,digest

def read(p):return p.read_text(encoding='utf-8')
def write(p,t):p.write_text(t,encoding='utf-8')

def main():
 s=Junction();fp=s.fingerprint()
 names=['analytic-validation.json','isolated-validation.json','preview-validation.json','coverage-delivery-validation.json','retained-and-light-validation.json']
 checks={n:json.loads(read(H/n)) for n in names}
 assert all(c['fingerprint']==fp for c in checks.values())
 clips=checks['preview-validation.json']['clips']
 assert clips[0]['validation']['frames']==1800 and clips[1]['validation']['frames']==5400
 assert clips[1]['exact_three_decoded_repetitions']
 for c in clips:assert digest(R/c['path'])==c['sha256']
 inspection='Inspected full-composition temporal and decoded stills, masks, forced-dim and actual light states. Continuous playback unavailable. User full-preview review pending.'
 changes=['Broader broken cloud bank travels right across upper sky with source cloud transport retained below', 'Far mist reaches spire bases; independent side wisps change edge shape, height and density as they travel', 'Door lamp dips reduced to 35-44 percent, with stronger local door/step spill coupling', 'Existing room holds lengthened independently by three seconds; steady windows remain', 'Deterministic minute-wide renewals retain forward motion and distinct 0/20/40-second states']
 save('delivery-v2.json',{'scene':'The Empty Junction','catalog':11,'version':'v2','date':'2026-10-07','status':'Complete improvement preview; awaiting user playback verdict','user_feedback_v1':'ok it is decent, but it needs to be 500% better','authorization':'User requested execution of proposed improvement pass: dio it','fingerprint':fp,'preview':clips[0],'repeat_review':clips[1],'validation_records':names,'changes':changes,'inspection':inspection,'optional_twilight_shading':'Maximum-strength 4.5-percent still study inspected; omitted because its contribution was slight at full composition and diffuse twilight did not support an emphatic moving shadow. Study retained separately.','limitations':['Procedural cloud density and mist are 2D optical approximations, not fluid simulation','Local zero-opacity cloud renewal needs user playback judgement','Technical checks do not establish artistic acceptance'],'user_approved':False,'duration_seconds':60,'fps':30,'dimensions':[1280,720],'silent':True,'source_dimensions':[1672,941],'source_unchanged':True,'master_4k':None,'music':None,'assembly':None,'remote_backup':None,'credits_spent':0})
 save('visual-review.json',{'status':'pending_user_playback','preview_sha256':clips[0]['sha256'],'inspection':inspection,'observations':['Broad dark blue-grey cloud fragments have visibly different positions and shapes across normal-size samples','Far mist alternately veils and clears the lower central spires; side cuttings remain independently active','Warm horizon and foreground railway remain open','Door lamp and illuminated door/tread samples dim together; unlit risers stay dark','Larger cloud bank is deliberately more prominent than v1; its naturalness still needs playback judgement'],'excluded_study':'twilight-shading-study-maximum.png','user_approved':False})
 save('feedback.json',{'v1_feedback':'ok it is decent, but it needs to be 500% better, using everything you have learnt for making these scenes, suggest improvements','execution':'dio it','interpretation':'Authorize v2 improvement build, not a numerical quality claim or v1/v2 full acceptance','v2_feedback':None})
 p=R/'final/11-empty-junction/manifest.json';m=json.loads(read(p))
 m['motion_preparation']['status']='V2 improved full-minute preview delivered; user playback review pending'
 m['animation']={'version':'v2','date':'2026-10-07','status':'Complete improvement preview; user review pending','record':'music/empty-junction-animation-v2/delivery-v2.json','preview':clips[0]['path'],'preview_sha256':clips[0]['sha256'],'repeat_review':clips[1]['path'],'repeat_review_sha256':clips[1]['sha256'],'duration_seconds':60,'fps':30,'dimensions':[1280,720],'silent':True,'seam_checks_passed':True,'user_approved':False,'master_4k':None}
 m['resolution_note']='Native artwork 1672x941; v2 preview 1280x720; 4K awaits complete-preview acceptance.'
 write(p,json.dumps(m,indent=2)+'\n')
 p=R/'final/11-empty-junction/README.md';t=read(p).replace('A complete v1 minute animation candidate is now delivered','A complete v2 minute animation candidate is now delivered')
 a=t.index('Current animation (2026-10-07):')
 t=t[:a]+'''Current animation (2026-10-07): [v2 complete minute](../../music/empty-junction-animation-v2/empty-junction-v2-preview-60s.mp4), [three-minute join review](../../music/empty-junction-animation-v2/empty-junction-v2-three-loops-180s.mp4), and [scene record/reproduction](../../music/empty-junction-animation-v2/README.md). User called v1 decent and requested a substantial improvement. V2 adds a broader broken cloud bank, evolving mist around spire bases, softer doorway dips with stronger spill coupling, and longer independent room holds. Silent 720p/30 fps, unchanged source artwork. Full decodes/timestamps, source protection, analytical/encoded seams, retained-light regressions and exact three repeats passed. Assistant inspected temporal/decoded stills, not continuous playback. V2 user review pending; 4K follows acceptance with identical settings and disclosed upscaling. V1 preserved. No music, assembly or remote backup in this pass.
'''
 write(p,t)
 p=R/'AGENTS.md';t=read(p);a=t.index('Current Empty Junction animation');b=t.index('\n\n',a)
 current='Current Empty Junction animation (2026-10-07): user called v1 decent but requested a substantial improvement, then authorized the proposed pass. V2 genuine sixty-second silent 720p/30 fps preview and exact three-repeat 180-second review are delivered in music/empty-junction-animation-v2/; see README.md and delivery-v2.json. Same approved artwork-v2.png SHA-256 ed7b02777c1dcc35504bc0628739688b56515f09ece89d58f299f2dd6013a4be, native 1672x941. Broader broken procedural cloud bank travels right at 3.4 native px/sec above retained source clouds; evolving far/side mist at 3.0/4.2 changes thickness, height and edges around spire bases. Minute lifetimes renew independently at zero opacity. Door-lamp dips softened to 35-44 percent, warm door/step spill coupling strengthened, room holds lengthened by three seconds. Five other light layers and sky occlusion masks match v1 exactly at sampled states. Optional 4.5-percent twilight-shade still study omitted after full-composition inspection. Camera, rails, wagons, source plate and v1 implementation/media preserved. Three isolated clips, finite/protected pixels, analytical seams/velocity diagnostics, five-region minute coverage, encoded transport/lights, retained-layer comparisons, full 1800/5400-frame decodes/timestamps, regional/composite encoded seams and exact three repetitions passed. Assistant inspected normal-size temporal/decoded stills, not continuous playback. V2 full-preview review pending; decent feedback on v1 is not acceptance of v2. 4K follows acceptance with identical settings and disclosed upscaling. Music/assembly separate; no paid tools, new model, commit/push or remote backup in this pass.'
 write(p,t[:a]+current+t[b:])
 p=R/'PRODUCTION_PIPELINE.md';t=read(p)
 line=next(x for x in t.splitlines() if x.startswith('| 11 |'))
 t=t.replace(line,'| 11 | [The Empty Junction](final/11-empty-junction/README.md) | V2 minute and 180-second review delivered: broader cloud bank, evolving spire mist, softer coupled door light and longer room holds; technical checks passed | Short/long prompts ready; no audio | Review [v2 complete preview](music/empty-junction-animation-v2/README.md); 4K after acceptance |')
 line=next(x for x in t.splitlines() if x.startswith('| 11 Empty Junction |'))
 t=t.replace(line,'| 11 Empty Junction | V2 broad broken cloud bank over retained source clouds; far and side mist evolve around mineral bases | Softer doorway dips with stronger spill coupling; longer independent window holds. Rails/wagons/camera fixed. V2 minute awaits playback review. |')
 write(p,t)
 p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';t=read(p);a=t.index('### 11 The Empty Junction');b=t.index('## Render and delivery improvements to retain',a)
 t=t[:a]+'''### 11 The Empty Junction

**Current candidate:** [V2](../music/empty-junction-animation-v2/README.md) complete sixty-second silent preview and exact 180-second review. User called v1 decent but asked for a major improvement; v2 implements that request. Full technical checks passed. Assistant inspected stills, not continuous playback; user review and 4K remain pending.

- V1 had technically sustained weather but narrow cloud/mist coverage. V2 adds a broader broken bank with readable edges above the retained source clouds, and taller mist around central mineral bases. Improve the distribution and structure of motion before merely increasing opacity. New procedural density is an optical approximation; this is a candidate, not an accepted preset.
- V2 mist parcels evolve internal advection, height and edges while traveling forward at separate far/side speeds. Independently phased zero-opacity renewals sustain the genuine minute. Check the final third and actual join; unique schedules alone do not establish natural motion.
- Doorway dips looked stronger than their remaining warm spill. V2 lowers the core dip, strengthens door/tread spill coupling and keeps ambient illumination. Sample the illuminated tread, not a dark riser, when testing spill response. Inspect actual event strengths as well as forced-dark diagnostics. Longer independent room holds add station activity without changing all windows together.
- Coarse sky masks once sampled rock fragments. Refine both extraction and destination near silhouettes; a global dark-pixel rejection froze real cloud cores. Restrict it to boundary neighborhoods. Extend only atmospheric residual through source occlusion gaps to avoid moving rock-shaped cutouts. V2 retains v1's corrected sky mask exactly.
- A small optional twilight-shade study added little at full composition and was omitted; diffuse light does not justify an emphatic moving shadow. The source has no readable screen or unambiguously open vent, so those effects remain absent.
- Preserve v1 media/source/dependency hashes and compare retained layers when replacing weather. V2 checks five unchanged light layers, source protection, five-region minute coverage, analytical/encoded seams, complete decodes/timestamps and exact repeat identity. These checks support implementation; the user's playback verdict decides quality.

'''+t[b:]
 t=t.replace('Empty Junction 11 now has a technically checked v1 full-minute candidate awaiting user review.','Empty Junction 11 has a technically checked v2 improvement candidate awaiting user review.')
 write(p,t)
 p=H.parent/'empty-junction-animation-v1/README.md';t=read(p)
 old="Current delivery: a genuine sixty-second silent 1280x720/30 fps candidate and a 180-second review made from three exact copies. The complete preview awaits the user's playback verdict. 4K follows explicit preview acceptance."
 new="Historical v1 delivery: genuine sixty-second silent 1280x720/30 fps candidate and a three-repeat 180-second review. User called it decent but requested substantial improvements. The current [v2 candidate](../empty-junction-animation-v2/README.md) implements those changes and awaits playback review. V1 code, configuration and media are preserved; no full artistic approval or 4K is implied."
 t=t.replace(old,new);write(p,t)
 print('V2 delivery and current scene records saved',flush=True)
if __name__=='__main__':main()
