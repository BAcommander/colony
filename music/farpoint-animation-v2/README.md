# Farpoint Station v2 — forward motion test

2026-10-07. Eight-second motion tests after the user rejected v1's planetary motion: “ok i just watched it, basically i can see no movement on the planet at all”. V1 remains preserved and rejected for visibility, despite its passing numeric checks.

- [Full scene at 720p / actual speed](farpoint-v2-full-scene-motion-test-8s.mp4)
- [Planet motion isolated in the full composition](farpoint-v2-planet-motion-test-8s.mp4)
- [Validation and hashes](delivery-v2.json)
- [Configuration](scene-plan-v2.json)

These are eight-second, 30 fps, silent excerpts with direct forward cloud travel. **They are not seamless loops.** Player restart will jump. The user has now confirmed cloud visibility: “yeah i can see them moving now”, and requested more planetary, monitor and instrument/LED activity. This confirms visibility, not a seamless-loop or final-export approval. Continue with the [v3 detail preview](../farpoint-animation-v3/README.md).

V1's small, nearby transported cloud copies were blended by periodic lifetimes. This left little apparent translation, especially at full composition. V2 removes that blend from the principal layer and uses a single forward curved mapping. Reference travel rates increase from 1.05/1.65 to 4.2/5.4 source pixels per second, with the same perspective reduction near the limb. Texture/masks remain tied to the original source; the support region expands to accommodate the actual travel. No camera or planet geometry moves.

The extracted cloud is converted to premultiplied colour and opacity, then composited over the fixed local terrain reconstruction. Direct additive transport initially produced a bright patch where a cloud crossed lighter ground; optical compositing corrected that sampled artifact before video delivery. The underlying reconstruction is approximate, and cloud remnants/soft exposed ground are still review points. This is not recovered terrain or physically simulated planetary rotation.

Template tracking of individual extracted features measures approximately 15–28 preview pixels of travel over eight seconds, primarily right/up-right. See `sample-validation.json` for actual measurements. These measurements support the diagnosis; they do not establish visual acceptance. The upper band and central diagonal wisps should be judged in the full-scene clip at 1x playback.

Sampled window, monitor, lamp and veil layers match v1 exactly at 0/5/8/12.95/18 seconds. The original source artwork and v1 implementation are unchanged and hash checked. Source pixels outside active masks are asserted on every rendered frame. Both delivered clips are fully decoded and timestamp checked. No seam result is claimed for an unlooped test.

Assistant inspected source/temporal and decoded stills, not continuous playback. Review whether the planet's movement is now sufficiently readable and whether cloud edges stay believable. After that direction is established, build and inspect the full seamless cycle while retaining this visible travel. Music, 4K and long assembly remain pending.

Reproduce from `C:/Colony` with `python music/farpoint-animation-v2/render_farpoint_v2.py`. Use `--samples-only` for diagnostics without encoding. Existing video paths refuse overwrite. The small v2 adapter inherits the hash-verified v1 implementation; this is a method change, not a duplicated whole renderer. No credits, new models, commit or push in this revision.
