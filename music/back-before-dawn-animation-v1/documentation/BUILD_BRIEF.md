# Back Before Dawn — first animation build brief

2026-11-05. The user selects the proposed DeLorean workshop for catalog 18 and requests the complete animation treatment. The purpose is a believable place to stay for a long listening session, with the time machine still the unmistakable focal point.

## Source and clocks

- Clean plate: `creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/concept-v1.png`, native 1672×941. Preserve the original bytes and source hash.
- First complete review: 120 seconds, silent 1280×720 at 30 fps, with native-coordinate effects before one downsample.
- Environment: a 60-second periodic phase. Keep physical rain/particle speeds and lifetimes separate from the duration.
- Attention: an independent 120-second review schedule for the rarer cues. A sparse 600-second mode is also implemented with `--attention-mode production600`; its full playback and user acceptance remain pending. Carry absolute time across chunks in both modes.
- Keep the original H1 thumbnail outside the animation source chain. Its brighter lighting and framing are a marketing adaptation.

## Main treatment

| System | Intended action | Required attachment and protection |
|---|---|---|
| Exterior rain | Fine, directional falling rain at different depths, readable beneath the streetlamp. | Trace the actual garage opening. Hold out the car, door, garage structure, trees, props and sheltered interior. Renew particles out of view. |
| Wet street | Impact rings, small moving water structure and breakup of existing streetlamp reflections. | Map verified exterior wet patches. Keep kerb, road boundaries, solid obstacles and source samples stable. Do not use one broad reflective mask across everything dark. |
| Cabin instruments | Independent held equipment states and restrained display activity. | Include complete emitters and saturated cores. Preserve the physical device layout and colour identity; avoid a synchronized dashboard countdown. |
| Workbench oscilloscope | A readable live trace with a soft phosphor-like response. | Perspective-map to the existing screen. The casing, bezel and knobs remain fixed. Use a bounded trace rather than a decorative full-screen waveform. |
| Instrument receivers | Small changes on nearby seat, door recess and appropriate metal edges. | Use the same emitter state, with material, facing and distance falloff. Preserve texture and avoid a global colour grade. |
| Work-lamp cue | Mostly steady workshop light with a brief uneven dip. | Couple the white emitter core and local bench/bonnet receivers in linear light. Leave unrelated lighting and exposure stable. |

The implementation also includes bounded original-source foliage deformation, sparse lamp-beam dust motes, occasional eave drips and one distant 1980s sedan pass. The foliage region boundaries stay fixed; source taps and local map Jacobians are checked. A first generated clean-sky/cutout attempt revealed a blue arc at an artificial internal canopy chord and is retained as rejected history, not consumed by the current renderer. The car's generated transparent source and measured headlamp centroids are preserved; body placement, contact shadow and lamp response share its actual path and source lens positions. The headlamp response is not a detached moving glow. A missing vent is not permission to invent an emitter, and an unproven route is not a traffic animation.

## Implemented review cues

The complete effect groups are `foliage`, `rain`, `road`, `drips`, `cabin`, `scope`, `lamp`, `dust` and `traffic`; use `--only` with those names for normal-strength isolated tests. The exact renderer settings and [exported cue sheet](cue-sheet.json) own the numeric schedule.

| Cue | 120-second review treatment |
|---|---|
| Shared gusts | Start9s with5s rise/7s hold/8s fall;65s with6/11/10s;104s with3/3/8s. Rain/road response and the selected foliage use that common wind state. |
| Lamp dips |27.4s at0.58 depth,27.76s at0.30,94.2s at0.28; each uses a0.055s rise,0.10s hold and0.33s recovery. Core, pegboard/bench, qualified bonnet highlight and lamp motes respond together. |
| Cabin banks | Six starts at12/34/45/76/87/102s, with independent depths/holds from their original bank settings. Nearby console rim, door recess and seat edge use selected bank signals. |
| Diagnostic sweep |78–90s across the existing upper yellow bank, with a smooth envelope at both ends. |
| Distant sedan | One nominal19s traversal starts54s and ends73s. It crosses the60s weather boundary on the attention clock; visibility begins/ends through viewport and physical occlusion, rather than opacity fades. |
| Continuous fields | Rain, road transport/impacts, the perspective-mapped scope, sparse motes and local drip lifetimes retain their own physical timing. The second minute is not a copied first-minute video. |

The 600-second mode widens those events: gust starts45/194/361/521s, lamp143.4/143.76/436.2s, panel starts72/153/248/327/418/507s, diagnostic382–394s and sedan starts214/489s. This is implemented long-schedule capability, not a claim that a ten-minute or full-length review has been completed.

## Source inspection before motion

Inspect the gullwing hinge and support, open-door silhouette, visible tyres and floor contact, cabin display faces, rear equipment arrangement, windscreen, bonnet and brushed-metal reflections at native size. Trace the complete structures rather than guessing from a crop or a thumbnail. If a correction is necessary, make a new confined source sibling and prove unrelated original pixels unchanged.

The raised door's small fin has a dedicated rain-exclusion polygon. It was missed by the main hero silhouette even though the broad allowed-mask protection check passed. Review that fin independently, and check foliage colour against the original palette as well as checking changed-pixel coverage. Numeric protection based on a semantically wrong allowed region cannot discover that the region itself is wrong.

The parked body, door, wheels, tools, camera and garage structure are stable in this treatment. The workbench vessel is lidded, so no cup steam is inferred. Rear equipment is illustrative hardware; it is not used as an unmotivated smoke, coolant or lightning source. A repeating departure, door cycle or time-travel burst would become the dominant story. Such events are not required to make the quiet workshop alive.

## Proof and delivery sequence

1. Freeze the source/configuration and inspect the native masks and occluders.
2. Render an eight-to-twelve-second principal proof for weather/street and instrument/receiver behaviour at normal strength. Inspect full composition before enlarged crops.
3. Correct the largest geometry or visibility defect. Do not raise every layer simply because one effect is hard to see.
4. Render the complete 120-second composite with one source/configuration stack. Save representative native and colour-aware decoded stills.
5. Fully decode all 3,600 frames, check sequential timestamps and silent 720p/30fps metadata, compare direct native-to-YUV controls, verify protected pixels and safe source sampling, then inspect each regional encoded last-to-first step against ordinary nearby motion.
6. Make detail crops from the actual final video without increasing effect strength or changing time. Make an actual tail/head join review with source-picture identity checks.
7. Deliver the visual candidate and capture the user's specific feedback. Technical passes and assistant still inspection do not establish a continuous-playback or artistic verdict.

Record exact rendered filenames, effect groups, timings, masks, dependency versions and hashes after the implementation stabilizes. Do not turn this intended build sequence into a claim that those steps have already passed.

## Longer version

Preserve any accepted native appearance and physical speeds. Use the implemented `production600` attention mode rather than merely increasing the environment duration or repeating the busy review. First review the complete ten-minute schedule, its quiet-to-event/event-to-quiet transitions and long-cycle join. Retain the same60s physical fields and carry absolute time across assembly chunks. Apply the current Colony opening once during later assembly, and keep the clean scene master available.
