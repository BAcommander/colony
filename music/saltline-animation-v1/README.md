# Saltline Receiver — accepted v5 preview

Current production: [one-minute 4K loop v7](LOOP_V7.md) implements the requested longer, irregular hut off periods from this accepted look. The new minute-long delivery awaits user review; v5 remains the accepted baseline below. [Twenty-second v6](LOOP_V6.md) is preserved.

User accepted the current look on 2026-09-29: “perfect, commit and push everything”.

Accepted review video: [saltline-v5-combined-12s.mp4](saltline-v5-combined-12s.mp4). Twelve seconds, 1280×720/30 fps, silent. This is a forward-motion preview, **not a seamless loop or 4K master**. Native artwork is 1672×941; future 4K will be upscaled. No soundtrack has been generated.

The accepted look retains moving upper clouds and textured far dust across the salt basin. Staggered incoming gusts keep the distant dust present after the original gusts leave view. Foreground road dust is removed following user rejection. Two foreground rooms and two ridge habitats have independent complete-window events with small attached spill; most lights stay steady. The service lamp has restrained dips. A localized passing cloud shadow affects the left sunlit dry crust; the sun and global exposure stay fixed.

[approved-v5-preview.json](approved-v5-preview.json) records exact feedback, approval scope and immutable source/config/code/mask/media hashes. [combined-v5-validation.json](combined-v5-validation.json) records all 360 decoded frames, sequential timestamps and per-source-frame protected-pixel assertions. Assistant inspection was through temporal/decoded stills; user acceptance is recorded separately. No seam gate has been claimed for this non-loop prototype.

## Reproduce

Use the existing local Python 3.12 installation with NumPy, Pillow and OpenCV, plus FFmpeg at the path in [scene-plan-v5.json](scene-plan-v5.json). From the repository root:

```text
python music/saltline-animation-v1/render_saltline.py --stage combined --config scene-plan-v5.json
```

The renderer preserves existing destinations. The accepted preview should be restored from Git rather than overwritten. For a fresh rerender, use a new trial version/output name in a new configuration; preserve v5. The adapter imports the existing scripts/render_floodplain.py encoder/validator and scripts/ambient_effects.py; its new dust method is dust_transport.py. Saltline masks are scene-specific and source-bound, not copied from another scene.

Exact imported code bytes are preserved in `dependency-snapshot/`, including the water module imported by the reused Floodplain adapter. Existing root-script Git rules can normalize their line endings; the snapshots and scene configs use narrow attributes to preserve the recorded hashes. For a hash-bound reproduction in a separate scratch checkout, restore these snapshots to their original `scripts/` paths before running. Preserve the current production checkout and approved files. Snapshot paths/hashes are recorded in the acceptance and validation manifests.

## Next production step

Review the requested v7 one-minute 4K delivery and its longer independent hut light events. The atmosphere preserves v6's local periodic cloud, dust and sunlight transport at unchanged speeds. The user explicitly requested commit/push on 2026-09-30; the exact short master uses a narrow Git LFS rule, with independent remote restore/hash evidence in `remote-backup-v7.json`. This backup request does not imply artistic acceptance of the new timing. No soundtrack has been generated.

## History and backup

Original art, preparation masks, configs v1–v5, generation helpers, diagnostic images, reports and exact rejection feedback remain preserved. [The archived review record](history/README-through-v5-review.md) records prior versions. V1b/v2 dust was rejected as invisible; v3 far dust was accepted but foreground gusts were rejected as excessive/fake. V4 retained the exact distant dust for the shared eight seconds, but longer playback lost coverage; v5 adds replacements. The audit and sample comparison reports remain here.

The accepted 8.3 MB v5 preview is backed up in ordinary Git using one exact-path ignore exception. Rejected draft videos and long exports remain ignored local files. A Git push does not back up ignored media, caches or runtimes.
