# Ambient Colony — production pipeline and tracker

Last updated: 2026-09-29. This is the live work queue for the first ten releases. Start here each session, then read the relevant scene manifest and specialist workflow. Update current status in place; keep exact feedback and old versions in the scene package.

## Where we are

All ten have artwork, thumbnails, descriptions and search tags in [final/](final/README.md). Packages 04–10 also have suggested upload titles and scene-specific ElevenLabs music prompts. New thumbnail revisions still need user review. These assets do not mean ten finished uploads exist.

| No. | Release / package | Motion | Music | Next action |
| --- | --- | --- | --- | --- |
| 01 | [Ringfall Observatory](final/01-ringfall-observatory/README.md) | Approved 20-second 4K loop | One-hour audio produced; join accepted | Review existing assembled export before any new production; confirm publication status |
| 02 | [Basalt Transmission](final/02-basalt-transmission/README.md) | Accepted 20-second 4K loop | Two-hour audio produced; join and eight-minute listening check accepted | Review existing assembled export; confirm publication status |
| 03 | [Glacier Sanctuary](final/03-glacier-sanctuary/README.md) | 60-second 4K v11 delivered from accepted v10 look | No soundtrack recorded as produced | Prepare a scene-specific music brief/test; confirm full v11 delivery review |
| 04 | [Floodplain Keeper](final/04-floodplain-keeper/README.md) | Draft masks and plan only; no renderer adapter or loop | Short/long prompts ready; no audio | Select clean source, validate masks, prototype channel reflections and clouds |
| 05 | [Saltline Receiver](final/05-saltline-receiver/README.md) | Draft masks and plan only; no renderer adapter or loop | Short/long prompts ready; no audio | Select clean source; prototype cloud and depth-separated dust transport |
| 06 | [The Last Cable Station](final/06-last-cable-station/README.md) | No motion implementation; v3 art accepted | Short/long prompts ready; no audio | Map valley cloud/fog and protected cable/structure masks |
| 07 | [Icebound Weather Post](final/07-icebound-weather-post/README.md) | No motion implementation; v3 art accepted | Short/long prompts ready; no audio | Map distant snow transport, low ice haze and practical lights |
| 08 | [Rainline Relay](final/08-rainline-relay/README.md) | No motion implementation; current art selected for packaging | Short/long prompts ready; no audio | Map rain, separate mist depths, canopy/walkway occlusion |
| 09 | [The Shoreless Colony](final/09-offshore-night-office/README.md) | No motion implementation; current art selected for packaging | Short/long prompts ready; no audio | Prototype convincing slow sea movement around fixed caissons |
| 10 | [Farpoint Station](final/10-nightward-station/README.md) | No motion implementation; current v3 art selected for packaging | Short/long prompts ready; no audio | Prototype cloud detail on the planet under a fixed horizon |

01/02 long exports are listed in [the local inventory](final/local-export-inventory.json); their existence does not establish full-video review or publication. Nothing in this tracker claims any video has been uploaded. Glacier's accepted look, technical delivery and full-export user review are separate facts.

09/10 retain their historical folder names to preserve links and provenance. Public names are **The Shoreless Colony** and **Farpoint Station**. Their current thumbnails are `thumbnail-v2.jpg`; other packages currently use v1. Use [catalog.json](final/catalog.json) to resolve current artwork and thumbnail paths.

## Exploration beyond the first ten

Updated 2026-09-29: user found the four rough v1s insufficiently otherworldly. A nine-reference analysis and new art direction are saved in [ALIEN_COLONY_ART_DIRECTION.md](creative/concepts/ALIEN_COLONY_ART_DIRECTION.md). All four v2 images have now been generated on request; user review is pending. V1 images and original prompts remain history, not selected production plates.

- [ ] Review generated v2 [The Empty Junction](creative/concepts/round-02/17-empty-junction/concept-prompt.md): pale mineral fins and a sheltered freight pass.
- [ ] Review generated v2 [Deepwell Station](creative/concepts/round-02/18-deepwell-station/concept-prompt.md): a dry gallery overlooking chalk terraces and brine.
- [ ] Review generated v2 [Below the Snowline](creative/concepts/round-02/19-below-the-snowline/concept-prompt.md): occupied rock ribs inside a translucent ice vault.
- [ ] Review generated v2 [Crater Rim Survey](creative/concepts/round-02/20-crater-rim-survey/concept-prompt.md): a survey room facing an inhabited terraced caldera and faint ring arc.

Ten additional prompts are queued below. All are ungenerated, unassigned to public release numbers, and awaiting selection. Each link contains a complete standalone prompt and later motion ideas; no additional paid service is required for planning.

- [ ] [Terminator Commons](creative/concepts/round-03/22-terminator-commons/concept-prompt.md) — Communal dining room at the boundary between a frozen plain and a habitable twilight district.
- [ ] [Crownroot Relay](creative/concepts/round-03/23-crownroot-relay/concept-prompt.md) — A forest communications clearing where the colony works around a coherent unfamiliar canopy.
- [ ] [Tideglass Lock](creative/concepts/round-03/24-tideglass-lock/concept-prompt.md) — A dry tidal-lock control gallery connecting a marine colony to a sheltered alien inlet.
- [ ] [Stillcore Exchange](creative/concepts/round-03/25-stillcore-exchange/concept-prompt.md) — A compact geothermal heat-exchange hall beneath a native upland, with a protected daylight oculus.
- [ ] [Meridian Archive](creative/concepts/round-03/26-meridian-archive/concept-prompt.md) — An inhabited civic records room overlooking a mature terraced colony city.
- [ ] [Nightside Threshold](creative/concepts/round-03/27-nightside-threshold/concept-prompt.md) — A warm colony service passage ends at a sealed observation vestibule facing a frozen nightside plain.
- [ ] [Cloudsea Mooring](creative/concepts/round-03/28-cloudsea-mooring/concept-prompt.md) — A maintenance room in an inhabited aerostat colony above a layered cloud sea.
- [ ] [Amber Canopy Nursery](creative/concepts/round-03/29-amber-canopy-nursery/concept-prompt.md) — A propagation room where human food production meets an unfamiliar native canopy.
- [ ] [Glassplain Tram Shelter](creative/concepts/round-03/30-glassplain-tram-shelter/concept-prompt.md) — A quiet enclosed tram stop crossing an immense naturally vitrified plain.
- [ ] [Hollowmoon Reservoir](creative/concepts/round-03/31-hollowmoon-reservoir/concept-prompt.md) — A water-storage gallery inside a sealed lunar excavation beneath a large pressure-rated viewing aperture.

Use [the round-03 backlog](creative/concepts/round-03/README.md) for the detailed concept queue. Prompt-only preparation does not mark artwork, motion or music complete; the first-ten production queue below is unchanged.

## Next work session: finish 04 as the next complete production

This is the proposed starting order, not a claim that rendering has started. Motion can progress locally while the user runs music tests. Keep one scene in visual look-development at a time to avoid seven simultaneous revision chains.

- [ ] Review Floodplain's clean `artwork-v2-animation.png` against the selected v1; record which plate will drive motion. The v2 candidate is not automatically approved because its preparation exists.
- [ ] Freeze the selected plate hash/dimensions. Confirm the existing [draft scene plan](final/04-floodplain-keeper/animation-prep-v1/scene-plan.json) targets that exact image; remap if it does not.
- [ ] Inspect water boundaries, sluice/structure occlusion, cloud texture sources and celestial exclusions. Refine draft masks before rendering.
- [ ] Adapt reusable effect functions into a Floodplain scene adapter/config. Draft masks alone are not an executable pipeline.
- [ ] Produce an approximately eight-second full-composition water-only test at 720p/30 fps, actual speed.
- [ ] Produce a separate sky/cloud test, then combine only after both principal motions read clearly.
- [ ] User runs two one-minute music tests with [the existing brief](final/04-floodplain-keeper/music/elevenlabs-prompt-v1.txt), checks the displayed cost and selects a direction.
- [ ] Record the motion verdict and chosen music test before extending either.
- [ ] Finish the full-loop, 4K, soundtrack and assembly gates below.

## Repeatable production gates

### 1. Select the source and write a motion brief

**Owner: Codex, with user selection where candidates remain unresolved.**

- [ ] Read the scene package, [animation workflow](creative/ANIMATION_WORKFLOW.md) and [next-scene runbook](creative/NEXT_SCENE_RUNBOOK.md).
- [ ] Identify the current clean source and record SHA-256/dimensions. Keep generated thumbnails separate: their lighting and geometry can differ from clean art.
- [ ] Choose one or two principal motions plus a few supporting effects. Describe a feature, direction, travel region and intended visual prominence.
- [ ] Record source-coordinate masks, anchors, depth order and protected geometry using [the scene-plan template](creative/scene-plan-template.json).
- [ ] Put scene-specific values in one config. Reuse effect logic, not another scene's coordinates or masks.

Exit: a selected plate and executable plan with explicit principal motions. No promise of automatic one-shot scene adaptation.

### 2. Make the motion readable before designing its loop

**Owner: Codex for local implementation; user for artistic verdict.**

- [ ] Use an immutable source plate plus independently masked local procedural layers. No paid/cloud video generation.
- [ ] Build the largest missing motion first; retain already-good layers.
- [ ] Render short isolated principal layers at full composition, 720p and normal speed, using `scripts/motion_review.py` where the scene adapter supports it.
- [ ] Review visible transport, natural scale, occlusion, attachment and intact geometry. Do not judge from amplified differences alone.
- [ ] If the method is wrong, change the method. If motion reads but is excessive, tune speed independently from shape and visibility.
- [ ] Record actual inspection and exact feedback. Still samples are not playback review.

Exit: principal background motion is recognisable without jank; no repeated tiny opacity changes presented as a new solution.

### 3. Build and validate the complete seamless loop

**Owner: Codex; user reviews the look.**

- [ ] Default to a genuine 20-second, 30 fps cycle (600 frames); change duration only for a specific artistic need or user request. Glacier's 60-second delivery is scene-specific.
- [ ] Keep established effect speeds when extending a cycle. Use one configured duration, forward travel, hidden local resets and matched state/velocity across the seam.
- [ ] Add supporting lights/screens/exhaust only where physically plausible. Stagger light schedules and preserve steady lights too.
- [ ] Render a complete 1280x720 silent preview with the same settings intended for final.
- [ ] Review the whole scene and repeated joins. No camera drift, ping-pong, duplicate endpoint or full-frame dissolve.
- [ ] Validate decoded frame count, timestamps, dimensions/fps, protected pixels and per-layer plus encoded seam behaviour. Never relax seam checks to pass a delivery.
- [ ] Record user visual acceptance separately from numeric checks; preserve rejected versions as history.

Exit: a complete reviewed preview and valid seam, with source/config/code hashes tied to the review.

### 4. Export the short 4K master

- [ ] Render 3840x2160 at 30 fps using the same source, masks, timings and strengths. Disclose that current 1672x941 plates are upscaled.
- [ ] Use the proven encoding path and recheck the encoded seam; correct analytic timing alone is insufficient.
- [ ] Fully decode-check the master, inspect a decoded frame and retain a repeated-loop review clip.
- [ ] Save a versioned master and validation record. Do not overwrite approved media or silently mark a new delivery user-approved.

Exit: a verified short master, its actual approval scope and a reproducible package. Do not repeatedly render a long upload during look development.

### 5. Choose and develop the soundtrack

**Owner: user for ElevenLabs generations and listening selection; Codex for briefs, local analysis and editing.**

- [ ] Read [the music workflow](creative/MUSIC_WORKFLOW.md) and the package's `music/README.md`.
- [ ] Use the scene's one-minute prompt for two short variants if supported; user checks current UI settings/cost and runs generation manually.
- [ ] Compare at matched comfortable levels. Select one and record what works; revise only an unresolved characteristic if needed.
- [ ] Use the selected own test as a style reference for one approximately five-minute new piece, with the longer prompt. Reference use is not exact continuation.
- [ ] Save the actual export and fill in `music/generation-record.json`: settings, filename/hash, real duration, selected variant and exact feedback.
- [ ] Inspect actual duration, fades, levels and candidate joins. Make a short join audition and three-repeat preview.
- [ ] User listens for repeat seams, vocal-like sounds, distracting transients, excessive bass and long-form fatigue. Technical analysis does not substitute for listening.

Exit: a selected soundtrack with an accepted join treatment. No fixed drone-note requirement; preserve independent harmonic voices and audible midrange. Music prompts do not authorize assistant spending.

### 6. Assemble and review the upload

- [ ] Confirm the desired runtime per release; do not assume every video needs the same length.
- [ ] Repeat the verified short visual loop efficiently and assemble audio with track-specific accepted crossfades. Add only one opening/closing audio fade as appropriate.
- [ ] If selected, use the subscribe overlay once at a suitable point, never once per ambient loop. Its own visual approval remains separate.
- [ ] Verify full-file decoding, runtime, video/audio stream properties, timestamp continuity and the actual assembly joins. Record encoding settings and hashes.
- [ ] Review the beginning, middle, end and joins in the combined video. Record the real extent of the user's listening/playback review.
- [ ] Check current thumbnail and title. Add accurate music and duration wording to the description/tags only after the actual upload is known.
- [ ] Mark ready for upload only when the combined release passes review. Record published URL/date only after publication is verified.

Exit: a completed upload file and checked publication package. No upload/publishing action is started by this document.

### 7. Save, reproduce and back up

- [ ] Update this tracker, scene README/manifest and relevant `AGENTS.md` current decisions.
- [ ] Commit source art, exact prompts, config, masks, renderer/dependencies, metadata, thumbnails, reports and feedback.
- [ ] Track approved short masters under the existing explicit policy; use narrow Git LFS rules where needed. Verify remote LFS content, not just pointer upload.
- [ ] Keep long audio/video exports under ignored `exports/`; record locations/hashes and reproduction steps in the repo. Arrange separate backup for these files and original music exports.
- [ ] Confirm clean Git status and local/remote agreement before saying the tracked work is pushed.

Exit: tracked production work is pushed; local-only media is explicitly identified. A clone does not restore ignored exports, models or runtime caches. See [EXPORTS.md](EXPORTS.md) and [remote short-master verification](final/remote-backup.json).

## Proposed motion direction for scenes 04–10

These are starting briefs, not implemented or approved effects. Validate each against its actual plate.

| Scene | Principal motion to test | Supporting motion / protection |
| --- | --- | --- |
| 04 Floodplain | Channel reflection movement; slow sky cloud transport | Small screen trace and separate habitat lights; preserve sluice edges, reeds, buildings and moon |
| 05 Saltline | Broad cloud travel plus independent near/far dust sheets | Small light events; preserve antennas and solid red-world terrain |
| 06 Cable Station | Valley mist/cloud transport at distinct depths | Subdued instruments and habitat lights; freeze cables, chair, cliffs and moon/planet; no new moving cable car by default |
| 07 Icebound | Distant wind-driven snow and low haze crossing the ice | Vent exhaust only from identifiable vents, practical lights; no foreground snow by default; freeze habitats and celestial body |
| 08 Rainline | Rain outside the window plus independent near/far forest mist | Water/reflection detail only if needed; protect canopy, roots and walkways; room stays dry |
| 09 Shoreless | Coherent slow ocean surface/reflection motion; horizon haze | Staggered habitat lights; fixed caissons, bridges and moons. Evaluate turbine rotation only after sea motion works, with correct blade occlusion |
| 10 Farpoint | Slow cloud-material travel confined to the alien world | Screen telemetry and restrained local lights; freeze planet silhouette, geology, stars, station and camera; no vacuum smoke or wind |

## Maintain this document

At the end of each production session, update the table and tick only completed checklist items. A rejected preview remains rejected until a new reviewed revision replaces it. Use explicit states: **proposed**, **implemented**, **technically verified**, **user accepted**, **exported**, **pushed**, **published**. These states are not interchangeable.

If a new technique changes the reusable method, update the specialist animation/music workflow once and link it here. Keep this file focused on present status, next actions and completion criteria rather than another chronological experiment log.
