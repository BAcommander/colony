# Basalt v3 — plainly visible background motion

User feedback: still struggling to see v2 background movement. This supersedes any suggestion that v2 met the visibility goal. Preserve the source architecture/camera and existing habitat effects.

Move actual photographic cloud detail to the right under the protected sky mask. Separate broad lighting from detail; advect two overlapping detail samples forward160sourcepixels per10seconds, using a smooth local blend to carry motion continuously across the boundary. Preserve the moon, mast, mesa silhouettes and scene exposure. This is a regional cloud-material transition, not a full-frame fade or a camera move. The overall scene still has a distinct20-second cycle.

Increase dust travel from190 to480sourcepixels per20-second lifetime, widen gusts by1.5 and thicken them by1.6. Use eight separately phased wispy gusts and higher density, behind the existing rock masks. Broaden coherent valley movement with280/360pixel material wavelengths. Avoid opaque rectangular fog, foreground contamination and synchronized pulses. Keep buildings, room-light schedule and vent effects as before.

Render a versioned20-second720p preview, inspect full-scene temporal changes, masks and the encoded seam. Then render the4K master and assemble the20-minute delivery through validated master stream-copy. Fully decode and check all36,000frames, timestamps and loop phases. Preserve v1b/v2. All output remains silent;4K is upscaled source artwork. User artistic review remains pending. Configuration: scene-plan-v3.json. CLI: --version v3 for render_basalt.py and assemble_basalt.py.
