# Deepwell Station — glazing, steam and pipeline lights, v3

2026-10-25. The user reports that window masking needs to be much better and asks
for foreground coffee/pipe steam, steam at distant containers, and possibly lights
running along the pipeline. [Exact feedback](user-feedback.json) and
[implementation brief](creative-brief.txt) are saved. V2 is preserved; this v3
candidate awaits its own user review.

- [Twenty-second silent 720p/30 fps preview](Deepwell-v3-preview-20s.mp4)
- [Three exact repetitions for a sixty-second join review](Deepwell-v3-three-loops-60s.mp4)
- [Source/mask/all-dim window comparison](window-source-mask-dim-comparison.png)
- [Changed masks](changed-mask-review.png), [configuration](scene-plan-v3.json)
- [Native source](v2-snapshot/baseline-snapshot/artwork-planet-v1.png), unchanged

The fixed 1672 × 941 plate retains SHA-256
`8c04e8fbf7af063d00cd05fb587c713f2e0a380b8274410016d072cdf9a25b9b`.
No image generation or source-art replacement was needed. The original approved
art/thumbnail and exact v1/v2 deliveries remain intact. The v2 renderer, helper,
weather/configuration and complete required baseline are copied and hash-frozen
in `v2-snapshot/`; the new renderer does not depend on live v2 folder changes.

The former window rectangles included parts of pillars and missed full glazing.
V3 traces eleven panes: ten animated glass panes in six lighting groups, and a
cool blue pane left steady. Fractional coordinates, 16× supersampling and an
inward-only feather follow the glass edges; no Gaussian blur spills onto nearby
stone or mullions. The wide central pillar, metal frames, sills and surrounding
facades stay fixed. An all-dim diagnostic checks complete pane coverage. Nine
explicit bright-core controls ensure that the white/bright lamp cores darken with
the room. The initial tiny-pane study misidentified a bright core at x1573/y204 as
a stile; source pixel inspection located the actual dark stile at x1570, and the
trace/guard were corrected before delivery. The internal study is preserved in
`history/initial-pane-steam-study/`.

Foreground steam rises from inside the coffee opening, behind the front rim and
cup body. Three independently varying distant plumes start at existing tank roof
outlets, interpreted artistically as process vents. Vessel roofs/shells and pipe
solids occlude the vapor. Filaments curl, broaden and disperse while their density
features travel upward. Emission changes use birth time, so they rise with the
material instead of fading the entire plume at once. Lifetimes divide twenty
seconds, with clamped finite envelopes and a smooth height taper. Coffee was
chosen as the clear foreground source; no leak was invented in sealed indoor
pipework. The initial optical-depth setting was too faint in assistant still
review; the selected setting is recorded alongside its unamplified comparison.

Twelve small muted-cyan indicators sit on the visible pipe face, with tiny attached
housing shadows and a restrained travelling acknowledgement pattern. The traced
route ends at the real plant inlet near x1390, rather than continuing across the
right cliff. Core/halo/housing masks stay on the pipe material. The v2 blanket
pipeline-pixel protection is superseded only for this explicit user-authorized
indicator footprint. Every other pipe/support pixel remains protected, and v2's
occlusion of basin air/mineral drift behind supports remains unchanged.

All twelve other v2 layers retain their source/configuration/math: water, sky,
planetary veil, far/middle/brine weather, both mineral-drift paths, monitor, work
lamp, amber service indicator and restrained daylight highlights. Native sampled
comparisons verify every pixel of each retained layer and the full composite
outside the old/new window plus new vapor/indicator masks. The old-window mask is
part of that comparison authority because removing its incorrect stone/pillar
dimming intentionally restores those pixels.

Separate eight-second full-composition tests are
`deepwell-v3-windows-isolated-8s.mp4`, `deepwell-v3-coffee-isolated-8s.mp4`,
`deepwell-v3-tank_steam-isolated-8s.mp4` and
`deepwell-v3-pipeline-isolated-8s.mp4`. Source/mask/native temporal and selected
colour-aware decoded stills were inspected, including full-composition and close
window/vapor views. This is not a claim of continuous playback review or user
artistic acceptance.

`analytic-validation.json` records changed-layer periodicity, ordinary/seam steps,
late coverage, bright-core controls and source guards. Every rendered native
frame asserts exact window-frame/stone/steady-pane, fixed-mullion and cup/tank/
pipe/support protection outside the explicit indicator footprint.
`preview-validation.json` covers all 600/1800 decoded frames, sequential timestamps,
silence, per-region/composite and quiet-neighbour joins, and identical encoded and
decoded repeat sequences. `direct-render-validation.json` compares twelve preview
pictures to direct native-to-YUV renders, twelve retained v2 layers and scoped
composites at six states, and all v2 manifest files. Exact runtime/source/config/
renderer/dependency/mask fingerprints are retained. No seam threshold was loosened.

Native frames receive one Lanczos scale to 1280 × 720 and explicit BT.709 conversion
before H.264 QP0 encoding. No endpoint is duplicated. The minute review is three
stream-copied twenty-second sequences, not a unique minute. No music, SFX, opening
or titles are baked in. 4K/long assembly are later stages after visual review.
No paid service, model installation, commit or push was requested; this package is
local. The main renderer refuses to overwrite media. For a fresh version with
absent/archived output files:

```powershell
& 'C:\Users\jazzs\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'G:\AI\colony\music\deepwell-animation-v3\render_deepwell_v3.py' --stage samples
& 'C:\Users\jazzs\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'G:\AI\colony\music\deepwell-animation-v3\render_deepwell_v3.py' --stage preview
```
