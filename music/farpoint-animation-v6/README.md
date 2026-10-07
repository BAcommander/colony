# Farpoint Station v6 — drifting stars and cabinet status lights

Complete sixty-second revision, silent 1280x720/30 fps. User playback acceptance remains pending; 4K follows acceptance.

- [Full minute](farpoint-station-v6-preview-60s.mp4)
- [Three-minute join review](farpoint-station-v6-three-loops-180s.mp4)
- [Delivery and fingerprints](delivery-v6.json)
- [Configuration](scene-plan-v6.json)

The user still could not see star movement in v5, authorized removal of the floating amber bars, and requested LEDs on the lower-right cabinet. The planet, weather, monitor and existing station lights retain v5. No new cloud approval is inferred.

## Visible changes

280 compact star sprites extracted from the source move together gently right and slightly upward. At 720p they travel about 7.66 pixels right and 0.80 pixels upward over eight seconds. Camera, station and planet geometry remain fixed. Positions now change; the six-star brightness treatment from v5 is disabled.

The safe sky mask excludes the planet, station and window borders both when extracting textures and when compositing. The faint background stays stationary. Stars renew independently at zero opacity, with five-second edge fades in their sixty-second lifetimes. This is a cinematic looping approximation, not physical celestial mechanics. There is no whole-field reset, reverse travel or global dissolve. Local fades and positional readability still require playback review.

The three queried amber/white bars beside the monitor are removed using a generated local repair patch. The desk lamp and its desk spill remain. The new animation plate is [artwork-v4b-reflection-cleanup.png](../../final/10-nightward-station/artwork-v4b-reflection-cleanup.png), native 1672x941, SHA-256 8eeffb7e02a09c61604b8ed36309eda86585f707b83e94dedab3db45c5f83247. Every pixel outside the small cleanup mask matches the original art. The old reflection dimming layer is disabled on this plate.

The cleanup used built-in image_gen edit mode. Its [exact prompt](reflection-cleanup-prompt.txt), generated patch, native mask and [provenance](asset-provenance.json) are saved. The first direct composite created dark oval patches; colour/gradient matching corrected that before video production. The failed artwork-v4 candidate and its initial provenance remain history, not the active source.

A small dark status strip follows the lower-right service door's perspective. Cyan power remains steady; green activity has short acknowledgements across the minute; amber status has longer holds around 18, 36.5 and 56.2 seconds. Core and nearby spill share each light's state. The LEDs are a procedural addition requested by the user, not pre-existing source details.

## Verification and inspection

- analytic-validation.json records finite/protected pixels, matching periodic states, per-layer seam gates and exact sampled retained v5 regions.
- isolated-validation.json records full decoding/timestamps for separate ten-second star and cabinet tests at actual strength.
- preview-validation.json records 1,800/5,400-frame full decoding, sequential timestamps, unchanged encoded regional/composite seam thresholds, no duplicate endpoint and three exact decoded repetitions.
- targeted-validation.json checks confined source cleanup, unchanged lamp/desk pixels, complete planet composite equality with v5 at 0/7/20/40/54 seconds, encoded star translation, forward star velocity across the join, LED states and silent video streams.
- visual-review.json records inspection scope and pending user verdict.

The assistant inspected native cleanup/cabinet crops, masks, full-composition temporal samples and decoded stills. Continuous playback was unavailable. Numeric tracking verifies transport survived encoding; it does not prove the movement looks right or that the loop is artistically accepted.

V1–v5 media and code and original artwork remain intact. The v4 aurora stays removed. Packaging artwork and thumbnails retain their original provenance; the narrowly corrected plate is separately recorded as the v6 animation source. No soundtrack, long assembly, paid credits or model installation was performed. User explicitly requested commit/push on 2026-10-07. The exact v6 minute preview, corrected plate, source/config/masks/records and dependency snapshots are selected for Git backup. See backup-manifest.json and the subsequent local remote-backup-verification.json for verified remote evidence. Three-minute review and older/isolated draft videos remain local. Backup authorization is separate from visual acceptance.

## Reproduction

From C:/Colony, with the saved clean plate and configuration:

~~~powershell
python music/farpoint-animation-v6/render_farpoint_v6.py --stage samples
python music/farpoint-animation-v6/render_farpoint_v6.py --stage isolated
python music/farpoint-animation-v6/render_farpoint_v6.py --stage preview
python music/farpoint-animation-v6/audit_delivery.py
~~~

Rendering refuses existing video destinations. Reproduce in a separate checkout with saved dependencies and no output videos, or choose new versioned destinations. Do not rerun the assets stage over the saved source; it is the one-time construction step. Fingerprints bind source, configuration, renderer chain, shared dependencies and native masks. The generated patch is retained so reproduction does not require another generation call.

After full-preview acceptance, export a sixty-second 3840x2160/30 fps silent master with the same motion settings. Disclose upscaling from 1672x941 and validate the encoded master again. This candidate does not authorize a finished-release or remote-backup claim.


## Backup and restoration

User explicitly requested commit/push on 2026-10-07. The exact v6 minute preview, corrected plate, source/config/masks/records and dependency snapshots are selected for Git backup. See backup-manifest.json and the subsequent local remote-backup-verification.json for verified remote evidence. Three-minute review and older/isolated draft videos remain local. Backup authorization is separate from visual acceptance.

The three shared scripts have exact-byte copies in dependency-snapshot/. If a future checkout or shared-script change no longer matches delivery-v6.json, restore those snapshots to their original scripts/ paths in an isolated checkout before reproducing. Farpoint hash-bound Python/JSON use -text Git attributes to preserve bytes. Do not replace shared scripts in an unrelated active production checkout.
