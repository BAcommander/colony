# Basalt Transmission — local animation

## Current revision: v2 background motion

User feedback on v1b: good start, insufficient activity in the plains/sky/haze. V2 adds nine independently drifting low dust sheets, stronger broader valley haze and protected moving cloud texture. Buildings, mesa silhouettes, moon, foreground rocks and the established habitat effects remain fixed. No user approval yet. Preview: baseline-v2-preview.mp4;4K loop: baseline-v2-loop-4k.mp4;20-minute delivery: baseline-v2-20min-4k.mp4. Compare baseline-v1-v2-comparison.mp4 (v1 left,v2 right).

Use `python scripts/render_basalt.py --version v2 --stage preview` or `--stage final`, then `python scripts/assemble_basalt.py encode --version v2`, `compare --version v2`, `assemble --version v2`, and `validate --version v2`. Parameters and masks: scene-plan-v2.json and masks-v2/. Prompt: production-prompt-v2.md. Existing v1b files are preserved. Long videos remain local; supporting files are tracked. Exact verification is recorded beside each version.

## Historical first version

Status: implemented first candidate; user artistic review pending. Source: ../../concepts/09-basalt-transmission.png (1672x941). No paid services or model inference used.

## Outputs

- baseline-v1-preview.mp4: twenty-second 1280x720 review loop.
- baseline-v1-loop-4k-master.mp4: twenty-second 3840x2160 QP0 master.
- baseline-v1b-loop-4k.mp4: twenty-second H.264/yuv420p QP0 delivery loop, identical video payload to the validated master.
- baseline-v1b-20min-4k.mp4: sixty copies of that delivery loop, exactly twenty minutes, 30 fps, silent.

All 4K outputs upscale the original artwork. Twenty minutes means repeated ambience, not unique generated action. Current videos remain local for artistic review; the long file is approximately664MB and exceeds ordinary GitHub per-file storage limits. Code and supporting evidence are versioned. Ringfall's approved media is unchanged.

## Visible effects

Two plumes emerge from inspected existing roof fittings: main cap at source(322,340), smaller shoulder outlet at(543,361). They rise and drift right with independent density detail. Two shallow haze bands move through the open right-hand valley, masked away from the habitat and two rock formations. The side-room and right-module windows change independently, including the whole aperture. Main room, corridor and exterior practical lamps remain steady. Optional sky/mast animation was omitted to preserve the source rather than introduce weak or artificial motion.

Scene-specific values live in scene-plan-v1.json. masks-v1/mask-overlay.png shows source anchors and the union of the effect regions; individual masks are saved alongside it. Existing source pixels outside those regions are preserved before encoding. Roof plume ROIs terminate above their outlets; haze polygons and blockers protect static structures.

## Reproduce

Run from the repository root. Requires existing Python with NumPy, Pillow, OpenCV and imageio-ffmpeg; no new installation is needed on this machine.

```powershell
python scripts/render_basalt.py --qa-only
python scripts/render_basalt.py --stage preview
python scripts/render_basalt.py --stage final
python scripts/assemble_basalt.py encode
python scripts/assemble_basalt.py compare
python scripts/assemble_basalt.py assemble
python scripts/assemble_basalt.py validate
```

Video commands refuse to overwrite existing exports. Use a new version/config/output stem for a deliberate revision. render_basalt.py reads the scene config and uses reusable ambient_effects.py plus the established encoder/checker in render_ringfall.py. It does not import Ringfall's scene-specific coordinates. assemble_basalt.py preserves the validated master video stream and repeats that cycle with stream copy, then decodes the long file for validation. QA-only replaces diagnostic images/reports, not videos.

## Review and evidence

Full-scene temporal samples, enlarged vent/window/haze samples, mask overlay and a decoded delivery frame were inspected. No continuous playback review is claimed. User artistic acceptance remains separate from numeric checks. The compression comparison checks matched decoded master/delivery frames in exhaust, haze and sky; numeric error is not a substitute for visual review.

Loop validation reports record static-pixel preservation, endpoint equality, frame count and seam differences. The long-file validator fully decodes every frame and hashes reduced images, checks all PTS/DTS increments at1/30second, and compares every repeating frame against the600-frame delivery cycle. Selected first/middle/last joins are also compared at full resolution. Exact outcomes are in baseline-v1b-20min-validation.json after validation completes; no completion is implied merely by the existence of a video file.

## Reusable lessons

Start from approved effect algorithms, but map anchors/masks anew. Store values in configuration so visual changes do not require a renderer fork. A simple scene with coherent primary motion can be built without extra diffusion experiments. Keep small-room changes separate from the main warm focal window. Use a high-quality master and separately checked delivery encoding; repeating a lossless master would waste long-form storage. Fully verify loop concatenation and report actual file size before backing up large deliverables.

## Encoding correction

Initial CRF16 delivery (v1) passed duration/timestamp checks but failed the encoded seam test: active-region seam difference0.753 versus maximum ordinary step0.144 at720p. It is a rejected encoding draft. V1b remuxes the validated QP0 master; identical encoded video-stream hashes confirm unchanged pixels and seam behavior. The master is only about11MB per20seconds, yielding approximately664MB for20minutes (about4.4Mbps), acceptable for this local review delivery. No threshold was weakened. Keep the smaller draft labeled rejected; do not deliver it as current.

## Completed verification

V1b fully decoded to36,000 frames, 3840x2160 at30fps,1200seconds, no audio. Every PTS/DTS is sequential; all reduced decoded frame hashes equal the corresponding600-frame loop phase. Seven selected frames around early/middle/late joins match the reference loop at full resolution. Master loop seam/static-region checks passed and delivery-loop encoded payload is identical to that master. Size664,036,456bytes; SHA256 is in delivery-manifest-v1b.json. No continuous playback review is claimed.

scene-config-rendered-v1.json freezes the exact configuration used for the recorded render hash; scene-plan-v1.json additionally records completed status and delivery. Both share the same effect parameters.

## V2 review limits and storage

V2 visual inspection covers full-scene temporal samples, mask overlay and a decoded4K frame; no continuous playback review is claimed. Cloud detail is a procedural traveling material field inside existing bands, not bulk movement of the whole sky. Wind uses independently phased soft dust sheets behind the rock masks. The current20-minute file is approximately1.38GB; the20-second4K loop is approximately23MB. Extra moving detail increases the lossless bitrate. Both stay local for artistic review; code, configurations, masks and verification evidence are pushed.

V2 completed verification:36,000 decoded frames,1200seconds,30fps,3840x2160,silent. All PTS/DTS increments sequential; every repeated frame hash matches its600-frame cycle phase. Full-resolution join samples at the beginning, middle and end match the reference loop. Final bytes1,381,581,376. Hashes and provenance are in delivery-manifest-v2.json. Master static-region and seam checks passed; delivery remux preserved the encoded video stream.
