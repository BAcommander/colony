# Resume Snowline: current two-hour V5 and reusable sound assets

Checkpoint 2026-11-03, branch `codex/concept-brainstorms-2026-10-27`. The user explicitly requested commit/push of everything from this sound-design session, including the supplied creak and lessons for future videos. Shared main is unchanged.

## Pull and restore on the other machine

From your Colony checkout on this branch:

```powershell
git pull --ff-only
git lfs pull --include="music/snowline-sound-design-2026-11-02/snowline-session-media.zip,music/snowline-sound-design-2026-11-03/media-*.bin,music/sfx-library/assets/*.mp3,music/sfx-library/previews/*.mp3"
python scripts/restore_snowline_session.py
python scripts/restore_snowline_nov3.py
```

If needed, first `git fetch origin` and `git switch codex/concept-brainstorms-2026-10-27`, preserving any local uncommitted work. **Resume Snowline.cmd** now runs both restores and opens this guide. Python 3.11+ and Git LFS are sufficient for restoring/listening; the audio render environment is not required. The new original creak is a small ordinary Git asset and is immediately available after pulling.

Both restores verify package and per-file SHA-256 hashes, skip identical files and refuse to overwrite conflicting local work. Use `--root C:/an-empty-folder` on both scripts for a separate restore, or `--verify-only` to audit an existing one. The November 2 archive supplies earlier music, wind, voices, receiver and ventilation dependencies; November 3 adds every new export from this continuation.

## Current result and next action

- Listen to `exports/13-below-the-snowline/audio-2h-v5/Below-the-Snowline-2-Hours-v5.mp3`: exactly two hours, fixed +0.4 dB playback gain, no baked opening and one 20-second closing fade. SHA-256 `aa19b58ed32c32bad07d7b19973f1bac615f8a4441ce54c0c8783f44b42d2d3e`.
- Lossless assembly source: same folder, `Below-the-Snowline-2-Hours-unfaded-master-v5.flac`. SHA-256 `4b4843823fbd032e3368f6945d94a600b8b97062b56779b15f9f48b3953b60c4`. Unity-stem sum, no entrance/closing fades or +0.4 dB playback gain. Match the audition by applying +0.4 dB once; apply the current intro and closing once. All SFX are already mixed in.
- **47 calls**, voice starts 122–176 seconds apart; **80 wind passages**, 22–31-second off gaps; **24 creaks**. Current levels: wind +2 dB and receiver −1.5 dB relative to V4, with V4 creaks retained (+4 dB versus two-hour V1). These changes are already applied.
- Nine-minute music/vent sources repeat. Fourteen receiver packets, one wind recording and one creak take are reused; a full two-hour SFX cue schedule does not imply two hours of unique source recordings.
- **Next: full two-hour user listening.** Settings were selected for this full render; full-session comfort remains pending. No new video assembly or paid generation was performed.

[Reusable lessons and current balance](../../creative/music/sound-design/receiver-2026-11-02/REUSE.md) · [Machine-readable current settings](../../creative/music/sound-design/receiver-2026-11-02/snowline-working-mix-current.json) · [Full case history](../../creative/music/sound-design/receiver-2026-11-02/README.md) · [SFX library](../sfx-library/index.html).

## Original creak and library

`music/sfx-library/assets/creak-painted-steel-frame-01.mp3` preserves the user-supplied MP3 byte for byte: 97,389 bytes, four decoded seconds, SHA-256 `8d126f0c72a3b2e991ba7e56347da2364d191823c12077d0e61d3eccf77f8ea6`. The catalogue saves provenance, measured duration/levels, source-specific gain history, contextual use and a browser preview. The prepared ElevenLabs creak prompt is a related brief; actual executed prompt/model/settings/cost remain unknown. The same take is used with two balances, not two independent recordings.

The six existing library sources and previews were imported exactly from production commit `aa62e427e3f6386217e90229c063820c8f54ccae`, without merging its production tree. Earlier library records remain distinct from the Snowline selection. Browser previews are listening aids, not mix gains.

## Exact media scope and format

`media-manifest.json` lists **all 271 files / 11,396,047,312 original bytes** under:

- `exports/sfx/snowline-creak-2026-11-03/`
- `exports/sfx/snowline-18min-2026-11-03/`
- `exports/13-below-the-snowline/`

This includes original/source copies, all stems, nine-/18-minute auditions, full two-hour V1–V5, level-test windows, recipes/meters/cues and the interrupted internal-path-check attempt. Nothing from those roots was excluded. Earlier November 2 media remain in their already-backed archive. Downloaded external reference recordings remain outside these session-media backups, as previously documented.

Seven `media-001.bin`…`media-007.bin` LFS files plus `media-index.json.gz` store the new exports in **3,766,051,376 bytes**. Repeated content-aligned binary chunks are stored once; there is no codec conversion, resampling or sound change. The gzip JSON index maps each original file to pack offsets; the readable manifest records full-file and pack hashes. `scripts/restore_snowline_nov3.py` implements reconstruction with Python's standard library. `build_media.py` preserves the exact packaging method; rerun it only into a fresh output folder.

The restore tests cover exact duplicate/offset-shifted/empty-file recovery, multiple packs, idempotence, conflict refusal before writes, corrupt packs and path traversal. A full local 271-file restore passed. See `backup-verification.json` for actual remote download/restore evidence after push; a local package alone is not remote verification.

## Continuing sound work

All eight November 3 render/audition scripts are retained under `scripts/`, with earlier implementation snapshots in the case `history/`. Use a fresh output directory; historical recipes retain this machine's absolute provenance paths. New tools accept a checkout root and use relative output references where implemented. Restored packet/voice WAVs avoid depending on the next machine having the same installed Windows voices.

For rendering, use the existing isolated Python environment or the pinned requirements in [the November 2 guide](../snowline-sound-design-2026-11-02/RESUME.md). Do not regenerate approved music, reapply historical pending gain adjustments, overlay the SFX twice, or treat old nine-minute environment settings as the current two-hour event schedule.
