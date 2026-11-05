# Lessons carried into Back Before Dawn

2026-11-05. These are reusable methods from today's Crater Rim and scene16/17 work. They are not transfers of another scene's artistic approval or exact settings. New observations from the workshop build should be added with the affected layer, actual defect, corrective action and evidence.

## What today's work established

| Lesson | Evidence and consequence for 18 |
|---|---|
| Native geometry seeds still need inspection. | City16's inherited water regions included foreground rooftops and bridge detail. Retrace wet street regions and source taps in the workshop before animating reflections. A protected output mask alone does not make the sampled material valid. |
| Readable emitters include white cores. | Crater Rim's stronger distant lights became useful through bright cores, bounded halos and longer holds. The workshop lamp and display masks must include complete apertures, not only warm or saturated colour keys. |
| Light changes need receivers. | Crater Rim coupled lamp dimming to wall/desk/thermos response; Gate Camp sends the same moving water front into stone and ring material. Use a shared workshop lamp/display signal for its nearby bench, cabin and metal response. |
| Static geometry and moving material are separate. | Gate Camp keeps its ring, world bodies and canopy supports fixed. Keep the car, door, wheels and instrument casings fixed; animate rain, water, display content and light inside their legitimate footprints. |
| Different depths need different treatment. | Baal and today's camp/city work separate near weather, distant air and sheltered foreground. Workshop rain belongs outside the opening, with fall distance, size and speed chosen for the streetlamp and road perspective. |
| A ground mask is not the whole moving-object volume. | The camp rover initially parked on a rocky shoulder, and a ground-only allowed region can cut off its roof. Any future passing vehicle or light route needs body clearance, contact and real foreground occlusion, rather than an approximate centreline alone. |
| Random timing does not guarantee plausible spacing. | City's raw traffic births put two vehicles too close; minimum headway, a longer-vehicle reservation and equal lane speeds resolved the schedule. Any road transit added to18 must earn a physical route/headway review. |
| Movable silhouettes need a true object boundary and revealed background. | The city leaves and camp line/scrub use confined generated clean fields beneath original cutouts. A partial tree-crown polygon is not a complete silhouette: revealing clean sky along its internal chord creates an artificial gap. The corrected workshop foliage instead uses original-source interior deformation with a fixed boundary and safe tap/Jacobian checks. Resample actual sprites premultiplied by alpha. |
| Duration is not speed. | City16's legacy normalized ten-second clock would slow traffic and rain if simply extended. Workshop physical speeds, weather phase and attention schedule must remain separate. |
| A showcase schedule is not a production cadence. | Scenes16/17 intentionally compress rare cues into a minute for review. Workshop uses a separate 120-second attention review; a later long schedule must keep intervals spacious and carry time across chunks. |
| Small masks can make a brittle seam baseline. | A single rain crossing on a tiny city beacon exceeded a four-step local baseline, while ordinary adjacent-second crossings were larger. Compare a representative nearby interval without including the seam itself. Do not hide a real reset with a fade or relax a threshold without explaining the motion. |
| Technical passes and artistic acceptance are independent. | Today's scene16/17 drafts have complete decode, source, colour and join evidence but still await the user's visual verdict. The workshop must also be delivered for normal-speed review before its look is called accepted. |

## Source and delivery records to reuse

- [Crater Rim V5](../../crater-rim-animation-v5/README.md): source-bound emitters, useful holds, coupled reflections and normal-size comparison.
- [Crater Rim long-version handoff](../../crater-rim-animation-v5/LONG_VERSION.md): preserve the weather phase and add an absolute attention clock instead of silently retiming the scene.
- [City16 V4](../../cyberpunk-apartment-animation-v4/README.md): irregular physical traffic, refractive glass, source-linked reflections, original leaf cutouts and corrected wet-region masks.
- [Gate Camp V3](../../gate-camp-animation-v3/README.md): steady periodic water, projected interactive light, shared gust cues and a fixed-source camp.
- [Shared core and review tools](../../scene-animation-core/README.md): native-first processing, portable FFmpeg, explicit BT.709 conversion/tags, direct native-to-YUV controls and actual-video detail reviews.

The scene-specific values remain in those packages. Reuse their methods, remap every source coordinate, and retain their recorded rejection/approval limits.

## Workshop feedback log

The workshop source audit adds three concrete safeguards. The bench's silver vessel is lidded, so inherited cup-steam logic is omitted. The generated sedan's two visible headlamp centres are measured from its actual RGBA sprite and transformed with the body; this avoids source-detached headlight wash. Original-source foliage deforms only inside fixed boundaries, keeping the whole-scene hero plate intact; the generated clean-tree experiment is retained but no longer consumed.

Two defects found after the first numeric pass expose the limit of broad protection gates. The generated clean sky produced a blue arc where a polygon cut through an internal tree-crown chord. An independent palette check can catch this colour injection, while a changed-pixel check based on the same allowed mask cannot. Separately, rain reached the small raised-door fin because that geometry was absent from the main hero exclusion. The correction needs a dedicated fin guard, not a more generous protection threshold. [Correction checks](../source-audit/correction-validation.json) bind those tests to the corrected renderer/settings. Preserve the rejected implementation and revalidate the corrected inputs before restoring delivery claims.

This build also implements the longer attention mode rather than leaving only a prose handoff: `--attention-mode production600` selects sparse600s cue arrays while the environment retains its60s physical phase. The review car event deliberately crosses60s at54–73s to expose accidental chunk-clock restarts. Implemented scheduling is still distinct from a fully rendered, listened-to or artistically accepted long version.

| Date | Layer or issue | Observation | Action and evidence |
|---|---|---|---|
| 2026-11-05 | Source interpretation | Hero car is coherent enough to preserve; rear machinery remains illustrative and the bench vessel is lidded. | Original whole-scene art unchanged. [Source audit](../source-audit/source-geometry-audit.json); no steam/unmotivated exhaust added. |
| 2026-11-05 | Additional motion assets | Generated clean-tree cutouts revealed a blue arc at an internal canopy boundary; the transparent distant sedan remains in use. | Replaced foliage cutouts with fixed-boundary original-source deformation and tap/Jacobian audit. Rejected code/settings/reports remain in `../history/first-cutout/`; old test media stays local. [Asset/provenance record](../assets/asset-manifest.json); sedan headlamp positions still share the actual car transform. |
| 2026-11-05 | Semantic protection | Rain reached a small door fin despite the broad numeric allowed-mask check. | Added a distinct fin exclusion and a dedicated regression guard. Palette and silhouette checks supplement, rather than replace, source/protection/phase checks. Fresh delivery validation required after correction. |
| 2026-11-05 | Independent clocks | Nine groups and both120s/600s attention modes are implemented; the review car crosses the minute boundary. | [Exact settings](../settings.json) and [cue export](cue-sheet.json). Full encoded delivery and the user's playback verdict remain separate checks. |
