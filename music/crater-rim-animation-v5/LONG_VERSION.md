# Resume Crater Rim Survey for a longer video

Saved 2026-11-05 at the user's request to preserve the details and commit/push. V5 received “ok brilliant” feedback. Preserve its appearance as the starting point; the proposed longer schedule still needs implementation and playback review. No long video, soundtrack or 4K master has been made here.

[Machine-readable plan](long-version-plan.json) · [Exact V5 settings](scene-plan.json) · [Delivery fingerprints](delivery.json) · [Local baseline/plan check](continuation-plan-validation.json) · [Music preparation](../../final/14-crater-rim-survey/music/README.md)

## Restore the backed-up reference

From `main`, fetch only the two retained review videos:

```powershell
git pull --ff-only origin main
git lfs pull --include="music/crater-rim-animation-v5/Crater-Rim-Survey-v5-60s-loop.mp4,music/crater-rim-animation-v5/Crater-Rim-Survey-v4-vs-v5-normal-size-20s.mp4" --exclude=""
```

Use an existing compatible render environment, or make one with Python 3.13 and the saved package versions:

```powershell
py -3.13 -m venv .local/crater-render
.local/crater-render/Scripts/python.exe -m pip install -r music/crater-rim-animation-v5/requirements-resume.txt
.local/crater-render/Scripts/python.exe music/crater-rim-animation-v5/validate_long_version_plan.py --check-only
```

The check verifies source/config/dependency/media hashes, renders six native V5 states and checks the draft schedule. It does not implement or approve a longer animation. Full frame/loop validation of the retained minute is already in `delivery.json`. The exact source is native 1672×941, SHA-256 `ffb509afd49853590d7b01a521288b3d5cca47f7758feaa50136feabc4241734`.

The minute and normal-size V4/V5 comparison are retained in LFS. Repeated reviews, enlarged videos, older drafts and most redundant diagnostic stills stay local; their settings, validation and selected evidence are saved. Recreate optional V5 close-ups with `make_detail_reviews.py` in fresh output destinations. Recreating the comparison also needs a fresh V4 minute from its saved renderer; the exact comparison itself is already backed up.

## Keep the look, lengthen the event clock

Create `music/crater-rim-long-animation-v1/` with frozen copies of the V5 files. Keep the backed-up V5 package unchanged. Use a proposed **600-second visual schedule**, preserving the existing 60-second weather phase. Final release runtime is unconfirmed; a ten-minute visual cycle is an implementation proposal, not the selected duration of the upload.

The important split is `weather_phase = absolute_time % 60` and `attention_phase = absolute_time % 600`. Do not change `Scene.duration` to 600 before construction: inherited cloud renewal and transport use that value. Keep it at 60 and add a separate attention-cycle clock.

Set the absolute clock before calling the frozen V5 `frame(weather_phase)`. Override `lamp_amount`, `glare_amount` and traffic activation to use the long clock. Do not let the inherited minute schedule fire those events again. A traffic override can check its global age first, then call the frozen local `vehicle_state` with the active age to preserve the corrected route and perspective. The JSON plan describes the calls and required guards.

The proposed attention schedule is explicit and reproducible:

| Detail | Starts in the ten-minute cycle | Preserve from V5 |
|---|---|---|
| Lamp clusters | 1:27.3 double dip; 6:37.7 single dip | Original dip shapes/depths and coupled bulb/wall/desk/reflection |
| Greenhouse sunbreaks | 0:48.2, 3:58.1, 7:53.6 | Broad glass reflection, radiance, pane mask and shadow attenuation |
| Rover passages | 0:52 down, 3:17.5 up, 5:51 down, 8:31.5 up | 25-second passages, pale/rust variants, road path, scale, contact and solid occlusion |

These timings are **unbuilt draft settings**. They leave the long-cycle join quiet. Keep regular tower warning beacons, weather, survey display, windows, ventilation and tiny terrace walkers on their existing V5 timing initially. Add variability only if a continuous review identifies a distracting repeat.

Keep the already solved details: full white lamp core and attached spill, bright beacon centres with bounded halos, correct mast anchors, pane-bound reflections, premultiplied tiny-vehicle compositing, actual asphalt centerline, and full-opacity rock/vegetation/ledge occlusion. Pass the absolute time into every render chunk so event clocks do not restart at chunk/minute boundaries.

## Audio and final production

The current music proposals are `elevenlabs-crater-room-v4.txt` and `elevenlabs-crater-basin-v4.txt` in the final scene's music folder. They are ungenerated candidates. The selected soundtrack, actual source exports, mix gains, joins and final runtime are still needed. No paid generation is authorized by this saved plan.

The listening position is a warm enclosed survey room. A soft indoor ventilation bed and occasional distant basin wind are sensible SFX auditions. Audition them against the supplied music and visible haze; keep separate controls and save the chosen levels. The distant rovers, walkers and tower beacons need not have audible effects through the glass. Snowline's radio, snow, creaks and gains are not a Crater Rim preset.

First build the ten-minute 720p timing audition and inspect normal-speed playback. After its timing is accepted, render native source frames directly to 3840×2160 with Lanczos, preserving V5 settings and explicit BT.709/TV colour handling. This is an upscale of native detail. Keep a clean silent master or ten contiguous minute units; place the current hash-verified Colony opening once during final assembly, outside the repeating cycle. Preserve silence to five seconds/audio fade to twenty, graphics clear by twenty-two, and a single chosen closing fade.

Validate all 18,000 frames/timestamps of a ten-minute master, every attention event, source protection, each chunk boundary, regional ordinary-frame steps versus the long-cycle join, and direct native-to-encoded picture controls. Inspect a short uninterrupted join review rather than storing a large triple copy by default. Full-length assembly follows the confirmed soundtrack/runtime, with complete video/audio decoding and the actual opening/audio envelope checked.

Put long masters and upload files under ignored `exports/14-crater-rim-survey/`, and keep caches in a per-run `.local` folder. Follow [EXPORTS.md](../../EXPORTS.md) for archival verification and cleanup. Save the accepted long recipe and short master through the same selective backup process; avoid growing Git with repeated full-length videos.
