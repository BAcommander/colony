# Ambient Colony - project context

Last updated: 2026-09-26.

## Current authority

Glacier Sanctuary v10 was accepted: "ok i think we can go with this, extend it out into the 60 second loop ij 4k?" V11 is the requested sixty-second 3840x2160, 30 fps, silent delivery. See creative/glacier-sanctuary/animation/README.md for output and verification status. Its source remains 1672x941, so 4K is upscaled. Preserve the accepted water method, distant snow/fog, vent smoke and light effects; no foreground snow.

Ringfall v9b and Basalt v6 remain approved references. AGENTS.md holds working instructions; creative/NEXT_SCENE_RUNBOOK.md holds the reusable pipeline. Earlier production chronology is preserved in creative/history/project-through-glacier-v10.md. Historical pending-review entries do not supersede current acceptance.

## Purpose and creative direction

- Channel: https://www.youtube.com/@ambientcolony
- Repository: https://github.com/BAcommander/colony
- Workspace: C:/Colony
- Tagline: Sci-fi soundscapes for sleep, focus and study.
- Store original artwork, music and animations with their production notes. Ringfall has a generated one-hour listening master (long-form evaluation pending); Basalt has a reference analysis and test prompt. See creative/MUSIC_WORKFLOW.md.
- Quiet remote environments, detailed retro-industrial equipment, warm inhabited shelters against vast landscapes, photorealistic framing and visible but calm movement.
- Prioritize free local MP4 production from this chat. No paid plugins, cloud video services, API fees or purchased credits.

## Accepted reference packages

- Ringfall: creative/ringfall/04-laptop-refined.png and animation/ringfall-ambient-v9b-20s-final.mp4. Approved 2026-09-24. Twenty seconds, 4K/30 fps/silent. Ordinary Git exception for the final.
- Basalt: creative/basalt-transmission/animation/baseline-v6-loop-4k-master.mp4, with delivery-v6.json and remote-backup-v6.json. Twenty seconds, 4K/30 fps/silent. Git LFS.
- Glacier: creative/glacier-sanctuary/animation/scene-plan-v11.json and production-prompt-v11.md. Sixty-second delivery from accepted v10 look. See scene README and final-v11 reports.

## Initial concepts

Nine source concepts are saved under creative/concepts, indexed by its README: Dusk Relay, Glacier Sanctuary, The Last Lookout, Cloudline Control, Tidal Listening Post, Ringfall Observatory, Forest Signal, Below the Ice, and Basalt Transmission. A tenth concept, Night Shift Greenhouse, was planned but no saved image was found.

## Storage

Source art, code, masks, prompts, configuration, feedback and checks belong in Git. Approved large masters use exact-path LFS tracking with independent remote verification; restore with git lfs pull and compare manifest hashes. Draft/repeated MP4s, .local runtimes and model weights remain local. Preserve approved exports and never overwrite them during experiments.
