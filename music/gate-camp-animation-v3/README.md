# The Gate Camp After Sunset — V3 first visual draft

Delivered2026-11-05 for visual review. [Play the full minute](Gate-Camp-V3-first-draft-60s.mp4) · [Review both scenes](../../creative/animation-development/2026-11-05-16-17/review.html). Silent1280×720/30fps, genuinely60seconds of motion; native1672×941 processing before one downsample. Camera locked. This is a draft for artistic review.

Shared wind rises:9–25s and35–54s. Rover:enters7–18s, parks18–32s and reverses out32–44s. Radio:15s and43s. Lantern dips:26.4/26.75s and53.2s. Water and interactive light continue throughout.

## Implemented first pass

| Candidate | Current visible treatment |
|---|---|
| G01 | True sixty-second periodic water with14/15/20 wave cycles,11/8 broad highlight cycles and bounded smooth drift. |
| G02 | Shared moving portal fronts projected onto actual steps and landing; subdued foreground blue rim. |
| G03 | Local source-cloud renewal in clear runs around fixed world bodies, ring, canopy and spires. |
| G04 | Separate far-basin air and near-ground streamers at different speeds, coupled to the gust envelope. |
| G05 | Broad interior cloth folds move and shade locally; outline, posts and joints remain fixed. |
| G06 | Original taut guyline vibrates with fixed endpoints; one selected scrub clump leans with the gust. |
| G07 | A few main-lantern dips with linked canvas/case response; path lamps stay predominantly steady. |
| G08 | Cool inner-ring material response from the same portal fronts; warm chevrons do not redial. |
| G09 | Perspective-mapped laptop route marker and modest status-line updates over the original map. |
| G10 | Small radio receive indicators at two review cues. |
| G11 | Confined left-handle mug repair, then light steam from the existing rim. |
| G12 | Generated RGBA expedition rover approaches on clear ground, parks, then reverses out; no gate crossing. |

The canopy uses interior folds; its free edge is intentionally fixed. The rover is an experiment, with a brief stationary hold and a reverse exit. Taut-line vibration is deliberately much smaller than cloth motion. The source mug has only its left handle repaired in a confined patch; the original source is preserved.

## Review clips from the actual encoded minute

Detail crops enlarge the picture2× for inspection, without changing effect strength or speed. Start with the full composition. The ten-second join review is source55–60s followed by0–5s; every decoded YUV picture matches that source sequence.

- [Gate-water-and-steps-detail.mp4](Gate-water-and-steps-detail.mp4) — 14s
- [Gate-canopy-and-wind-detail.mp4](Gate-canopy-and-wind-detail.mp4) — 16s
- [Gate-rover-approach-detail.mp4](Gate-rover-approach-detail.mp4) — 20s
- [Gate-loop-join-10s.mp4](Gate-loop-join-10s.mp4) — 10s

## Rebuild and verification

Use `.local/audio-analysis/Scripts/python.exe music/gate-camp-animation-v3/render.py` from the repo root, with a new `--output` name to preserve the current delivery. `--only` accepts comma-separated effect groups for isolated tests; see frame() in [the renderer](render.py). [Settings](settings.json) · [Complete validation](delivery-validation.json) · [Detail provenance](detail-review-validation.json) · [Implementation/cue record](implementation.json).

The full decode checks all1800 sequential timestamps and pictures. Fifteen direct native-to-YUV controls are exact. Source protection is checked on every encoded native frame; an independent241-state check validates protected pixels and source taps/non-folding cloud or water maps. Regional encoded last-to-first changes are checked against ordinary nearby steps. RGB conversion and full video tags are explicit BT.709/TV. Native/mask and colour-aware decoded temporal stills were inspected; assistant continuous playback and user acceptance are not inferred.

The showcase minute deliberately contains rare vehicle/practical cues for review. The separate600s attention schedule, long-session listening, soundtrack/SFX balance and4K master remain future work. No production cadence, old scene gain or approval transfers automatically. Original art/previous masters are preserved; no commit, push, upload or paid API generation was requested in this build.
