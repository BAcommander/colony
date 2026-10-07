# The Empty Junction — v3

Current candidate: full sixty-second silent 1280x720/30 fps loop and exact three-repeat 180-second review. V2 feedback was "it's ok still overall feels kinda static". User authorized the recommended near/middle/distant motion combination. User requested commit/push and said v3 still needs work. This is a work-in-progress checkpoint, not visual acceptance; 4K remains gated.

- [Complete minute](empty-junction-v3-preview-60s.mp4)
- [Three-minute join review](empty-junction-v3-three-loops-180s.mp4)
- [Delivery record](delivery-v3.json)
- [Configuration](scene-plan-v3.json)
- [Preserved v2](../empty-junction-animation-v2/README.md)

## What moves

**Yard powder:** two broken streamers follow shallow curved ground routes, one beside the right-hand track and one across the lit approach near the cabin steps. Native path speeds are 17/22 pixels per second. Density fragments advance, sway and dissipate along the routes, with clear ground between them. The turnout equipment and small trackside post occlude the powder. Local source illumination tints it; the full composite uses current light states. This explicitly authorized addition supersedes the earlier no-foreground-weather proposal only within these masks.

**Cabin condensation:** the original image already contains a small louvred grille to the right of the door, at native x520/y389. It supplies the plume's anchor; no artwork edit or added hardware was needed. Wisps travel right/up, expand and fade over ten-second lifetimes. Independent emission strength follows a sixty-second schedule. Warm tint near the outlet follows the doorway lamp state. Treating this grille as an exhaust is a plausible artistic interpretation, not established engineering.

**Terrain-guided mist:** a separate density stream emerges near the central mineral gap, descends the visible slope and bends along the valley at 8 native pixels per second. A near ridge and antenna occlude it. The v2 mist remains underneath; this addition gives the weather a specific route through the landscape.

The sky, previous far/side mist and all station lighting remain sample-exact to v2 as isolated layers. Full composite pixels outside the new masks also match v2 at the recorded times. Solid geometry and camera remain fixed. No person, hanging hardware, train movement or soundtrack was added.

## Source and method

Unchanged approved artwork: final/11-empty-junction/artwork-v2.png, native 1672x941, SHA-256 ed7b02777c1dcc35504bc0628739688b56515f09ece89d58f299f2dd6013a4be. Existing artwork and v1/v2 media/code/configuration are preserved.

The v3 adapter subclasses v2. Catmull-Rom paths map advected density to terrain; integer harmonic timing closes the minute while preserving forward travel. Gaussian optical puffs follow the mapped grille outlet route, renewing at zero opacity. These are 2D cinematic approximations, not fluid or thermal simulations.

One sixty-second clock drives the scene. No whole-frame dissolve, reverse motion or duplicated endpoint. The 180-second review is three exact repetitions of the unique minute.

## Review and validation

The assistant inspected normal-size temporal and decoded stills, new-motion masks and isolated samples. Continuous playback was unavailable. Numeric change is implementation evidence; only user playback review can establish that the scene feels sufficiently alive.

Initial corrections: evenly spaced exhaust wisps first formed a nearly steady pale streak; birth-time emission variation gives the plume moving concentrations and quiet intervals. The near-ground mask was corrected to exclude a small post, and the valley flow now passes behind the foreground ridge. Earlier occlusion candidate files are retained under history/initial-occlusion/.

Evidence:

- analytic-validation.json: periodic states, layer seam steps and velocity diagnostics, distinct 0/20/40 states, finite pixels and exact source protection outside active native masks.
- isolated-validation.json: three actual-strength ten-second full-composition tests.
- coverage-delivery-validation.json: v2 dependency preservation, retained layers, outside-new-mask comparisons, new effects through the final third, encoded isolated changes and silent streams.
- preview-validation.json: complete 1800/5400-frame decoding, sequential timestamps, unchanged regional/composite seam thresholds, no duplicate endpoint and exact decoded three-cycle repetition.

Fingerprints bind source, configuration, renderer dependencies and native masks. There is no visual quality percentage claim.

## Reproduce

From C:/Colony:

~~~powershell
python music/empty-junction-animation-v3/render_junction_v3.py --stage samples
python music/empty-junction-animation-v3/render_junction_v3.py --stage isolated
python music/empty-junction-animation-v3/audit_delivery.py --preflight
python music/empty-junction-animation-v3/render_junction_v3.py --stage preview
python music/empty-junction-animation-v3/audit_delivery.py
~~~

Use the saved scene-plan-v3.json and fingerprinted dependencies. build_plan.py records plan construction. Existing videos refuse overwrite; use a fresh reproduction checkout or a new versioned destination. finish_records.py updates current project records only after validation fingerprints agree.

Local Python/NumPy/OpenCV/Pillow/FFmpeg only. No image generation, paid services, new models, music or assembly. User explicitly requested commit/push of this version; the exact minute preview, code/config/masks/records and dependency snapshots are selected for backup. See backup-manifest.json and the local remote-backup-verification.json for verified remote evidence. The repeated review and other draft videos remain local. A silent 4K minute follows full-preview acceptance, with identical motion and disclosed upscaling from 1672x941.

For a restored checkout, compare delivery fingerprints before rendering. If a shared dependency has changed or undergone line-ending conversion, restore its exact bytes from the path mapped in backup-manifest.json within an isolated reproduction checkout. Do not overwrite newer shared code in the active project.
