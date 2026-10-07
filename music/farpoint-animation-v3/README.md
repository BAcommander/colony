# Farpoint Station v3 — planetary depth and instrumentation

2026-10-07. User confirmed v2 cloud visibility and requested more activity on the planet, monitor, instrument lights and LEDs. This version retains that cloud transport and adds supporting effects. New additions await visual review.

Latest feedback: the user still sees no distinct planetary activity beyond clouds, asks whether the amber streaks beside the truss are reflections, and asks about stars. The streaks are in the original still; interior reflections are a plausible interpretation with no verified emitter. A [new completion prompt](../../final/10-nightward-station/animation-completion-prompt-v2.txt) proposes aurora/storm illumination, restrained star variation, connected reflections and a genuine minute delivery. That follow-up requested a prompt only. The user subsequently invoked it; the new effects and complete minute are delivered as the [v4 candidate](../farpoint-animation-v4/README.md), awaiting playback review. See `user-feedback-2026-10-07.json`.

- [Twelve-second 720p detail preview](farpoint-v3-detail-preview-12s.mp4)
- [New atmosphere only, eight seconds](new_atmosphere-v3-isolated-8s.mp4)
- [Room and habitat activity, eight seconds](habitation-v3-isolated-8s.mp4)
- [Delivery record](delivery-v3.json)
- [Configuration](scene-plan-v3.json)

These are forward-motion excerpts, **not seamless loops**. A player restart will jump. The twelve-second preview gives the independent instruments time to act while preserving the reviewed principal cloud travel. Loop closure, 4K, music and assembly remain pending.

## New detail

**Planet:** a separate lower cloud patch now moves across the lower-right hemisphere, above and to the right of the prominent foreground crater. It is extracted from the original pale atmospheric detail and uses the same optical compositing approach as v2, with independent slower travel. Its mask explicitly excludes the crater. Soft cloud shadows move over the ground beneath the upper formations. They follow cloud opacity with a displaced, blurred field and a local change relative to the original lighting state; opaque clouds attenuate the ground-shadow contribution. No geometry is warped and the planet's rim stays fixed. Under-cloud terrain reconstruction remains approximate.

**Monitor:** the original small right-hand dial has a rotating sweep, the station diagram has sequential cyan connection highlights, and the bottom status panels have changing segmented indicators. All additions stay inside the original perspective and chair occlusion. The original tracking marker and log scroll remain. This is activity within the existing screen layout, not a replacement display.

**Instruments and LEDs:** two existing blue indicators, the amber wall status light, the upper blue strip and both pink desk strips have independent dim/blink schedules. Emitting cores and local colour spill are masked together. The lower blue column indicator, unrelated practicals and right habitat window remain steady. The original habitat schedules and desk-lamp behaviour are retained; the twelve-second excerpt ends before the existing 12.7-second lamp dip.

## Evidence and scope

`sample-validation.json` records exact sampled retention of the v2 principal clouds, veil, habitat windows and desk lamp at 0, 3, 7, 8 and 11.5 seconds. This is layer-level preservation: new cloud shadows and the lower cloud deliberately alter the final planet composite. `new-mask-review.png`, `forced-dark-leds.png` and the temporal sheets document source mapping and dim states. Renderer assertions check every frame outside the active source masks.

`isolated-validation.json` and `preview-validation.json` record complete decoding, timestamps, dimensions, frame counts and hashes. No seam test is claimed for these unlooped excerpts. Assistant inspection covers source crops, masks, forced-dark lights, temporal samples and decoded stills, not continuous playback. User confirmation applies to v2 cloud visibility only; the new effects have no artistic approval yet.

## Reproduction

From `C:/Colony`:

```powershell
python music/farpoint-animation-v3/render_farpoint_v3.py --stage samples
python music/farpoint-animation-v3/render_farpoint_v3.py --stage isolated
python music/farpoint-animation-v3/render_farpoint_v3.py --stage preview
```

The small v3 adapter inherits the hash-verified v2/v1 implementations. Existing renderers and videos are preserved. `prepare_plan.py` records how the added configuration was constructed; routine renders read the saved `scene-plan-v3.json`. Video paths refuse overwrite. Source artwork is unchanged, native 1672x941; output is 1280x720/30 fps/silent. No paid tools, credits, model installation, commit or push in this revision.
