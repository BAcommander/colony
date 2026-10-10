# Saltline Receiver - two-hour Colony export

2026-10-03: user requested use of their existing tool to render the YouTube video. Completed with the actual Colony engine at C:/dev/SpeedySlideShow/colony/render.py through assemble-with-colony.py. Application source is unchanged; no upload performed.

Finished video: [Saltline Receiver - 2 Hours - 4K](../../../exports/05-saltline-receiver/Saltline-Receiver-2-Hours-4K-v1.mp4).

7,200 seconds, 3840x2160, 30 fps, H.264 with stereo 48 kHz AAC at 192 kb/s. The verified v7 sixty-second scene repeats 120 times. Native artwork is 1672x941 upscaled. The two-hour Red World Basin soundtrack includes its approved twelve-second joins and existing opening/closing fades. Colony adds no gain, crossfade, fades or overlay; its default peak limiter is below its trigger for the supplied soundtrack.

## Preserving the source

The runner seeds Colony's existing Prepared cache with a byte-identical master, following the established Floodplain workaround for the app scaler's colour changes. Colony performs its normal long assembly, audio encoding, progress, output protection and full decode. There is no scene re-encode or application modification.

All 1,800 decoded YUV frames of the first assembled minute exactly match the source. All 216,000 video packets have sequential presentation/decode timestamps; every one of the 120 repeated payloads is identical. The original v7 encoded seam checks therefore remain applicable. MP4 concat may add parameter-set headers, so repeated packet hashes are compared with the first assembled minute after its decoded pictures are verified against the master.

## Checks and review

Colony fully decoded the video/audio with fatal-error checking. Stream type, duration, size and frame rate checks passed. See [Colony manifest](colony-export.json) and [delivery validation](delivery-validation.json) for settings, hashes and results. Opening, middle and ending stills are inspected separately; this is not continuous playback or full musical listening. User acceptance covers the v5 look and short music transition, not full combined playback or v7 scheduling.

The runner refuses existing destinations. Use a new version for a new render; --verify-only resumes checks on this export. The master, source music and prior exports are preserved. Finished video/audio and cached media remain local ignored exports, not Git-backed. New session records are saved locally; no commit or push performed.
