# Cyberpunk Apartment — V4 first visual draft

Delivered2026-11-05 for visual review. [Play the full minute](Cyberpunk-Apartment-V4-first-draft-60s.mp4) · [Review both scenes](../../creative/animation-development/2026-11-05-16-17/review.html). Silent1280×720/60fps, genuinely60seconds of motion; native1672×941 processing before one downsample. Camera locked. This is a draft for artistic review.

Bus:8–26s. Lamp dips:20.4/20.72s and47.15s. Ferry:approximately37–52s, behind the central foreground tower line. Signs, rain, traffic, water, steam and leaf motion continue through the minute.

## Implemented first pass

| Candidate | Current visible treatment |
|---|---|
| A01 | Source-cloud local renewal plus separate moving gap mist. |
| A02 | Six source-road lanes, solid cars, separate physical speeds and filtered minimum headways. |
| A03 | One longer commuter bus on the existing upper road, sharing the lane speed and a reserved birth gap. |
| A04 | Ten independent source-emitter programmes, including bright cores, and bounded local glow. |
| A05 | Source-bound water movement, selected sign-linked river/floor response and small vehicle wet-road streaks. |
| A06 | Exterior rain, optically refractive glass beads, sliding/holding tracks and one explicit two-drop merge. |
| A07 | Gap wisps substituted for rooftop emission: no unambiguous vent grille was available on this source. |
| A08 | Seeded, overlapping cup wisps against the dark sofa. |
| A09 | Held occupancy groups and existing red-core mast modulation; many windows remain steady. |
| A10 | Brief coupled table-lamp core/table-reflection dips in linear light. |
| A11 | Two original leaf cutouts moving over confined generated clean background. |
| A12 | Small service ferry on retraced open water north of the foreground tower roof, with narrow wake. |

The two leaves, procedural bus and tiny ferry are included as experiments. Gap mist replaces an unsupported rooftop-vent claim. Water masks were retraced after the legacy seeds caught rooftops/bridge pixels. A minimum headway filter and bus reservation replace raw random births; random times alone do not guarantee safe spacing.

## Review clips from the actual encoded minute

Detail crops enlarge the picture2× for inspection, without changing effect strength or speed. Start with the full composition. The ten-second join review is source55–60s followed by0–5s; every decoded YUV picture matches that source sequence.

- [City-neon-and-traffic-detail.mp4](City-neon-and-traffic-detail.mp4) — 16s
- [City-cup-lamp-and-leaves-detail.mp4](City-cup-lamp-and-leaves-detail.mp4) — 10s
- [City-ferry-and-glass-detail.mp4](City-ferry-and-glass-detail.mp4) — 12s
- [City-loop-join-10s.mp4](City-loop-join-10s.mp4) — 10s

## Rebuild and verification

Use `.local/audio-analysis/Scripts/python.exe music/cyberpunk-apartment-animation-v4/render.py` from the repo root, with a new `--output` name to preserve the current delivery. `--only` accepts comma-separated effect groups for isolated tests; see frame() in [the renderer](render.py). [Settings](settings.json) · [Complete validation](delivery-validation.json) · [Detail provenance](detail-review-validation.json) · [Implementation/cue record](implementation.json).

The full decode checks all3600 sequential timestamps and pictures. Fifteen direct native-to-YUV controls are exact. Source protection is checked on every encoded native frame; an independent241-state check validates protected pixels and source taps/non-folding cloud or water maps. Regional encoded last-to-first changes are checked against ordinary nearby steps. RGB conversion and full video tags are explicit BT.709/TV. Native/mask and colour-aware decoded temporal stills were inspected; assistant continuous playback and user acceptance are not inferred.

The showcase minute deliberately contains rare vehicle/practical cues for review. The separate600s attention schedule, long-session listening, soundtrack/SFX balance and4K master remain future work. No production cadence, old scene gain or approval transfers automatically. Original art/previous masters are preserved; no commit, push, upload or paid API generation was requested in this build.
