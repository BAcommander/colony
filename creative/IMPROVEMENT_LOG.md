# Ambient Colony improvement log

**Rule (user instruction, 2026-11-11):** every new video must try to improve on the last in its video, its thumbnail and title, and its music and sound. Each release names what it is trying, how the result will be measured, and what happened. Nothing is "improved" until the numbers or the user's own listening and viewing say so.

This is the one place to see what we are testing and what we have learned from it. Detailed evidence stays in the linked records; reusable conclusions also go into [LEARNINGS.md](LEARNINGS.md).

## How to use it

1. **Before starting a video:** take a fresh Studio snapshot (same tables as the [11 November snapshot](music/channel-research-2026-10-30/studio-export-2026-11-11/README.md)), fill in the results column for earlier videos that have reached 14 and 28 days, and read the open findings below.
2. **When planning the video:** add a row saying what this video changes in each of the three areas and which number or review will judge it. Change as few things at once as is practical, so a result can be read.
3. **Before assembly:** run [scripts/compare_texture_pace.py](../scripts/compare_texture_pace.py) on the final mix and record the figures beside the reference ranges.
4. **After release:** record the 2-day, 14-day and 28-day figures. Keep losing experiments in the table.

## Baseline, 11 November 2026

From the [Studio snapshot](music/channel-research-2026-10-30/studio-export-2026-11-11/README.md), lifetime 23 Sep – 10 Nov: 2,188 views, 820.9 watch hours, 29:36 average view duration, 26,808 impressions, 3.1% click-through, 23 subscribers. 92% of the monthly audience is new; none is regular.

## Open findings

| Finding | Evidence | Status |
| --- | --- | --- |
| Viewers watch about a third of any length, so longer videos earn more watch time per click. | One-hour videos average 11–23 min, two-hour 36–43 min, the four-hour 56 min. | Observed across 14 videos; confounded by age and topic. |
| Click-through is the weakest number, and lower on the four uploads with scene-specific titles (1.4–2.4%) than on most earlier ones (3.0–4.6%). | Studio snapshot. | Not a clean test: age and traffic mix differ. |
| Playlists and the channel page give the longest sessions (1:04:14 and 50:17) and click-through above 7%. | Studio snapshot; 107 and 193 views. | Small counts. |
| Both long-session reference streams carry a constant noise-like weather bed, very few stand-out moments, flat long-term level and quiet loudness. Our tracks are mostly sustained tone with intermittent effects. | [SIGNAL STATION analysis](music/reference-analysis/signal-station-2026-11-11/README.md). | Hypothesis for long-session comfort; untested in our own mixes. |
| Rainline's intermittent, quiet rain did not hold viewers (19.0% viewed, second lowest). | Studio snapshot. | Does not test a constant bed. |
| Choosing music from a one-minute sample on its own, then looping one 6–8 minute piece, rewards a quick hook and repeats the music 9–18 times per video. | Pipeline review, 2026-11-11. | Judgment, not measured. |

## Standing plan for each new video

1. Two hours or longer.
2. Build a continuous environment bed first, from sources with unequal loop lengths, that never switches off.
3. Audition music candidates under that bed at final level, during other work, before choosing.
4. Generate more than one long piece and alternate them so the music repeats less often.
5. Check the final mix against the reference ranges before assembly.
6. Name the ambience and the runtime in the title, and run a native thumbnail test.

Reference ranges from the two streams (SIGNAL STATION / WINTER WATCH): noise-like share 31% / 29%; 2–8 kHz band −18 / −21 dB relative to the mix, varying 2.9 / 7.6 dB second to second; 6 dB stand-out moments 2.4 / 1.5 per minute; 30-second level spread 1.9 / 3.1 dB; −25.7 / −22.6 LUFS. These are targets to test, not proven causes.

## Per-video experiments

| Video | Published | What it tries | Judged by | Result |
| --- | --- | --- | --- | --- |
| #13 Below the Snowline | 9 Nov 2026 | Two-hour runtime. Title names the ambience ("Hoth-Inspired Snowstorm Ambience"). Six separate effect layers with scheduled events. | Click-through, average view duration and % viewed at 14 and 28 days. | At 2 days: 47 views, 1.4% click-through, 42:21, 35.3% viewed. 14-day due 23 Nov. |
| #14 Crater Rim Survey | Planned 12 Nov 2026 | Short-title thumbnail V2 ("CRATER RIM"). Two alternating music pieces with a 526-second recurrence. One hour, built before the length finding. | Same figures; compare click-through with Junction and Deepwell. | Not yet published. |
| #15 Beneath a Crimson Sky | Planned 16 Nov 2026 | Full standing plan: continuous storm bed, music chosen under the bed, more than one long piece, measured mix, two hours or longer, ambience-led title, thumbnail test. | Mix figures against the reference ranges before assembly; user work-session listen; Studio figures at 14 and 28 days against #13 and #14. | In progress. |
