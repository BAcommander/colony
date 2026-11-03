# Historical Snowline checkpoint — November 2

**Current continuation:** use [the November 3 resume guide](../snowline-sound-design-2026-11-03/RESUME.md) for the full two-hour V5, supplied creak, all later auditions and current settings. The root launcher now restores both packages. The November 2 archive remains unchanged and supplies earlier dependencies. The manual creak-generation next step below was completed by a user-supplied export on November 3; do not treat it as a pending required generation.

## Historical state and original archive instructions

Checkpoint: 2026-11-02. This package restores the exact audio needed to continue this chat's workflow on another machine. The Git branch is `codex/concept-brainstorms-2026-10-27`. The later November production branch was read for provenance; its production tree was not merged into this branch.

## Pull and restore

Run these from your Colony checkout, on the branch above:

```powershell
git pull --ff-only
git lfs pull --include="music/snowline-sound-design-2026-11-02/snowline-session-media.zip"
python scripts/restore_snowline_session.py
```

If another branch is checked out, first run `git fetch origin` and `git switch codex/concept-brainstorms-2026-10-27`. Keep any uncommitted work on that machine before switching. The root **Resume Snowline.cmd** runs the same restore and opens this guide. Python 3.10+ and Git LFS are needed for restoration; no audio libraries are needed just to restore or listen.

The restore verifies the archive and every restored file against SHA-256, restores the original relative `exports/` paths and skips identical existing files. It refuses to overwrite different local files. `--verify-only` checks a completed restore; `--root <empty-folder>` allows a separate restore. Original absolute paths in historical recipes are provenance from this workstation: resolve the relative `exports/...` paths below against your new checkout.

## Current decision and files

- **Accepted atmosphere balance:** environment V2, wind and ventilation +3 dB relative to V1. User: “Enough—keep this level.” This accepts the plateau balance, not a full nine-minute/all-day session or final video.
- **Music:** the approved nine-minute Shelter/Outpost pair is unchanged. The portable archive includes its exact original FLAC/MP3, current artwork V5 and original wind file, restored from production commit `aa62e427e3f6386217e90229c063820c8f54ccae`.
- **Radio:** fourteen distinct blurred synthetic phonetic transmissions, irregular quiet gaps, receiver opening/closing clicks, gated hiss/carrier and five acknowledgements. No film/reference audio was sampled.
- **Optional B/C:** B changes only wind variation; C adds two procedural settling creaks. The user says the creak needs work and suggests ElevenLabs. No B/C winner or wind preference was selected. V2 stays current.

After restoration, use:

| Purpose | File relative to repo |
| --- | --- |
| Approved balance, complete audition | `exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-radio-wind-and-ventilation-9min-v2.mp3` |
| Approved balance, lossless parent | `exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-radio-wind-and-ventilation-9min-v2.flac` |
| Accepted plateau check | `exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-environment-v2-plateau-check-66s.mp3` |
| B, wind variation only, lossless comparison base | `exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/B-wind-only/Snowline-wind-variation-9min-test.flac` |
| Previous C check, first creak at 0:37 | `exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2/C-wind-and-creaks-90s-check.mp3` |
| Original approved dry music | `exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.flac` |

[Current preset](../../creative/music/sound-design/receiver-2026-11-02/snowline-ambience-preset-current.json) · [Exact approval](../../creative/music/sound-design/receiver-2026-11-02/environment-v2-balance-approval.json) · [Full history and links](../../creative/music/sound-design/receiver-2026-11-02/README.md) · [Living learning guide](../../creative/LEARNINGS.md).

## Next step: manual ElevenLabs creak test

Open **Sound Effects** and copy [the exact isolated steel-frame creak prompt](../../creative/music/sound-design/receiver-2026-11-02/elevenlabs-settling-creak-v1.txt). Proposed settings: **4 seconds, looping off, UI default prompt influence for the first batch, WAV 48 kHz if available**. Record the actual model, settings, cost and export; these have not yet been observed. No generation or credit spend has occurred in this session.

Choose two distinct useful takes if the returned batch provides them. Keep the original exported bytes and generation details; then audition replacement creaks at **1:31 and 5:38** on the same B base. Judge attack, material body, natural tail and level in context. Old procedural source gains do not automatically transfer to generated files. Compare against B without creaks and old C; update the current preset only after user selection.

**Keep snow/wind separate from the creak.** Existing wind supplies the broad exterior bed. [Optional snow-grain surface detail](../../creative/music/sound-design/receiver-2026-11-02/elevenlabs-spindrift-detail-v1.txt) is a separate, unselected proposal: 6 seconds, looping off. “Snowdrift” describes a visible form; the prompt describes grains skimming a ledge. Earlier [receiver-bed](../../creative/music/sound-design/receiver-2026-11-02/elevenlabs-receiver-bed.txt) and [garbled-transmission](../../creative/music/sound-design/receiver-2026-11-02/elevenlabs-garbled-transmission.txt) prompts are also saved as alternatives, not mandatory new generations.

[Prepared prompt/settings record](../../creative/music/sound-design/receiver-2026-11-02/elevenlabs-creak-test-preparation.json) · [Wind/creak test method and feedback](../../creative/music/sound-design/receiver-2026-11-02/wind-and-creaks-test.md).

## Tools and reproducibility

The archive includes all locally authored receiver versions, voice pools, packets, stems, mixes, optional tests and internal trials, including intermediate listening passes. Existing files stay intact. `media-manifest.json` records each original relative path, byte size and SHA-256. Music/wind originals already existed on the production branch; including exact copies here makes this checkpoint self-contained. It does not create a new artistic approval.

For rendering/analysis on a new machine, create an isolated environment with Python 3.13 (the recorded runtime), then install the pinned three-library audio requirements:

```powershell
python -m venv .local/audio-analysis
.local/audio-analysis/Scripts/python.exe -m pip install -r music/snowline-sound-design-2026-11-02/requirements-audio.txt
.local/audio-analysis/Scripts/python.exe scripts/render_snowline_wind_and_creaks.py --parent exports/sfx/snowline-receiver-2026-11-02/environment-session-v2 --wind exports/restored-snowline-2026-11-02/wind-soft-exterior-01.mp3 --out exports/sfx/snowline-receiver-2026-11-02/new-wind-creak-test
```

Use a fresh output directory; renderers refuse overwrites. Restored voice WAVs avoid depending on another computer having the same Windows voices. The PowerShell voice-generation tools use installed Windows speech voices only when explicitly rerun. Full reconstruction commands for radio/environment are in the case README. A later hour needs a longer radio arrangement; do not simply repeat this nine-minute SFX score.

Analysis tools, tests, compact reference measurements and full non-audio reports are committed. Downloaded WINTER WATCH audio and its filtered audition clips remain outside this backup, as in the earlier research backups. Supply a local reference recording to rerun **Inspect Radio Texture.cmd**; a later live DVR excerpt is not the same original sample. No all-day listening result, semantic sound recognition or short reference loop was established. No new video was assembled.
