# Basalt Transmission — complete local production prompt

Status: prepared 2026-09-25; not rendered or approved. Source: creative/concepts/09-basalt-transmission.png, 1672x941. Source hash and delivery settings are in scene-plan-v1.json.

## Assignment and exact deliverables

Create Ambient Colony's next ambient visual using the supplied Basalt Transmission still. Follow the user-approved Ringfall v9b compositing approach and the current AGENTS.md. The request is a TWENTY-MINUTE finished video. Build one excellent twenty-second seamless loop, then repeat it exactly sixty times to make 1,200 seconds at 30 fps: 600 frames per loop, 36,000 frames in the finished video. This interpretation is explicit: the deliverable is not twenty minutes of unique motion. Do not silently substitute a twenty-second final for the requested twenty-minute video.

Deliver a 1280x720 twenty-second review loop, a 3840x2160 twenty-second master loop, and a 3840x2160 twenty-minute H.264 MP4. Silent by default: no music or ambience has been supplied for this scene. Do not synthesize or source audio. Preserve the source still. The 4K output is an upscale of 1672x941 artwork, not native 4K source detail. Keep the composition essentially unchanged; use a consistent negligible aspect correction for exact 16:9, with no appreciable cropping.

Use existing free local Python/NumPy/OpenCV/FFmpeg tooling. No paid services, credits, new model downloads or whole-image video diffusion. Reuse accepted effect algorithms; map every position and mask to this new image. Do not alter the approved Ringfall code or exports. The goal is an excellent first candidate using known lessons, not a guarantee that a long prompt eliminates visual review.

## Emotional and visual direction

A solitary weathered communications habitat shelters beneath a black basalt overhang on an immense alien plateau. Warm occupied rooms contrast with cold dark volcanic stone. A copper sunset illuminates the distant mesas; a small pale moon hangs high to the right. The habitat is functioning quietly at the end of a long shift. It should feel inhabited, secure, remote and plausible, not abandoned, under attack or operating as a nightclub.

Preserve the visual strengths of the still: the dark natural frame at upper left, detailed rocky foreground, asymmetrical low habitat, tall mast, connecting corridor, outlying right-hand module, layered distant terrain and warm sky. Let the viewer settle into the image. Movement should be readable at normal playback size within the first few seconds, but should not repeatedly demand attention over twenty minutes.

The image visually suggests an atmosphere through its clouds and existing low haze. Use that as this scene's artistic premise; do not import Ringfall's airless-moon rule. Interpret subtle rightward vapor drift as a gentle consistent breeze, not a storm.

## Motion hierarchy

### 1. Principal near motion: roof exhaust

Identify two existing plausible roof outlets during a close inspection: one on the main left habitat and a smaller outlet near the roof shoulder toward the corridor. Use actual visible hardware; do not invent chimneys, cut holes or emit vapor from the antenna. Record source coordinates and roof occlusion polygons before implementation. If there is only one convincing second outlet, use one strong plume rather than attaching a second to arbitrary geometry.

The main plume should be visible against the orange sky and rise approximately 55–90 source pixels before dispersing. Begin tightly at the outlet, broaden gradually, and drift about 10–25 pixels to the right over its visible lifetime. The secondary plume should be lower, narrower and less opaque. These are initial scale targets, not permission to ignore the actual outlet's size or background contrast.

Use pale warm grey vapor, gently sunset-lit, with a narrow continuous origin, irregular internal filaments, varying density and soft vanishing edges. Layers of detail must travel upward and rightward, not boil in place. Allow wisps to separate and fade without leaving detached circular blobs. Keep the base attached through all phases. Preserve roof panels, equipment, antenna, cables and foreground occluders above the plume where they are closer to the camera. Do not cover the broad main window or the entire building with haze.

Offset plume timing and detail so they do not look duplicated. Keep a steady emission population across the loop boundary. Do not fade the entire plume away every twenty seconds to hide a reset. No black smoke, fire, sparks, giant clouds, puff trains or obvious repeated sprites.

### 2. Principal distant motion: valley haze

Animate the existing ground-hugging haze in the middle and far distance, especially the open plain to the right of the habitat. Use two or three shallow irregular density layers at different depths. The near layer may travel roughly 20–40 source pixels across a twenty-second cycle; more distant detail should move more slowly. Prefer gentle left-to-right motion matching the vapor drift. These are material speeds, not whole-image translations.

Keep haze close to the terrain and low contrast, with broad thin bodies and smaller wispy variations. Make its movement discernible against darker ground without turning the plain into a bright white fog strip. Retain the scene's sunset color; distant haze can carry a faint dusty copper-grey tint. Avoid uniform horizontal bars, opaque curtains or a screen-wide gradient pulsing in brightness.

Clip haze behind the habitat, stairs, bridge supports, isolated rocks and foreground basalt. Restore occluding silhouettes cleanly. Vary depth through overlap and softness rather than moving the mesas. Do not animate foreground rocks, add rolling debris or send dust over the lens. Source pixels outside the union of accepted effect masks remain unchanged before resizing/encoding.

### 3. Supporting inhabited detail: room lights

Keep the broad inviting main window predominantly steady throughout the loop. Do not extinguish the building's main visual anchor or move the silhouettes inside it. Animate two or three smaller existing apertures or interior light groups: the narrow side window, the corridor interior and the right-hand module's small window are candidates to verify against the source.

Use independent event schedules rather than sine-wave breathing. For example: one small room dims over 0.6 seconds, holds for 3–5 seconds, then returns; another small window turns off later, stays dark for 4–6 seconds, and switches back with a soft electrical transition. Let the corridor remain mostly lit and change only a localized practical light group if the source supports a clean mask. Keep multiple lights continuously on. Do not repeat the same event timing across every aperture.

Mask the entire illuminated aperture including saturated white pixels, while protecting window frames, dividers and metalwork. When a lamp goes off, retain a plausible dark interior with texture; no black rectangular sticker. Adjust only its immediate spill or reflection, not the whole facade or sunset. Use a gently smoothed 0.3–0.8 second change rather than flashing. Avoid colored cycling, global flicker, moving shadows of unseen people or invented display text.

### 4. Optional quiet sky movement

If existing clouds can be isolated cleanly, move only their fine internal texture slowly to the right. Preserve the large cloud shapes, sunset gradient, moon, horizon, mast and mesa silhouettes. Cloud detail should travel a few source pixels over several seconds, with constant mean illumination. Do not shift the entire sky, warp the moon or paint new cloud streaks across the antenna.

Separate texture from broad lighting; transport the residual under a fixed protected mask. Reject halos, visible patch edges, smeared cloud forms or texture boiling. If this effect cannot be made clean with the local pipeline, omit it and report that choice. Convincing exhaust and valley motion are the priorities; optional sky movement must not damage the still.

### 5. Optional mast activity

Only if a suitable existing indicator can be identified, animate one small steady-to-dim amber status light. Give it a different schedule from the windows and a long steady hold. Preserve the mast, aerials, dish and all cables exactly. Do not add a large beacon, light cone, radar beam or rotating dish. Omit this effect if it requires inventing a prominent new lamp.

## Immutable scene and exclusions

Lock the camera completely. No pan, zoom, dolly, parallax, shake, focus pull or lens breathing. Preserve buildings, panel seams, rust, stairs, bridge, windows, antenna, dish, moon, mesa edges and every foreground stone. No spacecraft, rovers, people, creatures, meteors, lightning, dramatic weather, flashing emergency lamps, added props, titles, logos, watermarks or audio. Keep exposure, white balance and broad lighting constant. The sky does not darken over twenty minutes; this is a continuous ambient loop, not a sunset timelapse.

## Temporal construction

Use one twenty-second phase and deterministic seeds. Choose periodic density fields, seamless material coordinates or smoothly recycled particles that disappear before recycling. Transport must continue forward across the seam; never reverse animation to make a loop. A periodic field must match its motion as well as its appearance at t=0 and t=20. Do not append frame 600 as a duplicate of frame zero.

Schedule lighting events on a circular timeline and place most transitions away from the boundary; preserve intentional on/off holds through the seam. Do not make every effect reach a minimum or maximum together. Avoid repeating an obvious ten-second composition twice; the combined scene should have a distinct twenty-second cycle.

Do not solve discontinuities with a full-frame crossfade, black frames, freeze frames, a global brightness dip or ping-pong playback. Check the actual encoded loop, not only the uncompressed equations.

## Efficient implementation and review

Create a scene-specific renderer/configuration under creative/basalt-transmission and scripts, using shared algorithms from the accepted workflow. Keep source coordinates and tunable values in scene-plan-v1.json or a dedicated implementation configuration. Current plan coordinates are intentionally unfilled; they must be mapped and inspected, not guessed from this prose. Save mask overlays with labeled anchors. Do not copy Ringfall's hardcoded coordinate tables simply because both images have the same dimensions.

Implement exhaust and valley haze first, then add the restrained light schedule. Generate one complete twenty-second 720p candidate plus temporal samples at 0, 2, 5, 9, 13, 17 and just before 20 seconds. Include tight reviews of vent attachment, terrain occlusion and lit/unlit window interiors. Keep the review focused: repair concrete defects and preserve working layers rather than rebuilding the full scene.

Visual gate: the main exhaust and haze feel alive at normal size; no magnification, arrows or heatmap should be needed to identify movement. The habitat remains solid, weathered and welcoming. Plumes have volume without looking like cartoons. Haze belongs in the valleys. Light changes feel like rooms in use, not electrical faults. No new distracting focal subject appears. A numerical pixel change or the label 4K does not establish visual success.

Technical gate: verify finite pixel values, protected regions unchanged before encoding, correct masks and occlusion, 600 frames/30 fps/20 seconds, correct output dimensions and no audio. Check per-layer periodic endpoints, frame-to-frame continuity and encoded last-to-first motion; compare seam steps to ordinary adjacent steps without weakening thresholds to conceal failure. Review at least three repetitions when playback is available. Describe exactly what was inspected; do not claim continuous playback review from still samples.

## 4K and twenty-minute assembly

Once the preview passes available visual checks, render the same accepted effects at 3840x2160. Preserve strengths and timing. Inspect a decoded final frame and validate the master loop. For the twenty-minute delivery, prefer a visually checked compatible H.264/yuv420p encode of the loop, then repeat at clean boundaries. Do not render 36,000 expensive procedural 4K frames when sixty exact repetitions of the approved 600-frame cycle suffice.

Use a bounded-quality delivery encode suitable for long playback instead of assuming Ringfall's QP0 master is economical for twenty minutes. Compare the delivery encoding against the master in low-contrast vapor and sky gradients; reject banding, macroblocks or disappearing motion. If stream-copy concatenation is used, verify keyframe structure, monotonic timestamps and exact duration. If that does not work reliably, encode the repeated stream once with fixed 30 fps. Never declare the assembly valid merely because FFmpeg exited successfully.

Verify the twenty-minute file contains exactly 36,000 decoded video frames at 30 fps, 1,200 seconds, 3840x2160 and no audio. Inspect joins near the start, middle and end and check for timestamp gaps or frozen/duplicated transition frames. Account for container rounding separately from actual frame count. This file is a repeated visual bed; do not describe it as twenty minutes of unique generated action.

Save baseline-v1-preview.mp4, baseline-v1-loop-4k.mp4 and baseline-v1-20min-4k.mp4 under this scene's animation directory, or use equally clear versioned names. Never overwrite existing exports. Include a poster, prompt, source/config hashes, masks, parameters, render commands, validation reports and a delivery manifest. Keep rejected candidates labeled as drafts. Show the real video in chat and ask for artistic feedback through normal delivery, without rating it 10/10 yourself.

Update AGENTS.md and PROJECT.md with the result and reusable lessons. Commit/push supporting files. Approved finals should be backed up as requested by the project's storage policy, but check the twenty-minute file's actual size before adding it to ordinary Git. If it exceeds repository limits, report that explicitly and use an appropriate agreed storage route; do not silently omit it or buy storage. The already-approved Ringfall video remains untouched.
