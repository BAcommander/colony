# Spirewatch — final two-hour 4K video

Upload packaging prepared 2026-10-27: [title, description, Studio tags and unchanged thumbnail copies](../spirewatch-upload-v1/README.txt). User requested its commit/push and durable lessons; see [backup scope](../spirewatch-upload-backup-2026-10-27/README.txt) and the subsequent local remote-backup-verification.json for actual backup evidence. No YouTube upload has been performed.

Delivered 2026-10-26 through the actual Colony export engine, with the current once-only v3 intro and the user-approved Horizon/Stillness transitions.

[Open final video](G:/AI/colony/exports/spirewatch/Spirewatch-2-Hours-4K-v1.mp4)

Exact runtime 2:00:00; 3840×2160, 30 fps, 216,000 frames. H.264 YUV420p BT.709 with stereo 48 kHz AAC at 192 kb/s. Size 72,432,193,092 bytes. Native artwork detail remains 1672×941, previously Lanczos upscaled in the verified clean master. SHA-256: `027bf487ded435b6899db004e589bf0f6b3432693a2a13f930a1c3aec96a7705`.

Opening: AMBIENT COLONY with orbital logo, closer PRESENTS, SPIREWATCH, then the lower “Stay a while and listen”. The current timings, 88% initial darkening and 22-second graphics budget are retained. Sound is silent until 0:05 and rises gently to the approved level at 0:20. Runtime and animation phase are unchanged. No repeated intro or extra subscribe overlay/SFX.

Soundtrack: the existing two-hour FLAC supplied once, gain0, no loudness matching or new playlist joins. Complete original Horizon and long Stillness alternate with the accepted eight-second overlaps, original -7.74/-7.08 dB source gains, and one existing twenty-second closing fade. Source pitch/tempo remain unchanged. The user approved both short transition auditions and requested the final duration; full combined playback review remains pending.

The installed local Colony copy predates the saved intro release. The saved v3 renderer/fonts were checked against their recorded SHA-256 and used via the package search path with recorded local exporter/SFX dependencies. No installed source or executable was changed. The first setup stopped before encoding because sparse source colour fields were passed directly; built-in colour completion fixes this, with the initial attempt preserved in history. The exact verified clean sixty-second loop is reused through Colony Prepared. The opening minute is rendered losslessly with job-local CRF0/veryfast settings; all pixels after22s match the source. Later119 clean minutes remain copied, with identical packet sequences and exact decoded source controls.

Validation: complete Colony video/audio decode without error; all216000 video timestamps and packet sequences checked; all1800 frames of the first clean minute equal the master; first-minute frames after22s equal the master. Every AAC sample over7200 seconds is finite/unclipped and compared with the expected full FLAC passed through Colony's actual intro/limiter graph. Levels, silence, fade and source hashes passed. See assembly-settings.json, colony-export.json, video-validation.json, audio-validation.json and delivery-validation.json. Assistant inspected final decoded opening/scene temporal stills, not continuous playback or full listening.

Sources, clean masters, older attempts and standalone soundtrack are preserved. The final file/cache are local under ignored exports/spirewatch; Git backup does not cover them. No new generation, paid service, upload, commit or push. Reproduction: assemble_with_colony.py, verify_final.py, then record_delivery.py after visual inspection. Scripts preserve existing output. The retained rendering cache is not needed to play the final MP4.
