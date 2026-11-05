> Current: [V3 full-minute visual draft](../../music/gate-camp-animation-v3/README.md) is delivered at720p/30fps, with all twelve candidates represented in the first pass. [Paired visual review](../../creative/animation-development/2026-11-05-16-17/review.html). Technical checks passed; user artistic review, the ten-minute event schedule, audio and4K remain pending. The historical planning checkpoint follows.

# 17 — The Gate Camp After Sunset: animation development plan

Prepared2026-11-05. Status: source/legacy-code audit and proposed build backlog. No new animation or repaired artwork is delivered by this plan. Current source and prior masters remain unchanged.

Proposed new build folder: `music/gate-camp-animation-v3/`. Preserve the current version while developing these candidates.

A sheltered expedition camp beside a steady open portal, with the alien landscape and fabric responding to the same wind.

[Interactive source map](../../creative/animation-development/2026-11-05-16-17/index.html#scene-17) · [Machine-readable backlog](../../creative/animation-development/2026-11-05-16-17/17-gate-camp-backlog.json) · [Fresh baseline audit](../../creative/animation-development/2026-11-05-16-17/baseline-audit.json)

## What exists

V1 and V2 are eight-second portal tests. V2 adds broad pearl-blue highlights and three small landing-light areas. Clouds, basin, canopy, foreground practicals, computer, radio and cup remain static. The portal tests are continuous auditions, not completed periodic loops.

Source: `creative/brainstorm/2026-10-27-three-worlds/e1-gate-camp/concept-v1.png`, native1672×941, SHA-256 `384fefe650ce8420b166a6fc55cc9f50bd878ec8379b514def985c8313cd9f08`. The existing preview was decoded completely in this task: 240frames/8s/30fps, silent with sequential timestamps. Source and decoded stills were inspected; no new continuous playback or user approval is inferred. Map pins are approximate planning locations, not finished masks.

## Candidate list

| ID | Candidate | Existing or new | Priority | Visible action |
|---|---|---|---|---|
| G01 | A steady watery portal with broad rolling motion | upgrade existing | Core | The open surface rolls slowly with darker pockets and pearl-blue highlights, retaining fine texture underneath. |
| G02 | Portal light that reaches the surrounding set | upgrade existing | Core | The same surface wave lights stair treads, rail edges and nearby stone; a restrained blue rim reaches appropriate camp objects. |
| G03 | Cloud layers crossing the alien sky | new candidate | Core | Cloud edges travel behind spires and in front of selected distant haze while the large world and small moon stay fixed. |
| G04 | Wind in depth: basin air and low ground streamers | new candidate | Core | Distant basin haze moves slowly while an occasional nearer dry-air tongue crosses the approach around the rocks. |
| G05 | Canopy fabric breathing between its supports | new candidate | Core | A soft gust lifts the broad cloth folds while seams, poles and fixed attachments hold their positions. |
| G06 | A loose strap and selected scrub responding to gusts | conditional experiment | Experiment | A verified loose strap twitches and one small scrub clump leans with stronger gusts. |
| G07 | Warm lantern and path-light presence | upgrade candidate | Support | Keep a strong warm place to sit, with a rare short practical-light dip and attached spill on canvas, case and ground. |
| G08 | Blue surface reflections on the ring and rail hardware | new candidate | Support | Portal ripples add moving cool highlights to the inner ring lip, rails and appropriate carved metal. |
| G09 | Live survey map on the laptop | new candidate | Support | A small route marker, restrained scan and occasional status-line refresh animate the existing map. |
| G10 | A radio receive indicator on the real device | new candidate | Support | A source-mounted receive indicator and small meter acknowledge occasional communications. |
| G11 | Mug steam after a small geometry repair | new candidate | Support | A few fine warm wisps rise from a correctly formed mug and disperse into the open air. |
| G12 | A rare expedition rover near the approach | stretch experiment | Experiment | A small wheeled survey rover makes a quiet approach along verified clear ground and settles by the expedition staging area. |

## Build order

1. Prepare a confined mug repair: the still visibly has a handle on both sides. Inspect the gate approach, rail joins and canopy rigging at native size too. Save the exact patch and prove all unrelated source pixels unchanged before freezing a new production plate.
2. Prove G01/G02 as one hero system: broad contained water motion with matching light on real stone, rail and ring surfaces. Keep the gate already open and the camera locked. Preserve warm foreground counterlight.
3. Test G05 on the broad cloth folds with fixed supports, then connect the same gust to G04 basin/ground air. Source-isolated moving free edges are a separate asset problem; do not smear the background to manufacture cloth motion.
4. Add source-safe G03 cloud layers around the fixed world and spires. Do not let transported samples contain pieces of the world, ring, canopy or rock. Clouds that truly cross the world need an independently prepared cloud-only element and new occlusion design.
5. Add laptop/radio indicators, corrected-mug steam and restrained warm practical behaviour. Feed the same portal field into local cool receiver masks, with different material/facing/falloff responses.
6. Build and validate the real sixty-second periodic scene at720p/30fps. The existing V1 drift grows linearly over time, and V2 highlight periods5.4/7.3s do not close on60s. See the provisional periodic-surface design; do not merely extend the eight-second settings.
7. Add a separate proposed600s attention clock and wind/SFX cue sheet. Optional strap/scrub motion or a rover follows acceptance of the base scene. Native-to4K/30fps production and audio assembly remain later steps.

## Source and motion guards

Keep the planet/moon, gate ring, stairs, poles, cases and chair structurally fixed. A path lamp is a warm practical, not an excuse for a whole path of flashing lights. Keep the gate in its steady open state; a repeated activation burst or human crossing is outside the initial build. Source repair and new rover/leaf/strap assets require their own proof before inclusion.

Implementation starting point: [provisional periodic water design](../../creative/animation-development/2026-11-05-16-17/17-periodic-surface-design.json). These are design records, not executable effect settings or proof that a new loop works.

[Existing native-coordinate geometry seeds](../../creative/animation-development/2026-11-05-16-17/geometry-seeds.json) preserve the current glass, roads, occluders, sign boxes and portal aperture. Refine them against the source before treating any new receiver or emitter box as a final mask.

Use eight-to-twelve-second full-composition proofs first, with isolated principal layers and unamplified source-size crops. Check both source taps and output coverage, complete emitter/aperture masks, material-linked spill, solid occlusion, and true local/long-cycle joins. No difference score or endpoint identity establishes natural-looking motion. Preserve named unchanged layers with exact controls while adding effects.

Proposed first complete review:60s at1280×720/30fps. Environmental motion and physical speeds need independent time controls; the later attention schedule is600s, not a default restart every minute. The native1672×941 plate will be upscaled for4K only after look/timing acceptance. Save source/config/code/asset/runtime hashes and exact feedback; apply the current opening once at later assembly.

## Sound and cue relationships

Start with open-air wind and an original low resonant gate bed, then selected cloth rustle tied to the same gust as the canopy/ground air. Radio receive sound is optional and sparse, informed by the Snowline chatter feedback, with no automatically reused gains. Cup, laptop and lamps do not each need a sound. Balance isolated effects and then the same music with/without ambience at matched level.

## Method and acceptance notes per candidate

### G01 — A steady watery portal with broad rolling motion

Convert V2 into a real60s periodic surface with bounded source-valid deformation and matched boundary velocity. Avoid a spinning texture or repeated activation burst.

**Proof:** Broad motion reads in the full scene without glitter noise, ring deformation or a detectable reset.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G02 — Portal light that reaches the surrounding set

Use the portal emission field for hand-mapped receiver masks with material/facing/falloff differences. The warm lantern remains the foreground counterlight.

**Proof:** Blue movement is visible on real surfaces at720p, follows the portal and does not wash the whole frame blue.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G03 — Cloud layers crossing the alien sky

Separate source-safe sky runs and planet/spire exclusions; advect coherent texture and hide local renewals.

**Proof:** Recognizable travel is visible across the open sky; neither world nor rock fragments enter moving samples.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G04 — Wind in depth: basin air and low ground streamers

Depth-specific sizes/speeds and shared gust cues; stone, steps, path lamps and the camp chair occlude the ground layer.

**Proof:** Far and near movement are both readable, with no straight fog boundary or opaque band across the valley.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G05 — Canopy fabric breathing between its supports

Start with a source-bound mesh deformation of interior cloth folds. Free-edge movement requires a clean revealed sky patch and a separate test.

**Proof:** A broad fold visibly responds to wind without dragging poles, stretching seams or revealing a duplicate cloth edge.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G06 — A loose strap and selected scrub responding to gusts

Distinguish free webbing from taut guy lines. Separate movable tips over clean background where silhouettes move; keep the motion subordinate to the canopy.

**Proof:** The same gust drives cloth and vegetation; tensioned lines remain believable and no original silhouette is doubled.

**Asset/preparation:** Requires precise movable-element isolation; omit a component that cannot be cleanly reconstructed.

### G07 — Warm lantern and path-light presence

Trace complete white cores and local lit surfaces. Most path lights stay steady; any lamp event uses a long independent clock.

**Proof:** Warm core and spill respond together without fire-like flicker on an electric lantern or synchronized path flashing.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G08 — Blue surface reflections on the ring and rail hardware

Tight material/facing masks driven by G01. Preserve the already-open gate state and steady warm chevron identity.

**Proof:** Metal reads as lit metal with stationary carvings; no floating halo, moving glyphs or mechanical redial every minute.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G09 — Live survey map on the laptop

Perspective-map inside the current screen; retain its original map texture and bezel. Use expedition telemetry rather than a prominent decorative waveform.

**Proof:** Readable activity stays inside the angled display; no laptop, keyboard or floor movement.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G10 — A radio receive indicator on the real device

Select a real screen/lens on the device; use short held acknowledgements on a long event clock, optionally linked to a later radio SFX audition.

**Proof:** Light is attached to hardware and survives720p; no random key sparkle or mandatory chatter.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### G11 — Mug steam after a small geometry repair

Repair the duplicated handle first, freeze the new plate/hash, then trace cup/rim and use irregular source-anchored steam.

**Proof:** One coherent mug handle, correct rim attachment, visible quiet steam and no changes outside the repair/effect masks.

**Asset/preparation:** The existing source has handles on both sides; prepare a confined repair before this effect or any final plate lock.

### G12 — A rare expedition rover near the approach

Requires a convincing asset, projected wheel contact/suspension, local shadows and solid rock/rail/chair occlusion. Keep it a rare narrative beat.

**Proof:** The rover sits on the uneven ground at the right scale and never cuts through steps or railings; the gate remains the main subject.

**Asset/preparation:** New reviewed rover asset and source-space ground/occlusion setup. Do after the base environment is accepted; defer human portal crossings.

## Lessons carried forward

Crater Rim V5 supplies emitter contrast, useful holds, full-size A/B review, coupled lamp spill and grounded vehicle compositing. Snowline supplies strict source/output exclusions and full-context structure tracing. Baal supplies depth and shared weather/audio cues. Rainline supplies inward glass masks, and Shoreless supplies the warning against a prominent decorative waveform. These methods require new masks and viewing tests; their old scene-specific values or approvals do not transfer.

The broader gate/city proposal, first proofs, optional assets, music, final runtime,4K master and long-form assembly are unbuilt. No paid service, image generation, commit or push is included in this planning task.
