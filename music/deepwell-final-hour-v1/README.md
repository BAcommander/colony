# Deepwell Station — one-hour 4K video

[Play final video](../../exports/12-deepwell-station/Deepwell-Station-1-Hour-4K-v1.mp4) (16.64 GB). Exact 3600 seconds, 3840×2160, 30 fps, 108000 frames; H.264 BT.709 TV with stereo 48 kHz AAC. SHA-256: 2ded2931f60db759cdbd0f563e2663cd3262f4364d751e769caa92d0b15f283f.

User direction: “ok i think it's decent shall we make the full version?”. This selects V4 for production following the accepted one-hour soundtrack. Full combined user review remains pending.

V4 source files and masks are frozen in source-snapshot/, checked against their earlier fingerprints and sampled decoded preview pictures. The same scene renders at native 1672×941 then directly scales with Lanczos to 4K. Five source-to-4K YUV control frames are exact. Complete 20-second and three-repeat 60-second masters decode with exact repeated pictures and sequential timestamps; inherited V4 seam checks remain applicable to unchanged motion. Earlier artwork, thumbnail and animation versions are preserved.

The accepted one-hour FLAC supplies both alternating music tracks and all water, wind and pump effects at unity gain. There is no new normalization, EQ, extra SFX or music join change. The existing twenty-second closing fade remains. Actual Colony v3 opening appears once: AMBIENT COLONY, PRESENTS, Deepwell Station, Stay a while and listen. Graphics clear by22 seconds, audio silence to5 then fade to20. Later59 minute units copy clean master packets.

The verified preserved Colony implementation is used because the installed app predates the opening. A job-local encoder argument wrapper completes H.264 colour metadata; no installed source changes. See assembly-settings.json and colony-export.json.

All final video/audio frames decode; every video timestamp and59 copied minute packet sequences pass. The clean minute matches the master in decoded YUV and all opening pictures after22 seconds are unchanged. Complete AAC audio matches the accepted FLAC through the actual opening graph within lossy encoding tolerance; finite and unclipped. See delivery-validation.json, video-validation.json and audio-validation.json. Assistant inspected decoded opening stills in opening-contact-sheet.jpg, not continuous playback or full-hour listening.

Reproduction: produce_master.py → assemble_with_colony.py → verify_final.py → record_delivery.cjs. Source records and production settings retained; long exports and regenerable master/cache files remain local. No paid generation, publication, commit or push.
