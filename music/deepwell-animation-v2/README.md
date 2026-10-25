# Deepwell Station — full refinement, v2

2026-10-25. The user's exact feedback was: “ok it's a decent first pass, but needs
a good bit more, lets make it 300% better, revisit every park”. This revision
treats that as a request to revisit every part. V1 is a decent checkpoint, not a
final accepted look. “300%” is ambition, not a measured improvement claim.

- [Current twenty-second silent 720p/30 fps preview](Deepwell-v2-preview-20s.mp4)
- [Three exact repetitions for a sixty-second join review](Deepwell-v2-three-loops-60s.mp4)
- [Exact feedback](user-feedback.json), [creative brief](creative-brief.txt), [source-bound configuration](scene-plan-v2.json)
- [Native planet artwork](baseline-snapshot/artwork-planet-v1.png), unchanged from v1
- [Mask review](mask-review.png), [first-pass record](../deepwell-animation-v1/README.md)

The source remains 1672 × 941, SHA-256
`8c04e8fbf7af063d00cd05fb587c713f2e0a380b8274410016d072cdf9a25b9b`.
No new image generation was needed. The approved original artwork and thumbnail,
v1 source/configuration/media, and v1 local manifest are preserved. Necessary v1
renderer, source and helper files are copied and hash-frozen in
`baseline-snapshot/`; rendering does not depend on live changes to the v1 folder.

The water revisits the accepted filtered reflection method with a different
direction distribution: predominantly horizontal crests and a weaker cross-wave
field, closer reflected detail, shoreline damping, stronger bounded displacement,
and small periodic gust and sunlight responses. This remains a source-based 2D
surface, not a fluid simulation. Warm reflected structures remain within the
water, and the photographed white terrace edges stay fixed.

The sky now uses two depth-weighted source-cloud speeds. A close guard replaces
the larger quiet circle around the planet, and a distinct source-derived thin
cloud veil passes in front of its lower body. The underlying planet image and
limb do not rotate or warp. Its pixels can change under cloud opacity; v1's strict
pixel-static planet rule is intentionally superseded for that explicit layer.
The cloud texture still comes from the original planet-free sky, with rocks and
window structures removed from the sampled texture.

Far airflow below the arches, middle-distance basin haze and low brine wisps use
separate masks, rates and seeded shapes. Two additional mineral-drift paths follow
dry terrace surfaces. The selected version uses coherent, curling wisps whose
centres travel forward, widen and disperse with zero-contribution lifecycle resets.
This avoids relying on almost invisible density shimmer or a continuous fog band.
The pipeline and supports explicitly occlude the air layers.

Habitation has eight independently scheduled existing window groups, while other
panes stay steady. The original monitor retains its housing/panel structure but
has clearer pressure, levels, twice-through forward log movement and an acquisition
cursor in its existing plot. The existing amber service indicator acknowledges
work with held/double events. Lamp dips affect its actual emitter, attached warm
wall/metal spill and a small desk highlight. A separate gentle daylight
change is confined to the real tabletop and window ledge highlights. There is no
full-scene exposure animation. Valves, machinery, furniture and camera stay fixed.

The first v2 soft-weather study passed numeric checks but remained too faint in
assistant still review. It was preserved in `history/soft-weather-study/` and
replaced before delivery. The final source-cloud veil also uses higher-contrast
cloud material so shape transport is easier to identify. This internal judgement
is not a user playback verdict. V1's old water-mask and monitor-seam findings remain
in its package, alongside the exact source and history.

A later explicit source-protection check caught 34 changed source pixels on one
pipeline support, where the mineral-surface drift mask had omitted the occlusion
already applied to the air layers. That internal candidate and diagnosis are
preserved in `history/support-occlusion-fix/`. The corrected drift mask excludes
the supports, and every rendered source frame now asserts exact pipeline/support
protection. The atmosphere and composite were rerendered; the gate was retained.

The four isolated eight-second full-composition clips are:

- `deepwell-v2-water-isolated-8s.mp4`
- `deepwell-v2-sky-isolated-8s.mp4`
- `deepwell-v2-atmosphere-isolated-8s.mp4`
- `deepwell-v2-habitation-isolated-8s.mp4`

Water/habitation were retained after the focused weather refinement. Their
original complete decode records and output hashes are preserved, and direct
native-to-YUV controls at frames 0/120/239 confirm that the final configuration
produces the same selected pictures. The changed sky/atmosphere were rerendered.
`isolated-validation.json` consolidates the records with that distinction.
After the final support-mask correction, only the atmosphere and full composite
needed rendering again; the sky isolate was also retained with the same direct
native/YUV controls. Three retained groups therefore have nine control pictures.

`analytic-validation.json` records every layer's source protection, finite values,
periodicity, seam step and coverage at 0/4/8/12/16 seconds. Weather shapes fade to
zero with zero slope before lifecycle resets. Cloud renewal has zero-weight,
zero-slope wraps; wave frequencies are integer cycles over twenty seconds. Water
frequency quantization deviations are recorded rather than described as exact
speed retention. `preview-validation.json` records all 600 and 1,800 decoded frames,
sequential timestamps, silence, per-region/composite encoded seams against normal
and nearby quiet steps, and three identical encoded and decoded sequences.
`direct-render-validation.json` checks twelve preview pictures against direct
native-to-YUV renders, retained-layer controls, exact pipeline protection and every
file in the v1 delivery manifest. Runtime/configuration/renderer/dependency/mask
fingerprints are retained. No gate was loosened for a failed result.

Assistant inspection includes native source, masks, normal-size temporal and
decoded stills, isolated exterior comparisons and local details. Continuous
playback review has not been claimed. Technical passes do not establish the
naturalness or artistic acceptance of this revision; the user's new verdict is
pending.

Rendering uses native frames followed by one Lanczos scale to 1280 × 720, explicit
BT.709 conversion, silent H.264 QP0 encoding and no duplicate endpoint. The minute
review is three stream-copied twenty-second sequences, not a unique minute. No
opening, titles, soundtrack or SFX are baked into the repeating loop. 4K and long
assembly remain later stages after review. No paid video service, model install,
commit or push was requested for this revision; files are local.

The renderer reads only this package and installed library/runtime files. Python
3.12.14, NumPy 2.4.4, OpenCV 5.0.0 and the actual FFmpeg version/binary hashes are
recorded. Preparation/study scripts are historical builders and must not overwrite
the frozen selection. The main renderer refuses to overwrite media. For a new
version with archived/absent output files:

```powershell
& 'C:\Users\jazzs\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'G:\AI\colony\music\deepwell-animation-v2\render_deepwell_v2.py' --stage samples
& 'C:\Users\jazzs\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'G:\AI\colony\music\deepwell-animation-v2\render_deepwell_v2.py' --stage preview
```
