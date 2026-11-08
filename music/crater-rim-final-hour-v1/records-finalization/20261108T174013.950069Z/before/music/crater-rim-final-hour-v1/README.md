# Crater Rim Survey — one-hour 4K production

The user authorized the complete one-hour video on November 8, 2026, using the longer animation timing and the approved November 7 soundtrack. The final path is `exports/14-crater-rim-survey/Crater-Rim-Survey-1-Hour-4K-v1.mp4`. Production is in progress; the final delivery receipt will establish completion.

The native 1672×941 scene is rendered from the frozen V5 artwork and code, then enlarged directly to 3840×2160 with FFmpeg Lanczos. It does not enlarge the old 720p review. Weather retains its original 60-second cycle and physical speeds. Larger events now use the saved ten-minute attention schedule:

| Event | Start times within each ten-minute cycle |
| --- | --- |
| Lamp flicker | 87.3 s double cluster; 397.7 s single cluster |
| Greenhouse reflections | 48.2, 238.1, 473.6 s |
| Rover passages | 52, 197.5, 351, 511.5 s; each lasts 25 s |

The original event strengths, terrain occlusion, vehicle geometry, cloud sampling and fixed room geometry are retained. Sun reflections remain coupled to the weather shadow at their new absolute times. The other weather, village, beacon and screen layers continue on their existing clock. The clean ten-minute master repeats six times inside the hour.

The approved FLAC is used at unity gain. Its music, wind, room air and existing 20-second closing fade are retained. Actual Colony v3 branding appears once inside the hour; audio is silent until five seconds and fades in through 20 seconds, and graphics clear by 22 seconds. No second closing fade, extra SFX, new generation or paid service is involved.

## Reproduce and verify

Run from the repository root. The local visual environment is `.local/crater-final-runtime/Scripts/python.exe`, using the exact package versions in `source-snapshot/music/crater-rim-animation-v5/requirements-resume.txt`. Python 3.12.10 reproduces all six original native controls with those packages. `runtime.json` records the actual environment. System FFmpeg 9.0 supplies the production encoder.

1. Run `visual/preflight_renderer.py`, then `audit/audit_long_scene.py native` using the visual environment. When reusing this run's existing weather cache, include `--verify-weather-cache` in the preflight command to retain its full-frame equivalence check. A fresh cache is built directly with the final renderer. Preserve completed receipts before starting a separate reproduction run.
2. Run `visual/produce_master.py cache`, then `render --workers 3`. Existing outputs are preserved; validated parts can be resumed only when input and encoder fingerprints match.
3. Run `visual/produce_master.py validate` and `audit/audit_long_scene.py decoded`. Then run `visual/produce_master.py approve` to bind the complete decode and independent picture controls to the same master hash.
4. Run `assembly/assemble.py` with its recorded dependencies. It uses the frozen actual Colony engine, brands only the first 60 seconds, stream-copies the remainder, and performs the complete final decode.
5. Run `assembly/verify_final.py --video --audio --stills --hash --review --finish`. This checks original timestamps, all copied video payloads, decoded opening and clean pictures, and every audio sample against the approved FLAC plus the opening envelope. It also makes a 135-second review from the completed final.

The weather cache can be reused after a renderer correction only with recorded all-frame equivalence. Original source snapshots and historical scene packages remain unchanged. Large native caches and assembly scratch stay under `.local/crater-rim-final-hour-v1/`; long video outputs stay under `exports/14-crater-rim-survey/`, per `EXPORTS.md`.

Numeric and decoded-still checks do not claim continuous playback, uninterrupted listening, user approval of the completed video, publication or remote backup. This task makes no new Git commit or push.
