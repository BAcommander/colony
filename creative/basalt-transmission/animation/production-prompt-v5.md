# Basalt v5 — coherent background transport test

Status: implemented; user review pending. Eight seconds, 1280x720, 30fps, silent. A non-looping motion prototype, not the twenty-minute delivery. Original still remains immutable.

Transport complete existing cloud forms rightward at 9 source pixels/second. Preserve their shape and shading rather than animating only their fine detail. Extend coverage through upper sky and the cloud bank above the mesa; feather the boundary entirely within sky. Protect the moon in the output and remove it from the sampled texture so it cannot duplicate. Preserve antenna, ridge silhouettes, exposure and all foreground geometry. No camera movement, aircraft, new objects or global dissolve.

Add broad, low, internally textured wind tongues in the left distant valley and right mesa foothills. Each tongue and its internal density travel together at 11–21 source pixels/second. Widths 76–115 source pixels and heights 8–11 pixels keep the forms ground-hugging. Terrain masks occlude rock spires. Use restrained warm dust opacity, capped at .33; reduce nearer wind opacity to .12 and existing nearer haze to 70% of v4. Retain existing roof exhaust and window timings.

Review sky alone, distant wind alone, near wind alone, then combined at normal speed and full-frame 720p. Identify a cloud feature translating and a far wind tongue crossing terrain. No acceptance from numerical pixel changes. First/last frames and tracked source-cloud correspondence are supporting checks, not playback review.

Reproduce with: `python scripts/motion_review.py --config creative/basalt-transmission/animation/scene-plan-v5.json --output creative/basalt-transmission/animation/review-v5` (new output directory required if it already exists).

After the user accepts motion quality, solve a twenty-second continuous loop with forward travel and unobtrusive local birth/dissipation. Do not impose a full-frame crossfade, reverse motion or cycle short excerpts to fake a final loop. Validate actual encoded seam and complete preview before 4K and long assembly.
