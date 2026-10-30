# Ambient reference analyser

Reusable local analysis for audio/video files and public YouTube audio. Built for the user's 2026-10-30 request after listening to Ambient Outpost's WINTER WATCH stream through much of the day.

Double-click [Analyze Audio.cmd](../../../Analyze%20Audio.cmd) for a file picker, or drag an audio/video file onto it. It opens an interactive HTML report after analysis. All new outputs default to Git-ignored `exports/reference-analysis/`, with a unique run folder. Earlier reports and source files are preserved.

## Run from PowerShell

```powershell
# This machine's isolated environment (NumPy and imageio-ffmpeg inherited).
.local/audio-analysis/Scripts/python.exe scripts/analyze_ambient_audio.py "C:/path/to/music.mp3" --open

# Live URLs capture a bounded public DVR excerpt; default five minutes.
.local/audio-analysis/Scripts/python.exe scripts/analyze_ambient_audio.py "https://www.youtube.com/watch?v=dDYH-75RJWA" --live-seconds 1800 --open

# Regression checks using known audio and a known repeated feature pattern.
python -m unittest discover -s scripts -p test_ambient_audio.py -v
```

For a new machine: Python 3, `numpy` and `imageio-ffmpeg`; optional `yt-dlp` for URLs. This machine uses `.local/audio-analysis/`, an isolated venv with system packages and yt-dlp 2026.10.26 installed from PyPI. The launcher falls back to `python` for local files if that environment is absent. No service/API subscription or model weights are required. FFmpeg comes from imageio-ffmpeg; `--ffmpeg` accepts an explicit executable.

## What the report measures

- Integrated LUFS, loudness range and true peak from FFmpeg's EBU R128 filter.
- One-second RMS/sample peaks and percentile spread, including the final partial second.
- Six spectral energy bands and spectral centroid, based on stereo power at a disclosed 48 kHz analysis rate. Opposite-polarity stereo does not disappear through a mono downmix.
- Stereo correlation and side-energy fraction, with silence reported as unavailable.
- Five-second spectral/level differences to suggest audition points.
- Candidate repeated patterns from multiband feature autocorrelation, searched from 30 seconds to half the recording. The top three candidates are checked against eight-second stereo waveforms at three positions, with a ±3-second offset search. Even strong sampled matches do not establish every section of a full loop. Low waveform similarity can reject an appealing spectral coincidence.
- Source SHA-256, capture scope, software/method provenance and machine-readable JSON.

Charts support hover inspection and click-to-seek; audio does not autoplay. If the viewer blocks the source path, choose the local recording using the report's file picker. The report and audio remain local; nothing is uploaded. Use the same method and listening level when comparing our tracks. There is no automatic preference score or quality ranking.

## Live versus finished tracks

The supplied link was a live stream when inspected. Public HLS DVR supplies an already-available bounded excerpt, captured faster than real time where supported. Capture metadata records requested duration, time of retrieval and approximate position behind the moving live edge. The analysed decoded duration is authoritative. It is not the entire broadcast or necessarily what the user heard earlier. Non-live URLs download the available audio rendition; local files are analysed directly. Unsupported/inaccessible sources should be supplied as local recordings; the tool does not use account cookies or bypass access checks.

External reference recordings stay under ignored exports. Preserve compact results/provenance and original descriptive learnings in the repo, not third-party audio. Do not infer instruments, key/BPM, absence of vocals, room/reverb identity or audience performance from these measurements. Personal enjoyment and listening comfort still need the user's listening judgment.

The six comparison reports and full timelines are also archived in [the Git-ready comparison](comparison-2026-10-30/comparison.html). Source audio and unlabelled listening clips remain local. User explicitly requests commit/push on 2026-10-30; see backup-2026-10-30.json for remote evidence.

Implementation: [analyser](../../../scripts/analyze_ambient_audio.py), [report template](../../../scripts/ambient_audio_report.html), [regression checks](../../../scripts/test_ambient_audio.py).
