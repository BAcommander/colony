# Ringfall Observatory — local animation

## Latest review export: original ambience v7b

The user rejected spacecraft. Current review exports are ringfall-ambient-v7b-preview.mp4 and ringfall-ambient-v7b-final.mp4: ten seconds,30fps,silent,4K final from upscaled source. Independent steam, laptop scan, moving colony ground-lights/windows and subtle procedural planetary clouds preserve the original scene. Numeric seam/static geometry checks pass; sampled-frame review completed, user artistic review pending. Prompt: [ambient-v7-prompt.md](ambient-v7-prompt.md). Renderer: scripts/render_ringfall_v7.py. Videos remain local.

## Historical direction: regional AI motion

No animation is approved as a final. v6 was rejected as too subtle. Two free local Wan tests produced more motion but distorted the scene; see [findings](wan-tests/README.md). The next task is the [isolated planet pass](next-planet-pass-prompt.md), not yet implemented. Experimental video files remain local and are excluded from Git; their settings and reports are tracked.

## Historical: layered v6

[Play the 4K MP4](ringfall-v6-b-final.mp4) — ten seconds, 30 fps, silent, approximately 24.1 MB; upscaled from the existing source artwork. [720p preview](ringfall-v6-b-preview.mp4).

Includes moving planetary cloud-band detail, two sweeping ground lights at the colony, linked faint window reflections, volumetric mug steam, laptop scan/telemetry and the mast beacon. The camera and solid geometry stay fixed. Per-layer mask/phase checks and decoded loop checks passed; the user subsequently rejected the result for insufficient noticeable movement.

Renderer: ../../../scripts/render_ringfall_v6.py. Parameters: [scene-v6.json](scene-v6.json). Reusable masks: masks-v6/. Results: [validation](ringfall-v6-b-final-validation.json), [layer checks](ringfall-v6-b-final-layer-checks.json), [render manifest](ringfall-v6-b-final-manifest.json).

## Previous revisions

Previous v5: [ringfall-loop-v5-4k.mp4](ringfall-loop-v5-4k.mp4). User rejected its limited scene-wide activity. Ten seconds, 30 fps, 3840x2160, silent, approximately 5.66 MB. Upscaled from the 1672x941 still; not native 4K image detail.

Current validation: [v5 measurements](ringfall-loop-v5-4k-validation.json) and [effect phase samples](ringfall-loop-v5-4k-detail-check.png). Confirmed 300 decoded frames, ten seconds, correct dimensions, and a loop boundary within ordinary frame-to-frame movement. Source frame pixels outside overlay patches are unchanged before encoding.

Previous deliverable, retained for comparison: [ringfall-loop-v4.mp4](ringfall-loop-v4.mp4).

Ten seconds, 30 fps, 1920x1080, no audio. Source still is 1672x941, resampled for a standard 1080p export. All animation is generated locally from three small overlays: delicate mug steam, dim laptop telemetry, and an existing distant mast lamp. Everything else stays stationary.

The final file uses H.264 QP0 coding after YUV420 conversion, preserving subtle frame changes. A player that does not support this H.264 profile may need a compatibility export; preserve this validated file as the master. No paid tools or services were used.

The current creative brief and user preferences are in ../../../AGENTS.md. The reusable renderer is ../../../scripts/render_ringfall.py. It refuses to overwrite an existing final video; change the version stem when making a new revision.

Validation: [measurements](ringfall-loop-v4-validation.json), [effect detail samples](ringfall-loop-v4-detail-check.png), and [poster](ringfall-loop-v4-poster.png). Exact duration and frame count verified; all effects are periodic, and the decoded loop-boundary change is within ordinary adjacent-frame variation. Media continuity is distinct from a player's buffering at playback restart.

The drafts folder contains earlier encoding experiments, not approved deliverables. Source images, scripts, prompts and reports are versioned in Git; experimental video files stay local.
