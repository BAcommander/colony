# Ringfall v8: twenty-second ambient loop

User feedback: v7b is much improved, subtle and not visibly broken. Preserve it as the preferred baseline. User requested a twenty-second loop and a few additional effects, especially the rings or distant activity.

Extend the existing independent-layer observatory animation to exactly twenty seconds at30fps/600frames. Keep the source, furnishings, camera, planetary outline, ring geometry and landscape unchanged. Preserve the established steam, laptop scan, cloud texture and moving colony surface lights. Let background motion breathe over the longer cycle; keep coffee vapor rising at a natural speed with a slower envelope varying its density.

Add a restrained traveling variation through the existing illuminated ring material on the visible right-hand arc. This is fine brightness/texture variation only, not a rotating, expanding or regenerated ring shape. Mask and feather inward from the ring edges, exclude the planet and sky, and retain the original bands and gaps. Avoid sparkling stars or flashing highlights.

Add a slow, softly phased sequence at five small colony service-light locations. Keep this subordinate to the established ground-light sweeps; do not add spacecraft, vehicles, beams in vacuum or new focal objects. All temporal functions must be periodic over twenty seconds, with different phases between effects.

Render a720p preview, inspect the full composition and ring mask, and verify a real twenty-second cycle rather than duplicating the ten-second clip. Validate600frames and continuity at the20-second boundary, then export a4K review file with source-upscaling disclosure. Preserve v7b for comparison and record user approval separately from numeric checks.

Implementation: scripts/render_ringfall_v8.py inherits v7b layers. Shared validation now uses the configured duration instead of a hardcoded ten-second endpoint. Settings and verification reports are saved beside each export. The right-ring effect is an artistic local material modulation, not a physical simulation of ring orbital rotation.
