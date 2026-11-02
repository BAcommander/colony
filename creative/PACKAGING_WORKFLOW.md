# Thumbnail and title workflow

Current working guidance: 2026-11-02. Read alongside the [learning guide](LEARNINGS.md), [historical approved thumbnail identity](../final/THUMBNAIL_STYLE.md) and the [dated feed review and evidence](packaging/2026-11-02-feed-review/README.md). These are design and measurement practices; no new thumbnail has demonstrated a CTR improvement yet.

## Design the invitation

For each future video, write one sentence explaining why someone would want to spend time there: warm shelter during a storm, a quiet wait for a train, isolation on an immense world, or another scene-specific experience. Make that invitation legible in the image and the opening words of the title.

- Choose one dominant visual subject. Use scale, framing, light and negative space to make it readable before small equipment, architecture or lettering. Keep a clear alien environmental cue.
- Check the actual feed-sized image, roughly 160–240 pixels wide, as well as the full master. Record whether the subject, atmosphere and alien setting still read; this size range is a practical preview convention, not a measured performance threshold.
- Give the inviting part of the scene enough image area: a warm dome, inhabited room or lit platform can become the focus instead of a small detail beneath a large destination label.
- Treat no text, sparse text and the established branded layout as alternatives to review. Earlier visual approval of the branded style is not evidence that it maximizes clicks. Junction already uses lighter text, so removing words alone is an unproven fix.
- Retain coherent colour and local contrast. Muted palettes can support clear silhouettes and atmosphere. Global saturation, brightness and desaturation are separate variables, not default repairs.
- Use titles that communicate an accurate situation or experience early. Original destination names and series branding can support that promise. Familiar IP associations in competing thumbnails are a recognition hypothesis, not a demonstrated cause of their view counts.
- Keep scene identity, materials and geometry consistent with the actual video. An alternative crop or generated image must not promise an event or feature absent from the release. Review any geometry/lighting drift and retain the clean source separately.

Proposed Junction title example, not applied: **Waiting for the Next Train on an Alien World | Sci-Fi Ambience**. The existing waiting-for-the-next-train wording already provides an experiential hook. Do not invent a last train, danger or urgency to make a title stronger.

## Review and test

1. Identify the current published artwork/thumbnail/title and source hashes. Later production branches may hold newer plates than the local preparation folder. Preserve the current asset and its approval history.
2. State the hypothesis before making alternatives. Example: enlarging Rainline's warm room may make the invitation clearer at phone size. A crop/composition/text change tests the whole thumbnail presentation; it cannot isolate typography as the cause.
3. For the proposed Rainline pilot, retain A=current thumbnail, make B=warm-room-led with the rainy exterior still legible, and C=rainy-colony-led. B/C are proposed text-free compositions. Hold the title fixed. No alternatives have been generated, selected or uploaded by the November 2 review.
4. Use YouTube Studio's concurrent thumbnail-only A/B test if available. Its current documentation supports up to three variants and evaluates watch-time share. Keep the title fixed for this question; changing an active test's title/thumbnail stops the test. Low traffic can leave it inconclusive. See the [official testing guide](https://support.google.com/youtube/answer/16391400?hl=en).
5. Record video ID/URL, upload age, test dates, exact assets/hashes, title, impressions and CTR by available traffic source, views, watch time, average view duration and the retention curve. Capture at comparable ages/windows; do not infer impressions by dividing all views by CTR.
6. Let the experiment reach its reported conclusion; YouTube says tests can take days to two weeks. Save the actual watch-time-share result, winner/performed-same/inconclusive status and any available uncertainty. A manual before/after swap remains observational because the audience and traffic mix can change.
7. Compare acquisition and listening separately. A low CTR does not identify a music problem; a long average duration from a few views does not establish all-day comfort. Inspect the first 30–60 seconds as well as longer-session behaviour.
8. Update the dated record and relevant scene metadata with the result. Carry a winning approach into another scene as a new test, retain rejected variants, and avoid declaring a universal channel rule from one result.

## Evidence discipline

Public competitor view counts combine age, reach, audience, familiarity and many other factors; they are not thumbnail CTR data. The user's feed is one personalized comparison, not a sample of all audience impressions. Early channel analytics are signals to investigate rather than a causal diagnosis. Use [YouTube's CTR guidance](https://support.google.com/youtube/answer/7628154?hl=en), [impressions definitions](https://support.google.com/youtube/answer/9314486) and [thumbnail/title guidance](https://support.google.com/youtube/answer/12340300?hl=en) when interpreting results; these support the measurement method, not a guarantee for a particular design.

Store the exact screenshot/export, its date and hash, distinguish visible facts from visual judgments and hypotheses, and leave missing metrics unknown. The next data needed for the November 2 review are impressions, CTR by Browse/Suggested/Search where available, and the retention curve over a longer comparable window. No public assets, titles, uploads or active tests are changed by saving this workflow.

Copy [the test-record template](packaging/test-record-template.json) into the next dated scene/test folder. Fill only observed fields; null means unknown, and a reported inconclusive result is a result worth retaining.
