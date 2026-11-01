# Junction and Deepwell — lessons to review before the next prompt

2026-11-01. User requests preserving learnings so existing prompts can be reviewed, and a reusable SFX library. This is a living review checkpoint, not proof that a new prompt recipe performs better.

[Reusable SFX library](../sfx-library/index.html) · [Deepwell audio measurements](../deepwell-production-2026-11-01/review-against-learnings/REPORT.md) · [Deepwell thumbnail candidates](../deepwell-thumbnail-v2/README.md) · [Review queue](review-queue.json)

## What we actually learned

| Evidence | Lesson | Prompt or workflow consequence |
|---|---|---|
| User preferred Rainline/Shoreless/WINTER WATCH at4/5; Spirewatch3/5 felt too fast, despite coarse spectral resemblance. | Preference and perceived pace outrank matching reference statistics. | Keep slow internal colour/voicing/depth changes. Do not impose reference band percentages, stereo correlation or a compulsory drone. |
| Waterworks: sub80Hz0.0049%,250Hz–1kHz73.3%,correlation0.744. Sheltered: sub80Hz0.0063%,80–250Hz43.0%,correlation0.525. | The new dry sources have very little sub-bass; they are not repeating Ringfall’s sub-heavy profile. | No automatic bass cut, treble boost or widening. Those would be listening experiments, not demonstrated improvements. |
| Sheltered LRA9.8LU over the full4min but3.2LU over20–180s; Waterworks4.7/4.4LU. | Generated fades can inflate a dynamics diagnosis. | Analyse complete sources and an interior window. Judge musical pace by listening, not LRA. |
| Actual supplied music files were4min each; prepared V3 briefs said120s. Exact generation wording/settings are unverified. | A prepared prompt is not proof of actual generation settings or a successful prompt experiment. | Keep duration in a separate settings note; record the real export length/model/cost/prompt when observed. Review drafts remove the120-second prose only. |
| Strong ending fades still occurred; Deepwell assembly uses measured trims and20/28s overlaps. | “No fade” in a prompt is a request, not a guarantee. | Preserve the open-ended musical request, then inspect and audition joins. Do not solve this by piling on exclusions. |
| Wind was missed in the mix; user requested+3dB. Water needed10% less amplitude; grit needed repeated reductions. | Audibility and restraint are contextual. Very quiet is not automatically useful ambience. | Audition effects in composition, including quiet music and the loudest effect plateau. Change one balance variable at a time. |
| Eight-second fade was mistaken for the wind’s event length; events were60s. | Source length, loop period, event duration and fade are different quantities. | Record each separately. Do not put a minute-long narrative into a short SFX prompt. |
| User wanted no voices; radio/static and a compressor direction did not work for Junction; train and quieter grit did. Pump worked in Deepwell. | Source identity and scene fit matter more than adding generic variety. | Reuse suitable accepted sources first. A source rejected in one location does not ban all machinery everywhere. |
| User requested Junction effects about25% more often. | More frequent does not mean louder or faster. | Adjust event count/spacing separately; record whole-event rounding. Preserve accepted source gains. |
| Deepwell dry arrangement repeats every388s after its entrance; SFX timing varies separately. | Independent timing varies the combined texture without erasing recognizable musical recurrence. | Avoid claiming a non-repeating hour. Use a30–60min work-session listen to judge fatigue. |
| Junction user requested scene-only/one-word options and stronger composition. Deepwell now has matching candidates. No concurrent CTR result exists. | Scene readability is a design hypothesis; it is not a proven performance lift. | Test sparse text at phone size. Keep title/scene/brightness fixed when isolating typography; generative variants are package comparisons. |
| Old Deepwell thumbnail omitted the planet now in the final video. | Packaging can drift behind production. | Start a thumbnail revision from the current clean final-scene plate and preserve important location cues. Never use text-bearing marketing art as the animation source. |

## What to keep from existing V3 music prompts

Keep four different scene identities, rounded attacks, slow unequal changes, restrained detail, free-time musical direction and separate environmental SFX. The accepted Deepwell export is not a reason to make every scene sound like Deepwell. The original generated prompt/settings remain unconfirmed, so these samples cannot prove V3 beat V2.

The four `review-drafts/*-music-v4-review.txt` files preserve each V3 musical description and remove only the duration from its first sentence. They are review drafts, not promoted production prompts or a request to regenerate accepted music. Current canonical V3 files are preserved byte-for-byte and hashed in review-queue.json. Review the existing long-version briefs separately before the next actual generation; set duration deliberately rather than inheriting their old eight-minute proposal.

## Short SFX briefs

Use one recognisable source, the listener’s viewpoint/distance, one evolving action and one or two material qualities. Put duration/variant count in the generation settings, then inspect the actual file. Keep the result useful in the mix rather than layering “barely audible” instructions until it has nothing to add. A saved related brief is not necessarily the exact prompt that produced a supplied MP3.

[Short SFX template](sfx-brief-template.txt). The library keeps source measurements, actual files, contextual gains/fades/schedules, related briefs and rejected approaches. Library listening previews are gain-adjusted for browsing; mix from the untouched originals.

## Thumbnail review

Use the current clean scene with its existing planet. Let the location, atmosphere and useful working light carry most of the image. Candidate copy is either absent or one short word; remove header, number, tiny slogan and decorative rules for this test. Inspect at320×180 or smaller. Preserve the earlier branded version as a control and do not declare the new version approved until selected.

Generative lettering edits can alter texture, lighting and geometry despite preservation instructions. Store the exact prompt, references and output hashes, inspect the actual result, and label the comparison honestly. If typography must be the only variable, use a deterministic overlay on an identical approved plate as a separately authorized production method.

## Next decisions

Select a Deepwell thumbnail candidate; gather a longer listening verdict when convenient; review the next scene’s existing brief and check the SFX library before generating another sound. None of these creates an upload, spend, automation, prompt promotion or Git backup. Future performance claims need Studio evidence or a concurrent test, not appearance alone.
