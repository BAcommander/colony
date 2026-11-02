# Snowline: original receiver sound design

**Portable backup requested 2026-11-02:** [resume guide](../../../../music/snowline-sound-design-2026-11-02/RESUME.md). The Git LFS archive includes the exact audio sources, stems, mixes and historical trials; the restore command recreates the `exports/` paths used below on another machine. This later backup supersedes earlier local-only statements in the historical sections. Current V2 balance stays accepted; the generated-creak step remains pending.

2026-11-02. User clarifies the goal is to generate our own radio/static texture for the next Star Wars-inspired video, and asks whether the repo contains last night's music. Treat this as an original sound-design experiment for Below the Snowline, not a replacement of its accepted music or a reopening of Junction's rejected radio direction.

## Current balance revision: environment v2, both layers +3 dB

**Balance approved 2026-11-02:** user says **“Enough—keep this level.”** Retain V2's wind/ventilation settings for Snowline. [Exact approval, context and file hashes](environment-v2-balance-approval.json) · [Current scene-specific preset](snowline-ambience-preset-current.json). This accepts the atmosphere balance heard in the plateau check; a full-session listening verdict or final combined-video approval is not inferred. No audio is changed by this status update.

**Optional wind/creak test is now rendered; no replacement selected yet.** [A: approved V2, 90 seconds](../../../../exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/A-approved-v2-90s-check.mp3) · [B: wind variation only](../../../../exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/B-wind-only-90s-check.mp3) · [C: wind variation plus two creaks](../../../../exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/C-wind-and-creaks-90s-check.mp3). All cover source0:54–2:24 using the corresponding full-track matched listening gain. C's first creak is around0:37 in the check. [Complete nine-minute B](../../../../exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/B-wind-only/Snowline-wind-variation-9min-test.mp3) · [Complete nine-minute C](../../../../exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/C-wind-and-creaks/Snowline-wind-and-creaks-9min-test.mp3). [Method and actual checks](wind-and-creaks-test.md).

**Creak revision requested:** user says the creak needs work and suggests ElevenLabs. [A short isolated-creak SFX prompt](elevenlabs-settling-creak-v1.txt) and proposed settings are prepared for manual generation; no credits spent or new output yet. Snow/wind should not be bundled into that source; an [optional snow-grain detail brief](elevenlabs-spindrift-detail-v1.txt) remains separate. Wind preference is not inferred, and approved V2 remains current.

**Included-layer audit:** approved V2 contains 14 distinct blurred transmissions, receiver clicks, gated hiss/carrier movement, five acknowledgement events, four wind passages and quiet ventilation. Two settling-creak candidates now exist only in optional test C. Distant door/servo/receiver-whistler additions remain proposals. [Next refinement candidates](ice-planet-layer-plan.md#included-layer-audit-and-next-refinement-candidates) retain the earlier audit and test priorities; V2 remains the approved comparison.

User reports **“Added atmosphere is too quiet”** in v1. V2 raises both existing wind and ventilation stems by 3 dB, preserving their ratio, timing, filters and textures. The comment concerns their combined audibility; it does not independently establish which source was too quiet. This is a controlled first gain revision, not a universal new preset.

[Complete nine-minute V2 audition](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-radio-wind-and-ventilation-9min-v2.mp3) · [66-second plateau check](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-environment-v2-plateau-check-66s.mp3) · [Same-window V1 comparison](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-environment-v1-plateau-check-66s.mp3) · [Lossless V2 mix](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-radio-wind-and-ventilation-9min-v2.flac).

The short checks start at **0:54 of the complete track** and run to 2:00; they begin at the first wind plateau. Each uses its corresponding full-copy constant gain, with no independent excerpt normalization. The full V2 MP3 measures -23.0 LUFS/-8.0 dBTP. Effective wind gain is +7.85 dB against the original source before the existing placement filter/envelope; ventilation is now -45.0 dBFS RMS. These are the accepted scene-specific atmosphere settings, not universal gain defaults.

The approved music/radio parent stays at unity in the lossless mix. All existing stems, radio events, wind passages, timbres and source masters are preserved. Six encoded files fully decode to their exact durations, with finite samples/no full-scale sample peaks. Across all 25,920,000 stereo frames, V2 wind and ventilation match V1 × 10^(3/20) within 1.20e-7; the final decoded lossless mix equals parent+raised stems exactly. No new generation, filter, fade, compression or video assembly.

[V2 recipe](recipe-environment-session-v2.json) · [Full-sample gain/mix checks](validation-environment-session-v2.json) · [Gain-only renderer](../../../../scripts/rebalance_snowline_environment.py). The user accepts the stronger plateau balance. Historical render-time pending fields in recipes/validation precede the linked approval record. No assistant listening verdict.

## Baseline environment audition v1: selected layers, too quiet

User selects **“Exterior wind and quiet ventilation”** after the full radio session. [Complete nine-minute listening copy](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v1/Snowline-radio-wind-and-ventilation-9min-v1.mp3) · [Two-minute check](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v1/Snowline-radio-wind-and-ventilation-2min-preview-v1.mp3) · [Lossless combined mix](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v1/Snowline-radio-wind-and-ventilation-9min-v1.flac). These are new balance auditions, not final environment approval.

The earlier nine-minute music/radio lossless mix is the unchanged unity-gain parent. Its fourteen voice events, source gains, clicks and acknowledgements are untouched. Two independent stems are added:

- **Exterior wind:** the verified original library source, with a second-order 1800 Hz low-pass as a proposed closed-window distance treatment. Four long passages begin at 0:42, 2:49, 4:58 and 7:18, lasting 72/58/83/69 seconds with different 11–20-second entrance/exit ramps and quiet gaps. Source gain +4.85 dB is the earlier audition's starting point, not an approved universal level. The 30-second recording supplies a 24-second prepared cycle, with a four-second overlap and different entry phases. Its source texture repeats within passages; the full gust envelope does not simply repeat every 24 seconds. No radio-synchronized ducking.
- **Ventilation:** newly synthesized rounded room air from the visible under-window grilles, nominal band 140–950 Hz, stereo, -48.0 dBFS RMS, with a few percent of slow internal level change. No tonal oscillator or periodic motor pulse. A complete nine-minute periodic noise source and wrap-aware resampling avoid a short tiled room-air sample. This level and timbre are proposed scene-specific starting points.

Both [wind](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v1/Snowline-exterior-wind-9min-v1.flac) and [ventilation](../../../../exports/sfx/snowline-receiver-2026-11-02/environment-session-v1/Snowline-ventilation-9min-v1.flac) remain available as separate lossless stems. No music/radio compression, EQ, pitch/rate change, production opening or new fade was added. Listening MP3s use constant whole-mix gain; the complete copy measures -23.0 LUFS, matching the prior full radio audition. The two-minute preview retains that same gain rather than being separately normalized. Wind reaches its first plateau around 0:54.

All five outputs pass full decode, exact duration, finite-sample and below-full-scale sample-peak checks. Every one of 25,920,000 stereo frames of the lossless output equals the decoded parent+wind+ventilation recipe exactly. Parent and source hashes match. Two targeted checks cover ventilation bandwidth/headroom/circular boundary and separated guarded wind passages. Numeric checks are not an assistant listening verdict; the user subsequently found this initial atmosphere too quiet. See V2 above.

[Environment recipe](recipe-environment-session-v1.json) · [Complete-sample validation](validation-environment-session-v1.json) · [Layer placement and source research](ice-planet-layer-plan.md). No paid tools or external audio upload. Other ice/structure/utility effects remain proposals. No publication, long video assembly, commit or push.

```powershell
.local/audio-analysis/Scripts/python.exe scripts/build_snowline_environment.py --parent exports/sfx/snowline-receiver-2026-11-02/full-session-v1 --wind exports/restored-snowline-2026-11-02/wind-soft-exterior-01.mp3 --out exports/sfx/snowline-receiver-2026-11-02/new-environment-review
.local/audio-analysis/Scripts/python.exe -m unittest discover -s scripts -p test_snowline_environment.py -v
```

## Nine-minute radio-only comparison

User requests trying the receiver over the complete approved Snowline track, with more randomly spaced transmissions so the same short radio loop is not repeated. [Listen: music and varied radio, 9:00](../../../../exports/sfx/snowline-receiver-2026-11-02/full-session-v1/Snowline-music-and-radio-9min-v1.mp3). [Lossless unity-music mix](../../../../exports/sfx/snowline-receiver-2026-11-02/full-session-v1/Snowline-music-and-radio-9min-v1.flac) and [separate nine-minute radio score](../../../../exports/sfx/snowline-receiver-2026-11-02/full-session-v1/Snowline-radio-score-9min-v1.flac) remain local.

This is a new 540-second event arrangement, not a repeated 67-second source. Fourteen distinct invented phonetic phrases are used once each, with the same voice-processing chain and design gain as the earlier prototype. Eight new local Windows voice sources extend the original six; the exact source pool and hashes are recorded. Every packet receives independently generated static/carrier motion and opening/closing clicks. Five packets have a soft acknowledgement. No new music, paid generation, reference extraction or film audio.

The first voice enters at 0:23.83. Quiet gaps between receiver packets vary from 18.03 to 58.12 seconds; the radio score is silent for 85.15% of its samples. The 14 packet hashes and voice-source hashes are distinct. This supports variety within this particular nine-minute arrangement; it is not proof of perceptual naturalness or an infinitely non-repeating radio source. For an hour, generate an hour-long event arrangement instead of tiling this score. The approved music's own nine-minute recurrence is a separate property.

The lossless mix retains the approved music at unity and the v4 clearer audition's radio-source gain, 0.2498415319. Reducing density does not raise event gains. No opening/closing fade, EQ, compression, pitch or rate change is added to the music. Its approved hash remains unchanged. A separate MP3 listening copy uses only constant whole-mix gain and measures -23.0 LUFS.

All three delivered audio files fully decode to exactly 540 seconds/25,920,000 stereo frames with finite samples and no clipping. Complete decoded lossless recipe comparison has maximum error 1.20e-7; the mix matches the music exactly wherever the decoded radio is zero. Two schedule checks cover deterministic unique-source ordering, irregular non-overlapping spacing, guarded edges and changed-seed variation. These checks do not replace full-session listening.

[Full recipe](recipe-full-session-v1.json) · [Complete-sample checks](validation-full-session-v1.json) · [Cue sheet](cue-sheet-full-session-v1.txt) · [Ice-planet layer proposals](ice-planet-layer-plan.md).

Implementation: [voice-pool extension](../../../../scripts/extend_receiver_voices.ps1), [full-session renderer](../../../../scripts/build_snowline_radio_session.py), [schedule checks](../../../../scripts/test_snowline_radio_session.py). Full-session user review is pending. Other environmental layers have not been added to this radio audition.

```powershell
.local/audio-analysis/Scripts/python.exe scripts/build_snowline_radio_session.py --voices exports/sfx/snowline-receiver-2026-11-02/voices-v2 --music exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.flac --parent exports/sfx/snowline-receiver-2026-11-02/v3 --out exports/sfx/snowline-receiver-2026-11-02/new-full-session
```

## Current audition: v4 sparse push-to-talk receiver

The user rejected the initial noise-led prototype as too static-heavy and requested more indistinct chatter, random beeps and influence from the diagnosed reference. V3 introduced six original synthetic-voice transmissions and five beep events. The user then judged the voices blurred enough, but too frequent; the static was too consistent and should cut in/out with radio clicks. This accepts the blur character only, not the whole effect or mix.

[Current receiver alone](../../../../exports/sfx/snowline-receiver-2026-11-02/v4/receiver-gated.mp3) · [Snowline plus quieter receiver](../../../../exports/sfx/snowline-receiver-2026-11-02/v4/music-gated-quiet.mp3) · [Clearer receiver audition](../../../../exports/sfx/snowline-receiver-2026-11-02/v4/music-gated-clearer.mp3) · [Music-only control](../../../../exports/sfx/snowline-receiver-2026-11-02/v4/music-only.mp3) · [Three-repeat effect review](../../../../exports/sfx/snowline-receiver-2026-11-02/v4/receiver-gated-three-repeat-review.mp3).

V4 uses three unchanged V3 voice packets, moved to 7.10, 32.30 and 55.85 seconds. Each receiver window has an opening click, restrained static/acquisition detail, voice and a closing click/tail. Hiss and carrier are gated off between windows; their level/colour also vary within open windows. Two softer acknowledgements belong to receiver events, rather than five free-running beeps. The 67-second source is exactly silent for 74.335% of its samples outside intended events, allowing the music to carry the scene. No background noise floor is left running by this effect.

**Preserve event gain when changing density.** V4 copies the three processed voice packets without changing their samples or normalization. Its quieter/clearer music auditions retain V3's effect-source gains (0.1252173862 / 0.2498415319). They do not re-normalize the sparser effect back to its earlier whole-clip RMS, which would make the remaining voices louder. Whole music+effect auditions are then constant-gain matched to -23 LUFS. They cover music 1:30–2:37, with one-second review fades; the approved nine-minute music file is unchanged.

All eleven delivered V4 files fully decode with finite samples/no full-scale sample peaks and their requested durations. All three comparison MP3s measure -23.0 LUFS. The circular source join is zero in a quiet gap. Copied voice samples match their V3 sections exactly before final quantization. These are technical and regression checks, not an assistant listening verdict. V4 source/mix review remains pending.

The carrier and beep family are original designs. The earlier reference's beep identity was never established; do not claim they were extracted or detected there. Reference influence is the user's description of indistinct activity and a rising/lowering tone, plus measured dark spectral character and level movement. V3's near-620 Hz carrier, slow frequency/level motion and current static-colour modulation are design choices, not a reproduction of a confirmed reference oscillator.

Implementation: [Windows voice-source renderer](../../../../scripts/make_receiver_voices.ps1), [voiced V3 construction](../../../../scripts/generate_polar_comms.py), [V4 event refinement](../../../../scripts/refine_receiver_events.py). Six invented phonetic phrases were rendered by installed Microsoft George/Hazel desktop speech voices locally, then band-limited, saturated, coarsened and given brief signal losses. No reference/film recording, meaningful scripted dialogue, character imitation, downloaded voice model or paid generation is used. Invented phrases may still have recognizable syllables; the user judged the processed blur sufficient.

[V4 recipe](recipe-v4.json) retains actual source gains, gate windows, click/beep/voice events, output hashes and metering. [Feedback/checks](feedback-and-checks.json) preserves exact corrections and approval scope. New effects/voice sources remain local ignored review media; they have not been backed up or added to the accepted SFX library.

Reproduce V4 from retained V3 sources into a fresh directory:

```powershell
.local/audio-analysis/Scripts/python.exe scripts/refine_receiver_events.py --parent exports/sfx/snowline-receiver-2026-11-02/v3 --music exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.flac --out exports/sfx/snowline-receiver-2026-11-02/new-v4-review
```

## Last night's music is present in Git LFS

Fetched branch `origin/codex/empty-junction-backup-2026-11-01`, commit `aa62e427e3f6386217e90229c063820c8f54ccae`, stores the approved nine-minute Shelter on the Ice Plain / Outpost on the Ice pair. Both five-minute sources were supplied on November 1; the paired master was accepted that night. Exact executed music-generation prompt/settings remain unverified.

The current checkout initially had the older music-preparation files, not these audio files. Two exact-path LFS objects have now been fetched and restored as local review copies under `exports/restored-snowline-2026-11-02/`. The MP3 is 12,961,196 bytes; lossless stereo 48 kHz/24-bit FLAC is 77,189,149 bytes. Both fully decode to 540 seconds with finite samples. The FLAC SHA-256 matches the prior approved master: `987b1509075da8a9202f24a6b765f4e2b6d88d90cb90c28bdaf8719af77b252b`.

[Restoration evidence](restoration.json) retains source commit, exact Git paths, LFS hashes and full-decode checks. No branch switch, production-tree merge or edit to the approved music was performed. Older G: paths in the approval are historical; the restored copies are here:

- [Nine-minute listening copy](../../../../exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.mp3)
- [Lossless approved master](../../../../exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.flac)

## First generation route: local procedural audio

[Generator](../../../../scripts/generate_receiver_texture.py) constructs original audio from seeded noise and oscillators. No reference recording, franchise audio, actual speech, voice model, paid service or audio upload is used.

Three separate stereo stems provide independent mix controls:

1. **Static:** filtered noise, nominally 180–3100 Hz, with slow irregular changes of strength.
2. **Carrier:** a quiet near-620 Hz tone with independent slow frequency and amplitude movement. Its pitch is a design choice, not an identification or copy of the earlier near-131 Hz reference candidate.
3. **Non-verbal activity:** gated resonant noise with irregular bursts and faster internal modulation. It is intended to suggest indistinct receiver activity, not verified realistic chatter or synthesized words. User listening will determine whether this works.

The speaker is deliberately close to mono with modest unequal room taps. This is a proposed small receiver inside the shelter, separate from exterior wind, room air and the musical bed. The source period defaults to 67 seconds and has periodic noise/control/phase construction. A three-repeat review supports seam listening; numeric closure is not an artistic seam verdict. Independent radio/music periods do not erase the nine-minute musical recurrence.

Outputs remain under ignored `exports/sfx/snowline-receiver-2026-11-02/`. The first `v1` rendering produced the isolated previews, but stopped because the encoded music-only audition measured -23.3 LUFS instead of its target. Preserve that attempt; the completed `v2` renderer measures the encoded output and adjusts constant gain, preserving each pass. No compression or musical re-arrangement is used for loudness matching. These initial non-verbal noise prototypes are superseded by the user's subsequent speech-cadence/gating corrections above.

Reproduce into a new directory:

```powershell
.local/audio-analysis/Scripts/python.exe scripts/generate_receiver_texture.py --out exports/sfx/snowline-receiver-2026-11-02/new-test --music exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.flac --music-start 90
.local/audio-analysis/Scripts/python.exe -m unittest discover -s scripts -p test_receiver_texture.py -v
```

The music comparisons use the same source region, 1:30–2:30 of the approved master. Conditions are music only, music with receiver at -20 dB relative RMS, and music with receiver at -14 dB relative RMS, before whole-mix constant-gain matching to -23 LUFS. These are experimental levels, not approved fader settings or perceived-loudness percentages. All three get the same one-second review entrance/exit fades. The accepted master is unchanged.

Two targeted checks pass: deterministic independent seeded layers with finite/headroom/phase-closure and circular-boundary checks, plus nominal static bandwidth, nonzero activity and near-mono speaker behaviour. Encoded outputs and comparison loudness are checked during generation. Exact parameters, software, generator hash, timing, output hashes and levels are saved in the output's recipe.json; a compact copy is retained here after the completed run. No assistant listening verdict or production approval is claimed.

## Second route: dedicated sound-effect generation

If the procedural activity sounds too synthetic, keep the controllable static/carrier and try a separately generated transmission layer. Two manual-use briefs are prepared: [receiver bed](elevenlabs-receiver-bed.txt) and [garbled transmission](elevenlabs-garbled-transmission.txt). They describe original equipment rather than requesting a film sound or character imitation.

Use ElevenLabs **Sound Effects**, with duration and looping selected in the actual UI; inspect the displayed cost and available model. Current official documentation describes separate SFX generation, duration up to 30 seconds, looping and prompt influence; v3 availability is limited. These settings do not guarantee a seamless or convincing result. [Official Sound Effects documentation, checked 2026-11-02](https://elevenlabs.io/docs/overview/capabilities/sound-effects).

No ElevenLabs generation or credit spend has been made. The user runs paid generations manually. Keep a generated transmission separate, judge it against the music, and preserve originals before changing gain or event spacing.

## Next listening decision

The initial and V3 checks have now received the corrections recorded above; V4 is the current audition. Judge its mixed versions as well as the isolated effect: event density, switching/click character, tuning-tone prominence, whether activity becomes distracting, and whether the sound plausibly belongs inside this particular shelter. Choose the useful components before attempting any full-length mix.
