# Ambient Colony animation knowledge bank

Updated 2026-10-06. Use the lessons from videos 01–09 to make future first drafts stronger and avoid repeating rejected experiments. Start with readable environmental motion, add a few believable signs of habitation, and preserve the photographed structure of the scene. Reuse methods and timing helpers; remap every mask, anchor and protected object to the new artwork.

Read this with [ANIMATION_WORKFLOW.md](ANIMATION_WORKFLOW.md) and [NEXT_SCENE_RUNBOOK.md](NEXT_SCENE_RUNBOOK.md). The [production tracker](../PRODUCTION_PIPELINE.md) owns current release status; linked scene records hold exact settings and feedback. Older version READMEs describe their delivery at that time and may contain superseded next steps.

## Start every new scene with these decisions

1. Freeze the clean artwork and its hash. Inspect construction, light apertures, screens, window frames, water boundaries and foreground occluders before mapping effects. A thumbnail can change the composition; never substitute it without freezing and remapping the new plate.
2. Choose one or two principal motions with a visible action and direction: a cloud edge crosses a valley, a reflection moves within a channel, snow passes beyond a cabin window. Test whether each survives a full-scene 720p view.
3. Give near, middle and far regions separate treatment where the composition supports them. A busy foreground does not compensate for a static distance. Leave some areas quiet.
4. Choose a few existing signs of habitation from the start: independent window holds, a lamp with attached spill, screen or radio activity, or small antenna beacons. Do not add equipment merely to create something to animate.
5. Record which previous scene supplies the method, its approval scope, what must be remapped and the failure to avoid. Use the `knowledge_reuse` fields in [scene-plan-template.json](scene-plan-template.json); these are planning notes, not automatic renderer controls.
6. Render short isolated tests of the principal or changed effects before a complete loop. Inspect full composition for visibility, then crops for masks and attachment. Change shape/coverage first, speed second and opacity last when the problem is unreadable transport.
7. Preserve accepted layers with sampled comparisons when adding a new effect. Use one source configuration and consistent timing for preview and final; version outputs and freeze code before extending a shared renderer.

## Choose a method by effect

| Need | Start from | Carry forward | Check in the new scene |
| --- | --- | --- | --- |
| Broad clouds and distant weather | Basalt, Cable Station, Icebound | Coherent source texture travel and separate depth layers | Coverage, recognizable travel, ghosting, horizon and mast protection |
| Sustained dust or mist | Saltline and Cable Station | Staggered incoming formations with locally hidden resets | The region stays active throughout the full loop without becoming an opaque stripe |
| Calm moving water | Glacier and Floodplain | Filtered 24-wave reflection surface, perspective and boundary damping | Shorelines, reeds, roots and posts stay stable; source sampling excludes solid objects |
| Window off periods | Ringfall, Saltline and Icebound | Whole-aperture masks, independent held events, small attached spill | White cores darken too; mullions and metal stay fixed; some windows remain steady |
| Brief lamp blinks | Floodplain and Cable Station; Rainline v5 candidate | Short events separated by stable illumination | Bulb, desk/wall light and nearby halo change together; no whole-image pulse |
| Computer and radio activity | Cable Station v3; Rainline v4 candidate | Perspective-mapped scrolling logs, route markers or segmented meters | Motion remains readable at 720p; preserve bezel, panel layout and equipment |
| Falling snow | Icebound v2 | Several depth/size/speed groups, subpixel footprints and invisible renewals | Scene scale, density, direction and whether foreground snow is appropriate |
| Antenna activity | Icebound v2; Rainline v3–v5 candidate | Small anchored cores/halos with independent schedules | Tip placement, colour transitions and restrained brightness; no invented sweeping beam |
| Rain on the view and glass | Rainline v5 candidate | Separate exterior streaks from sparse sliding refractive glass beads | Clip to real panes, protect frames/equipment and retain the view outside |
| Passing daylight | Saltline and Cable Station | Local shading tied to sunlit surfaces | Plausible affected surfaces and soft transitions; stable global exposure |

Settings below are scene-specific examples, not universal presets. Candidate methods must still earn visual acceptance in their new scene.

## Lessons by video

### 01 Ringfall Observatory

**Accepted baseline:** v9b, user verdict “finally good.” [Brief](ringfall/animation/ambient-v9-final-brief.md), [approval](ringfall/animation/approved-v9b.json), [renderer](../scripts/render_ringfall_v9.py).

- Tiny steam, screen and beacon changes left the scene too static. Visible vent exhaust, independent windows and coherent material travelling within fixed ring bands established activity at full composition.
- Brightness modulation on the rings was too hard to see. Advect recognizable texture within protected bands; retain gaps, silhouettes and planet occlusion. This is stylized material movement, not simulated orbital motion.
- Warm-pixel-only masks left saturated white window cores lit. Include the complete emitting aperture and couple local spill to the lamp state.
- Full-scene/cropped diffusion attempts introduced deformation and texture artifacts; the added spacecraft was rejected as cheap-looking. Keep the immutable source and masked local effects as the default.
- Anchor exhaust precisely, evolve its internal wisps and restore rooflines over it. For this airless setting, vent direction explains the exhaust; terrestrial wind and buoyant chimney smoke do not.

### 02 Basalt Transmission

**Accepted baseline:** v6 look and requested seamless completion. [Delivery record](basalt-transmission/animation/delivery-v6.json), [renderer](../scripts/render_basalt.py), [motion review](../scripts/motion_review.py).

- Increasing opacity in one middle-ground patch did not make the far/upper landscape active. Split depth layers and spread coherent weather through the visible terrain.
- Numeric pixel change and fine high-pass shimmer did not prove readable cloud travel. Track a recognizable shape at normal size; do not use amplified difference maps as the visual acceptance test.
- Protect the moon in both the moving texture source and output mask. Protecting only the output can allow sampled copies to drift elsewhere.
- Center trajectories on the visible region. Slower clouds were preferred after motion became readable; slower motion and lower visibility are separate controls.
- Local overlapping lifetimes can conceal resets but may soften or double texture. Check that tradeoff in playback. CRF16 produced an encoded seam outlier despite correct analytic timing; the verified QP0 master resolved that delivery problem. Keep the seam gate unchanged.

### 03 Glacier Sanctuary

**Accepted baseline:** v10 look; v11 is the requested unique sixty-second 4K delivery with adjusted timing. [Scene record](glacier-sanctuary/animation/README.md), [water method](../scripts/water_surface.py), [delivery renderer](../scripts/render_glacier_delivery.py).

- Sparse glints and tiny image warps repeatedly failed to read as water. The 24-wave reconstructed reflection surface became the working method, then v9 calmed it and v10 slowed/filtered it.
- Preserve a successful method while changing speed, contrast or strength independently. Use sampling-aware filtering and boundary damping to reduce fine shimmer and shoreline distortion.
- Foreground snow remained absent for this composition. Icebound's later snowfall approval does not reverse Glacier's scene-specific choice.
- Extending to sixty seconds must not slow every effect. Quantize wave frequencies to integer cycles and particle lifetimes to divisors of the new duration; hide resets locally. Glacier's recorded mean/max wave-speed deviations were 5.15%/12.11%, not zero.
- Render preview and final from the same source-frame pass where supported. The 4K image is upscaled from 1672×941; motion and source quality matter more than the output dimensions.

### 04 Floodplain Keeper

**Accepted baseline:** v2 look, followed by the requested 4K master and one-hour Colony assembly. [Initial methods](../final/04-floodplain-keeper/animation-v1/README.md), [lighting revision](../final/04-floodplain-keeper/animation-v2/README.md), [delivery](../final/04-floodplain-keeper/delivery-v2/README.md).

- The user found clouds and water fine, then requested light flickering. Retain those environmental layers; add independent habitat-window and desk-lamp events with coupled warm spill.
- Exclude reeds, sluice walls and other solid objects from both water/cloud sampling and effect output. Inpaint unsuitable texture sources before transport where needed. Reduced displacement corrected reed interference.
- A beacon mask created an unwanted rectangular sky patch; tighten the mask to the actual light instead of dimming its entire bounding rectangle.
- Config-driven events allowed the lighting revision without changing water/sky logic. Sampled old/new isolated layers and composite pixels outside lighting masks verified preservation.
- During long assembly, Colony's usual scaler changed decoded source colour values. Reusing the verified loop through its existing Prepared cache preserved the pictures while still using the actual Colony engine. See [assembly record](../final/04-floodplain-keeper/assembly-v1/README.md); this is a measured workaround, not a reason to bypass verification on future exports.

### 05 Saltline Receiver

**Accepted baseline:** v5 look. The requested v7 sixty-second 4K loop is technically verified; its longer lighting schedule remains a separate review. [Accepted look](../music/saltline-animation-v1/README.md), [history](../music/saltline-animation-v1/history/README-through-v5-review.md), [minute delivery](../music/saltline-animation-v1/LOOP_V7.md).

- Early dust was invisible. The later distant dust worked, but foreground road gusts were rejected as excessive/fake. Retain the distant effect and remove the rejected foreground layer rather than increasing both.
- A short excerpt looked active while the longer preview lost its dust after initial gusts left frame. Add staggered incoming formations and inspect coverage across the full delivery duration.
- Hut lights benefit from independent held off periods. V7 freezes seeded events lasting 12.4–17.7 seconds, including events crossing the end/start boundary; unmapped lights stay steady.
- The minute reuses local twenty-second atmospheric cycles at unchanged speeds while lighting uses the whole minute. Full scenes at 0/20/40 seconds differ; three copies of a twenty-second MP4 would not satisfy that request.
- Frozen seeds provide repeatable variation. Randomness must be generated once into the configuration or deterministic schedule, not sampled afresh during each render.

### 06 The Last Cable Station

**Accepted baseline:** v3, user verdict “ok perfect.” [Environmental revision](../music/cable-animation-v2/README.md), [screen revision](../music/cable-animation-v3/README.md), [approval](../music/cable-animation-v3/approved-v3-preview.json).

- “Movement seems okay” was not the end of the distant-weather work. V2 increased upper cloud/valley transport and added three independent haze formations at different heights; closer cloud layers retained their existing rates.
- Add room-light activity and local daylight variation without pumping the whole image. Lamp aperture/core and nearby spill change together; shading follows the left sky and sunlit desk with soft transitions.
- Screens should do something specific. A route marker with timed nodes, forward-scrolling log texture, a cursor and a changing meter gave readable activity inside the original layouts. Perspective masks protect bezels.
- Fade a marker before its return and wrap log texture forward through the join. Do not move the entire screen image or distort the monitor geometry.
- Sampled pixels outside the computer apertures matched v2 exactly. This is the model for a focused revision: implement the requested addition while preserving the rest.

### 07 Icebound Weather Post

**Accepted baseline:** v2 snowfall/beacon look, user verdict “i think it's good.” V3 adds requested minute-long lighting variation and was used for the requested final assembly; do not infer a separate full-timing verdict. [First draft](../music/icebound-animation-v1/README.md), [snow/beacons](../music/icebound-animation-v2/README.md), [minute timing](../music/icebound-animation-v3/README.md), [final delivery](../final/07-icebound-weather-post/delivery-v3/).

- The first draft already included broad cloud transport, independent basin weather and practical-light events based on previous feedback. Choose these early instead of waiting for repeated requests to make the background alive.
- Pale spindrift was easier to distinguish from the ice than the first test colour at unchanged opacity. Contrast and colour separation can solve visibility without adding density.
- Requested snowfall uses several size/speed groups, a sparse nearer group, directional blur and locally faded path renewal. The moon and mast are excluded from moving cloud sampling as well as output.
- Antenna lights use compact red cores/halos and staggered double flashes. Anchor them to existing antenna tips; “radar-style” did not require a sweeping beam or new geometry.
- V3 retained exact weather speeds/local cycles while varying room holds and beacon gaps over a frozen sixty-second schedule. Cache repeated weather frames where useful, but composite the correct independent lighting state for every frame.

### 08 Rainline Relay

**Current candidate:** v4 received “about there”; v5 lamp/glass-rain changes await artistic review. The explicit commit/push request backed up the latest twenty-second preview and records; it did not approve the new look. [V4 fixes](../music/rainline-animation-v4/README.md), [V5 changes](../music/rainline-animation-v5/README.md), [backup scope](../music/rainline-animation-v5/BACKUP.md), [shared renderer](../music/rainline-renderer/render_rainline.py).

- Window masking needed repeated correction. Trace separate panes at source resolution, use softened/supersampled edges and retain mullions, roof edges and metal. A warm/white emission gate can help after geometry is correct; thresholding alone cannot identify the right aperture.
- Inspect fully dimmed states as well as bright ones. Incorrect spill/reflection rectangles were removed from the rear building. Increasing blur is not a substitute for fixing the polygon.
- Initial water was too quiet; later movement was too strong. The current v4/v5 setting reduces displacement from .45 to .3375 and also reduces contrast/specular/rain-impact brightness by 25%, retaining speed .12. Preserve root, post and vegetation boundaries. Those numbers belong to Rainline's schema and mask, not a general water preset.
- Small additive radio changes were still hard to see. Two segmented meter rows and a perspective-confined cyan screen signal made the foreground action more explicit. Test at full scene size, not only enlarged crops.
- Antennas alternate red/green on successive pulses with dark intervals, avoiding an unintended mixed-colour state. The complete colour cycle must divide the loop.
- V5 makes the desk lamp blink briefly around seconds 4 and 14, dimming emitter, desk spill and nearby halo together. The early halo omission showed why the whole light pool needs inspection.
- Separate rain in the environment from water on glass. V5 adds twelve sparse sliding beads with local refraction/highlights and narrow trails, clipped to the panes and faded at lifecycle resets. This is an implemented, technically checked candidate—not an accepted rain preset or fluid simulation.

### 09 The Shoreless Colony

**Current candidate:** genuine sixty-second v3 revision, user review pending. User prefers v2 left-monitor activity and rejected its conspicuous right waveform. [Scene record](../music/shoreless-animation-v3/README.md), [configuration](../music/shoreless-animation-v3/scene-plan-v3.json), [adapter](../music/shoreless-animation-v3/render_shoreless_v3.py). V1/v2 remain preserved.

- Local criticism needs a local correction: user found only water beyond the third tower too strong. V3 smoothly reduces displacement from .40 to .30 across source x1085–1145; sampled water to the left remains exactly v2. Preserve sea speed, texture and the unaffected composition.
- Readable screen activity can still be excessive. The large cyan waveform was rejected; preserve original imagery with small route/tracking details. The left v2 route/node treatment is explicitly preferred. V3 preserves it at sampled times throughout the minute and restores the original right display with restrained details. New right treatment awaits review.
- Walkway flickers attach to three actual emitters, include white cores and local warm spill, and are staggered over the minute. Leave other lamps steady. No new invented light geometry.
- Complete pane masks need forced-dim crop review: small coordinate errors left bright strips on middle/far cabins in earlier attempts. Correct against actual source pixels, include bright cores/warm dividers, and preserve dark frames. V3 retains corrected v2 apertures.
- Foam follows photographed moving crests with broken coverage and caisson wash; it is an optical approximation. Tune independently of underlying water displacement. V3 retains v2 foam settings.
- Red/green antenna colors need a complete color cycle dividing the loop. Five-second pulses give a ten-second color cycle here; preserve true mast-tip placement and protected sampling/output.
- Extend a loop without slowing it: v3 retains twenty-second atmospheric fields and composes unique sixty-second cabin, lamp, walkway and sunlight schedules. Check full scenes at 0/20/40 and decoded sections for distinctness. Cached environment pixels are lossless float32 and bound to code/config/source fingerprints; light composition uses the actual minute time.
- Localized shafts and water warmth avoid global exposure pumping. The minute uses three distinct sunlight openings, not a stretched twenty-second timing envelope.
- Existing turbine blades rotate optically over reconstructed sky with fixed hub/mast restored. This remains an unapproved candidate method; inspect extraction edges/background before reuse elsewhere.

## Render and delivery improvements to retain

- Use the existing local Python/NumPy/OpenCV/FFmpeg pipeline. Reuse effect primitives and configuration instead of whole-scene generation or a new renderer copy for every parameter change. Existing adapters still require scene-specific work.
- Use region-limited calculations and cached repeated layers where the renderer supports them. Freeze accepted renderer snapshots before shared edits. Do not change a hashed implementation in place and continue citing an old validation report.
- Render only changed isolated layers first, then the complete short composite. Preserve working layers through sampled pixel comparisons; label these as sampled regression checks, not proof of continuous visual quality.
- Loop timing must match states and motion through the boundary. Keep forward transport, local zero-opacity resets, deterministic events, wrapped holds and no duplicate endpoint. No ping-pong or full-frame dissolves.
- Validate analytic individual layers and the encoded regional/composite seam. Fully decode, check frame counts and timestamps, and compare repeated payloads. QP0 solved a particular encoding failure; it does not remove the need to check future encodes.
- Use a repeated review to expose joins without player restart. Label it clearly: three repeated twenty-second loops are a sixty-second review, not a unique sixty-second animation.
- Render the short master once, then use stream copy for long repetition. Preserve colour and pictures when assembling with Colony; check decoded samples or payloads against the verified master. Validate all long-export video/audio and timestamps.
- Keep source dimensions and upscaling explicit. Separate user acceptance of a short look, acceptance of a music join, requested longer timing, technical verification and full combined review.
- Save exact source/config/code/dependency/mask hashes. Git line-ending conversion can change recorded hashes; use narrow byte-preserving attributes or exact dependency snapshots. Verify remote media bytes after a requested backup; ignored exports are not backed up by a code push.

## Sound lessons that affect scene production

Animation and music are separate decisions. Icebound's repeated SFX-like bed was rejected as boring; the later selected direction used audible chord changes, bass movement, a short melodic phrase with varied replies and a later countermelody. The user liked that direction but reported lyrics, so instrumental intent and an actual vocal check remain part of the music workflow. See [Icebound music](../final/07-icebound-weather-post/music/README.md) and [MUSIC_WORKFLOW.md](MUSIC_WORKFLOW.md).

Make short variants first, let the user choose, then work from a longer supplied piece. Choose loop points, overlap and level for that particular track; a prompt does not guarantee a usable join. A technically clean hour/two-hour export does not establish full listening approval. Do not add sound effects simply because the visual contains rain, radios or machinery.

## Do not repeat these shortcuts

- Treating stronger opacity, higher output resolution or more objects as a universal improvement.
- Copying source coordinates or masks from another scene, or sampling protected objects into moving textures.
- Tiny brightness changes as a substitute for recognizable motion; judging only crops or difference maps.
- Synchronized breathing across lights, lit white cores inside supposedly dark windows, or spill that stays bright when its lamp blinks.
- Scaling all effect speeds down to fill a longer loop, or letting a convincing short gust disappear for most of the full video.
- Weakening a numeric seam gate to pass an export, or treating passed numeric gates as artistic approval.
- Applying old experimental presets without checking their outcome. [effect-presets.json](effect-presets.json) contains historical glint and foreground-snow options; their availability is not evidence of acceptance.

## Keep the bank useful

After each meaningful revision, update the relevant video section and effect guidance in place. Record: the user's actual feedback; the visible failure; the implemented fix; a link to its source/config/renderer/report; its reuse conditions; and whether it is accepted, technically checked, rejected or still a proposal. Keep exact chronology in the scene package. Promote a candidate to an accepted example only after the user's verdict, and retain failed approaches so they are not rediscovered.

For videos 10–14, the current artwork and motion proposals are starting material, not implemented animation evidence. Choose applicable lessons here during planning; do not invent a success history for them.
