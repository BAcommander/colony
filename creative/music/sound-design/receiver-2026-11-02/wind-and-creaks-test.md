# Snowline: wind variation and two settling-creak test

2026-11-02. User explicitly says **“ok lets do the test”** after the proposed wind-variety/two-creak comparison. This authorizes a separate local experiment; it does not replace the accepted V2 atmosphere balance. All original masters, source files, approved preset and earlier auditions remain unchanged.

## Comparisons

| Version | Change | Listening state |
| --- | --- | --- |
| A | Existing approved V2 | Accepted atmosphere balance; comparison control |
| B | Wind variation, with music/radio/ventilation held fixed | Supplied, selection pending |
| C | Identical B mix plus two quiet settling-creak candidates | Supplied, selection pending |

**Subsequent feedback:** user says “i feel like th creek needs work should we try and generate it from elevel labs?” The procedural creak is not accepted. Wind preference and A/B/C selection remain unresolved; do not infer a preference for B from criticism of C's creak. The approved V2 preset stays current.

## Next creak source: manual ElevenLabs SFX test

[Prepared creak prompt](elevenlabs-settling-creak-v1.txt) targets one window-frame joint, with audible material friction and a natural release. Use **Sound Effects**, proposed duration **4 seconds**, **looping off**, and the current UI's default prompt influence for the first batch. Record the actual model/cost/settings shown. One batch supplies candidate variations; do not assume a fixed variant count or price across interfaces. Choose two different useful takes if available, and download WAV48kHz for local editing. These are proposed settings, not an executed generation.

Generate a clear, dry source and set its final quiet level in the mix. Do not ask the model to make an entire barely audible polar soundscape. Listen for plausible contact/friction, a non-musical body, useful attack/release and a natural tail. If it produces a door squeal or exaggerated groan, revise the positive source/action description; do not keep adding mood words and exclusions blindly.

The user also asks whether the prompt should include snowdrifts/snow sounds. The creak prompt can identify a frame settling as it warms, but wind/snow layers should remain separate. “Snowdrifts” names scenery; an actionable sound brief describes moving grains brushing/skimming a surface. [Optional later snow-grain prompt](elevenlabs-spindrift-detail-v1.txt) is prepared as an independent detail source, not a selected extra layer or part of this creak test. Its proposed6-second, non-looping source would be placed/filtered locally if chosen. Existing wind already supplies the broad weather bed.

After user supplies a generated creak export, retain original bytes and actual generation details, inspect the complete file, select/trim the event and audition two different takes at the same source1:31/5:38 positions. Set comparable event level in context; old source gain coefficients are not transferable automatically. Compare the replacement against the same B wind-only base and the old procedural C. No new source file is available yet and no generation/credit spend has occurred. User runs paid generations manually under the existing workflow.

Official documentation checked2026-11-02: [SFX product guide](https://elevenlabs.io/docs/eleven-creative/playground/sound-effects) supports duration/looping settings, non-looping WAV48kHz downloads and generating individual effects for later combination; [capability guide](https://elevenlabs.io/docs/overview/capabilities/sound-effects) gives concise action/source prompting and notes that results vary. These support the workflow, not a guarantee that an AI creak will be preferred. Prompt/settings manifest: [prepared brief record](elevenlabs-creak-test-preparation.json).

All 90-second checks cover source0:54–2:24. Each retains its corresponding complete listening copy's gain; previews are not separately normalized. B/C full listening copies measure -23.0 LUFS, matching A's full-copy convention. C's first creak is source1:31, around0:37 in the check; the second is source5:38. Full B/C files are each nine minutes. [Audio links](README.md#current-balance-revision-environment-v2-both-layers-3-db).

## Wind method and provenance

Only one original wind source is in the current library. This experiment does not supply genuinely independent new wind recordings. Instead, each long passage is assembled from 9–14-second sections of the existing original, with unequal3.5–5.3-second advances and smooth power-normalized overlaps. Sections play at original speed and retain stereo pairing. Same second-order1800Hz placement filter; source fragments can recur.

The four approved passage start times, durations and entrance/exit fades are retained. Internal movement varies slowly. Each passage's RMS is calibrated to the corresponding decoded V2 wind passage, with measured differences below1e-8dB before encoding. A bounded source-assembly search selects a restrained crest; no master limiter is used. RMS matching does not guarantee identical perceived level, identical peaks or a preferred timbre. Music, radio and ventilation use their existing sources at unchanged gains.

The former24-second waveform recurrence was checked at four six-second pairs inside the wind passages. V2 normalized correlations at lag24s are0.99947–0.99992. The new assembly gives -0.01524 to0.01448 at those same sampled positions. This is evidence that the known fixed return is reduced there, not an exhaustive proof of no recurrence or improved listening comfort. No fixed24-second prepared cycle is tiled in B/C.

## Settling details

Two newly made procedural frame/pipe friction studies are placed during wind passages and gaps between radio calls:

- Source1:31: approximately1.69s, right window-frame position.
- Source5:38: approximately2.19s, left lower pipe/frame position.

They use irregular stick/slip excitation, broad moving material resonances, friction noise, source-only soft waveshaping, slow edges and short finite room taps. No recorded foley, franchise sound, downloaded model or paid service. Their identity/realism needs user listening; they are intended as quiet building movement, not asserted physical recordings of this scene.

The first internal render had very spiky low-RMS candidates. The effect source was refined to retain a little more contact body without increasing the peak ceiling. Source RMS rises about12dB in that internal revision while the panned peak remains around0.020–0.021; the music is not processed. Internal V1 media remain under `wind-creak-test-v1/`; an exact earlier renderer snapshot is retained under `history/`. Only the later `wind-creak-test-v2/` comparison was supplied for user selection.

## Actual checks and status

Eleven output files pass complete decoding, exact durations, finite samples and below-full-scale sample peaks. Every one of25,920,000 stereo frames confirms:

- B minus A equals varied wind minus original V2 wind exactly.
- C minus B equals the sparse two-creak stem exactly.
- C equals B exactly wherever the creak stem is zero.

Source, approved-audio and output hashes match. These validate intended changes and delivery integrity, not an assistant listening verdict. User selection is pending; the scene's approved current preset still points to V2.

[Recipe, sources, grain map and levels](recipe-wind-creak-test-v2.json) · [Full-sample validation](validation-wind-creak-test-v2.json) · [Renderer](../../../../scripts/render_snowline_wind_and_creaks.py).

Reproduce into a fresh directory:

```powershell
.local/audio-analysis/Scripts/python.exe scripts/render_snowline_wind_and_creaks.py --parent exports/sfx/snowline-receiver-2026-11-02/environment-session-v2 --wind exports/restored-snowline-2026-11-02/wind-soft-exterior-01.mp3 --out exports/sfx/snowline-receiver-2026-11-02/new-wind-creak-test
```

No publication, video assembly, new music, credit spend, commit or push. New test media remain local ignored outputs; compact code/records are local and uncommitted.
