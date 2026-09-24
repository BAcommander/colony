# Ringfall Observatory — local animation

## Approved final

User-approved on 2026-09-24: [4K v9b MP4](ringfall-ambient-v9b-20s-final.mp4). Twenty seconds, 30 fps, silent; upscaled source artwork. This final video is tracked in Git at the user's request. See [acceptance and hash](approved-v9b.json). V9b is the accepted reference for future scenes. Earlier sections below describe historical review states; draft videos remain local.

## Latest review export: v9b colony exhaust and ring material

Twenty seconds, 600 frames, 30 fps, silent. Local exports: ringfall-ambient-v9b-20s-preview.mp4 and ringfall-ambient-v9b-20s-final.mp4 (3840x2160, upscaled source art). Original still left/candidate right: ringfall-v9b-original-comparison.mp4. Adds two directed roof exhaust plumes, four independently scheduled window on/off states and angular ring-material texture transport through a fixed mask. Preserves previous ambient layers and exports.

Renderer: ../../../scripts/render_ringfall_v9.py. Brief: [v9](ambient-v9-final-brief.md). Preview and final numeric checks passed: duration, frame count, periodic endpoint, static pixels before encoding and seam within ordinary motion. Full-scene and enlarged temporal samples inspected; no continuous playback review or user artistic approval yet. Initial v9 left white window cores lit; v9b corrects that aperture mask. Initial v9 artifacts are historical drafts, not current exports. Videos stay local; code, masks, settings and reports are tracked.

## Latest review export: twenty-second ambience v8

Exports: ringfall-ambient-v8-20s-preview.mp4 and ringfall-ambient-v8-20s-final.mp4. Twenty seconds, 600 frames, 30 fps, silent; 3840x2160 final upscaled from the original artwork. Adds slow material variation within the lit ring bands and five phased distant colony lights. Retains steam, laptop telemetry, planetary cloud detail and colony ground lighting. Ring geometry stays fixed. This is a genuine twenty-second cycle, not two repeated ten-second clips.

Numeric endpoint, static-region and encoded seam checks passed. Sampled frames, including a decoded final frame, were inspected; continuous playback and user artistic review remain pending. Prompt: [ambient-v8-20s-prompt.md](ambient-v8-20s-prompt.md). Renderer: ../../../scripts/render_ringfall_v8.py. Videos remain local; reusable code, settings and reports are versioned.

## Preferred baseline: original ambience v7b

The user rejected spacecraft, then described v7b as much improved, subtle and without broken or janky motion. Preserved baseline exports are ringfall-ambient-v7b-preview.mp4 and ringfall-ambient-v7b-final.mp4: ten seconds,30fps,silent,4K final from upscaled source. Independent steam, laptop scan, moving colony ground-lights/windows and subtle procedural planetary clouds preserve the original scene. Numeric seam/static geometry checks pass. Prompt: [ambient-v7-prompt.md](ambient-v7-prompt.md). Renderer: scripts/render_ringfall_v7.py. Videos remain local.

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
