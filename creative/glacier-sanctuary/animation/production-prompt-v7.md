# Glacier Sanctuary v7 — foreground snow and readable water reflections

User requested foreground snow and said water movement remained hard to see. Keep v6 distant snowfall, fog, roof smoke and all lighting unchanged.

Add28 larger soft foreground flakes in the lower view, beginning at source y540, gently falling diagonally right at25–44px/s vertical and7–16px/s horizontal. Fade at upper/lower boundaries. Flakes pass in front of rocks naturally; do not warp the scene. Keep the view to the warm sanctuary clear and avoid a dense lens-wide blizzard.

Retain the photographed water rather than distortion. Use18 irregular elongated reflection patches,22–55 source pixels wide,1.1–2.4px high, opacity .22 capped .26, moving right at8px/s. Broader and brighter than v6 tiny glints. Protect ice and shore and retain smooth appearance/disappearance. Visual review must decide whether movement is visible and natural; no numeric pass establishes that.

Eight-second720p30fps silent study. Water and foreground_snow isolates plus combined. Not seamless/final. Reusable parameter presets foreground_snow_sparse and water_readable_glints added to creative/effect-presets.json; foreground top_y must be remapped for another scene.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v7.json --output creative/glacier-sanctuary/animation/review-v7
