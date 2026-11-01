# The Empty Junction — more frequent SFX, final video v2

[Full one-hour 4K video v2](../../exports/11-empty-junction/The-Empty-Junction-1-Hour-4K-v2.mp4) (9.93 GB). [Six-minute audio check](Empty-Junction-more-frequent-SFX-check-6min.mp3). [Revised full-hour FLAC](../../exports/11-empty-junction/The-Empty-Junction-1-Hour-final-SFX-v4.flac).

User feedback: “i think the video is fine but we need to increase the 3 sfx to provide more variance, like they need to be 25% more frequent”. V6 visuals are accepted as fine. This revision changes frequency while keeping the selected music arrangement, source durations, gains and fades.

| Effect | Before | Now | Increase |
|---|---:|---:|---:|
| One-minute wind passages | 20 | 25 | 25% |
| 25-second distant trains | 7 | 9 | 28.6% |
| 12-second grit events | 19 | 24 | 26.3% |

Train and grit use the nearest whole-event count to 25% more. Wind quiet gaps vary between one and two minutes; exact starts are in mix-recipe.json. Trains stay within quiet wind intervals. Grit events occur within selected wind minutes, with occasional pairs and unused gusts to keep variation. Gains remain wind +7.85 dB, train +4.5 dB and grit −3.3 dB. Source playback speed is unchanged.

The previous SFX-only stem was reconstructed from the exact sources and verified across the entire hour. The approved V3 mix minus that verified stem supplies the existing music; new SFX replace the old schedule. This preserves the dry music within 24-bit/float quantization. The new full FLAC and separate SFX stem were completely decoded and compared against the deterministic render, with finite samples and no clipping. The separate stem must never be added to the already mixed FLAC/video. The six-minute MP3 is a mix audition before the video opening envelope.

Existing 4K wind/quiet masters are copied, with only the powder-active minutes rescheduled to follow the sound. Every other effect stays at its existing phase and treatment. The exact first minute of v1 supplies the approved Colony opening. H.264 colour tags are completed on copied units before assembly. The actual Colony renderer runs with a job-local playlist adapter, unity audio gain, no loudness matching, and its current once-only silence-to5/fade-to20 envelope. No installed app source is changed and no pictures are re-encoded.

Delivery is exactly 3600 seconds, 3840×2160, 30fps, 108000 frames, H.264 BT.709/TV with 48kHz stereo AAC. Native artwork remains 1672×941, previously Lanczos upscaled. Full video/audio decode passed. Every video timestamp and coded-picture payload matches the selected original unit; only SPS colour metadata is excluded from picture-payload hashes, retaining PPS, SEI and all coded picture slices. The full AAC track was compared against the revised FLAC through the actual opening graph. See delivery-validation.json, video-validation.json, final-audio-validation.json and the exact Colony record.

Final SHA-256: 2c65f3aa44b834f84bde50043c426b55a38c82ec8e89e61a4ae498910da08b29. The earlier v1 video, approved V3 mix and all sources remain unchanged. New schedule listening/user review is pending; no assistant listening or continuous playback is claimed. No publication, commit, push or new generation.

Reproduction order: revise_audio.py → assemble_revision.py → verify_revision.py --video / --audio / --finish. Source hashes, schedule and level preservation evidence are saved in this package. Existing source/mix files live at the explicit paths in the recipe. Cache and full media remain local under project policy.
