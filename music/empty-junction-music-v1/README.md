# The Empty Junction — first long-music and wind audition

Audio chosen, 2026-10-31: user accepts [final SFX mix V3](delivery-hour-final-sfx-v3/README.md) after the additional 1.5 dB grit reduction. Lock this current balance and move to visual/animation work; no more effects revisions unless requested. [Exact approval and scope](delivery-hour-final-sfx-v3/user-approval-2026-10-31.json). Earlier pending-listening notes are historical; no continuous full-hour listening or new visual acceptance is claimed.

Latest trial revision: [final SFX mix v3](delivery-hour-final-sfx-v3/README.md) lowers only grit by another 1.5 dB after the user says V2 is "much better" but requests a tiny bit more reduction. Source gain is now −3.3 dB, 7.5 dB below original V1. Other gains, schedules and fades are retained. [V2](delivery-hour-final-sfx-v2/README.md) and V1 remain available for comparison; V3 listening verdict is pending.

Current requested final combination: [one-hour music + wind + train + grit](delivery-hour-final-sfx-v1/README.md), with a separate SFX-only stem and three one-minute example sections at the actual mix levels. The user asks for these examples to check the balance; listening acceptance is pending. Earlier mixes and rejected effect directions remain preserved below as history.

New optional mix: [one-hour distant-train option](delivery-hour-train-option-v1/README.md) adds the supplied 25-second train sample seven times in wind-free gaps. The original one-hour music/wind delivery remains available as the baseline. A 90-second audition includes the first train at 0:30. Exact timings, gains and validation live in the option package. [Mineral-grit rustle](mineral-grit-sfx-prompt-v1.txt) is the proposed next optional source, not generated or mixed.

Latest SFX direction: user rejects the latest effect as insufficiently ambient and asks about a train or intermittent whistle. [Very distant train proposal](distant-train-sfx-prompt-v1.txt) supersedes the cabin-compressor and radio experiments as the next optional test: a diffuse off-screen passage beyond the mineral pass, with one low breathy whistle. [Exact feedback](feedback-distant-train-2026-10-31.json). No new SFX generated or added; the delivered one-hour mix remains as supplied.

Current delivery: [one-hour ambience v1](delivery-hour-v1/README.md), requested by the user with "ok we're not making progress, lets just get the 1 hour version of the ambience ready". Alternates the existing music with one minute of wind followed by two minutes off; radio experimentation ends here. Delivery records and actual verified paths live in that package. Earlier provisional feedback remains historical; the request authorizes the extension without implying complete one-hour listening approval.

Current revision: [7:30 intermittent-wind v2 preview](review/Empty-Junction-A-B-intermittent-wind-v2.mp3), with wind at 0:00–1:00, 3:00–4:00 and 6:00–7:00. Wind is absent at 1:00–3:00, 4:00–6:00 and 7:00–7:30. Five-second entrance and eight-second exit fades sit inside each active minute. Music arrangement/gains are retained from the existing dry FLAC. [V2 recipe](mix-recipe-v2.json), [V2 validation](validation-v2.json), [reproduction script](build-intermittent-wind-v2.cjs).

Current SFX proposal: [station equipment/radio v3](radio-station-prompt-v3.txt). User found v2 better but too static-focused and asks for beeps, chimes and more variety. V3 proposes coherent equipment activity with short acknowledgement beeps, relays, telemetry and status chimes; this is fictional sound direction, not a claim about documented railway equipment. No speech, new generation or assistant listening verdict. [Exact current feedback](feedback-wind-radio-revision-2026-10-31.json). Earlier wind previews, radio prompts and feedback remain history.

Latest feedback, 2026-10-31: user says the Junction preview "so far sounds good"; retain it as the current listening candidate, without inferring final approval. Radio v1 was too quiet and contributed too little. [Radio v2](radio-sounds-prompt-v2.txt) requests clear receiver activity for later placement/level adjustment; the no-voices preference remains. No new radio file was supplied or generated here. [Exact feedback and interpretation](feedback-2026-10-31.json).

2026-10-31. User supplied two four-minute music exports and a thirty-second wind sample, asking to combine them for review. Their earlier preference was Signal Cabin Drift over Freight Yard Waiting Room. This is not an approval of either new long export. They explicitly prefer radio equipment crackle rather than voices; the separate [radio prompt](radio-sounds-prompt-v1.txt) replaces the previous speech proposal.

## Earlier continuous-wind v1 comparisons

- [Music and quiet wind, 7:30](review/Empty-Junction-A-B-soft-wind-v1.mp3)
- [Same music without wind, 7:30](review/Empty-Junction-A-B-dry-v1.mp3)
- [One-minute music handover excerpt with wind](review/Empty-Junction-music-handover-60s-v1.mp3)

Matching 24-bit FLAC copies are in review/. The dry music has exactly the same gains and arrangement in both full versions, with no compensation for the small loudness addition from wind. The handover excerpt covers full-mix 3:12–4:12; the crossfade is at excerpt 0:20–0:32.

## Arrangement and scope

Signal Cabin Wait source 0:00–3:44 leads into Quiet Signal Cabin source 0:02–4:00, using a proposed twelve-second equal-power handover at output 3:32–3:44. The first track's long generated closing fade is excluded; the second track's two-second opening is excluded. The first opening and second ending remain as generated. The sources each have 240 seconds of audio, although their MP4 video streams extend to 244.4 seconds. Audio duration owns the assembly.

Fixed gains are −9.13 dB for Signal Cabin Wait, −9.76 dB for Quiet Signal Cabin and +7.85 dB for the unusually quiet wind source. The measured source music was −13.87/−13.24 LUFS; wind was −42.85 LUFS. Isolated nominal targets are −23 LUFS music and −35 LUFS wind, a trial balance for listening rather than a universal preset. No dynamic normalization, EQ, limiter, compression, time stretch or pitch shift is applied. Loudnorm is used only to measure and discard its processing output.

Wind source 0:01–0:29 supplies a steady-state 24-second period, with a four-second equal-power tail/head crossfade. It runs independently through the music handover with three-second entrance and ten-second exit fades. This remains a repeated short generated source, not non-repeating natural ambience. No radio, voices, new music generation or paid service is added. The sources have not been independently auditioned by the assistant for unwanted voices or other musical content.

This is a local listening preview, without the production intro or video. Evaluate the handover, both musical directions and whether the wind adds depth or becomes tiring. Technical checks do not establish musical compatibility or listening approval. No long release assembly, publication, commit or push is performed.

## Files and reproduction

Original supplied bytes are copied and SHA-256 verified under sources/. Downloads are unchanged. [Recipe and provenance](mix-recipe.json), [validation](validation.json) and [measurement logs](measurement-logs.json) document actual results. Actual generation settings, reference use, prompt versions and displayed cost for these supplied exports were not verified.

[build-review.cjs](build-review.cjs) uses local Node built-ins and FFmpeg. It refuses to overwrite existing review media or PCM cache; reproduce in a fresh package copy retaining the sources and update the explicit intake locations if needed. review/ and .cache/ are ignored local audition/render outputs. No remote backup is implied.
