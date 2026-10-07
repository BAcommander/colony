"""Update current authority only after completed v5 delivery evidence."""
import json
from render_farpoint_v5 import H,R,save,digest,FarpointV5

def read(p):return p.read_text(encoding='utf-8')
def write(p,t):p.write_text(t,encoding='utf-8')
def main():
 s=FarpointV5();fp=s.fingerprint()
 records=['analytic-validation.json','isolated-validation.json','preview-validation.json','coverage-star-validation.json']
 data={n:json.loads(read(H/n)) for n in records}
 assert all(d['fingerprint']==fp for d in data.values())
 clips=data['preview-validation.json']['clips']
 assert clips[0]['validation']['frames']==1800 and clips[1]['validation']['frames']==5400 and clips[1]['exact_three_decoded_repetitions']
 for c in clips:assert digest(R/c['path'])==c['sha256']
 feedback='music/farpoint-animation-v4/user-feedback-coverage-2026-10-07.json'
 inspection='Source/mask, normal-size temporal and decoded stills inspected. Continuous playback unavailable. User artistic verdict pending.'
 save('delivery-v5.json',{'scene':'Farpoint Station','catalog':10,'version':'v5','date':'2026-10-07','status':'Complete revised minute candidate; user playback review pending','feedback_record':feedback,'fingerprint':fp,'preview':clips[0],'repeat_review':clips[1],'validation_records':records,'changes':['Rejected aurora removed','New broken clouds over central and lower planet','Stronger independent brightness variation in six original fixed stars'],'retained':'Original weather and station layers match v4 at sampled times','inspection':inspection,'user_approved':False,'master_4k':None,'native_source_size':[1672,941],'preview_size':[1280,720],'fps':30,'silent':True,'music':None,'assembly':None,'remote_backup':None,'credits_spent':0})
 save('visual-review.json',{'status':'pending_user_playback','preview_sha256':clips[0]['sha256'],'inspection':inspection,'observations':['No blue auroral strokes remain','Additional cloud patches cross central/lower regions in temporal samples, with clear gaps and stationary terrain','Encoded original-star peak brightness changes survive 720p downsampling','Cabin, monitor and light schedules retained'],'limitations':['Procedural weather is an optical approximation','Numerical regional coverage and brightness range do not prove natural-looking motion or perceptual success'],'trial_correction':'First wide-field trial read as diffuse haze; narrowed density transition and made distinct cloud patches before video rendering'})
 path=R/'final/10-nightward-station/manifest.json';m=json.loads(read(path))
 if m['animation']['version']=='v4':
  m['animation']['status']='User requested changes: sparse coverage, implausible blue glow, imperceptible star variation'
  m['animation']['feedback_record']=feedback;m['animation_history'].append(m['animation'])
 else:assert m['animation']['version']=='v5'
 m['animation']={'version':'v5','date':'2026-10-07','status':'Revised minute candidate; user playback review pending','record':'music/farpoint-animation-v5/delivery-v5.json','preview':clips[0]['path'],'preview_sha256':clips[0]['sha256'],'repeat_review':clips[1]['path'],'repeat_review_sha256':clips[1]['sha256'],'duration_seconds':60,'fps':30,'dimensions':[1280,720],'silent':True,'seam_checks_passed':True,'user_approved':False,'master_4k':None}
 write(path,json.dumps(m,indent=2)+'\n')
 path=R/'AGENTS.md';t=read(path);a=t.index('Current Farpoint animation');b=t.index('\n\n',a)
 current="Current Farpoint animation (2026-10-07): user rejected v4's large static planetary areas, implausible blue glow and imperceptible star changes. V5 genuine sixty-second 720p/30 fps silent preview and exact three-repeat 180-second review are delivered in music/farpoint-animation-v5/; see README.md and delivery-v5.json. Aurora removed entirely. Added separate broken procedural cloud fronts over central and lower hemisphere, with gaps, fixed terrain and local shadow/compositing; these are synthesized optical weather, not recovered photographic cloud detail or physical simulation. Six original stars now have stronger independent 10–20-second brightness cycles at fixed positions/footprints. Existing v4 weather, monitor, windows, lamp, reflections and LEDs match exactly at 0/7/20/40/54 seconds. Source unchanged: SHA-256 9728b8a9baa773365b2eff1a7b0bb030836050f02309e4a04e29bae6d2104c4b, native 1672x941. Initial wide weather read as haze and was revised to distinct patches before video rendering. Analytical seams/protection/regressions, six-region minute coverage, encoded-star ranges, full 1800/5400-frame decoding/timestamps, encoded regional/composite seams and exact repeated payloads passed. Assistant inspected full-size temporal/decoded stills and masks, not continuous playback. User confirmation still covers only v2 cloud visibility; v5 cloud look, coverage and star visibility await playback review. 4K follows full-preview acceptance with identical motion and disclosed upscaling. Music/assembly remain separate. V1 invisible-motion failure, v3 clouds-only feedback and v4 rejection remain recorded; historical source/code/videos preserved. No paid tools, model installation, commit/push or remote backup in this pass."
 write(path,t[:a]+current+t[b:])
 path=R/'PRODUCTION_PIPELINE.md';t=read(path)
 line=next(x for x in t.splitlines() if x.startswith('| 10 |'))
 t=t.replace(line,'| 10 | [Farpoint Station](final/10-nightward-station/README.md) | V5 minute and 180-second review delivered: broader central/lower weather, aurora removed, stronger fixed-star variation; technical checks passed | Short/long prompts ready; no audio | Review [v5 coverage and stars](music/farpoint-animation-v5/README.md); 4K after full-preview acceptance |')
 line=next(x for x in t.splitlines() if x.startswith('| 10 Farpoint |'))
 t=t.replace(line,'| 10 Farpoint | Original cloud travel plus broken fronts across central/lower hemisphere; no aurora | Retained station/monitor activity and lamp-linked reflections; six original stars brighten/dim independently at fixed positions. V5 complete minute awaits playback review. |')
 write(path,t)
 path=R/'final/10-nightward-station/README.md';t=read(path);a=t.index('Current clean artwork:');b=t.index('Thumbnail:')
 current="""Current clean artwork: [artwork-v3-close-world-leds.png](artwork-v3-close-world-leds.png), unchanged. V1 motion was rejected as invisible; v2 cloud visibility was confirmed. V4 was rejected for sparse coverage, an implausible blue glow and imperceptible stars. Earlier versions and exact feedback are preserved.

Current animation: [v5 complete minute](../../music/farpoint-animation-v5/farpoint-station-v5-preview-60s.mp4), [180-second join review](../../music/farpoint-animation-v5/farpoint-station-v5-three-loops-180s.mp4), and [scene record/checks](../../music/farpoint-animation-v5/README.md). Silent 1280x720/30 fps. The aurora is removed. New broken cloud fronts cover central/lower regions; six original stars vary more strongly without moving. Existing weather, monitor, cabin lights and reflections retain v4 at sampled times.

Full decode, timestamps, protected pixels, analytical/encoded seams and exact three-cycle identity passed. Assistant inspected temporal/decoded stills and masks, not continuous playback. User review of the new coverage and star visibility remains pending. Export 4K only after acceptance, with identical motion and disclosed upscaling from 1672x941. No soundtrack or long assembly yet.

"""
 write(path,t[:a]+current+t[b:])
 path=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';t=read(path);a=t.index('**Current state:**',t.index('### 10 Farpoint Station'));b=t.index('\n\n',a)
 current="**Current state:** v1 motion was rejected as invisible; v2 cloud visibility was confirmed. V3 still read as clouds alone. The user then rejected v4's sparse planetary coverage, blue auroral glow and imperceptible stars. [V5](../music/farpoint-animation-v5/README.md) delivers a revised sixty-second candidate and exact 180-second review: broader central/lower cloud fronts, no aurora, stronger fixed-star light variation, retained station activity. Technical gates passed; user playback review and 4K remain pending. Assistant inspected stills, not continuous playback."
 t=t[:a]+current+t[b:]
 at=t.index('## Render and delivery improvements to retain')
 new="""- V4's technically checked aurora was rejected as an implausible blue glow. Remove a rejected phenomenon rather than continuing to polish it. V5 has no active aurora layer; [exact feedback](../music/farpoint-animation-v4/user-feedback-coverage-2026-10-07.json).
- Motion inside existing upper-cloud masks did not make the broader planet feel alive. V5 adds separate broken fronts across the central/lower hemisphere while retaining terrain positions and existing weather. The first wider field read as haze; sharper density transitions created identifiable edges and gaps. This procedural optical weather remains a candidate, not an accepted preset.
- Nineteen-percent modulation of six tiny star cores was invisible to the user. V5 uses stronger independent 10–20-second light changes on those original stars, preserving positions and footprints. Check the encoded 720p brightness range and real playback; a nonzero source-pixel delta is insufficient.
- Coverage checks must name previously bare regions, including the final third of the full minute. V5 checks six regions and preserves supporting v4 layers through sampled exact comparisons. Neither those checks nor full-size stills establish artistic success.

"""
 t=t[:at]+new+t[at:]
 t=t.replace("v4's complete minute and new effects await playback review, with technical delivery recorded.","v4 was rejected for coverage/glow/stars; v5's revised full minute awaits playback review, with technical evidence recorded.")
 write(path,t)
 path=H.parent/'farpoint-animation-v4/README.md';t=read(path);note="Latest verdict: the user rejected sparse planetary coverage, the blue glow and invisible star changes. V4 is not accepted. See [feedback](user-feedback-coverage-2026-10-07.json) and the [v5 revision](../farpoint-animation-v5/README.md).\n\n"
 if note not in t:
  pos=t.index('\n\n')+2;t=t[:pos]+note+t[pos:];write(path,t)
 print('V5 delivery and current production records updated',flush=True)
if __name__=='__main__':main()
