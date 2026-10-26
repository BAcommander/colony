# Spirewatch v8 — 60-second 4K loop

[Open the clean 4K loop](Spirewatch-v8-60s-4K-loop.mp4)

Spirewatch v8 now has a verified clean sixty-second 3840x2160/30fps silent master at music/spirewatch-animation-v8/delivery-4k-v1/Spirewatch-v8-60s-4K-loop.mp4, requested with "sure make a 60s 4k loop". Exact saved source/config/renderer/dependency/mask/runtime fingerprint retained. Native 1672x941 frames upscaled directly with Lanczos; no 720p video enlargement or effect changes. All 1800 frames/timestamps, regional/composite and quiet-neighbour loop seams passed; ten decoded 4K pictures including chunk boundaries match direct native-to-YUV renders exactly. Assistant inspected decoded stills, not continuous playback. No audio or opening baked into the loop; apply the current opening once during later Colony assembly. User authorized 4K delivery; full combined playback remains separate. New master and delivery records are local, not committed/pushed. The prior v8 preview/source backup remains verified at b456b82. See delivery-4k-v1/delivery-validation.json.

Master size: 601,798,678 bytes. SHA-256: `c5bc500c98532d1d53229b17fd699c05f737a4809ee5b1dd87cc2393eb5b225f`. H.264 QP0, YUV420p, BT.709. The lossless encoded master is intended for reuse during final assembly. Native source detail remains 1672x941.

Checks: source-verification.json, render.json, delivery-validation.json. Reproduce with render_delivery.py; use --verify-only to recheck an existing master. Existing preview, older renders and intermediates are preserved.

Two exploratory storm PNGs in the parent directory differ from the delivered preview; do not treat them as final source states. Their corresponding delivered preview frames (552 and 1296) match the current native renderer exactly. Six other saved native stills also match. This finding did not change any effects.
