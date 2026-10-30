# WINTER WATCH versus five Ambient Colony releases

2026-10-30. User explicitly requests an evidence-led comparison and a way to develop ElevenLabs music with the same all-day listening appeal. User supplies [Ambient Colony's channel](https://www.youtube.com/@AmbientColony). Current listening goal is stronger than approval of an unobtrusive crossfade: music the user wants to leave playing while working for hours.

[Open archived comparison report](comparison.html) · [Unlabelled listening trials](../../../../exports/reference-analysis/comparison-2026-10-30/listening-trials/trials.html) · [Exact compact measurements](comparison.json) · [ElevenLabs test package](elevenlabs/README.md)

## Current listening verdict

[Exported first-pass ratings and decoded identities](feedback-2026-10-30/README.md): WINTER WATCH, Rainline and Shoreless tie at 4/5; Basalt and both Ringfall versions score 3.5/5; Spirewatch scores 3/5 and feels too fast to the user. The earlier Spirewatch starting-point suggestion was based on signal resemblance and is superseded as a preference recommendation. No preference benefit demonstrated by the Ringfall EQ treatment. Current next brief: [environment first](elevenlabs/D-environment-first-after-ratings.txt), ungenerated. Long-session acceptance remains pending.

## Actual material and method

The local checkout lacks the earlier generated music sources/long exports, and old `G:/AI/colony` is unavailable. Channel identity was verified as `UCT5K7bJk5yJGUO_uu_17BdQ`. Five published audio renditions were acquired, then identical **02:00–32:00** passages were copied locally and fully decoded with the same analyser used for the earlier 30-minute WINTER WATCH excerpt. Every decoded passage is within 0.1 seconds of 1,800 seconds. These are published mixes, including any baked SFX, not dry generation masters. Rainline rain and Shoreless water cannot be isolated from these files. Source URLs, hashes, format and capture scope are recorded. The reference is an earlier moving DVR sample, not an entire broadcast or necessarily all the hours the user heard.

Downloads initially stalled through direct FFmpeg remote seeking. Incomplete attempts were preserved under ignored history, excluded from the accepted comparison. The corrected process uses yt-dlp's standard chunked download with its official EJS dependency and the existing Node runtime, then selects audio locally. Full candidate passages are validated, not inferred from a file existing. No account cookies, upload, paid service or new model weights.

## Results

| Thirty-minute passage | LUFS | LRA, LU | Below 80 Hz, energy % | 80–250 Hz | 250 Hz–1 kHz | Above 1 kHz | Stereo correlation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| WINTER WATCH | −22.6 | 5.0 | 33.25 | 35.94 | 26.70 | 4.12 | 0.263 |
| Ringfall | −16.0 | 7.4 | 70.49 | 13.21 | 16.01 | 0.29 | 0.402 |
| Basalt | −17.8 | 5.4 | 30.48 | 13.74 | 55.61 | 0.17 | 0.283 |
| Rainline | −20.8 | 2.0 | 0.03 | 64.59 | 35.12 | 0.26 | 0.441 |
| Shoreless | −20.8 | 6.1 | 0.00 | 30.16 | 68.75 | 1.09 | −0.021 |
| Spirewatch | −20.1 | 2.3 | 37.52 | 31.01 | 28.58 | 2.90 | 0.724 |

Spectral energy is not perceived loudness. Correlation is not a quality score or complete description of width. Quiet master level and spectral resemblance do not establish all-day comfort. Published encoding/SFX and the particular sampled passages are practical limits on causal inference.

## Initial measurement-led hypotheses, before the ratings

1. **Spirewatch is the clearest tonal starting point**, without declaring it the user's preferred music. Its coarse spectral distribution is already close. First test more independent spatial layers and more gentle level movement; its channels are much more similar and its loudness range smaller. Do not simply add treble or more bass.
2. **Ringfall has too much sub-bass relative to this target**, and more/larger overall level variation. A lower output gain can match loudness but will not repair the sub/low-mid relationship. A diagnostic low shelf reduces sub-bass on the same recording; hearing that against its gain-matched control tests a concrete mixing hypothesis. The shelf gain is derived from below-80-Hz energy odds, but the real shelf is an approximation, not guaranteed spectral matching. Original masters are untouched.
3. **Rainline is not sub-heavy**: almost no energy below 80 Hz, a strong 80–250 Hz concentration and only 2 LU loudness range. A generic bass cut or instruction to make it more static would move it away from this reference. Test quiet swells and independent layers; keep SFX judgment separate when dry sources return.
4. **Basalt is a useful comparator for dynamic range and channel difference**, but has about twice the energy share in 250 Hz–1 kHz. Shoreless is even more midrange concentrated. An increase in low foundation is a tonal hypothesis for these tracks, not a universal instruction across the channel.
5. **All five have less energy above 1 kHz than the reference** in the sampled mixes. The reference can feel dark while retaining more soft upper-mid detail. A blanket low-pass or another list of “no melody/no movement” instructions is not supported by these data. This does not establish what instruments are present.

The reference's measured median absolute one-second RMS change is 0.77 dB: Rainline 0.20, Spirewatch 0.50, Basalt 0.61, Ringfall 0.71 and Shoreless 0.99. This is a signal movement descriptor, not a perceptual event count. LRA and this descriptor measure different timescales. None should be optimized alone.

## Does WINTER WATCH loop?

It may contain recurring motifs, harmony, layers or a longer repeated assembly. The current recording does **not** establish which. Six-band feature similarity near 10:28 was not confirmed by strong sample waveform matches. A second whole-excerpt stereo waveform search at 2 kHz (testing the bulk 0–1 kHz range), over 30 seconds–28 minutes (requiring at least two minutes of overlapping audio), peaked at only about 0.318. The best lags were checked at three locations using 8 kHz stereo; they remained weak. [Exact deeper search](reference-deeper-recurrence.json). This is not a search over every component, time stretch or longer period; it does not prove the reference is unlooped.

The same analyser strongly detects our known recorded repeats:

| Published track | Repeated passage separation | Three sampled waveform correlations |
| --- | ---: | --- |
| Ringfall | 4:55 / 295 s | 0.9990–0.9999 |
| Basalt | 8:19 / 499 s | 0.9996–0.9998 |
| Rainline | 6:16 / 376 s | 0.9930–0.9993 |
| Shoreless | 6:32 / 392 s | 0.9993–0.9998 |
| Spirewatch | 11:14 / 674 s | 0.9990–0.9997 |

Ringfall/Basalt/Rainline/Shoreless separations also agree with the saved production recipes. The Spirewatch number is an observed published recurrence, not a claim about how it was generated. High short-window matches support repeated recorded passages, not identical decoding of every frame/sample or audible joins. A loop itself is not a defect. We need to test whether recurring details become noticeable or tiring, not assume a longer loop solves composition.

## Listening trials and next decision

Seven three-minute FLAC trials: reference, five published tracks and one EQ treatment of the exact Ringfall control passage. All use passage seconds 60–240; each was individually measured and adjusted to **−23 LUFS with constant gain**, then remeasured within ±0.15 LU, true peak below −1 dBTP. No compressor/limiter or stereo effect was applied. Treatment mapping is in the local answer key; rate first to reduce label/expectation bias. The external reference is local only. These are unlabelled personal trials, not a formal double-blind study.

Keep the same headphones/speakers and playback volume. Rate comfort, willingness to leave it running and attention diverted, with timestamps. Repeat in another order; short preference only screens candidates. Then audition the preferred direction for 30–60 minutes while doing normal work, followed by a longer repeat session. The user's reported all-day preference is the deciding outcome, not a fabricated similarity score.

No paid ElevenLabs generations have been made. The prepared test package contains explicit candidate prompts, matched-parameter replicated tests, an API composition-plan alternative and evidence required to promote a candidate. Generation remains stochastic and prompt hypotheses remain untested until exports are received. No claim that a specific prompt, EQ setting or model is already proven to achieve the user's goal.

Code: `scripts/compare_ambient_audio.py`, `scripts/prepare_ambient_trials.py`, `scripts/investigate_ambient_repetition.py`. Actual audio, full timelines/reports, intermediate and failed downloads are local under ignored exports. Compact measurements, six full timelines/chart reports, trial validation, research and prompts are saved here. User now explicitly requests commit/push; see ../backup-2026-10-30.json for verified scope and remote evidence. Audio and listening clips remain local.
