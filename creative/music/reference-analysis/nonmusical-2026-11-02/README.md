# WINTER WATCH: non-musical texture investigation

User request, 2 November 2026: diagnose the non-musical parts of [WINTER WATCH](https://www.youtube.com/watch?v=dDYH-75RJWA). This extends the earlier full-mix comparison; it does not replace the user's listening ratings.

## Result and current limit

A fresh ten-minute recording has been measured and processed into listening aids. The non-tonal diagnostic residual is predominantly low/mid frequency, varies in level, and has less similar left/right channels than the sustained-tone output. This supports inspecting a diffuse background texture. **The actual sound sources have not been identified.** There has been no assistant listening verdict. The user now describes radio static, indistinct chatter and a rising/lowering tone in the boosted inspection clip; see the follow-up below.

The creator's current description mentions immersive sound design but does not name the effects or provide stems. Its music/authorship statements are creator claims, not independent verification. The picture and the title are not evidence that a particular environmental sound is present.

## Measured observations

These numbers describe this recording and this processing method, not an isolated environmental recording.

| Measurement | Original mix | Sustained-tone output | Uncertain residual output |
| --- | ---: | ---: | ---: |
| RMS, dBFS | -23.97 | -27.13 | -33.65 |
| Left/right correlation | 0.248 | 0.349 | 0.108 |
| Spectral energy below 1 kHz | 96.19% | 97.64% | 92.98% |
| One-second RMS, 5th–95th percentile | -27.32 to -21.29 dBFS | -32.17 to -24.08 dBFS | -36.21 to -30.92 dBFS |

The transient-shaped output has substantially lower RMS (-44.25 dBFS) than the other outputs. This is an algorithmic allocation, not proof that identifiable brief effects are absent. A tonal machine hum could enter the sustained output; musical noise or reverberation could enter the residual. Do not call the residual a clean SFX stem, use its level as an original SFX fader setting, or report mask allocation as a percentage of non-musical sound.

## Audition

Local [comparison player](../../../../exports/reference-analysis/nonmusical-2026-11-02/inspection-v1/listen.html) provides three 30-second regions, each with original, reduced sustained tones at the same gain, and a boosted inspection version. Media remain under ignored exports and are not a Git backup.

| Selection | Start in this ten-minute recording | Purpose |
| --- | --- | --- |
| Residual focus | 5:58 | Largest average residual/original ratio across a 30-second window |
| Transient focus | 5:44 | Largest transient/original one-second ratio within a 30-second window |
| Steady texture | 1:20 | Least variable residual level across a 30-second window |

These are recording-relative positions, not absolute timestamps in the moving YouTube stream. Selection labels are measurement labels, not heard event descriptions. Boosted versions add 12 dB and are for inspection; use the original and same-gain processed pair to judge relative level. The processed versions can contain musical leakage and processing artefacts.

The initial user check is answered below. Radio-like static and indistinct chatter are user listening observations, not verified physical radio/voice provenance. Do not change November's SFX briefs to a purported replica until the target sound is established in the original recording.

## Follow-up: tone and texture inspector

The user hears radio static, louder than expected, indistinct chatter and a rising/lowering tone cutting through it. Their exact [listening feedback](listening-feedback.json) is preserved. They heard the earlier residual-plus-transient aid boosted by 12 dB, approximately four times its same-gain amplitude. This does not establish that the original effects balance is too loud, or that the radio-like detail is present unchanged in the original. Musical leakage and processing artefacts remain possible contributors.

Built [Inspect Radio Texture.cmd](../../../../Inspect%20Radio%20Texture.cmd), [the analysis script](../../../../scripts/analyze_radio_texture.py) and [the report template](../../../../scripts/radio_texture_report.html). The local tool provides:

- Click-to-seek, frequency-range and time-zoom spectrogram controls.
- Candidate continuous narrow-tone tracks, with separate frequency and spectral-level measurements, to distinguish a possible pitch sweep from a swell/fade.
- Original, candidate narrow tones, those tones reduced, and a 250–3500 Hz inspection band. Processed versions have same-source-gain and explicitly labelled boost options. None is a clean music/SFX/voice separation.
- Four frequency-band RMS envelopes and a conservative screen for candidate steady level modulation. No voice detection or transcription.

The current [interactive report](../../../../exports/reference-analysis/nonmusical-2026-11-02/radio-inspector-v2/inspect.html) covers recording 5:58–6:58, including the earlier 30-second audition. All time positions are relative to the saved ten-minute recording. Open the report directly, or use the currently running localhost preview at `http://127.0.0.1:8766/radio-inspector-v2/inspect.html`. The static report and its seven MP3 files work together; no server is required when opened locally in a browser that permits local media.

Actual results: the longest retained narrow-tone candidate spans recording 6:17.3–6:57.5, with frequency percentiles 129.8/130.9/132.0 Hz and a 13.9 dB 5th–95th percentile spectral-peak level span. A second candidate near 196 Hz also varies substantially in level. These support amplitude motion in some nearly stable-frequency components. They may be musical partials and have not been matched by listening to the particular sound the user means. Other moving/fragmented candidates exist; no blanket claim that pitch never changes is justified. The 75 retained ridge fragments are not 75 distinct sounds.

No frequency band's level envelope passes the current 0.05–2 Hz consistency screen in this minute. Irregular swells, slower motion, different windows and filtered-noise motion remain possible. This is not a loop test or proof of absent modulation. An earlier internal report (`radio-inspector-v1`) listed prominence-only timing peaks; its rhythm candidates are superseded. A noise-only negative control caught these unreliable peaks before delivery. The revised screen requires at least six cycles, concentration near the peak and compatible substantial sinusoidal motion across three disjoint sections. These are disclosed heuristics, not a calibrated statistical detector.

The complementary candidate-tone filters reconstruct the decoded source with maximum error 5.96e-8. Three targeted signal checks pass: a noisy known up/down frequency sweep, a fixed-frequency amplitude-modulated opposite-polarity stereo tone, and a broadband-noise negative control for both continuous-tone and modulation claims. All seven MP3 files fully decode to 60 seconds with finite samples and sample peaks below full scale. Browser checks cover metadata loading, source selection, gain labels/reset, zoom and seek preservation while switching versions; no console errors were observed. The assistant inspected the rendered UI, not the sound. The file picker and drag/drop launcher have not been exercised through native UI.

Double-click the launcher to choose an audio/video file and start/duration, or drag a local file onto it. A new report opens after processing; the source is preserved. Command-line reproduction:

```powershell
.local/audio-analysis/Scripts/python.exe scripts/analyze_radio_texture.py "exports/reference-analysis/nonmusical-2026-11-02/current-10min/reference-sample.m4a" --start 358 --seconds 60 --out "exports/reference-analysis/nonmusical-2026-11-02/radio-inspector-new" --open
.local/audio-analysis/Scripts/python.exe -m unittest discover -s scripts -p test_radio_texture.py -v
```

Fresh-machine dependencies are Python 3, NumPy, SciPy and imageio-ffmpeg in `.local/audio-analysis/`. The launcher uses that existing environment. Analysis runs locally without an audio upload, paid generation or a downloaded model. New output directories are required to preserve prior reports. [Follow-up validation and hashes](radio-inspector-validation.json) retain exact scope, findings and code hashes; external media and full diagnostic timelines remain ignored.

## Production implication to test

Test a separate, continuous, subdued environment layer with gentle variation, underneath the music, against a music-only control. Judge at matched full-mix loudness and quiet listening level, then in a longer session. This is a proposed experiment informed by the measurements and the earlier positive Rainline feedback; it has not been generated, tested, or shown to explain the reference's all-day appeal. No universal bass cut, exact EQ curve, effects level, event schedule, or source identity follows from this investigation.

## Reproduce and inspect

```powershell
.local/audio-analysis/Scripts/python.exe scripts/diagnose_ambient_texture.py "exports/reference-analysis/nonmusical-2026-11-02/current-10min/reference-sample.m4a" "exports/reference-analysis/nonmusical-2026-11-02/inspection-v2"
.local/audio-analysis/Scripts/python.exe -m unittest discover -s scripts -p test_ambient_texture.py -v
```

Dependencies: NumPy, SciPy and imageio-ffmpeg. SciPy 1.18.1 was installed from PyPI into the existing isolated audio-analysis environment. No audio upload, model weights, paid API or generation was used.

Method: stereo 16 kHz analysis, 2,048-point STFT, 512-sample hop, 31-frame temporal and 31-bin frequency median filters, shared stereo soft masks with separation margin 2. Three outputs sum back to the decoded input with maximum absolute error 8.94e-8. Analysis is limited to 8 kHz bandwidth. Reconstruction does not prove semantic separation accuracy.

The approach is adapted from [Driedger, Müller and Disch's harmonic/percussive/residual separation work](https://www.audiolabs-erlangen.de/resources/2014-ISMIR-ExtHPSep/). Their method separates spectral structures and explicitly addresses ambiguous sounds and leakage; it is not an environmental-sound recognition method. This implementation uses one STFT resolution and soft masks, not the paper's complete iterative procedure.

Two synthetic checks pass: known-tone routing with opposite-polarity stereo preserved, and noise reconstruction/routing. All nine encoded MP3s passed complete decode, exact 30-second duration, finite-sample and below-full-scale sample-peak checks. These checks do not establish audible quality or sound identity.

Compact [measurements](diagnosis.json), [capture provenance](capture-metadata.json), [creator metadata](creator-metadata.json), [clip checks](clip-validation.json), and [implementation hashes](validation.json) are retained here. The source hash is `6ba9caecdca380dd6f23f11b1776c5599d1e7510d10d537f39b94b6801a759a6`; decoded duration is 600.003625 seconds. The capture began approximately 615 seconds behind the live edge when retrieved at 08:52 UTC on 2 November 2026. It is not the complete stream, nor necessarily the passage heard by the user or the earlier October recording.

User subsequently requests a portable commit/push on 2026-11-02. Full non-audio timelines and the current inspector HTML/screenshot are archived under [reports](reports/README.md); original/filtered reference recordings remain excluded. [The Snowline handoff](../../../../music/snowline-sound-design-2026-11-02/RESUME.md) covers tools, dependencies and restoration of our own sound-design audio. No user approval of a reference texture or all-day production recipe is inferred.
