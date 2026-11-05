> Current: [V4 full-minute visual draft](../../music/cyberpunk-apartment-animation-v4/README.md) is delivered at720p/60fps, with all twelve candidates represented in the first pass. [Paired visual review](../../creative/animation-development/2026-11-05-16-17/review.html). Technical checks passed; user artistic review, the ten-minute event schedule, audio and4K remain pending. The historical planning checkpoint follows.

# 16 — Cyberpunk Apartment: animation development plan

Prepared2026-11-05. Status: source/legacy-code audit and proposed build backlog. No new animation or repaired artwork is delivered by this plan. Current source and prior masters remain unchanged.

Proposed new build folder: `music/cyberpunk-apartment-animation-v4/`. Preserve the current version while developing these candidates.

A warm, still apartment above a rainy city that carries on living outside the glass.

[Interactive source map](../../creative/animation-development/2026-11-05-16-17/index.html#scene-16) · [Machine-readable backlog](../../creative/animation-development/2026-11-05-16-17/16-cyberpunk-apartment-backlog.json) · [Fresh baseline audit](../../creative/animation-development/2026-11-05-16-17/baseline-audit.json)

## What exists

The existing V3 already has road traffic, three travelling signs, three animated panels, window modulation, rain, sliding bead marks, gap mist, water/floor reflections and cup steam. Plants are deliberately static. Four hovering vehicles were repaired out; preserve those repairs and the no-aircraft direction. The current loop is ten seconds at sixty fps.

Source: `final/16-cyberpunk-apartment/artwork-v3.png`, native1672×941, SHA-256 `3ae5b38ec7c6c5fa31d1df38a6659c39efdec5b717bfa199b0b839a1c0fc634d`. The existing preview was decoded completely in this task: 600frames/10s/60fps, silent with sequential timestamps. Source and decoded stills were inspected; no new continuous playback or user approval is inferred. Map pins are approximate planning locations, not finished masks.

## Candidate list

| ID | Candidate | Existing or new | Priority | Visible action |
|---|---|---|---|---|
| A01 | Cloud banks travelling between the towers | upgrade existing | Core | Move coherent cloud shapes across several skyline depths, with clear gaps and near towers staying sharp. |
| A02 | Convincing irregular road traffic | upgrade existing | Core | Clear vehicle bodies and distinct head/tail lights follow the existing near and elevated roads, with pairs, gaps and safe headways. |
| A03 | A rare commuter shuttle on the elevated road | new candidate | Support | One longer illuminated bus crosses the existing elevated roadway, briefly disappearing behind towers. |
| A04 | Independent sign programmes with local light spill | upgrade existing | Core | A few existing large signs have readable travelling heads, dimmer holds and different rhythms. |
| A05 | Reflections that belong to each light source | upgrade existing | Core | Selected sign and traffic changes echo in the river, wet roads and the cool floor strip. |
| A06 | Refractive droplets with trails and occasional merging | upgrade existing | Core | Several readable close glass drops bead, stick and slide while finer rain stays outside. |
| A07 | Ventilation vapour in the lower city | new candidate | Support | Two anchored exhaust plumes rise from verified rooftop outlets, then drift into the existing street mist. |
| A08 | Better cup steam against the dark sofa | upgrade existing | Support | Soft uneven wisps leave the existing cup, separate and disperse rather than drawing a repeating corkscrew. |
| A09 | Occupied windows and existing mast lights | upgrade and candidate | Support | A few complete apartment windows hold different occupied states; selected existing mast lights have readable small bright centres. |
| A10 | One warm practical with coupled reflections | new candidate | Support | The table lamp has an occasional gentle hesitation, shared by its nearby pool and marble reflection. |
| A11 | A few leaves moving in indoor ventilation | conditional experiment | Experiment | Only selected leaf tips bend gently from their attachments while stems, pot and sofa remain anchored. |
| A12 | An occasional river service ferry | stretch experiment | Experiment | A small utility boat crosses a verified open-water route with a narrow wake and a soft reflected light. |

## Build order

1. Preserve V3 and audit its source/encoded colour path. Replace the machine-specific ShareX FFmpeg path in a new renderer with the portable bundled binary. Keep native1672×941 coordinates through the effect pass; upscale once at delivery.
2. Prove A04/A05 together: two independent sign signals with matching haze/river/floor response. Also prove A02 on one road with exact body/occluder registration before expanding traffic.
3. Add A01 coherent city cloud transport and A06 true glass optics. Review these principal actions at720p/60fps at actual speed before supporting effects.
4. Build a genuine sixty-second unique scene. V3 uses normalized10s time for almost every layer and forces each traffic identity through its entire route in that period. Simply changing DURATION to60 slows all traffic/rain/steam by six. Separate physical speeds, particle lifetimes, sign programmes and held window events from the master period.
5. Add rooftop vapour, cup steam, selected occupancy states and one practical-light cue with their own remapped receivers. Then audition the rarer commuter shuttle.
6. Only include leaves or the ferry after their isolated geometry/contact tests work. Use a separate proposed600s attention schedule for rare transit, lamp and occupation events, preserving the approved appearance while avoiding a short repeated show.
7. Review the complete new loop and timing at normal size; then make the accepted native-to4K/60fps master, with explicit colour conversion/tags and the Colony intro applied once during final assembly.

## Source and motion guards

Retain the source warm/cool balance, the repaired absence of hovering cars, locked furnishings and exact window-frame/building/shoreline geometry. Readability comes from useful shape, contrast and timing; no synchronized skyline pulse. True droplet refraction may affect architecture only locally through the bead, with source-valid sampling. The sampled1080p file reports a BT.709 matrix but unspecified primaries/transfer; audit the old RGB-to-YUV conversion and set the full colour chain explicitly in new work without silently grading the still.

Implementation starting point: [legacy timing and route audit](../../creative/animation-development/2026-11-05-16-17/16-retiming-design.json). These are design records, not executable effect settings or proof that a new loop works.

[Existing native-coordinate geometry seeds](../../creative/animation-development/2026-11-05-16-17/geometry-seeds.json) preserve the current glass, roads, occluders, sign boxes and portal aperture. Refine them against the source before treating any new receiver or emitter box as a final mask.

Use eight-to-twelve-second full-composition proofs first, with isolated principal layers and unamplified source-size crops. Check both source taps and output coverage, complete emitter/aperture masks, material-linked spill, solid occlusion, and true local/long-cycle joins. No difference score or endpoint identity establishes natural-looking motion. Preserve named unchanged layers with exact controls while adding effects.

Proposed first complete review:60s at1280×720/60fps. Environmental motion and physical speeds need independent time controls; the later attention schedule is600s, not a default restart every minute. The native1672×941 plate will be upscaled for4K only after look/timing acceptance. Save source/config/code/asset/runtime hashes and exact feedback; apply the current opening once at later assembly.

## Sound and cue relationships

Start with indoor room air and rain heard through closed glass. Add distant city/road movement only if the room perspective supports it. Couple significant sign changes to reflections, and weather changes to the rain bed. A rare bus/ferry cue is an optional later audition, with filtered distance and no sharp horn or advertising voice. Existing music prompts remain drafts; no new sound or generation is made in this plan.

## Method and acceptance notes per candidate

### A01 — Cloud banks travelling between the towers

Source-texture transport and separately renewed gap mist; preserve both source taps and destination silhouettes. V3 has translating density patterns, not a complete source-cloud transport pass.

**Proof:** A recognizable cloud edge moves at full-scene720p without dragging a tower or producing a flat fog stripe.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A02 — Convincing irregular road traffic

Replace normalized10s whole-route travel with source-space speed and explicit event births/occlusion. Perspective-scaled silhouettes, premultiplied edges, contact/reflection response. Preserve the removed hovering-car repairs.

**Proof:** Traffic reads as vehicles on asphalt at normal size; no overtaking collisions, curb-following errors, floating lights or repeating short tile.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A03 — A rare commuter shuttle on the elevated road

Road vehicle, not a new railway or aircraft. Low-contrast body with a few attached windows and wet-road response; one passage in a proposed3-5min interval.

**Proof:** The body remains aligned with the road and correctly occluded, and the larger transit moment feels occasional.

**Asset/preparation:** New small vehicle asset or a carefully projected procedural body; inspect its geometry before a full pass.

### A04 — Independent sign programmes with local light spill

Map complete existing emitters including white cores; preserve glyphs. Give each sign its own schedule and drive nearby haze and surfaces from that same signal.

**Proof:** At least two signs visibly change in the full scene; city exposure and building edges remain fixed.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A05 — Reflections that belong to each light source

One emission signal per source with separate perspective-mapped receiver masks; calm source-detail-preserving water motion. Retain warm furniture reflections.

**Proof:** Colour, timing and apparent source position agree; river motion has no shoreline tearing or broad floor wobble.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A06 — Refractive droplets with trails and occasional merging

Replace a few flat bead marks with local source-valid refraction, a narrow highlight and a fading wet trail; selected merge events need continuous volume/paths.

**Proof:** Drops survive normal-size viewing; refraction never samples a frame or interior object and trails do not cover the view.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A07 — Ventilation vapour in the lower city

Choose actual flues in the source before drawing anchors; broad overlapping wisps, wind-linked drift and building occlusion.

**Proof:** Plumes clearly leave their outlets and stay behind intervening masonry; no emission from an invented antenna.

**Asset/preparation:** Trace actual visible outlets first; if no convincing outlet is present, retain this as gap mist instead.

### A08 — Better cup steam against the dark sofa

Keep the cup and table fixed; broaden the useful vapour footprint and vary density independently of the neon programmes.

**Proof:** Visible but quiet at720p, attached to the liquid surface, with no repeated spiral or smoke-like plume.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A09 — Occupied windows and existing mast lights

Trace larger real panes and hardware instead of scattering random dots. Most windows stay steady; source-mounted beacon halos remain bounded.

**Proof:** Window states are local and independently held; no whole-district breathing or lights placed in haze.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A10 — One warm practical with coupled reflections

Reuse the Crater lamp core/spill method with new source geometry. Include the white bulb; keep most room lighting steady and use a long attention clock.

**Proof:** Core, nearby table and warm reflected contribution dip together; no room-wide exposure change or constant flicker.

**Asset/preparation:** Existing clean plate; new source masks must be traced at native size.

### A11 — A few leaves moving in indoor ventilation

Use isolated leaf elements over a clean background; do not warp the whole plant or smear the scene behind it. A constrained test earns inclusion.

**Proof:** No doubled original leaf, rubbery edge or displaced pot; the movement is subtle and credible at source scale.

**Asset/preparation:** Requires leaf separation and a clean revealed background patch; existing V3 deliberately keeps the plant static.

### A12 — An occasional river service ferry

Map a true water corridor, bridge/building occlusion and perspective before making an asset. Keep the passage sparse over several minutes.

**Proof:** A solid hull sits on water with a restrained wake; no crossing dry terraces, emerging through a bridge or bright floating dot.

**Asset/preparation:** New vessel asset plus independently reviewed water/occlusion masks; optional after the main city pass is accepted.

## Lessons carried forward

Crater Rim V5 supplies emitter contrast, useful holds, full-size A/B review, coupled lamp spill and grounded vehicle compositing. Snowline supplies strict source/output exclusions and full-context structure tracing. Baal supplies depth and shared weather/audio cues. Rainline supplies inward glass masks, and Shoreless supplies the warning against a prominent decorative waveform. These methods require new masks and viewing tests; their old scene-specific values or approvals do not transfer.

The broader gate/city proposal, first proofs, optional assets, music, final runtime,4K master and long-form assembly are unbuilt. No paid service, image generation, commit or push is included in this planning task.
