# Floodplain Keeper v2 - lighting flickers

2026-09-29: user feedback on v1: "clouds and water look kinda fine, can we add some flickering to any of the lights outside or inside?"

Preserves v1 cloud, water, screen and beacon settings/masks. Adds occasional separate dimming events to two exterior habitat windows, plus brief desk-lamp flickers with coupled warm wall/desk spill. Other fixtures stay steady. Existing habitat off/on holds remain. Events are smooth, brief and separated by steady intervals; no full-frame exposure changes. The source artwork and previous videos remain unchanged.

Exterior flickers occur near 1.2, 5.1, 10.4 and 18.3 seconds, with short secondary dips in the first two bursts. Desk lamp dips near 6.2/6.7 and 15.3 seconds. All added effects are steady through the loop join. Frozen source is still 1672x941 artwork-v2-animation.png; preview is silent 20 seconds, 30 fps, 1280x720. No new 4K or combined upload.

The existing renderer gained optional config-driven flickers and versioned filenames; the water and sky implementation is unchanged. preservation-check.json verifies identical v1/v2 samples for water, sky, screen and beacon and exact full-frame equality outside the revised lighting masks at ten times. All frames assert protection outside active masks before resizing/encoding. V1 remains reproducible using its old config; its original code fingerprint can be recovered from commit 392df07.

Inspected lamp aperture/spill masks and a steady/dimmed crop pair. This is still-sample inspection, not continuous playback. User approval of the new lighting remains pending. delivery-validation.json records full decode, sequential timestamps, encoded seam checks and three identical repeated payloads once rendering completes.

Run the same Python/OpenCV environment documented in ../animation-v1/README.md:

```powershell
python scripts/render_floodplain.py --config final/04-floodplain-keeper/animation-v2/scene-plan-v2.json --stage samples
python scripts/render_floodplain.py --config final/04-floodplain-keeper/animation-v2/scene-plan-v2.json --stage preview
```

prepare-flicker-v2.py reproduces config/masks only into a nonexistent v2 directory. The source-bound v1 masks remain dependencies. Version outputs rather than replacing existing files. Local ignored media: exports/04-floodplain-keeper/animation-v2/floodplain-keeper-v2-preview-20s.mp4 and floodplain-keeper-v2-three-loops-60s.mp4. Git stores code/config/masks/reports, not these draft videos.
