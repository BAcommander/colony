# The Last Cable Station - two-hour Colony export

2026-10-03. The user accepted the v3 preview with "ok perfect", requested assembly through the existing tool and confirmed two hours. The actual Colony engine at C:/dev/SpeedySlideShow/colony/render.py produced the final MP4. App source was unchanged.

[Finished two-hour 4K video](../../../exports/06-last-cable-station/Last-Cable-Station-2-Hours-4K-v1.mp4)

7,200 seconds, 3840x2160 at 30 fps, H.264 and stereo 48 kHz AAC at 192 kb/s. The twenty-second master repeats 360 times. The original artwork is 1672x941, upscaled with Lanczos; no new native detail is claimed.

The selected Mineral Valley Transit soundtrack retains source 0:38-7:43, sixteen-second equal-power overlaps and fixed -7 dB gain, with one ten-second opening and twenty-second closing fade. Colony adds no gain, crossfade or overlay. The tool's peak limiter remains below its trigger for this soundtrack.

## Verification

The 4K loop passed full decoded frame/timestamp checks, per-region and composite encoded seam checks, and three exact decoded repetitions. Colony then fully decoded the two-hour video/audio. All 216,000 copied video packets have sequential timestamps, and every one of the 360 loop payloads matches. The first assembled loop's 600 decoded YUV pictures exactly match the verified 4K master. This carries the short-master seam validation through the full file.

See delivery-validation.json, colony-export.json and ../delivery-v3/delivery-validation.json. Opening, middle and ending decoded stills were inspected; continuous assistant playback, extended musical listening, upload checks and user approval of the full export are not claimed.

The runner seeds Colony's existing Prepared cache with a byte-identical master, preserving the established Floodplain/Saltline workaround for source colour changes from the app scaler. Colony performs the actual audio chain, stream-copy assembly, progress and full decode. Existing outputs are protected; --verify-only resumes delivery checks.

Video, MP3 and cached media remain local ignored exports; they are not backed up by Git. No commit, push or upload was performed.
