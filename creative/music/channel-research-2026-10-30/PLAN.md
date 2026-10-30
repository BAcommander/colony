# Channel recovery plan — four weeks from 2026-10-30

Companion to [the research note](README.md). Dates are proposals; move them, but keep the order, because each gate decides the next step. "User" tasks need the YouTube account or ElevenLabs credits; "Assistant" tasks run locally. Nothing in this plan spends credits, uploads, retitles or commits without an explicit request at that moment.

## Principles

1. Change one variable at a time on the back catalogue, and keep Ringfall and Basalt as untouched controls until the end of November.
2. Judge any upload or change at 7 and 28 days, never at day one.
3. Discovery fixes (titles, thumbnails, metadata) are reversible and cheap; do them first. Sound fixes are the lasting ones; do them through the November lineup.
4. Record every change with its date so the weekly numbers can be read against it.

## Week 0 — this weekend, 2026-10-31 to 11-01: measure and tidy

| # | Task | Owner | Output |
| --- | --- | --- | --- |
| 0.1 | Export YouTube Studio analytics: Advanced mode, per video, lifetime: impressions, impressions click-through rate, views, average view duration, average percentage viewed, traffic source types (Browse, Search, Suggested, External), subscribers gained. Also the audience-retention curve screenshot for Ringfall and for Shoreless. | User | CSV and screenshots saved to `studio-export-2026-10-31/` in this folder |
| 0.2 | Set the "AI use" attribute (altered or synthetic content) to Yes on all eleven videos. Required by policy; does not limit reach. | User | Note in change log |
| 0.3 | Change category from Film & Animation to Music on all eleven videos. | User | Note in change log |
| 0.4 | Build `scripts/snapshot_channel_views.py`: pulls public view/like counts for both channels with yt-dlp into a dated JSON, so views-per-day can be tracked weekly without Studio. | Assistant | Script, first snapshot, weekly routine |
| 0.5 | Start `change-log.md` in this folder: date, video, what changed, by whom. | Assistant | File |

**Gate A (after 0.1):** read the Studio numbers.
- Impressions CTR under about 3% on most videos: thumbnails and titles are the first problem; Weeks 1–2 proceed as written.
- CTR fine but average view duration under about three minutes, or a retention cliff inside the first 30 seconds: move the opening and the sound ahead; shorten or quieten the 22-second intro on the next upload and prioritise Week 3.
- Impressions near zero regardless of CTR: the channel is not being tested at all; the continuous stream (Week 4) and the retitle (Week 2) move up, and we stop uploading on a three-day cadence.

## Week 1 — 2026-11-02 to 11-08: thumbnail test and title drafts

| # | Task | Owner | Output |
| --- | --- | --- | --- |
| 1.1 | Produce three thumbnail variants for one mid-catalogue video (Shoreless Colony, the lowest views-per-day with a strong scene): A current branded; B same art, one short title only ("SHORELESS"), no channel block, subtitle or number; C scene only. Same crop and brightness. Rendered locally with the bundled Barlow Condensed fonts; preview at 240 px wide. | Assistant | Three JPEGs under 2 MB plus a side-by-side preview sheet |
| 1.2 | Run Test & compare on that video with A/B/C, if the Studio account offers it. Hold the title steady during the test. If the feature is not offered, replace the thumbnail with B on Shoreless only and let the weekly snapshot judge it against the untouched neighbours. | User | Test started, date logged |
| 1.3 | Draft new titles and descriptions for all eleven videos in `retitle-drafts-v1.md`: scene name, narrative or sound hook, runtime, 4K; description keeps the second-person opening, adds one line stating what the sound contains, runtime, the AI line and the sign-off. Nothing applied yet. | Assistant | Draft file for review |
| 1.4 | Review the drafts and mark the three to apply first. | User | Marked file |

Traffic is low, so a native test may not reach a result in a week. Leave it running; do not restart it.

## Week 2 — 2026-11-09 to 11-15: retitle three, prepare the first pilot

| # | Task | Owner | Output |
| --- | --- | --- | --- |
| 2.1 | Apply the approved title and description to three mid-catalogue videos only (proposed: Saltline Receiver, Icebound Weather Post, Last Cable Station). Leave Ringfall, Basalt, the thumbnail-test video and the three newest untouched as controls. | User | Change log entries |
| 2.2 | Generate the Empty Junction pilots: two independent V3 two-minute runs from `final/11-empty-junction/music/elevenlabs-prompt-v3.txt`, and one "uneasy" variant (prepared by the assistant in 2.3) at the same length. Record the model shown and the cost shown. | User | Three exports in `final/11-empty-junction/music/` |
| 2.3 | Write the uneasy variant of the Empty Junction brief: same palette and roles, cooler mood, one unresolved low element, no horror effects. This is hypothesis 4 from the research note. | Assistant | `elevenlabs-prompt-v3-uneasy.txt` |
| 2.4 | Level-match all three pilots to −23 LUFS, build an unlabelled trial page as on 2026-10-30, and run the analyser on each export. | Assistant | Trial page, measurements |
| 2.5 | Rate the three pilots unlabelled; then listen to the preferred one for 30–60 minutes while working. | User | Ratings, notes |

**Gate B (after 2.5):** the preferred pilot becomes the Empty Junction reference. If none is comfortable, revise the brief once before generating again; do not reroll the same text.

## Week 3 — 2026-11-16 to 11-22: long source, ambience, assembly

| # | Task | Owner | Output |
| --- | --- | --- | --- |
| 3.1 | Generate the eight-minute Empty Junction source from the preferred pilot using the long brief and the owned reference. | User | Long export |
| 3.2 | Generate or select the separate ambience source from `ambience-prompt-v3.txt` (exterior wind around the signal cabin). | User | Ambience file |
| 3.3 | Produce the one-hour soundtrack two ways at matched loudness: music only, and music plus ambience on an independent on/off period that does not divide the music repeat interval. Audition the join and three repeats. | Assistant | Two hour-long candidates, join review, validation record |
| 3.4 | Listen to the preferred candidate for a full work session. | User | Verdict |
| 3.5 | Finish the Empty Junction animation from the v3 checkpoint only if the sound passes; otherwise hold the video and keep improving sound. | Assistant | 4K master, Colony assembly |
| 3.6 | Prepare the Empty Junction thumbnail in the style the Week 1 test favours (or B if the test is inconclusive), and the retitled-style title and description. | Assistant | Upload pack |

**Gate C (end of Week 3):** compare views-per-day for the three retitled videos against their own prior 14 days and against the untouched controls. A clear lift on all three: retitle the rest except the two controls. No lift: keep the new titles anyway for policy reasons, and treat discovery as not the main constraint.

## Week 4 — 2026-11-23 to 11-29: publish, stream, review

| # | Task | Owner | Output |
| --- | --- | --- | --- |
| 4.1 | Upload The Empty Junction with the AI attribute set, Music category, chapters if the hour has distinct passages. Log the date. | User | Live video |
| 4.2 | Continuous stream test: a 24-hour stream of three existing exports (Ringfall, Rainline, Shoreless) with the intro played once at the start, outside the loop. Assistant prepares an FFmpeg playlist streamer and a dry run to a local file; user supplies the stream key and starts it. | Assistant then user | Streamer script, dry-run record, stream date |
| 4.3 | Monthly review against the Week 0 numbers: impressions, CTR, average view duration, subscribers, and the weekly public snapshots. Write the outcome into the research note's status. | Assistant with user data | Updated README status |
| 4.4 | Decide the December lineup: Deepwell, Snowline and Crater Rim with whatever the Empty Junction cycle taught; a Ringfall or Basalt sequel only if the November numbers justify a series test. | User | Decision logged |

## Cadence during the plan

No new uploads until The Empty Junction, so the back-catalogue changes can be read without new-upload noise. After that, one release per week at most, each judged at 7 and 28 days.

## What the assistant can start immediately without account access

0.4 snapshot script, 0.5 change log, 1.1 thumbnail variants, 1.3 title and description drafts, 2.3 uneasy brief, and the Week 4 streamer dry run. Everything else needs the Studio export, credits or a decision from the user at the marked gate.

## Not in this plan

New artwork, paid tools beyond the existing ElevenLabs credits, changes to the approved Ringfall identity on the two control videos, or any claim that a step worked before the numbers say so.
