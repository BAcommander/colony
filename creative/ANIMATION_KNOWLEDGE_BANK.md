# Ambient Colony animation knowledge bank

Updated 2026-10-07. Use the lessons from videos 01–11 to make future first drafts stronger and avoid repeating rejected experiments. Start with readable environmental motion, add a few believable signs of habitation, and preserve the photographed structure of the scene. Reuse methods and timing helpers; remap every mask, anchor and protected object to the new artwork.

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

### 10 Farpoint Station

**Current state:** v1 motion was rejected as invisible; v2 cloud visibility was confirmed. V3 still read as clouds alone. V4 was rejected for sparse coverage, blue auroral glow and imperceptible stars. V5 removed the aurora and expanded weather, but stronger fixed-star brightness still failed the user's movement review. [V6](../music/farpoint-animation-v6/README.md) delivers a complete minute and exact 180-second review with positional star drift, confined amber-bar cleanup and bottom-right cabinet LEDs. V5 planet and existing station activity retained. Technical gates passed; user playback review and 4K pending. Assistant inspected stills, not continuous playback.

- V1 repeated the old failure: passing pixel-change, coverage and seam checks did not establish visible principal motion. Blending nearby shifted copies muted apparent cloud travel. V2 removes that principal-layer timing blend and increases direct travel, then measures recognizable feature displacement as supporting evidence. Require normal-speed full-scene user review before rebuilding the loop; do not call small nonzero deltas a visibility pass.
- Faster additive cloud transport created a bright patch when pale radiance crossed lighter ground. V2 converts the separated cloud to premultiplied optical colour/alpha over the stationary local reconstruction. This correction was inspected in stills and remains a candidate, not an accepted planetary preset.
- V2 direct travel now has user-confirmed visibility. V3 preserves the principal layer exactly at sampled times while adding a separate lower cloud patch and displaced soft cloud shadows. This preserves the readable transport while expanding depth. The new lower mask excludes the prominent foreground crater; additions remain candidates.
- More instrument activity uses the existing small radar dial, schematic connections, status panels and real coloured emitters. V3 includes complete LED cores and nearby colour spill, independent schedules, and steady lights elsewhere. Forced-dark samples check attachment; technical and still checks do not approve the new timing/look.
- The user still described v3's planetary activity as clouds alone. Adding another cloud patch and shadow did not establish a distinct new planetary phenomenon for them. The requested [completion prompt](../final/10-nightward-station/animation-completion-prompt-v2.txt) proposes an aurora and sparse intracloud illumination plus star variation; v4 implemented them; the user subsequently rejected the aurora as an implausible blue glow. The queried amber streaks beside the truss are present in the clean source; treating them as cabin reflections is an artistic interpretation with an unverified emitter. V4 linked their complete bright cores and local haze to the desk lamp; the user later authorized removing the confusing bars in v6. Brightness-aware core masking excludes surrounding dark glass, avoiding rectangular dim patches.

- Clouds over a rocky planet need separation from geology before transport. This candidate extracts positive pale-cloud radiance inside mapped regions and reconstructs stationary underlying colour locally, then transports the cloud field along curved paths with a protected limb. The reconstruction is approximate; inspect exposed texture and softened/doubled cloud edges in playback. Do not claim recovered terrain or physical planetary rotation.
- The first thin veil produced no 8-bit change at sampled times despite nonzero floating-point motion. Its failed test is retained in the scene history. Increasing its own travel/strength produced quantized activity while retaining principal cloud rates; numeric activity still does not prove visual success.
- Initial pane masks left lit strips; supersampled source-coordinate contours and separate dimming of warm divider reflections corrected the forced-dark samples. The desk emitter required its actual irregular tube outline, not a rectangular patch. Existing frames, shells and equipment retain their geometry.
- Upper, central and right weather regions change throughout two-second samples. Sampled exposed foreground craters, stars and truss match the original. These are coverage/protection checks, not artistic acceptance. Source/temporal/decoded stills were inspected; continuous playback was not.


- Extending the direct cloud excerpt required a new coverage/renewal design. V4 partitions extracted optical clouds into separate feathered formations, preserves v2 velocities, and staggers sixty-second lifetimes with zero-opacity resets. This avoids blending nearby copies of the entire weather field. The composite arrangement changes: exact source-array retention is not identical frames or artistic acceptance. Inspect local fading/overlap and reconstructed terrain in playback.
- The first aurora draft read as a comb in full-frame stills. Seeded irregular spacing, widths/heights, gentle curvature, gaps and softened detail corrected it before delivery. Minute-periodic transport and masking protect the original limb; fictional plausibility is separate from physical simulation.
- Storms must be placed in the cloud present at their event time. The middle event initially hit thin cloud and was moved within the extant optical formation. Pixel changes support but do not establish visibility. See [v4 review](../music/farpoint-animation-v4/visual-review.json) and delivery evidence.

- V4's technically checked aurora was rejected as an implausible blue glow. Remove a rejected phenomenon rather than continuing to polish it. V5 has no active aurora layer; [exact feedback](../music/farpoint-animation-v4/user-feedback-coverage-2026-10-07.json).
- Motion inside existing upper-cloud masks did not make the broader planet feel alive. V5 adds separate broken fronts across the central/lower hemisphere while retaining terrain positions and existing weather. The first wider field read as haze; sharper density transitions created identifiable edges and gaps. This procedural optical weather remains a candidate, not an accepted preset.
- Both v4 subtle modulation and v5 stronger fixed-star brightness failed the user's movement review. Large encoded brightness ranges did not answer a positional-motion expectation. V6 transports extracted source star sprites together right/up while keeping camera and geometry fixed; native footprints are preserved with subpixel sampling. Local zero-opacity renewals close the minute. This is a cinematic approximation pending playback review, not a proven preset. [Feedback](../music/farpoint-animation-v5/user-feedback-stars-bars-leds-2026-10-07.json) and [encoded transport evidence](../music/farpoint-animation-v6/targeted-validation.json).
- Ambiguous source reflections can remain confusing after correct lamp-linked dimming. V6 removes only the queried bars using a generated patch and source-coordinate mask. Direct blending caused dark ovals; gradient matching corrected the surrounding glass. Freeze the revised plate/hash, remap and disable obsolete reflection masks, prove unchanged pixels outside the edit, and inspect the full composition.
- New cabinet LEDs were explicitly requested. V6 places a small housing along the door perspective, with one steady light, independent events and attached local spill. Do not scatter unsupported bright dots over bare panels. Sampled full-planet and supporting-layer comparisons protect earlier motion while these additions change.
- Coverage checks must name previously bare regions, including the final third of the full minute. V5 checks six regions and preserves supporting v4 layers through sampled exact comparisons. Neither those checks nor full-size stills establish artistic success.

### 11 The Empty Junction

**Current candidate:** [V3](../music/empty-junction-animation-v3/README.md) complete minute and exact 180-second review. V2 still felt static to the user despite wider clouds and mist. User authorized near-ground streamers, cabin condensation and directed valley flow. Technical gates passed; assistant inspected stills. User then requested commit/push but explicitly said v3 still needs work. Treat it as an unapproved checkpoint, not an accepted motion reference.

- V2's wider upper weather did not resolve the static overall impression. V3 redistributes movement nearer the viewer: two mineral streamers beside the tracks and cabin approach, a short grille plume and a specific curved valley flow. The new foreground weather is explicitly authorized for this scene; do not overwrite other scenes' accepted foreground restraint.
- Inspect the source before adding hardware: an existing cabin grille supplies the new plume anchor, avoiding an unnecessary art edit. The capped roof pipe remains unused. Exhaust attribution remains an artistic interpretation.
- Uniform puff spacing made a nearly steady streak. Vary emission at puff birth on minute-periodic schedules, then advect and dissipate the concentrations. Preserve attached roots and inspect the actual full-scene effect. Protect the small trackside post and near ridge as occluders.
- V1 had technically sustained weather but narrow cloud/mist coverage. V2 adds a broader broken bank with readable edges above the retained source clouds, and taller mist around central mineral bases. Improve the distribution and structure of motion before merely increasing opacity. New procedural density is an optical approximation; this is a candidate, not an accepted preset.
- V2 mist parcels evolve internal advection, height and edges while traveling forward at separate far/side speeds. Independently phased zero-opacity renewals sustain the genuine minute. Check the final third and actual join; unique schedules alone do not establish natural motion.
- Doorway dips looked stronger than their remaining warm spill. V2 lowers the core dip, strengthens door/tread spill coupling and keeps ambient illumination. Sample the illuminated tread, not a dark riser, when testing spill response. Inspect actual event strengths as well as forced-dark diagnostics. Longer independent room holds add station activity without changing all windows together.
- Coarse sky masks once sampled rock fragments. Refine both extraction and destination near silhouettes; a global dark-pixel rejection froze real cloud cores. Restrict it to boundary neighborhoods. Extend only atmospheric residual through source occlusion gaps to avoid moving rock-shaped cutouts. V2 retains v1's corrected sky mask exactly.
- A small optional twilight-shade study added little at full composition and was omitted; diffuse light does not justify an emphatic moving shadow. The source has no readable screen; the capped roof pipe remains unused. V3 later uses the visible cabin grille as a deliberately interpreted exhaust.
- Preserve v1 media/source/dependency hashes and compare retained layers when replacing weather. V2 checks five unchanged light layers, source protection, five-region minute coverage, analytical/encoded seams, complete decodes/timestamps and exact repeat identity. These checks support implementation; the user's playback verdict decides quality.

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

For videos 12–14, current artwork and motion proposals are starting material, not implemented animation evidence. Empty Junction 11 has a technically checked v3 checkpoint that the user says still needs work. Farpoint 10's v2 cloud visibility is user-confirmed; v4 was rejected for coverage/glow/stars; v5 stars were still imperceptible; v6's positional stars, bar cleanup and cabinet LEDs await full-preview review, with technical evidence recorded. Choose applicable lessons here during planning; do not invent a success history for them.
