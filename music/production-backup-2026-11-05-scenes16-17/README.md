# Scene16/17 visual-draft backup

User explicitly requests commit/push of the full checkpoint on main. `selection.json` inventories the exact scope and existing source dependencies; `backup-manifest.json` binds working files to staged Git blobs and media to LFS object hashes. It excludes itself from its file list.

Both complete one-minute drafts and all eight linked detail/join clips are included, along with source art/repairs, generated assets and prompts, renderers/settings, validation, source plans and learnings. The unlinked eight-second gate proof, older city proofs, `.local` render history/caches and bytecode stay local. No long or4K export was produced in this checkpoint. Artistic review remains pending.

After pulling main, restore just these review videos with:

```powershell
git lfs pull --include="music/cyberpunk-apartment-animation-v4/*.mp4,music/gate-camp-animation-v3/*.mp4" --exclude=""
```

The include patterns cover only these two version folders; Git can restore only their ten tracked review files. Then open `creative/animation-development/2026-11-05-16-17/review.html`. Render from the pinned source/settings for later revisions, with new output names.

`verify_remote.py` verifies the advertised main commit, restores selected Git blobs from a fresh remote fetch and downloads each selected LFS pointer into independent storage. It checks sizes/hashes, runs both restored renderers' geometry/link checks and removes only its verified run folder under `.local/restore-scratch/`. Its post-push receipt remains local and ignored.

`prepare_backup.py` is a once-per-checkpoint preparation script; do not rerun it over a finalized checkpoint. `build_manifest.py` reads the staged selection before the commit. Neither script pushes automatically.
