# Crater Rim accepted audio backup — November 7, 2026

The user accepted the presented mix and requested commit/push on main. This checkpoint preserves both original music files, all five listening/scene reviews, the unchanged mix renderer, exact settings, source measurements, approval and current scene records. Seven new media files use exact Git LFS paths. Existing library wind and the V5 visual minute are included in the verification inventory.

Full-hour MP3/FLAC and stems remain local under `exports/14-crater-rim-survey/audio-1h-v1/`, following `EXPORTS.md`. Their exact sizes and hashes are in the production package's `delivery-validation.json`; this Git backup is the sources, reviews and rebuild recipe, not an archive of those long exports. Original files and local scratch are retained. The long visual schedule, final video and publication remain pending.

## Restore on another PC

Pull main in an ordinary checkout. From the repository root, restore only this scene's media:

```powershell
$craterAudio = Get-Content music/production-backup-2026-11-07-crater-rim-audio/selection-policy.json -Raw | ConvertFrom-Json
$craterPaths = @($craterAudio.new_media_lfs) + @($craterAudio.existing_media_dependencies)
git lfs pull --include=($craterPaths -join ',') --exclude=""
```

Use Python 3.12.10, the pinned NumPy/SciPy versions in `music/crater-rim-production-2026-11-07/requirements.txt`, and FFmpeg 9.0 (full Gyan build) on PATH. `runtime-snapshot.json` records exact FFmpeg/ffprobe hashes. FFmpeg needs FLAC, libmp3lame, AAC and loudnorm; ffprobe is needed only for historical analysis. Source SFX are restored from the library, never the louder listening-preview copies. Room air is fully generated in the saved renderer; no paid generation or Snowline source is required.

Run the read-only input/runtime preflight:

```powershell
python music/crater-rim-production-2026-11-07/rebuild.py --scene-review
```

To reconstruct the hour, stems, listening checks and optional scene preview into NEW destinations:

```powershell
python music/crater-rim-production-2026-11-07/rebuild.py --build --scene-review
```

Allow at least 10 GB free. The wrapper rebases preserved sources to this checkout, directs new records/cache into a unique `.local/crater-rim-audio-rebuilds/` run and audio into a unique `exports/14-crater-rim-survey/audio-restored-*` directory. It keeps the original accepted renderer unchanged, avoids overwriting backed-up reviews, runs the renderer's full checks and compares all reconstructed output hashes with the accepted files. A mismatch is reported for review, never silently adopted. Do not invoke `build_mix.py` directly over existing outputs. Historical analysis scripts record the original machine's Downloads and scratch locations and are evidence rather than the portable entry point. The wrapper preflight was tested here; a complete second-hour rebuild was not run during this backup.

## Remote verification

`selection.json` defines the exact scope, and `backup-manifest.json` records working-file and staged Git-blob hashes, distinguishing ordinary Git from LFS. The manifest excludes its own hash. After pushing, run:

```powershell
python music/production-backup-2026-11-07-crater-rim-audio/verify_remote.py
```

The verifier fetches the exact remote commit into a separate per-run `.local/restore-scratch/` folder and downloads only the selected LFS objects into a fresh private store. It checks Git blobs and full media hashes, writes the actual result to ignored `remote-backup-verification.json` outside scratch, then removes only its verified run folder. This checks backup recovery, not continuous listening or a new full video render.
