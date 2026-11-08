# Crater Rim final production backup — November 8, 2026

The user accepted the **CRATER RIM short-title V2** and explicitly requested: “looks good, commit and push all the crater rim work”. This checkpoint is on **main**. It preserves the completed production, approved thumbnail, scene-only alternative, upload copy, original inputs, exact generation prompts, implementation and validation. It does not infer publication or full-video artistic approval.

## Exact scope

[selection.json](selection.json) enumerates this commit and existing restore dependencies. [backup-manifest.json](backup-manifest.json) binds every selected Git blob and LFS payload to its size and SHA-256. Original source music, wind and the accepted audio recipe were already backed up on November 7; they are verified again as dependencies here.

- The unique clean **600-second 4K master** is archived without remuxing/transcoding as four ordered raw LFS chunks, each at most 1,000,000,000 bytes. [master-chunks.json](../crater-rim-final-hour-v1/visual/master-chunks.json) binds their order and hashes. Concatenation restores the exact 3,408,440,080-byte MP4, SHA-256 `3bb88151f697bd2fbb93dde4b70737629d687df8856bef7c9259a23ff1f66ed8`.
- The actual **135-second final opening/scene review**, frozen V5 art/renderer, Colony opening engine/fonts, ten-minute timing, audio/assembly recipes, complete technical evidence and representative decoded stills are included.
- The accepted thumbnail, both generated PNG masters, JPEG exports, exact prompts, phone comparison, user approval and upload title/description/tags are included. Original art and earlier thumbnails remain preserved.
- Per [EXPORTS.md](../../EXPORTS.md), the **20,691,244,438-byte full-hour export**, prepared hour audio and regenerable native caches/parts stay local. Their production receipts/fingerprints are retained. No original or local export is deleted by this backup. This is not an external archive of the exact full-hour upload file.

Actual push and independent remote verification are recorded only in the ignored `remote-backup-verification.json` after completion. The verifier fetches selected Git blobs and exact LFS objects into fresh private storage under `.local/restore-scratch/`, checks every byte and the concatenated master, saves the receipt outside scratch, then removes its own successful scratch directory. It does not use the checkout's LFS cache or download unrelated media.

## Restore on another PC

Use the existing checkout on main; do not create a branch. Clone/pull with LFS smudging disabled as documented in EXPORTS.md. From the repository root, download only the exact paths listed in this backup:

```powershell
$craterManifest = Get-Content -Raw music/production-backup-2026-11-08-crater-rim/backup-manifest.json | ConvertFrom-Json
$craterLfsPaths = ($craterManifest.files | Where-Object storage -eq 'git-lfs' | ForEach-Object path) -join ','
git lfs pull --include=$craterLfsPaths --exclude=""
python -B music/production-backup-2026-11-08-crater-rim/restore_master.py
```

The helper requires Python 3.12 or later and no external Python packages. It checks every chunk and complete master hash, never overwrites a different existing destination, and creates `exports/14-crater-rim-survey/production-v1/restored-master-validation.json`. Only this new receipt rebases the current master/frame-evidence paths; the original validation remains unchanged. `--verify-only` checks without writing a master or receipt.

### Rebuild the approved audio and hour

Use Python **3.12.10** with the exact packages in `music/crater-rim-production-2026-11-07/requirements.txt` and `music/crater-rim-final-hour-v1/assembly/requirements.txt` (NumPy2.4.4, SciPy1.18.0, Pillow12.2.0). Put the recorded FFmpeg9.0 and FFprobe binaries on PATH; exact hashes are in the audio runtime snapshot. These binaries are external dependencies, not bundled executables.

```powershell
python -B music/crater-rim-production-2026-11-07/rebuild.py --build
```

The audio rebuild writes a new `exports/14-crater-rim-survey/audio-restored-<runid>/` folder and compares all original output hashes. It never overwrites the original package. Select its FLAC and verify SHA-256 **`333c0fe1b94ac899d0fa6a91ed009c693de312c791913a838662bf7433b5c994`**, size **484,181,535 bytes**, before copying it into the canonical `exports/14-crater-rim-survey/audio-1h-v1/Crater-Rim-Survey-1-Hour-music-and-SFX-v1.flac`. If a canonical file already exists, verify it; preserve any different file and stop. The optional `--scene-review` also needs the saved V5 minute; it is not required for final assembly.

Preserve historical assembly evidence before a new production run: the existing assembly scripts write new receipts/stills in place. Keep a byte-exact copy of `music/crater-rim-final-hour-v1/assembly/` in a new `.local/` history folder first, then run:

```powershell
python -B music/crater-rim-final-hour-v1/assembly/assemble.py --master-validation exports/14-crater-rim-survey/production-v1/restored-master-validation.json
python -B music/crater-rim-final-hour-v1/assembly/verify_final.py --video --audio --stills --hash --finish
```

The already-restored 135-second review is preserved; omit `--review`, which intentionally refuses to overwrite it. Preserve any existing full-hour output before reproduction. A rebuilt container must be checked by the saved picture/audio validators; do not claim identical full-hour bytes from a recipe alone. No long rebuild is needed merely to verify this checkpoint's backup.

For a native visual rerender, use the separate pinned visual environment in `source-snapshot/music/crater-rim-animation-v5/requirements-resume.txt` (NumPy2.4.3/OpenCV-headless5.0.0.93/Pillow12.1.1/imageio-ffmpeg0.6.0) and follow [the production guide](../crater-rim-final-hour-v1/README.md). Do not install the audio/assembly NumPy version into that visual environment.

## Verify a pushed checkpoint

After local main equals remote main, run `python -B music/production-backup-2026-11-08-crater-rim/verify_remote.py`. The fresh downloads total approximately 3.5 GB, plus selected Git blobs. The receipt records the commit, all checked paths, exact master reconstruction and successful scratch cleanup. This verifies archived bytes, not continuous playback/listening or YouTube checks.
