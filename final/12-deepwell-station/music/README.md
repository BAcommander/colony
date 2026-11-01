# 12 — Deepwell Station soundtrack preparation

Deepwell combined music/SFX review (2026-11-01): user now explicitly selects both Waterworks Gallery and Sheltered Replenishment for use like Junction and requests combining earlier water and wind. Existing Shoreless source Clear_ocean_water_re_#1-1791650516724.mp3 and Junction Soft_wind_moving_thr_#4-1793463971195.mp3 found and hash-verified. Eight-minute A/B/A review, dry full music, separate SFX stem, two-minute effect check and both ninety-second dry joins are in music/deepwell-production-2026-11-01/combined-review-v1/. Music gains −8.35/−6.80 dB retained; A-to-B 3:24–3:44 (20s), B-to-A 6:32–7:00 (28s), cuts/overlaps based on measured generated fade tails. Water source gain −12.9 dB (nominal −40 LUFS), wind +1.85 dB (nominal −41 LUFS, 6dB below Junction), independent events and 26s/24s source periods. Exterior sounds auditioned quietly from gallery; water is not a new pump recording. All files fully decoded and compared with recipe; finite/unclipped and loop-boundary checks passed. Listening/join/balance review pending; no assistant listening verdict. Both-use authorization supersedes earlier keep-as-candidates decision; it does not approve this new mix. No full-hour export, artwork change, paid generation, commit/push or publication.


Deepwell music samples received (2026-11-01): user supplies Waterworks_Gallery_2026-11-01T171541.mp4 and Sheltered_Replenishment_2026-11-01T171541.mp4. Both decode to exactly 240 seconds, stereo 48kHz. Originals copied and SHA-256 verified in music/deepwell-production-2026-11-01/sources/. Source integrated loudness −14.65/−16.20 LUFS; fixed −8.35/−6.80 dB gains make approximately −23 LUFS full-length audition MP3s under review/. All samples decoded, finite/unclipped audition and full gain-reference comparison passed. No EQ, compression, extra fades, SFX, joins, stretching or new generation. Actual prompt/model/cost unverified. Music choice/approval pending; no assistant listening verdict. Earlier proposed 120-second test is superseded by actual supplied 240-second durations, not evidence of incorrect files. V4 visuals and original thumbnail unchanged.


V3 prepared 2026-10-30 after ambient-practice research and the user's listening ratings, for the confirmed November lineup. Proposed musical direction only; no V3 audio generated, evaluated or approved. V1/V2 from 2026-09-29 remain history. [Research and month pack](../../../creative/music/november-2026/README.md).

Read [the shared music workflow](../../../creative/MUSIC_WORKFLOW.md). The user runs any ElevenLabs generations manually after checking the actual displayed cost and available controls. Do not use a paid API or plugin.

1. Use elevenlabs-prompt-v3.txt in the Music description field, not lyrics. Choose instrumental output and aim for 120 seconds/two variants if supported.
2. Listen at comfortable matched volume and choose a test; revise the specific defect if neither works.
3. Use the selected own test as an audio reference, if the current interface offers it, with elevenlabs-long-version-v3.txt; aim for about eight minutes/one variant. A reference guides feel and palette, not exact continuation.
4. Save original exports and fill generation-record.json with actual settings, cost shown, filenames, durations and feedback.
5. Inspect the supplied export locally for duration, fades, levels and candidate loop points; make a short join audition. Choose overlap from the actual piece rather than assuming Ringfall's 15 seconds fits.
6. Assemble a long version only after listening approval and a chosen duration. Large repeats live under ignored exports/ with reproduction records; they are not backed up merely because prompts are in Git.

## Current V3 listening check

Clear and replenishing with no felt-piano sequence; water can add presence without dominating quiet music. Compare the same dry musical bed with and without the proposed ambience at matched loudness. Source viewpoint and SFX balance remain proposals.

### Previous V2 question, retained for history

Do the overlapping voices move at different times? Is the reflective upper layer soft rather than tinkly, and does the piece avoid literal water effects or a pumping rhythm?

Also check for unwanted vocals, percussion, abrupt level changes, uncomfortable sub-bass, thin midrange and poor mono translation. Keep scene sound effects separate from the music pass. Do not impose a fixed named key or a compulsory drone note.

The publication copy is a draft. Add accurate soundtrack wording and runtime once known; do not claim human composition or no AI music for generated audio.

## Prompt versions

Current: `elevenlabs-prompt-v3.txt` and `elevenlabs-long-version-v3.txt` (2026-10-30), with separate `ambience-prompt-v3.txt`. Read the November research and V3 workflow. V2 files from 2026-09-29 are preserved untested history. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. None of these scene prompt versions has been generated or heard.

Notes kept out of the prompt text on purpose:

- Attach a short excerpt of your selected own dry test as reference, following the actual UI limit, before running the long prompt. A reference guides feel and palette, not exact continuation.
- The long prompt says "about eight minutes". If the actual supported/chosen duration differs, edit that number before pasting.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
