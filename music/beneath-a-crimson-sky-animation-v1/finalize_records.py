"""Write delivery records only after the complete media checks pass."""
from pathlib import Path
import json, hashlib
from PIL import Image

H=Path(__file__).resolve().parent
R=H.parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n): return json.loads((H/n).read_text())
def main():
    preview=load('preview-validation.json'); analytic=load('analytic-validation.json')
    isolated=load('isolated-validation.json'); still=load('still-export.json')
    assert preview['fingerprint']==analytic['fingerprint']==isolated['fingerprint']
    assert [x['validation']['frames'] for x in preview['clips']]==[1800,5400]
    assert preview['clips'][1]['exact_three_decoded_repetitions']
    for clip in preview['clips']:
        assert digest(R/clip['path'])==clip['sha256']
        assert all(c['pass'] for c in clip['validation']['encoded_seam'].values())
    art=H/'beneath-a-crimson-sky-still-4k-v1.png'
    assert Image.open(art).size==(3840,2160) and digest(art)==still['output_sha256']
    records=['scene-plan-v1.json','render_crimson.py','build_plan.py','finalize_records.py',
             'analytic-validation.json','isolated-validation.json','preview-validation.json',
             'still-export.json','colour-validation.json','cloud-travel-diagnostic.json',
             'inspection-notes.txt','media-stream-validation.json']
    files=[H/n for n in records]+list((H/'dependencies').glob('*.py'))+list((H/'masks').glob('*.png'))
    streams=load('media-stream-validation.json')
    assert streams['silent_video_only']
    record={'title':'Beneath a Crimson Sky','date':'2026-10-08',
        'status':'complete_preview_delivered_user_playback_review_pending',
        'authority':'User invoked animation-production-prompt-v2.txt: ok so shall we execute the prompt?',
        'source':load('scene-plan-v1.json')['source'], 'still':still,
        'videos':preview['clips'], 'fingerprint':preview['fingerprint'],
        'record_hashes':{p.relative_to(R).as_posix():digest(p) for p in files},
        'timing':'Unique 60-second dust and habitation schedule. Paired sky texture fields repeat every 30 seconds. The minute is rendered frame-by-frame, not copied from a shorter video.',
        'inspection':'Source, masks, forced light states, temporal stills and colour-correct decoded full-composition frames; no continuous playback inspection claimed.',
        'user_visual_acceptance':None,'animation_4k':None,'music':None,'credits_spent':0,
        'source_upscaled_for_4k':True,'new_models_installed':False,
        'public_copy':'creative/live/skies-of-baal/release-v2',
        'release':'Unnumbered live special after actual publication of catalog 10 Farpoint Station. No broadcast scheduled.',
        'backup':'New production remains local; no commit/push performed. Historical 2026-10-07 art backup does not cover these files.'}
    (H/'delivery-v1.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    (H/'README.md').write_text('''# Beneath a Crimson Sky — animation v1

Delivered 2026-10-08 after the user invoked the production prompt. **Complete silent 60-second 720p/30 fps candidate and exact three-repeat review; user playback review pending.** The clean 4K still is an upscale from the 1672 × 941 source. The 4K animation follows acceptance of this full preview.

## Watch

- [Complete minute](beneath-a-crimson-sky-v1-preview-60s.mp4)
- [Three-repeat, 180-second review](beneath-a-crimson-sky-v1-three-loops-180s.mp4)
- [Clean 3840 × 2160 still](beneath-a-crimson-sky-still-4k-v1.png)
- [Delivery and hashes](delivery-v1.json)

Cloud texture travels to the right, with slower apparent motion near the horizon. Both sampling and destination masks exclude roof, fortress, world and its clear opening. Movement tapers before those boundaries. Two forward texture fields renew invisibly; their paired atmospheric pattern repeats every 30 seconds. Separate far/middle dust gusts and six room schedules span the whole minute, including a held room event across the join. The main sanctuary window stays steady. The lantern varies gently with its local wall and paving spill. The fixed source supplies terrain, ruins, furniture and the existing dust-bank silhouette.

The cloud method is a 2D approximation. Local texture overlap can soften some edges; check this during playback, alongside dust visibility and light timing. No user approval is inferred from measurements. [Inspection notes](inspection-notes.txt) distinguish actual still inspection from continuous playback, which was unavailable.

## Evidence

Three ten-second isolated tests, analytic periodicity/source protection, all 1,800/5,400 decoded frames, timestamps, regional/composite encoded joins and exact three-cycle identity passed. See [analytic](analytic-validation.json), [isolated](isolated-validation.json), [preview](preview-validation.json), [streams](media-stream-validation.json) and [colour](colour-validation.json) records. FFmpeg supplies colour-correct decoded pixels; OpenCV frame grabs supply independent timestamps. Initial OpenCV RGB decoding misinterpreted BT.709 and is not used for final colour inspection.

The frozen v11 source has SHA-256 `30f0d2d0261875556fd7a96b6b9c1f02788d41e4254b23348a0859b2be376a5f`. [Scene plan](scene-plan-v1.json) binds all coordinates, seeds, schedules, exclusions and reuse decisions to it. [Still export](still-export.json) records deterministic Lanczos resampling and the quarter-native-pixel top/bottom crop for exact 16:9. No new detail was generated.

## Reproduce and continue

Run `python music/beneath-a-crimson-sky-animation-v1/build_plan.py` to verify the source and frozen dependencies. `render_crimson.py --stage samples`, `--stage analytic`, `--stage isolated` and `--stage preview` supply diagnostics and media. Existing video destinations are protected from overwrite; use a new version for any revision. Configuration is authoritative; `build_plan.py` validates it rather than regenerating stale coordinates.

After full-preview acceptance, export 3840 × 2160 using the same frame function, source, masks and schedules, and repeat delivery validation. No 4K animation or soundtrack exists yet. Current public title/descriptions/tags remain in [release-v2](../../creative/live/skies-of-baal/release-v2/README.txt). Unnumbered live special after catalog 10; no broadcast or upload scheduled.

Original art and unsuccessful internal tests are preserved. `history/initial-signed-clouds/` records the rejected blurred/gapped cloud extraction. `history/initial-colour-conversion/` contains the interrupted render and earlier inspection records. New files remain local; historical art backup does not cover them. No paid service, new model, commit or push was used for this execution.
''',encoding='utf-8')
    print('Delivery records and README written')

if __name__=='__main__': main()
