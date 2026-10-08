"""Finalize only after the preview, full repeat decode and seam checks pass."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import numpy as np
from PIL import Image

H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H))
from render_crimson import Crimson,fit_frame
def read(n):return json.loads((H/n).read_text(encoding='utf-8'))
def write(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    s=Crimson();preview=read('preview-validation.json');analytic=read('analytic-validation.json');isolated=read('isolated-validation.json')
    assert preview['fingerprint']==analytic['fingerprint']==isolated['fingerprint']==s.fingerprint()
    assert [v['validation']['frames'] for v in preview['clips']]==[1800,5400]
    assert preview['clips'][1]['exact_three_decoded_repetitions']
    assert len(isolated['clips'])==7
    streams=[]
    for clip in preview['clips']:
        file=R/clip['path'];assert sha(file)==clip['sha256']
        assert all(v['pass'] for v in clip['validation']['encoded_seam'].values())
        proc=subprocess.run([s.config['ffmpeg'],'-hide_banner','-i',str(file)],capture_output=True,text=True)
        lines=[line.strip() for line in proc.stderr.splitlines() if 'Stream #' in line or 'Duration:' in line]
        assert len([x for x in lines if 'Video:' in x])==1 and not any('Audio:' in x for x in lines)
        assert any('1280x720' in x and '30 fps' in x and 'bt709' in x for x in lines)
        streams.append({'path':clip['path'],'probe_lines':lines,'silent_video_only':True,'size_bytes':file.stat().st_size})
    write('media-stream-validation.json',{'clips':streams,'full_decode_evidence':'preview-validation.json'})
    samples=[];file=R/preview['clips'][0]['path']
    for frame in [256,630,1001,1178,1440,1690]:
        t=frame/30
        raw=subprocess.check_output([s.config['ffmpeg'],'-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        f=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
        dest=H/'inspection'/f'delivery-event-{frame:04d}.png';Image.fromarray(f).save(dest)
        mae=float(abs(f.astype(float)-fit_frame(s.frame(t),(1280,720))).mean())
        assert mae<3.0,(frame,mae)
        samples.append({'frame':frame,'seconds':t,'file':dest.relative_to(R).as_posix(),'decoded_vs_compositor_rgb_mae':mae})
    write('delivery-colour-validation.json',{'decoder':'FFmpeg RGB24 with tagged BT.709','samples':samples,'pass':True})
    paths=[H/n for n in ['render_crimson.py','finalize_records.py','scene-plan-v2.json','production-prompt.txt','analytic-validation.json','isolated-validation.json','preview-validation.json','cloud-transport-validation.json','light-validation.json','media-stream-validation.json','delivery-colour-validation.json','inspection/implementation-notes.txt']]
    paths+=list((H/'masks').glob('*.png'))+list((H/'dependencies').glob('*.py'))
    record={'title':'Beneath a Crimson Sky','version':'animation v2 / source v12','date':'2026-10-08',
        'status':'complete_preview_delivered_user_playback_review_pending',
        'authority':{'request':'make the animation','invoked_prompt':'creative/live/skies-of-baal/animation-production-prompt-v3-storm-and-embers.txt'},
        'source':s.config['source'],'videos':preview['clips'],'fingerprint':s.fingerprint(),
        'record_hashes':{p.relative_to(R).as_posix():sha(p) for p in paths},
        'effects':['Source cloud texture transport with unequal phase spacing and sharper/staggered renewals','Independent sustained far/middle dust','Three cloud-gated local intracloud events','Six independent room schedules with a wrapped hold','Terrace lantern variation/dip with attached wall, paving and nearby object spill','Two textured red-pane illumination events with confined arch/wall spill'],
        'optional_precipitation':s.config['optional_precipitation'],
        'timing':'Genuine sixty-second frame-by-frame scene. Sky, dust and event schedules do not repeat as a twenty- or thirty-second full composite. Review repeats the identical encoded minute three times.',
        'inspection':'Native/full-composition masks and temporal/decoded event stills inspected; continuous playback not claimed.',
        'user_visual_acceptance':None,'animation_4k':None,'music':None,'upscale_required_for_4k':True,
        'credits_spent':0,'new_models_installed':False,'originals_preserved':True,
        'backup':'Local only; no commit/push requested for this execution.',
        'release':'Unnumbered live special after actual publication of catalog 10 Farpoint Station; no date/runtime/broadcast set.'}
    write('delivery-v2.json',record)
    (H/'README.md').write_text('''# Beneath a Crimson Sky - animation v2

Complete silent sixty-second 1280 x 720/30 fps preview and exact three-repeat 180-second review, delivered after the user requested "make the animation" on 2026-10-08. **User playback review pending.** Uses rebuilt v12 artwork, with fresh masks throughout. Original art and animation v1 remain preserved.

- [Watch the complete minute](beneath-a-crimson-sky-v2-preview-60s.mp4)
- [Watch three repetitions](beneath-a-crimson-sky-v2-three-loops-180s.mp4)
- [Delivery, hashes and checks](delivery-v2.json)
- [Source-bound scene configuration](scene-plan-v2.json)
- [Exact executed prompt](production-prompt.txt)

Cloud texture moves right with unequal phase spacing, sharper dominant texture fields and depth-staggered renewal. Its sky field now spans sixty seconds. Separate far and middle dust travel across the plains throughout the minute. The main gold window and the world/clear opening remain fixed. Six room groups dim independently, including one held event across the join. The terrace lantern varies gently, with its visible core and attached wall/paving/nearby-object illumination coupled.

Three distant intracloud events begin at 8.4, 33.2 and 56.2 seconds. Light follows the actual moving cloud density and stays away from the world opening. The second has a weaker return. Two ember-red events run at 18.1-25.4 and 44.2-52.1 seconds in the recessed lancet above the lit doorway on the domed wing. Existing pane shading and divider remain visible; red spill is confined to adjacent stone. The lamp dip starts at 39.1 seconds. These timings are candidates, not user-approved presets.

The optional rain curtain was omitted because the narrow sunset gaps beneath the far-right cloud bank offer insufficient convincing fall distance before the mesas. No foreground rain or dust was added. This is a silent animation; no thunder or music was produced.

## Checks and inspection

Seven ten-second isolated/baseline/composite tests and full analytical source-protection/periodicity checks passed. Both dust depths and clouds remain active in four sampled intervals, including the final third. An encoded cloud feature moves 16 preview pixels right over eight seconds (template correlation 0.974). This supports travel, not an artistic verdict. Paired source textures can still briefly overlap during renewal; review their look in playback.

Every frame of both deliveries was decoded: 1,800 and 5,400 frames, sequential timestamps, 30 fps, no audio, exact three-repeat identity. Regional/composite encoded seams passed the existing gate. A separate comparison to quiet neighbouring frames also passed, so large lightning steps cannot hide a loop-boundary jump. Tagged BT.709 is inspected through FFmpeg RGB decoding. [Validation](preview-validation.json), [analytic checks](analytic-validation.json), [cloud diagnostic](cloud-transport-validation.json), [colour samples](delivery-colour-validation.json).

The assistant inspected source detail, masks, temporal stills and colour-correct decoded event frames at normal composition size; continuous playback was not inspected. User playback review is separate from technical checks. See [implementation notes](inspection/implementation-notes.txt), including the corrected flat-red initial still and omitted precipitation.

## Source and reproduction

Source-v12.png is a byte-identical copy of the rebuilt native artwork: 1672 x 941, SHA-256 bbcb566dac5704b0a046c2c7769f3a73bd0f092851d723988489d627eb12e0b5. No new image generation or detail enhancement was used. Future 3840 x 2160 video will be upscaled from these native coordinates.

Run `python music/beneath-a-crimson-sky-animation-v2/render_crimson.py --stage samples`, `--stage analytic`, `--stage isolated` or `--stage preview` from the repository root. Existing MP4 destinations cannot be overwritten. The original v1 renderer and local effect dependencies are frozen in dependencies; the v2 subclass replaces source mapping, cloud renewal and new light events. Run finalize_records.py only after complete validation. The scene configuration is an immutable build snapshot; delivery-v2.json records current completion/review status.

After complete-preview acceptance, export and validate a matching sixty-second 4K master with the same motion. No 4K video, soundtrack, live broadcast, commit or push was produced here. Current generic release copy remains in creative/live/skies-of-baal/release-v2. Unnumbered special after catalog 10; catalog 11 is unchanged. All new media remain local.
''',encoding='utf-8')
    print(json.dumps({'delivery':'delivery-v2.json','preview_mib':round(streams[0]['size_bytes']/2**20,2),'review_mib':round(streams[1]['size_bytes']/2**20,2),'colour_samples':samples}))
if __name__=='__main__':main()
