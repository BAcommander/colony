# Deepwell Station — visible rolling steam and purple return sequence, v4

2026-10-25. The user reports that v3 steam in every location and the cyan lights
are very hard to see, requests purple lights travelling up and down the pipeline,
and asks for a much better pass. This is a visibility failure report, not approval
of v3. [Exact feedback](user-feedback.json) and [brief](creative-brief.txt) are saved.

- [Current twenty-second silent 720p/30 fps preview](Deepwell-v4-preview-20s.mp4)
- [Three exact repetitions for a sixty-second join review](Deepwell-v4-three-loops-60s.mp4)
- [Full twenty-second purple light round-trip test](deepwell-v4-pipeline-roundtrip-20s.mp4)
- [Configuration](scene-plan-v4.json), [changed footprints](changed-mask-review.png)

The fixed 1672 × 941 source retains SHA-256
`8c04e8fbf7af063d00cd05fb587c713f2e0a380b8274410016d072cdf9a25b9b`.
V3 and the earlier original art/thumbnail/deliveries remain intact. Necessary v3
code/configuration and its complete v2/v1 dependency chain are frozen in
`v3-snapshot/`, with exact hashes. No new artwork generation was needed.

Steam is rebuilt as a wider rolling material body with broken filaments, larger
lateral curl and a smoother spreading profile. Taller coverage, whiter scattering
colour and more persistent source emission help it read against the photographed
background. It is not simply the old thin strand with a small opacity adjustment.
The coffee rises from inside the opening, behind its front rim/body. Three tank
outlets retain independent plume shapes, birth-time source variation and solid
vessel/pipe occlusion. The far-right plume's path is less wind-swept into the pale
cliff, retaining more material against the grey sky. That internal contrast study
is preserved in `history/far-plume-contrast-study/`. These are artistic 2D vapor
fields, not a physical process/fluid simulation.

Twenty short purple indicator segments replace the small cyan dots. Their length,
cross-section, saturated colour, attached housing and confined metal halo are
larger/more readable. Geometry coverage preserves bright pipe-face highlights;
the previous luminance cutoff cannot erase a core simply because the source metal
is bright. The travelling head reaches the plant at ten seconds, then returns to
the distant left at twenty seconds. Its analytic cosine path has zero speed at
both turnarounds, and the directional tail changes continuously. The scene/video
is not reversed. A complete indicator-only twenty-second test covers both legs.

The stronger lights exposed approximate placement at the distant end: two mounts
needed moving onto the actual dark pipe face rather than the pale area below it.
Source profiles and close decoded views guided the correction. The initial full
candidate, clips/configuration/checks and alignment study remain in
`history/pipe-mount-alignment-study/`. Only the affected pipeline isolation and
full composite were rerendered; the coffee/tank isolated clips are retained with
their original complete-decode records, hashes and final-config native/YUV controls.

Thirteen v3 layers are retained, including the corrected whole-glass light masks,
water, sky/weather and room activity. White-core coverage, the steady blue pane
and fixed mullions/stone also remain intact. Sampled native
controls verify those layers and the complete scene outside the old/new vapor/
indicator footprints. Every rendered source frame still asserts the window,
mullion, stone, steady-glass, cup/tank and pipe/support guards; only the defined
vapor/indicator footprints authorize the requested new pixels.

Unamplified actual-conversion 1280 × 720 samples were inspected alongside v3,
followed by isolated decoded views and selected final decoded stills. Native-only
crops and difference metrics are not the visibility criterion. Assistant
inspection remains still-based; continuous playback and user artistic approval
have not been claimed. The user's verdict on this v4 candidate is pending.

`analytic-validation.json` covers the changed fields, continuing late motion,
source guards, periodicity, ordinary/seam steps, retained bright-core coverage and
the outward/return path. `isolated-validation.json` consolidates both eight-second
vapor tests and the full indicator round trip, distinguishing retained steam
clips after the focused alignment fix. `preview-validation.json` covers all
600/1800 decoded pictures, sequential timestamps, silence, regional/composite and
quiet-neighbour joins, and three identical encoded/decoded repeats.
`direct-render-validation.json` checks fourteen preview pictures, six pipeline
round-trip pictures and six retained vapor controls against direct native-to-YUV
rendering, thirteen retained v3 layers and scoped composites at seven states,
all snapshot hashes and every file in the v3 delivery manifest. Numeric checks
do not establish aesthetic success, and no gate was loosened.

Native frames use a single Lanczos scale to 1280 × 720, explicit BT.709 conversion
and H.264 QP0 encoding. There is no duplicated endpoint. The sixty-second file
stream-copies the unique twenty-second sequence three times; it is not a unique
minute. The clean review contains no audio, opening or titles. 4K and long assembly
remain later stages after review. No paid service, model installation, commit or
push was requested; files are local. The renderer refuses to overwrite media.
Preparation/refinement scripts are historical builders, not commands to run over
the frozen selection.
