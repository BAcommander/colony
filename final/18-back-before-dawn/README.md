# 18 — Back Before Dawn

Selected for animation on 2026-11-05 from H1, **The Time Machine at Midnight**, the existing Back to the Future inspired workshop concept. The user asks for the complete animation treatment and for today's learning to be saved. This selects the scene for development; the new motion, public title, thumbnail, soundtrack and finished video still require their own review.

The viewer stays inside a warm working garage beside the parked time machine, looking past it into a wet, quiet street. The car is the main subject. The continuous life should come from weather, instruments and their attached light, with quiet intervals between the larger practical cues.

[Clean source artwork](../../creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/concept-v1.png) · [Original concept and source notes](../../creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/README.md) · [Existing thumbnail study](../../creative/brainstorm/2026-10-27-retro-worlds/h1-workshop/thumbnail-v1.jpg) · [Source and status manifest](manifest.json)

[Animation build brief](../../music/back-before-dawn-animation-v1/documentation/BUILD_BRIEF.md) · [Today's reusable lessons](../../music/back-before-dawn-animation-v1/documentation/LEARNINGS.md) · [Sound and cue design](../../music/back-before-dawn-animation-v1/documentation/SOUND_AND_CUES.md)

## Current build

<!-- delivery-status -->
Current delivery: [watch the120s visual draft](../../music/back-before-dawn-animation-v1/Back-Before-Dawn-v1-first-draft-120s.mp4). The complete encoded delivery and source checks passed against the current files. User full-speed artistic review, full600s schedule playback, audio and4K remain pending. [Technical evidence](../../music/back-before-dawn-animation-v1/delivery-validation.json).
<!-- /delivery-status -->

The complete first review is a silent 120-second 1280×720 video at 30 fps, processed from the native 1672×941 clean plate. A continuous 60-second weather phase and a separate 120-second attention schedule keep physical motion independent of the review length. The renderer also implements a sparse 600-second attention mode; full ten-minute playback and user acceptance of that schedule remain pending.

The nine implemented effect groups are exterior foliage, rain, wet road, eave drips, cabin instruments and receivers, oscilloscope, work-lamp/bonnet response, lamp-beam dust and passing traffic. Foliage uses bounded original-source deformation with fixed region boundaries and source-tap/Jacobian checks. The generated clean-sky cutout attempt is retained as rejected history and is not consumed by the current renderer. A generated RGBA 1980s sedan supplies the distant pass, with headlamp response anchored to its measured source lenses. The parked hero car and original whole-scene source remain untouched.

The review cues start with gusts at 9, 65 and 104 seconds; lamp dips at 27.4/27.76 and 94.2 seconds; six independent panel changes at 12/34/45/76/87/102 seconds; an upper-bank diagnostic sweep at 78–90 seconds; and one 19-second passing-car event starting at 54 seconds. Its path crosses the minute boundary without restarting. Actual vehicle visibility depends on the viewport and source occluders.

Read the manifest's delivery fields for current media/check status. Native checks, full encoded-delivery checks, assistant still inspection and user visual acceptance are separate records. Source artwork and the earlier thumbnail study are preserved separately.

The first visual pass exposed two semantic mask defects despite numeric checks: a generated blue arc appeared along an artificial cut through a tree crown, and exterior rain reached the small raised-door fin. The corrected foliage keeps its boundary fixed and samples the original canopy; rain now has a separate fin exclusion. [Independent fin/palette guards](../../music/back-before-dawn-animation-v1/source-audit/correction-validation.json) supplement the usual checks. Old code/settings/reports and test media are preserved as history. Current delivery claims require fresh checks against the corrected inputs.

## Review priorities

1. Rain and street movement must read at full composition and normal speed, while the interior and parked car remain structurally stable.
2. Cabin displays and the oscilloscope must animate the photographed instruments, with their bezels, controls and original hardware retained.
3. A lamp or instrument change must carry into the nearby surfaces it illuminates. Avoid a full-image exposure pulse or a broad blue wash over the car.
4. Any optional wind or passing-light layer must follow the actual source geometry and have its own normal-strength review, rather than adding motion for its own sake.
5. The complete 120-second composite and actual loop join need review before a matching 4K master or long assembly.

## Packaging and sound

**Back Before Dawn** is the working scene title. The existing H1 thumbnail is a candidate from the earlier brainstorm, not a newly approved design or a pixel-preserved version of the clean source. Any new inspired-by title or thumbnail should keep the car readable at phone size and follow the established Colony typography.

No new soundtrack or SFX balance is approved in this build. The listening position supports quiet equipment air and rain heard from inside the open garage. Selected relay/servo details can follow the implemented attention cues. The exact [cue sheet](../../music/back-before-dawn-animation-v1/documentation/cue-sheet.json) should drive later sound timing; Snowline's gains and event frequencies are not presets for this scene. No steam is added to the lidded workbench vessel.

The [official production notes](https://www.backtothefuture.com/movies/production-notes-1985) inform the handmade equipment direction. This workshop and its generated car remain an illustrative interpretation, not a screen-accurate prop or set reconstruction.

## Production handoff

Keep the scene review clean and silent. Apply the current Colony opening once during a later finished assembly, rather than baking it into repeating scene motion. Record the final runtime, music, SFX, source gains, joins, closing fade and upload package separately.

The source is 1672×941. Any later 3840×2160 delivery is a disclosed upscale from that plate. User visual acceptance, full-length listening, publication and remote backup are distinct checkpoints.

[Review page and chapter controls](../../music/back-before-dawn-animation-v1/review.html) · [Continuation recipe](../../music/back-before-dawn-animation-v1/CONTINUE.md)
