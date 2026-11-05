# Crater Rim continuation checkpoint — 2026-11-05

Authority: the user requested saving all details needed for the longer version, then committing and pushing. Work stays on `main`.

Start with [the continuation guide](../crater-rim-animation-v5/LONG_VERSION.md). It preserves the V5 visual baseline and an explicit proposed ten-minute attention-event schedule. The longer renderer, soundtrack selection, final runtime and 4K/full-length production remain pending.

The backup includes V2–V5 code, exact settings/dependencies, useful internal history records, feedback and validation, selected source-scale/decoded evidence, updated shared learnings and scene records. The exact V5 minute and full-size V4/V5 comparison use two narrowly scoped LFS paths. Original scene artwork, music prompts and workflows are existing Git dependencies and are included in the verification inventory. Most redundant PNGs, old/intermediate/repeated MP4s, long exports and caches remain local. No local media was deleted.

[Selection policy](selection-policy.json) · [Exact selected paths](selection.json) · [Git/LFS hash manifest](backup-manifest.json). The manifest excludes itself to avoid a recursive hash. The remote verifier checks that self-excluded manifest separately.

After the content commit and push, run `python music/production-backup-2026-11-05-crater-rim/verify_remote.py`. It obtains the exact remote commit in isolated `.local/restore-scratch/`, checks every selected Git blob, downloads only the two media objects into a fresh LFS store, materializes the selected resume package and executes its source/media/plan check plus six native V5 frames. It records actual evidence in local ignored `remote-backup-verification.json`, then removes the completed scratch run, including its private Git/LFS cache. It verifies this selected package rather than cloning and testing every project asset.
