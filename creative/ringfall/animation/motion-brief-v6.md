# Ringfall Observatory — living scene, local animation brief v6

Status: authorized, implemented and rendered locally. Current export: ringfall-v6-b-final.mp4; 720p preview: ringfall-v6-b-preview.mp4. Technical checks and sampled-frame visual review completed; user artistic review pending. Source artwork is upscaled to 4K. This brief supersedes the three-small-overlays approach.

## Production prompt

Create a locally rendered cinematic scene from `creative/ringfall/04-laptop-refined.png`, with clear, coordinated movement across foreground, midground, and background. The viewer should notice life throughout the composition within two seconds at normal viewing size. Build a rich, calm observatory atmosphere suitable for ambient music; prioritize convincing motion and depth over decorative effects.

Keep the camera locked and preserve the composition, window structure, furniture, rug, single-handled mug, lunar terrain, and overall warm/cool balance. Separate the necessary elements into carefully feathered masks and layers before animation. Preserve the original source and reusable masks. Do not apply a global image warp or rely on brightness changes across the whole picture.

BACKGROUND HERO — THE PLANET: animate slow, flowing atmospheric currents within the planet's cloud bands. Develop broad, low-amplitude rolling structures with smaller secondary eddies so a substantial region of the vista feels alive. Keep the planetary silhouette, lighting terminator, ring geometry, rings crossing the disc, stars, and horizon rock-steady. Use constrained, masked texture advection; do not rotate or wobble the whole planet. The atmospheric texture must flow without stretching, boiling, smearing, or detaching from the sphere. Design a periodic flow field with varied phases, not a conspicuous forward/reverse playback. If foreground rings cannot be protected cleanly, repair the masks before proceeding.

BACKGROUND ACTIVITY — THE COLONY: add two slow moving pools of warm work-light sweeping across separate patches of ground near the base. Ground illumination should follow the terrain perspective, remain confined to plausible surfaces, and respect occlusion by buildings and rocks. Use a ten-second patrol cycle with softened turnarounds. No visible light shafts or airborne dust in the lunar vacuum. Retain one restrained amber mast beacon, offset in phase from the work-lights. These are new lighting effects proposed for this revision, not movement already present in the still.

MIDGROUND CONNECTION — THE WINDOW: add very faint, broad reflections on the lower window glass that track the colony work-lights. Clip reflections to the glass and keep them behind the opaque window frame and furniture. They should help connect the interior and exterior without making the window look like a screen or washing out the landscape. Keep exposure and the practical room lamps stable.

FOREGROUND — THE ROOM: retain a clearly visible, translucent plume of coffee steam. Use rising volume with changing density, curl breakup, branching wisps, and natural dissipation rather than repeating identical sine-wave strands. Animate the laptop's existing lunar display with a measured scan and readable telemetry movement. Keep its bezel and interface structure fixed. These effects support the larger scene rather than carrying all of the animation.

MOTION DIRECTION: use different phases and compatible speeds across layers. Avoid having everything pulse together. Preserve pauses and visual breathing room. No camera movement, arbitrary star twinkling, strobing, global exposure pumping, warped furniture, neon glows, added people, or unrelated objects. The mood should be an operational observatory at night, not an effects demonstration.

LOOP: exactly ten seconds. All motion must be periodic with continuous position and velocity through the seam. Natural steam always rises. Do not ping-pong the scene, visibly reverse the planetary flow, or hide a seam with a full-frame dissolve. Render 300 frames at 30 fps without duplicating the endpoint.

OUTPUT: first make a 1280x720 motion preview and inspect the whole composition over repeated playback. Only after its motion and masking pass review, render the 3840x2160 MP4. The background plate is upscaled from 1672x941; do not describe it as native 4K artwork. Use local tools, with no paid plugins, external generation calls, or separate credits.

## Definition of a successful draft

- The planet and colony provide independently visible background movement at normal full-scene scale; laptop and steam alone cannot satisfy the brief.
- The foreground, midground, and background each contribute, with the window reflection deliberately quieter than the principal layers.
- Motion is recognizable in a normal-size 720p preview, without zoomed-in crops or an explanation of where to look.
- Mask boundaries do not swim, rings and terrain do not distort, and reflected light never paints over furniture.
- The loop is continuous in both the analytic render and the encoded file. Brightness matches alone are insufficient.
- Changes are described concretely. Never claim a percentage improvement from increasing a parameter or passing technical tests.

## Implementation order

1. Prepare masks for the planet atmosphere, rings, terrain-light patches, window glass, opaque occluders, mug plume and screen.
2. Prototype the two background effects first. If they do not work, improve them before adding foreground polish.
3. Add linked glass reflections, then steam and laptop layers. Keep each independently toggleable.
4. Review a full-scene motion preview and isolated effect previews. Record artistic observations separately from numeric seam results.
5. Fix the largest visual defect, re-render only the preview, then export 4K once the scene works.

Implementation: scripts/render_ringfall_v6.py, with parameters and mask geometry in scene-v6.json. It reuses the earlier renderer for established foreground effects and encoding. The atmospheric effect moves image-band detail within protected masks; it is local compositing, not a physical planetary simulation or AI-generated video.
