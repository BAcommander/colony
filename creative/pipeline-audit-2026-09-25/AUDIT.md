# Basalt motion pipeline audit — 2026-09-25

## Finding
The pipeline optimized periodic pixels and export correctness before proving readable motion. The user's repeated feedback is the artistic evidence: v2 invisible, v3 excessive middle-right smoke with static far/top, v4 too subtle again. No Basalt version is accepted. This audit does not claim continuous playback inspection; it uses source/history/configuration review and sampled/decoded-frame diagnostics.

## Evidence and causes
- source-inventory.json indexes 89 source, history, configuration and report files with hashes. Ringfall's approved-v9b.json and final MP4 establish its accepted reference; prior experimental success flags do not override rejection.
- Ringfall v9b provides localized recognizable actions: exhaust, whole-aperture window events and traveling ground light. Its protected ring field is stylized material motion, not a general cloud simulation. Transferring effect math did not transfer landscape motion design.
- render_basalt.py moves high-pass sky residuals after removing broad shading, blending two translated copies for periodicity. Broad cloud mass stays mostly fixed. Expanding its mask into featureless upper sky cannot create visible cloud features. This is an algorithmic diagnosis, not a claim that playback was inspected.
- Far haze is sinusoidal density modulation within shallow polygons. Near dust concentrates in another small region. More alpha changes contrast/opacity but does not establish convincing broad coherent wind transport; less alpha removes what was visible. Depth coverage and identifiable trajectories must be solved separately.
- Existing workflow already requested isolated effects and normal-speed review, but Basalt lacked a layer-isolation CLI and final exports did not enforce any recorded visual verdict. Still montages, endpoint equality and pixel changes were substituted for artistic review. Repeated long exports added time and storage without resolving that failure.
- Ringfall's earlier lossy-compression seam failure was repeated in Basalt before returning to a QP0 master. Historical learnings must become executable defaults/checks, not merely more prose.

## Changes delivered
Basalt frame rendering now exposes independent layers without modifying their strength/timing. motion_review.py makes full-frame eight-second sky, far-haze, near-wind and combined clips, checks frozen geometry before encoding, decodes every output frame, saves diagnostic change maps and hashes, and starts an explicitly pending review. Final/long-export commands reject missing/rejected/stale visual reviews. Approved Ringfall code/media remain untouched.

Change maps show where pixels vary, not perceived motion. Full-frame changed area and peak change are diagnostics with no artistic pass threshold. Actual playback and user verdict remain distinct from numeric validation.

## Next creative experiment
Do not call another opacity tweak v5. Prototype sky alone with a recognizable, broad soft cloud edge drifting consistently behind the protected moon and above protected mesas. Move coherent cloud structure rather than only its fine residual. Prototype far-valley wind separately as broad low sheets with identifiable leading/trailing density, correct terrain occlusion and sustained lateral travel. Keep near dust at supporting strength until distant motion reads. Use a short non-looping transport prototype first if looping constrains the motion; solve periodic birth/dissipation after the motion itself succeeds. No camera motion, spacecraft, moving mountains, global exposure shifts or giant opaque smoke banks.

Compare candidates at 1x/720p with the original composition. State the visible feature and direction before acceptance; do not promise percentage improvements. Only then combine, review the full twenty-second seam, export 4K and assemble the twenty-minute delivery. The new diagnostic clips deliberately reproduce rejected v4 for diagnosis; they are not an improved scene or an approved delivery.
