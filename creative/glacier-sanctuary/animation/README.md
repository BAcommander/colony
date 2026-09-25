# Current candidate — v3

Snow and smoke preserved from user-approved v2 effects. Wider distant fog, slow outdoor amber halos and broader traveling water reflections. Eight-second study in review-v3/combined.mp4; isolated mist, water and exterior_lights clips. Not seamless; visual acceptance pending. Review water for artificial stripes and halo strength. See production-prompt-v3.md. Older status below is historical.

# Current candidate — v2

Snow unchanged following user approval. Stronger coherent mist banks, readable water ripples/reflection highlights, larger roof plume and controlled right-annex lighting. Eight-second motion test: review-v2/combined.mp4; isolated mist.mp4, water.mp4 and roof_lights.mp4. Review pending; not seamless. See production-prompt-v2.md. Historical v1 status below is superseded.

# Glacier Sanctuary

Current: v1 eight-second motion study, 1280x720, 30fps, silent. Visual review pending. Source artwork is 1672x941. This study is not a seamless loop.

- review-v1/combined.mp4: full-scene motion.
- review-v1/atmosphere.mp4: snowfall and coherent mountain mist.
- review-v1/water.mp4: isolated water ripples.
- scene-plan-v1.json: deterministic seed, source hash, source-coordinate masks and effect settings.
- production-prompt-v1.md: intended behavior and review criteria.
- review-v1/review.json: hashes and decoded-frame verification.

Reproduce from repository root with `python scripts/render_glacier.py`. Choose a new output folder with --output when one already exists. Renderer refuses to overwrite clips. Python dependencies are NumPy, Pillow, OpenCV, imageio-ffmpeg, and local ambient_effects.py. No paid service, model download or plugin required. Draft MP4s stay local; source/settings/scripts/reports are tracked.

Review at normal speed and full composition. Snow should fall beyond the rock shelter; mist should travel rather than simply brighten; open water should ripple without warping ice or the shoreline. Warm interior light and fixed camera must remain stable. The supplied masks are manually mapped, so inspect boundary/ice coverage before finalizing. Numeric outside-mask invariance does not prove that a mask was drawn correctly. After the motion reads well, solve and validate a twenty-second loop, then export 4K. Do not build a long delivery before acceptance.
