# Local exports and media storage

Long finished video/audio and local source-audio copies live under `exports/`, which is ignored by Git. This folder remains on this computer but will not appear after cloning. No export was deleted or transcoded during the move; hashes were verified before and after.

- `exports/01-ringfall-observatory/`: Ringfall video and one-hour soundtrack, plus original generated audio/video under `source/`.
- `exports/02-basalt-transmission/`: Basalt video and two-hour soundtrack, plus original generated audio/video under `source/`.
- `exports/previews/`: local review clips.

Tracked inventory: `final/local-export-inventory.json` records paths, sizes and SHA-256. Keep a separate external-drive/cloud backup of these files, especially generated soundtrack originals, which cannot be recreated identically by rerunning a prompt. No separate backup has been performed in this task. Git push does not upload ignored files.

Keep code, prompts, settings, thumbnails, descriptions, feedback, validation and inventories in Git. Existing approved short visual masters retain their exact Git/LFS rules and paths under `creative/` and `final/`. The small restored green-screen subscribe MP4 is explicitly tracked as a draft asset; that is backup status, not creative approval. Large repeated deliveries do not need LFS.

For future final deliveries use `exports/<scene>/`. Keep tracked manifests beside scene documentation under `final/<scene>/`. A moved export must be selected again if an editor still references its old path. The existing `final` folders now contain production packages and short masters, not the long upload files.

## Restore verification and cleanup

- Run each backup verification in its own folder under `.local/restore-scratch/`. When a script owns the scratch folder, use a temporary directory or explicit success cleanup. Put the receipt outside the scratch folder and record the source commit, asset sizes and SHA-256 results before removing the verified copy.
- After a successful check, remove that run's checkout, extracted media and private LFS cache. Keep a failed run only while diagnosing it. Check that the resolved path is the exact run folder under the intended scratch root and that no transfer or restore is active.
- Keep one working copy of the approved master and the original music and SFX. Archive originals and long masters separately, with the archive location, file sizes and SHA-256 in the scene manifest. Verify a restore from that archive before retiring its local copy. Keep one short review preview and the build recipe in Git by default.
- Treat `.git/lfs/tmp` as transfer scratch and `.git/lfs/objects` as the local object store. For the object store, run `git lfs prune --dry-run --verify-remote --verify-unreachable` first. If every candidate verifies and the store belongs to this checkout, rerun without `--dry-run` to prune. Preserve any object that fails the remote check.

## Download only the scene you need

On each machine, run these commands once from the Colony checkout to enable on-demand media and require remote checks before pruning. The options apply to this checkout and preserve its push hook.

```powershell
git lfs install --local --skip-smudge --skip-repo
git config --local lfs.pruneverifyremotealways true
git config --local lfs.pruneverifyunreachablealways true
```

Pull `main` as usual, then use the scene's exact `git lfs pull --include="..."` command before opening or restoring its media. A small LFS pointer in the checkout means that asset still needs to be fetched. The [Snowline resume guide](music/snowline-snow-2026-11-03/RESUME.md#pull-and-restore) lists its required paths.

## November 4, 2026 cleanup

Removed nine verified restore and round-trip folders from the working checkout. The checkout's file sizes fell from 118.3 GB to 73.2 GB. The removed folders contained 40.3 GB of distinct file data after accounting for hard links. LFS transfer scratch was already empty at the start of cleanup. The LFS remote check could not verify three candidate objects totaling about 3.5 GB, so their local copies were retained. The current Snowline two-hour MP3 and FLAC both matched their saved SHA-256 hashes after cleanup.
