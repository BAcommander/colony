# Floodplain Keeper - one-hour Colony export

2026-09-29: user requested "can you use the tool we made and make it?". Completed using the actual Colony application export engine at C:/dev/SpeedySlideShow/colony/render.py through assemble-with-colony.py. No application source changes, UI interaction or publishing action.

Finished video: `G:/AI/colony/exports/04-floodplain-keeper/Floodplain-Keeper-1-Hour-4K-v1.mp4`.

One hour, 3840x2160, 30 fps, H.264 video and stereo 48 kHz AAC at 192 kb/s. The accepted twenty-second visual loop repeats 180 times. Native artwork detail is 1672x941 upscaled to 4K. The one-hour Shelter Recovery MP3 supplies the soundtrack; its approved joins and existing opening/closing fades remain, with no added crossfade or gain. No overlay was selected. The default limiter remains below its trigger for the supplied track's measured peak.

## Preserving the approved picture

Colony's normal preparation re-encodes and tags the source through a scaler. A lossless trial changed decoded YUV values (first-frame mean absolute difference 1.5287, maximum 20), so it was rejected before long assembly. The diagnostic loop remains local at exports/04-floodplain-keeper/assembly-v1/colony-loop-4k.mp4 and is not used in the finished video.

The runner instead seeds Colony's existing Prepared loop cache with a byte-identical copy of the verified short master. This bypasses the problematic preparation while retaining Colony's real render(), audio processing, concat assembly, overwrite protection, progress, manifest and full-decode checks. Source tags remain as supplied; no colour transform is introduced. All 600 decoded YUV frames in the reused loop matched the accepted master exactly. The app's source and GUI defaults are untouched.

## Validation and review scope

Colony fully decoded every video frame and audio sample with fatal-error checking. Streams, resolution, frame rate and duration passed. Separate packet verification checked all 108,000 video packets, sequential presentation/decode timestamps, and exact payload identity for all 180 repetitions. The unchanged master already passed the encoded seam gate. See colony-export.json and delivery-validation.json for inputs, settings, tool/source/output hashes and checks.

Opening/middle/ending stills were extracted for inspection. This is not continuous assistant playback or full-hour musical listening approval. User acceptance covers the short animation look and music join. The finished combined export and any upload checks remain for user review.

Reproduce with the saved runner using the local Python runtime and Colony app installation. It refuses existing output/cache destinations; version them for another export. The script records the exact app renderer/exporter hashes. Code, manifest and validation records are tracked here; the finished video, audio and cached loops remain ignored local exports, not Git-backed media.
