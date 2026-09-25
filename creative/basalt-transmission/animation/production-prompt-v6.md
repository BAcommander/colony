# Basalt v6 — slower clouds and restored plains smoke

Twenty-second 720p/30fps silent loop test. User liked visible v5 clouds, considered their speed excessive, and missed plains smoke. User acceptance remains pending.

Cloud copies travel right at 4.5 source pixels/second, half v5 speed. Two overlapping source-cloud lifetimes use sin-squared weights summing to one; each copy resets only at zero weight and zero weight derivative. Phase offsets vary smoothly across sky, avoiding a synchronized sky-wide fade. This local blending can soften/double cloud detail, so playback review remains necessary. No claim of physical cloud simulation. Moon excluded from output and texture source; fixed terrain masks retained.

Restore near-plains wind opacity .29, capped .34, with broader tongues. Center 340-pixel trajectories around seeded positions instead of sending most gusts off the right edge. Restore v4 underlying haze density. Retain broad distant sheets from v5, now using paired staggered periodic lifetimes. Keep roof exhaust and window events.

Preserve original source, geometry, camera, illumination and foreground. Review at normal playback speed: cloud readability without rushing, visible low smoke across open plains without a solid smoke wall, no moon copies, no edge wobble and no conspicuous reset. Technical checks do not establish artistic acceptance.

Render: python scripts/motion_review.py --config creative/basalt-transmission/animation/scene-plan-v6.json --output creative/basalt-transmission/animation/review-v6 --seconds 20

Output: review-v6/combined.mp4 with separate sky_clouds.mp4, far_haze.mp4 and plain_wind.mp4. No long or 4K export until visual review. Preview uses original timing; no speedup, duplicate endpoint, ping-pong, global dissolve or camera movement.
