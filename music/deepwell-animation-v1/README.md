# Deepwell Station — planet and first animation candidate

2026-10-25. The user requested an alien planet in Deepwell's sky and the start of
animation using accumulated project lessons. This is a new candidate for review;
neither the planet artwork nor this motion has received a user verdict.

- [20-second silent 720p/30 fps preview](Deepwell-v1-preview-20s.mp4)
- [Three exact repetitions for a 60-second join review](Deepwell-v1-three-loops-60s.mp4)
- [Clean native planet artwork](artwork-planet-v1.png), 1672 × 941
- [Exact executed image prompt](planet-edit-executed-prompt.txt), built-in image_gen edit mode
- [Motion brief](creative-brief.txt), [source-bound configuration](scene-plan-v1.json)

The original approved `final/12-deepwell-station/artwork-v2.png` and its thumbnail
remain intact. Imagegen produced the planet edit, retained in
`planet-imagegen-original.png`. Its complete output contained small changes
elsewhere, so only its local sky patch was composited into the original plate.
A feathered boundary and additive perimeter colour match join that sky patch.
All original pixels outside the edit mask remain byte-identical. See
`artwork-provenance.json` for exact inputs, mask bounds, hashes and matching data.
Final source SHA-256:
`8c04e8fbf7af063d00cd05fb587c713f2e0a380b8274410016d072cdf9a25b9b`.

The genuine twenty-second animation has perspective-aware brine reflection
movement, rightward cloud transport, a bounded pressure marker and log/level
changes on the existing monitor, four independently scheduled existing cliff
window groups, and brief work-lamp dips at 5.6 and 15.8 seconds with attached warm
wall spill. The planet, terrace edges, arches, buildings, pipeline, equipment,
window frame and camera stay fixed. Existing cloud veiling on the planet is
part of the static artwork; no new moving cloud veil is claimed. The cloud source
comes from the original planet-free sky, excluding rocks and window structures.

The filtered 24-wave reflection method is reused from Glacier through the frozen
Floodplain `ChannelSurface` adapter. Local staggered cloud renewal follows
Floodplain/Shoreless; full apertures and coupled lamp spill follow the Rainline/
Spirewatch lessons. Only effect logic is reused: this package has new Deepwell
coordinates, masks, perspective, seeds, timings and water settings. Historical
artistic acceptance does not transfer to this candidate.

The first mask incorrectly left warm water reflections static; the colour gate
now acts only near mapped shorelines. Rounded screen updates also failed the
initial analytic seam check and were replaced with continuous needle/marker and
fractional bar coverage. A broad-wave water study passed technical checks but
looked too soft in still review. The finer brine-specific study is the selected
candidate, retaining more reflected detail. Preserved internal history and exact
configuration live in `history/`, with `water-scale-comparison.png` for context.
These are assistant internal findings, not user feedback.

Principal isolated clips are `deepwell-water-fine-isolated-8s.mp4` and
`deepwell-sky-isolated-8s.mp4`; `deepwell-screen-isolated-8s.mp4` isolates the monitor.
The older broad water test remains for history and is not the selected candidate.

Verification records are `analytic-validation.json`,
`water-fine-isolated-validation.json`, `preview-validation.json` and
`direct-render-validation.json`. They cover finite rendered arrays, exact source
protection outside masks and on the planet, periodic endpoints, regional and
composite last-to-first steps against ordinary and nearby quiet steps, complete
600/1800-frame decodes and sequential timestamps, silence, and three identical
encoded and decoded picture sequences. Twelve decoded preview pictures are also
compared byte-for-byte to direct native-to-YUV renders. Retained secondary
isolates are checked against the final configuration without rerendering them.
The original complete isolated validation and its fingerprint remain under
`history/broad-water-study/`.

Assistant inspection comprises source and mask images, native temporal stills,
water-scale comparison, isolated cloud temporal crops and selected BT.709-aware
decoded stills. This does not establish continuous playback review or natural
motion on the user's behalf. Numeric motion/seam checks are separate from the
user's visual verdict.

Rendering uses the saved native plate, then a single Lanczos scale to 1280 × 720,
explicit BT.709 conversion and H.264 QP0 encoding. The 60-second review stream
copies the twenty-second payload three times; it is not a unique minute. No titles,
opening, audio, SFX or music are baked in. 4K and long assembly follow review.
This package is local; no commit, push, paid video service or model install was
requested for this new task.

The renderer imports the frozen `dependency-snapshot/` files, not live renderer
changes elsewhere in the repository. Its validation fingerprint records source,
configuration, renderer, masks, NumPy/OpenCV/Python and FFmpeg versions. This run
used the bundled Python 3.12.14 and existing ComfyUI package libraries via a
read-only import path. No packages were installed. Restore the frozen files and
versions; do not rerun the historical preparation or refinement builders over
the selected configuration. The main renderer refuses to overwrite media:

```powershell
& 'C:\Users\jazzs\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'G:\AI\colony\music\deepwell-animation-v1\render_deepwell.py' --stage samples
# Only in a fresh version directory with no existing output media:
& 'C:\Users\jazzs\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'G:\AI\colony\music\deepwell-animation-v1\render_deepwell.py' --stage preview
```

Further feedback should create a new revision and preserve these exact source,
configuration, diagnostics, clips and recorded acceptance boundaries.
