# Saltline Receiver — one-minute 4K loop v7

Requested 2026-09-30: “if we're doing a longer loop , can the lights in the huts stay off for longer intervals or be more random, do that then make the 1 minute 4k loop”. The accepted v5 look and twenty-second v6 records remain preserved.

Delivery: `final/05-saltline-receiver/video-4k-v7-60s.mp4`. Sixty seconds, 1,800 frames, 3840×2160/30 fps, silent. Native artwork is 1672×941, upscaled with Lanczos. A matching 720p preview and three-cycle, three-minute 720p join review are in this folder. The user explicitly requested “commit and push” on 2026-09-30: the 4K master uses a single-path Git LFS rule; the two review videos remain local ignored files. Backup authorization does not imply visual approval of the longer light schedule. See `remote-backup-v7.json` for independent remote restore/hash evidence when completed.

Four hut apertures have independent irregular off events lasting 12.4–17.7 seconds including their short switching transitions. Each has two events per minute, with varied intervening on holds. Two events continue smoothly through the end/start join. The seed and resulting events are frozen in `scene-plan-v7.json`; every repetition preserves the seam. Other windows and the door light stay steady. The service lamp retains two brief restrained dips, at separate times in the minute.

The atmosphere retains v6's twenty-second local cycles within the full minute: clouds 2.5 source pixels/s, distant dust 20 pixels/s, sunlight shadow 28 pixels/s. The full scene differs at 20 and 40 seconds because of its minute-long lighting schedule. This is rendered as 1,800 source frames, not three copies of the previous video. Dust coverage, opacity, colour, geometry and masks are preserved; foreground dust remains absent. `SaltlineMinute` shares the existing source, masks and atmosphere renderer, and changes only the light clock/events and delivery orchestration.

`v7-analytic-validation.json` records exact periodic layer endpoints, sampled source seam gates, unchanged atmospheric pixels at sampled times, and distinct complete-scene states at 20/40 seconds. `v7-delivery-validation.json` records full decodes, sequential timestamps, each encoded layer-region/composite seam, no duplicate endpoint, dimensions, silence and hashes. Both resolutions are encoded from one source-frame pass with H.264 QP0/yuv420p. Three stream-copied 720p cycles are fully decoded and checked for identical repeated payloads. Every source frame asserts that protected pixels remain unchanged.

Inspection covers full-composition temporal samples and a decoded final frame; it does not claim continuous playback or user acceptance. V5 remains the accepted artistic baseline; the new minute-long lighting/export awaits the user's verdict. Code/configuration/records and the explicitly requested 4K master are backed up together; ignored repeated previews are reproducible local outputs.

Reproduce from the repository root using the existing local Python with NumPy, Pillow/OpenCV and configured FFmpeg:

```text
python music/saltline-animation-v1/render_saltline_minute.py --stage samples
python music/saltline-animation-v1/render_saltline_minute.py --stage render
```

Existing video destinations are protected against overwrite. `--stage prepare` records the deterministic v7 configuration only when that file does not exist; do not run it over the saved configuration. Use the preserved dependency snapshots for exact imported code bytes as described in the package README.
