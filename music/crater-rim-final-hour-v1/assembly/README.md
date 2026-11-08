# Crater Rim final-hour assembly

This portable package freezes the actual Colony v3 intro renderer, its fonts and the required exporter dependencies. No installed application changes are needed. `engine-manifest.json` fingerprints every frozen file. `requirements.txt` records the working Python package versions; FFmpeg and FFprobe must be on PATH.

The input is the verified `exports/14-crater-rim-survey/production-v1/Crater-Rim-Survey-clean-600s-4K.mp4`: silent H.264, 3840×2160, 30fps, 18,000 frames, YUV420p BT.709/TV, no B-frames, and a closed keyframe at 60 seconds. Production uses QP0/veryfast, GOP60, minimum key interval60 and scene-cut0. The source should retain its 600-second attention cycle over the validated weather motion.

Before assembly, `visual/master-validation.json` must contain `status: passed`, the absolute master `output`, its `sha256`, `seconds: 600`, `dimensions: [3840,2160]` and `fps: 30`. Optional `full_4K_decode: true` and `raw_frame_hashes` (the full 18,000-frame FFmpeg SHA256 framehash path) let final verification reuse the completed source decode. A relative hash path resolves from that validation file's directory. Decoded-picture checks use `-fps_mode passthrough`; cached hashes must explicitly identify SHA256 and contain64-character digests.

A600s decoded-picture check runs five120s closed-GOP chunks concurrently, with two FFmpeg decoder/output threads each. Every chunk must decode all3600 frames with exact local timestamps; the combined evidence retains all18,000 SHA256 digests in time order with continuous timestamps. The first60s opening remains one decode chunk. This changes verification throughput only.

The approved 3600-second music-and-SFX FLAC is fixed by SHA-256 `333c0fe1b94ac899d0fa6a91ed009c693de312c791913a838662bf7433b5c994`. It receives unity gain and the actual Colony entrance once: silence through five seconds, then half-sine fade to twenty seconds. Its existing twenty-second closing fade remains intact. There is no additional SFX, normalization, crossfade or closing fade during this assembly. Colony's standard limiter remains below threshold; independent verification compares the final AAC to the approved source plus only the entrance envelope.

Only the first sixty seconds are encoded for the opening. Two source parts are copied at the 60-second keyframe and every copied packet is checked against the original master. A local playlist adapter runs Colony's unchanged opening function on the first minute, appends the untouched remaining540s, then repeats the complete master. The full hour contains six600s cycles and one opening; the final filename is `exports/14-crater-rim-survey/Crater-Rim-Survey-1-Hour-4K-v1.mp4`.

From this folder, with the chosen interpreter and dependencies:

```powershell
python assemble.py --preflight-only
python assemble.py
python verify_final.py --video --audio --stills --hash --review --finish
```

`--master` and `--master-validation` can override input locations. Final output is never overwritten. The assembly itself performs a complete actual-Colony audio/video decode. Independent validation checks every108,000 packet timestamp/duration, every copied picture payload after the first60s, all decoded pictures in a complete clean600s unit, opening clearance from22s, all172,800,000 stereo AAC sample frames, each minute's gain/correlation, and the final file fingerprint. Stills are prepared for inspection without claiming continuous playback/listening. `--finish` requires the decode and independent evidence to pass against the same output size/mtime and unchanged inputs.

Regenerable source splits, opening encode and processing caches live under repository `.local/crater-rim-final-hour-v1/assembly/`. Compact validation and frame/packet evidence remain alongside the scripts. `--review` makes the actual final's first135s as a720p MP4 with its sound and verifies the whole excerpt and AAC against that final; no new graphics or fades are added. Actual output, user review, upload and backup status must come from the completed records; the presence of this tooling does not imply a finished render.
