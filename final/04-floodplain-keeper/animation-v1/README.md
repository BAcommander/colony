# Floodplain Keeper - first animation candidate

2026-09-29: first 20-second, 30 fps, 1280x720 silent preview rendered locally. Technical gates passed; user playback/artistic approval is pending. No 4K master or combined music video exists yet.

## Source and effects

The prepared `../artwork-v2-animation.png` (1672x941) was chosen for this trial under the request to try the first version. Its exact hash, source-coordinate masks and settings are frozen in scene-plan-v1.json. This does not establish standalone art approval. V1 art, thumbnails and earlier preparation remain untouched. A future 4K render will upscale this source detail.

Principal effects: reconstructed channel reflections using 24 filtered waves, plus overlapping source-cloud transport layers with local invisible resets. Reeds, sluice walls, pipework, moon, terrain, window framing and furniture are protected. Invalid water and cloud source pixels are inpainted before motion sampling to avoid importing protected objects. Water displacement was reduced after still inspection caught reed interference. Two habitat windows change independently; small screen and beacon activity supports the background. The beacon mask was tightened to prevent a rectangular sky dimming patch. No camera motion or added objects.

Water reuses scripts/water_surface.py with scene-specific perspective; scripts/ambient_effects.py supplies timing helpers. Existing shared and approved renderers were not edited. The twenty-second wave quantization changes component speeds by a mean absolute 14.26%, maximum 31.40%; see analytic-validation.json. This is a 2D reflection approximation, not a fluid simulation.

## Inspection and limits

Inspected the source, coordinate crops, mask overlay, temporal still samples and an actual decoded preview frame. Eight-second full-composition isolated sky/water tests were rendered and fully decoded before the combined preview. Continuous playback was not reviewed by the assistant. Water is the more apparent change in sampled frames; sky softness and overlapping layers may make directional travel too subtle. User normal-speed playback is the next visual gate. Numeric deltas do not prove convincing motion.

The technical records confirm exact analytic periodicity, source-pixel protection outside active masks before resizing/encoding, 600/1800 decoded frames at 30 fps, sequential timestamps, per-region encoded seam gates and identical decoded payloads across all three repetitions. The full preview has no duplicate endpoint. The 60-second review file is three repetitions, not a new sixty-second animation cycle.

## Local media and reproduction

Outputs live under ignored exports/04-floodplain-keeper/animation-v1/: floodplain-keeper-v1-preview-20s.mp4, floodplain-keeper-v1-three-loops-60s.mp4, water-isolated-8s.mp4 and sky-isolated-8s.mp4. These draft videos are local only; Git stores the source, masks, code and reports. Exact hashes are in delivery-validation.json, isolated-review.json and the local export inventory.

From repository root, using Python with NumPy, Pillow and OpenCV:

```powershell
$env:PYTHONPATH='G:/AI/youtube/.runtime/scene-tools'
& 'C:/Users/jazzs/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/render_floodplain.py --stage samples
& 'C:/Users/jazzs/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/render_floodplain.py --stage isolated
& 'C:/Users/jazzs/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/render_floodplain.py --stage preview
```

FFmpeg location is in the config. Existing MP4 destinations refuse overwrite; use a versioned output directory/config for revisions and regenerate reports. build-masks-v1.py reproduces the masks and initial config; do not run it over later edited configuration. The new adapter provides scene-specific isolation because motion_review.py currently targets Basalt. Its current encoder delivers 720p; final-size configuration is a target for the next delivery implementation, not an implemented 4K export switch.

Next: user judges water movement, cloud visibility and geometry at normal speed; revise the specific defect if needed, then implement/export and validate 4K before assembling the approved hour-long soundtrack.
