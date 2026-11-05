"""Record a verified Snowline final delivery without publication or Git actions."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1]

def main():
    if (H/'record-update.json').exists():
        print('Delivery notes already recorded; preserve existing notes.')
        return
    d=json.loads((H/'delivery-validation.json').read_text(encoding='utf-8'))
    assert d['status']=='passed' and d['seconds']==7200 and d['frames']==216000
    out=Path(d['output']);assert out.is_file() and out.stat().st_size==d['bytes']
    v=json.loads((H/'visual/master-validation.json').read_text(encoding='utf-8'))
    a=json.loads((H/'audio-validation.json').read_text(encoding='utf-8'))
    text=f"""# Below the Snowline — final two-hour 4K video

[Open the final video](../../exports/13-below-the-snowline/Below-the-Snowline-2-Hours-4K-v1.mp4)

Exact runtime **2:00:00**, 3840×2160 at 30 fps, 216,000 frames. H.264 YUV420p BT.709/TV with stereo 48 kHz AAC. Size {d['bytes']:,} bytes ({d['bytes']/10**9:.2f} GB). SHA-256 `{d['sha256']}`.

The user approved the V6 scene with its corrected cliff masking, blue-white shuttle engines and stronger cannon charge, then requested this full export. The production renderer preserves that treatment and renders at the original 1672×941 artwork dimensions before Lanczos scaling to 4K. Continuous sky, weather and equipment phases are adjusted to whole cycles within 120 seconds. Snow and fog keep moving forward; shuttle/bridge/cannon events retain their scheduled passes and reach hidden/off states at the boundary. There is no whole-scene dissolve or reversed footage. The 120-second visual cycle repeats independently of the full audio event schedule; all audio event timings remain untouched. The native/source, cloud-map, cliff-occlusion and seam checks are recorded under `visual/`.

The existing two-hour V6 soundtrack contains all six layers. The original unfaded FLAC was hash-verified, then given +0.4 dB once and one 20-second linear closing fade. Every preparation sample was checked independently. Actual Colony v3 adds its opening once: AMBIENT COLONY/logo/PRESENTS, BELOW THE SNOWLINE and “Stay a while and listen”; graphics clear by 22 seconds. Sound is silent through 5 seconds and rises to the supplied level at 20 seconds. No extra SFX, music joins, stretching or loudness matching are added.

The first 120-second unit carries the opening; the following 59 clean units retain identical compressed picture payloads. Colony decoded the entire finished file. Independent validation checked all 216,000 timestamps, the copied units, all decoded pictures of the first clean unit, exact source pictures after the opening clears, and every AAC sample against the original master plus the intended gain/fades. Audio correlation {a['full_track_correlation']:.9f}; gain difference {a['gain_difference_db']:.6f} dB. Opening and closing diagnostic windows also passed individual checks.

## Files and reproduction

- `production-plan.json`: user authority and exact source audio.
- `visual/`: frozen source snapshot, native periodic renderer, render/audit/encoded-master checks and 4K master.
- `prepare_audio.py` and `audio-preparation-validation.json`: exact assembly FLAC recipe and sample checks.
- `assemble_with_colony.py`: verified preserved intro engine, 120-second Prepared master and final assembly; no installed application modifications.
- `verify_final.py`: `--video`, `--audio`, `--stills`, `--hash`, then `--finish`.
- `delivery-validation.json`, `video-validation.json`, `audio-validation.json`, `colony-export.json`: final evidence.
- `final-contact-sheet.jpg`: decoded opening, shuttle/cannon and repeat-boundary stills.

Original V6 preview, artwork, music and SFX are preserved. The complete long-form video is technically checked; user combined-playback review and YouTube upload/checks remain separate. Assistant inspection covers decoded temporal stills, not continuous playback or full listening. No paid generation, upload, commit or push was performed for this export. Long media and regenerable caches remain local under project policy. A Git push of records does not archive the full upload file.
"""
    (H/'README.md').write_text(text,encoding='utf-8',newline='\n')
    scene=R/'final/13-below-the-snowline'
    (scene/'final-video-v1.json').write_text(json.dumps({'delivery':d,'production_package':'music/below-the-snowline-final-two-hours-v1','upload_status':'not uploaded by this task','release_number':13,'follows_release':12,'thumbnail_selection':'Existing November4 candidates retained; no new selection inferred'},indent=2)+'\n',encoding='utf-8')
    path=scene/'README.md';b=path.read_bytes()
    title='# 13 — Below the Snowline';assert b.startswith(title.encode())
    note='Current delivery (2026-11-05): [two-hour 4K final video](../../exports/13-below-the-snowline/Below-the-Snowline-2-Hours-4K-v1.mp4), built from the approved V6 scene and full V6 audio with the actual Colony intro once. Exact 7200 seconds, 3840×2160, 30 fps and 216,000 frames. Native 1672×941 artwork is rendered directly then Lanczos upscaled. Full decode, all timestamps/repeated picture payloads and complete audio comparison passed. [Production notes and verification](../../music/below-the-snowline-final-two-hours-v1/README.md) · [Delivery record](final-video-v1.json). Full combined user review/upload checks remain pending.\n\n'
    insert=b.find(b'\n')+1;b=b[:insert]+b'\n'+note.encode()+b[insert:]
    b=b.replace(b'No4K/two-hour video has been assembled.',b'The final two-hour 4K video is now delivered above.')
    next_start=b.index(b'## Next')
    next_text="""## Next

Review the finished two-hour video, select the upload thumbnail, then run YouTube's upload checks. The final export already contains the full V6 music and all six sound layers, +0.4 dB playback gain once, the current Colony opening once and a 20-second closing fade. No further audio assembly is needed.

The earlier approved two-minute preview remains available above. It uses 3:00–5:00 of the V6 master with short review fades; the final video uses the complete soundtrack and a separately validated 120-second visual loop.

The [November 4 packaging draft](packaging-2026-11-04/README.md) pairs the V3 thumbnail candidate with the revised [title](youtube-title.txt), [description](description.txt) and [tags](youtube-tags.txt). The title says Hoth-inspired, and the description names Star Wars. The verified final runtime is 2:00:00 at 3840×2160/30fps. Catalog 13 maps to creative concept 19.
"""
    b=b[:next_start]+next_text.encode('utf-8')
    path.write_bytes(b)
    path=scene/'description.txt';b=path.read_bytes();prefix=b'2 hours of Hoth-inspired snowstorm ambience in 4K.\n\n'
    if not b.startswith(prefix):path.write_bytes(prefix+b)
    path=scene/'packaging-2026-11-04/README.md'
    packaging=path.read_text(encoding='utf-8')
    packaging=packaging.replace('The first sentence of the description names Star Wars','The description names Star Wars')
    packaging=packaging.replace('Packaging is ready for user review. Add the verified final runtime and resolution once the long video is assembled.','Packaging is ready for user review. The [completed video](../../../exports/13-below-the-snowline/Below-the-Snowline-2-Hours-4K-v1.mp4) is verified at 2:00:00, 3840×2160 and 30 fps. Thumbnail selection and YouTube upload checks remain pending.')
    path.write_text(packaging,encoding='utf-8',newline='\r\n')
    path=R/'PRODUCTION_PIPELINE.md';lines=path.read_bytes().splitlines(keepends=True)
    for i,line in enumerate(lines):
        if line.startswith(b'| 13 |'):
            end=b'\r\n' if line.endswith(b'\r\n') else b'\n'
            lines[i]=b'| 13 | [Below the Snowline](final/13-below-the-snowline/README.md) | Approved V6 treatment; native120s periodic master with cliff masking and blue engines | Full2h V6, all six layers retained; gain/fades applied once | [Two-hour4K final delivered and verified](music/below-the-snowline-final-two-hours-v1/README.md); combined review/upload checks pending |'+end
    path.write_bytes(b''.join(lines))
    path=R/'creative/music/november-2026/README.md';b=path.read_bytes();insert=b.find(b'\n')+1
    note='Snowline final delivery (2026-11-05): [two-hour4K video and verification](../../../music/below-the-snowline-final-two-hours-v1/README.md) now available. Approved V6 visual treatment uses a native120-second periodic production loop; full V6 music/SFX, +0.4dB once, one Colony opening and one 20-second closing fade. Full decode, picture/timestamp and complete AAC comparison passed. Upload and combined user review are not inferred.\n\n'
    path.write_bytes(b[:insert]+b'\n'+note.encode()+b[insert:])
    path=R/'AGENTS.md';b=path.read_bytes();idx=b.index(b'Below the Snowline V6 approval')
    note='Below the Snowline final two-hour4K delivery (2026-11-05): user requests immediate final assembly after approving V6. exports/13-below-the-snowline/Below-the-Snowline-2-Hours-4K-v1.mp4 is exact7200s/3840x2160/30fps/216000frames, H.264 BT.709/TV and48kHz stereoAAC. music/below-the-snowline-final-two-hours-v1/ freezes V6 inputs and adapts native1672x941 effects to120s periodic phases with forward snow/fog, continuous bounded sky, original shuttle/charge events and corrected masks; final frames Lanczos upscale to4K. Source V6 full FLAC unchanged; +0.4dB once and one20s closing fade, all six layers already included. Actual Colony v3 opening once: sound silent to5/fade to20, graphics clear by22. Full decode, every timestamp and59copied clean-unit payloads, decoded opening/master controls and completeAAC-to-original gain/fade comparison passed. Native/decoded temporal stills inspected, not continuous playback/full listening. Full combined user review/upload checks pending. Earlier no-final statements are historical. Source assets/preview/earlier deliveries preserved; no paid generation, upload, commit or push. Work remains on main. Exact delivery evidence is delivery-validation.json.\r\n\r\n'
    path.write_bytes(b[:idx]+note.encode()+b[idx:])
    (H/'record-update.json').write_text(json.dumps({'status':'recorded','output':str(out),'sha256':d['sha256'],'files':['AGENTS.md','PRODUCTION_PIPELINE.md','creative/music/november-2026/README.md','final/13-below-the-snowline/README.md','final/13-below-the-snowline/description.txt','final/13-below-the-snowline/final-video-v1.json','final/13-below-the-snowline/packaging-2026-11-04/README.md']},indent=2)+'\n',encoding='utf-8')
    print('Verified final delivery recorded in scene, index and production notes.')

if __name__=='__main__':main()
