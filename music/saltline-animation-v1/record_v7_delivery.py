"""Update the live Saltline package after its requested local delivery passes."""
import json
from render_saltline import HERE,ROOT

def main():
    delivery=json.loads((HERE/'v7-delivery-validation.json').read_text())
    assert delivery['master']['frames']==1800 and delivery['master']['full_decode']
    assert delivery['repeat']['repeated_decoded_payloads_identical']
    delivery['media_backup']='User explicitly requested commit/push on 2026-09-30. Master uses exact-path Git LFS; remote upload/restore verification pending. Review previews remain local ignored files.'
    (HERE/'v7-delivery-validation.json').write_text(json.dumps(delivery,indent=2)+'\n')
    master_path=delivery['master']['path']
    p=ROOT/'.gitattributes';text=p.read_text(encoding='utf-8')
    rule=master_path+' filter=lfs diff=lfs merge=lfs -text'
    if rule not in text: p.write_text(text.rstrip()+'\n'+rule+'\n',encoding='utf-8')
    p=ROOT/'.gitignore';text=p.read_text(encoding='utf-8')
    if '!'+master_path not in text: p.write_text(text.rstrip()+'\n\n# Saltline one-minute 4K master, explicit commit/push request 2026-09-30.\n!'+master_path+'\n',encoding='utf-8')
    package=ROOT/'final/05-saltline-receiver'
    p=ROOT/'PRODUCTION_PIPELINE.md';text=p.read_text(encoding='utf-8')
    text=text.replace('Last updated: 2026-09-29.','Last updated: 2026-09-30.',1)
    rows=text.splitlines()
    for i,row in enumerate(rows):
        if row.startswith('| 05 |'):
            rows[i]='| 05 | [Saltline Receiver](final/05-saltline-receiver/README.md) | V5 look accepted; requested 60-second 4K v7 delivered and technically verified, longer light schedule review pending | Short/long prompts ready; no audio | Review [v7 minute-long light schedule and 4K/join](music/saltline-animation-v1/LOOP_V7.md); user requested exact-master Git LFS backup, see remote-backup-v7.json for verification |'
    p.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    p=ROOT/'AGENTS.md';text=p.read_text(encoding='utf-8')
    start=text.index('Current Saltline animation (');end=text.index('\n\nCurrent Floodplain production',start)
    authority='Current Saltline animation (2026-09-30): user accepted the v5 look with “perfect, commit and push everything”. Preserve its twelve-second 720p preview, approved-v5-preview.json, source/config/code/dependency hashes and exact-path ordinary-Git backup. Foreground dust remains absent; accepted distant dust stays sustained. Genuine twenty-second v6 is preserved. User then requested longer/random hut off intervals and a one-minute 4K loop. V7 is delivered at final/05-saltline-receiver/video-4k-v7-60s.mp4, 60 seconds/1,800 frames, 3840x2160/30 fps/silent, upscaled from 1672x941. render_saltline_minute.py and scene-plan-v7.json reuse v6 atmospheric local twenty-second cycles at unchanged speeds and use independent seeded 12.4–17.7-second hut off events across the complete minute, including wrapped holds at the join. It is not three copied twenty-second videos. Matching 720p and three-cycle 180-second join review are local. All source protection, analytical layer seams, full delivery decodes/timestamps, encoded region/composite seams and repeated 720p payload checks passed; see LOOP_V7.md, v7-analytic-validation.json and v7-delivery-validation.json. Assistant inspected temporal/decoded stills, not continuous playback. V5 artistic acceptance does not imply review of v7 light scheduling or full export. New media remains ignored/local pending user review; code/config/records backup does not back up these videos. No soundtrack yet.'
    authority=authority.replace('New media remains ignored/local pending user review; code/config/records backup does not back up these videos.','User explicitly requested “commit and push” on 2026-09-30; the new 4K master uses a single-path Git LFS rule with independent remote restore/hash verification recorded in remote-backup-v7.json when completed. Backup authorization is separate from visual acceptance. Review previews remain local ignored files.')
    p.write_text(text[:start]+authority+text[end:],encoding='utf-8')
    p=package/'README.md';text=p.read_text(encoding='utf-8')
    text=text.replace('Updated 2026-09-29: v2 source selected for animation; principal-motion trials implemented. No completed loop or soundtrack yet.','Updated 2026-09-30: v5 motion look accepted; requested one-minute 4K v7 delivered and technically verified. New longer light schedule awaits visual review. No soundtrack yet.')
    text=text.replace('The source hash and mask dimensions were verified; edge refinement and a scene-specific renderer adapter are still needed. No video has been rendered. Native source is 1672x941; future 4K delivery will be resampled.','The source hash and dimensions are verified; the scene adapter refines sky/equipment, basin/dish and light-aperture boundaries. See the current delivery below. Native source is 1672x941, upscaled for 4K.')
    old='V6 visual/join review is pending; 4K remains next.'
    text=text.replace(old,'V6 remains preserved; the user subsequently requested a longer minute-long cycle and more irregular hut off periods. [V7 delivery and validation](../../music/saltline-animation-v1/LOOP_V7.md) contains the resulting [one-minute silent 4K master](video-4k-v7-60s.mp4), matching 720p preview and three-cycle join review. Full decode/timestamps, source/encoded seams and repeated 720p payload checks passed. The longer light schedule and full export await user review; new videos remain local ignored media. Source artwork is upscaled from 1672x941.')
    text=text.replace('new videos remain local ignored media.','the explicitly requested 4K master uses exact-path Git LFS, while review previews remain local ignored media.')
    p.write_text(text,encoding='utf-8')
    p=package/'manifest.json';data=json.loads(p.read_text(encoding='utf-8'))
    data['video']={**delivery['master'],'file':'video-4k-v7-60s.mp4','status':'Requested 60-second 4K delivery technically verified; v7 visual review pending','backup':'Exact-path Git LFS by explicit commit/push request; remote verification pending','validation':'../../music/saltline-animation-v1/v7-delivery-validation.json'}
    data['delivery_note']='V5 look accepted; requested one-minute silent 4K v7 rendered with longer irregular hut off intervals. New timing/export visual review pending; no soundtrack.'
    data['animation_artwork_candidate']['status']='User selected for animation; immutable v5-v7 source. Separate clean-art review not inferred.'
    data['animation_preparation'].update(mask_status='Draft masks refined by source-bound scene config and adapter',renderer_status='v5 accepted; v6 periodic transport preserved; v7 minute delivery implemented',animation_rendered=True)
    p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    p=ROOT/'final/catalog.json';data=json.loads(p.read_text(encoding='utf-8'))
    for item in data:
        if item['folder']=='05-saltline-receiver':
            item.update(status='V5 look accepted; requested 60-second 4K v7 technically verified, visual review pending',duration_seconds=60,video='video-4k-v7-60s.mp4',animation_source='artwork-v2-animation.png',animation_delivery='../../music/saltline-animation-v1/LOOP_V7.md')
    p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    p=ROOT/'final/README.md';text=p.read_text(encoding='utf-8')
    text=text.replace('an artwork/preparation package (05)','Saltline (05) with an accepted v5 look and requested one-minute 4K v7 delivery awaiting visual review')
    text=text.replace('Animations for 05-14 have not been produced.','Animations for 06-14 have not been produced.')
    text=text.replace('05 remains preparation only.','05 has the current v7 minute-long delivery in music/saltline-animation-v1.')
    text=text.replace('| [05 - Saltline Receiver](05-saltline-receiver/) | [Selected artwork](05-saltline-receiver/artwork-v1.png); no video yet |','| [05 - Saltline Receiver](05-saltline-receiver/) | [60 seconds, 4K v7](05-saltline-receiver/video-4k-v7-60s.mp4), new visual review pending |')
    text=text.replace('The video files are byte-identical copies of their original approved production exports; original paths remain available.','Approved copied media retain their original production paths. Saltline v7 is a new requested delivery with a separate pending visual-review status.')
    text=text.replace('Video paths use exact LFS rules.','Video paths use exact LFS rules. Saltline v7 is included by explicit commit/push request, with its visual review still pending; review previews remain local ignored files.')
    p.write_text(text,encoding='utf-8')
    print('Saltline package, catalog, live tracker and current authority updated')

if __name__=='__main__': main()
