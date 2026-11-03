# Resume Snowline — two-hour V6 with both snow takes

Current continuation,2026-11-03. The user requested another1dB snow reduction, reuse of a second supplied take, a new two-hour mix with snow around every5minutes, and commit/push of everything from today. Branch:`codex/concept-brainstorms-2026-10-27`. Full-session/new-take listening remains pending; no video was assembled.

## Pull and restore

On this branch, from the Colony checkout:

```powershell
git pull --ff-only
git lfs pull --include="music/snowline-sound-design-2026-11-02/snowline-session-media.zip,music/snowline-sound-design-2026-11-03/media-*.bin,music/snowline-snow-2026-11-03/snow-delta-*.bin,music/sfx-library/assets/*.mp3,music/sfx-library/previews/*.mp3"
python scripts/restore_snowline_session.py
python scripts/restore_snowline_nov3.py
python scripts/restore_snowline_snow_session.py
```

**Resume Snowline.cmd** runs all three restores and opens this guide. Preserve local work before switching branches; if needed, `git fetch origin` then `git switch codex/concept-brainstorms-2026-10-27`. Python3.11+ and Git LFS suffice to restore/listen. The two new original snow MP3s are small ordinary Git assets, directly available after pulling.

Restores skip identical files, verify package and per-file hashes, and refuse different existing files. For a separate restore, pass `--root C:/an-empty-folder` to each script. `--verify-only` audits a completed restore. The snow continuation links its verified base packs into a temporary workspace and uses the same byte-checked restore engine; it does not modify the base media. A copy fallback supports filesystems without hard links.

## Latest audio and levels

Listen to `exports/13-below-the-snowline/audio-2h-v6/Below-the-Snowline-2-Hours-v6.mp3`: exactly7200seconds,48kHz stereo192kb/s,−23.0LUFS/10.2LU LRA/−7.5dBTP. SHA-256:`0c1e97b58cd353834aa58412ed6c6ac4324fa14512d4e15bdf0a5b706489c83f`.

The separate `Below-the-Snowline-2-Hours-unfaded-master-v6.flac` has SHA-256:`6c46365081e88d55b198387ea0b53259b7a90b12181e279ddb6dc12e8f474257`. It is the unity V5-plus-snow sum, without playback gain or opening/closing fades. Apply+0.4dB once to match the MP3, and apply the current intro/closing once during assembly. Every SFX layer is already present.

- **Existing layers:** music,47radio calls,80wind passages,24creaks and ventilation retain V5 exactly. Radio stays−1.5dB versus V4, wind+2dB versus V4, creaks+4dB versus the first two-hour mix. The nine-minute music/vent source recurrence remains.
- **First snow take:**+2dB versus its initial placement,1dB below the last+3dB test. Earlier+9/+7/+5/+3 comparisons are history, not gains to add again.
- **Second snow take:** separately calibrated after the same2800Hz filter and20/80ms edges, to match the reduced first take's event-wide RMS. This is a starting match, not proof of equal perceived loudness or user approval.
- **Snow timing:**24ten-second passages total, alternating the two takes12times each. Starts243.47–359.88seconds apart, average295.38seconds. All sit within selected wind plateaus with at least6seconds clearance from radio/creaks. First snow is3:44.783; second take first appears8:18.686. Full cue sheet is in the delivery folder and case records. No five-minute composite loop is tiled.

[Exact V6 recipe/full checks](../../creative/music/sound-design/receiver-2026-11-02/two-hour-with-snow-v6-2026-11-03.json) · [Current settings](../../creative/music/sound-design/receiver-2026-11-02/snowline-working-mix-current.json) · [Sound-design lessons](../../creative/music/sound-design/receiver-2026-11-02/REUSE.md) · [SFX library](../sfx-library/index.html).

## Sources and backup scope

Original library files:

- `music/sfx-library/assets/snow-grains-ledge-01.mp3`: user take#2,241,389bytes, SHA-256`58bb38ca9b8447b0cbdd1a389a756896244d7e54198517af4afdd9d6ab98346e`.
- `music/sfx-library/assets/snow-grains-ledge-02.mp3`: user take#3,241,389bytes, SHA-256`91b720bfa80a6aeda743cf8419ca1e01105cca460e071ad162f24e2cf50fb562`.

Both decode to10seconds. Prepared prompt suggested6seconds; executed provider/model/prompt/settings/cost remain unknown. No new paid generation was performed. Browsing previews have separate gains and are not mix presets.

The earlier checkpoint preserves271files/11,396,047,312bytes unchanged. This continuation preserves **all68later exports/1,404,360,837bytes**, including every snow audition/gain step, source copy, stem, full V6, previews, meters and cue sheets. The index reuses exact binary chunks from the already-backed base packs; only150,864,785new payload bytes are stored in `snow-delta-001.bin`. No audio re-encoding occurs during backup. `media-manifest.json` records every file and the required base-pack hashes/locations.

Four new backup tests cover shared-byte reuse/round trips/idempotence, conflicting local files, corrupt payloads and unsafe/duplicate metadata without modifying base packs. The renderer checks all345,600,000frames: exact V6=V5+snow, exact preservation outside snow windows, exact snow PCM cue plan, finite samples and no clipping. These checks establish delivery integrity, not a listening verdict. See `backup-verification.json` for actual remote evidence after push.

## Animation status

The November production branch already has [Snowline animation V2](https://github.com/BAcommander/colony/blob/aa62e427e3f6386217e90229c063820c8f54ccae/music/below-the-snowline-animation-v2/README.md):20-second720p loop with snow/mist/steam, monitor/base/room activity and corrected dish masking. It needs user review; there is no4K/full-video assembly. That production tree was not merged here. Do not use this checkout's historical “no animation” preparation status to assume the V2 work is missing.
