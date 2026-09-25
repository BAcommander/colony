# Basalt v2 — stronger background life

User feedback: v1b is a good start, but needs more wind across the plains and movement in the sky/haze. Preserve its habitat, roof exhaust and room-light behavior. Increase background motion rather than adding props or changing the camera.

Make the right-hand plain visibly windy with nine irregular low dust sheets traveling right, each with independent placement, width and life phase. Give them smoothly fading birth/dissipation and steady forward transport. Keep their color consistent with copper-grey terrain, soften their edges and clip them behind the existing rock formations. Do not blanket the foreground or make opaque fog bars. Broaden the two existing haze layers and increase their material travel so the valley participates in the motion.

Add slow evolving material detail within the existing central/right cloud bands, protecting the moon, clear sky, mast and mesa silhouettes. Keep the cloud bank's overall placement and sunset lighting fixed. This is procedural internal texture movement, not a physically simulated cloud system or camera shift. Avoid broad exposure pulsing, hard patch boundaries and cloud geometry melting.

Keep the approved direction's calm tone, but make the background change readable at normal scene size. Retain source pixels outside accepted masks. Use a genuine twenty-second phase and a silent20-minute4K delivery made from60 repeats. Reuse QP0 master payloads for delivery: the prior CRF16 seam test failed, so do not repeat that encoding experiment. Keep v1b unchanged for comparison.

Implementation: scripts/render_basalt.py --version v2 reads scene-plan-v2.json. Versioned previews, masks, settings and final masters. scripts/assemble_basalt.py --version v2 handles remuxing, long assembly and full decode verification. Inspect temporal samples/masks and record actual validation; user artistic approval remains pending.
