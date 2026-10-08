# Beneath a Crimson Sky - animation v2

Complete silent sixty-second 1280 x 720/30 fps preview and exact three-repeat 180-second review, delivered after the user requested "make the animation" on 2026-10-08. **User feedback: decent, but needs more work. This is a checkpoint, not a final-approved animation.** Uses rebuilt v12 artwork, with fresh masks throughout. Original art and animation v1 remain preserved.

- [Watch the complete minute](beneath-a-crimson-sky-v2-preview-60s.mp4)
- [Watch three repetitions](beneath-a-crimson-sky-v2-three-loops-180s.mp4)
- [Delivery, hashes and checks](delivery-v2.json)
- [Source-bound scene configuration](scene-plan-v2.json)
- [Exact executed prompt](production-prompt.txt)

Cloud texture moves right with unequal phase spacing, sharper dominant texture fields and depth-staggered renewal. Its sky field now spans sixty seconds. Separate far and middle dust travel across the plains throughout the minute. The main gold window and the world/clear opening remain fixed. Six room groups dim independently, including one held event across the join. The terrace lantern varies gently, with its visible core and attached wall/paving/nearby-object illumination coupled.

Three distant intracloud events begin at 8.4, 33.2 and 56.2 seconds. Light follows the actual moving cloud density and stays away from the world opening. The second has a weaker return. Two ember-red events run at 18.1-25.4 and 44.2-52.1 seconds in the recessed lancet above the lit doorway on the domed wing. Existing pane shading and divider remain visible; red spill is confined to adjacent stone. The lamp dip starts at 39.1 seconds. These timings remain candidates. The user gave general positive-but-incomplete feedback without identifying specific remaining defects; do not invent a requested fix.

The optional rain curtain was omitted because the narrow sunset gaps beneath the far-right cloud bank offer insufficient convincing fall distance before the mesas. No foreground rain or dust was added. This is a silent animation; no thunder or music was produced.

## Checks and inspection

Seven ten-second isolated/baseline/composite tests and full analytical source-protection/periodicity checks passed. Both dust depths and clouds remain active in four sampled intervals, including the final third. An encoded cloud feature moves 16 preview pixels right over eight seconds (template correlation 0.974). This supports travel, not an artistic verdict. Paired source textures can still briefly overlap during renewal; review their look in playback.

Every frame of both deliveries was decoded: 1,800 and 5,400 frames, sequential timestamps, 30 fps, no audio, exact three-repeat identity. Regional/composite encoded seams passed the existing gate. A separate comparison to quiet neighbouring frames also passed, so large lightning steps cannot hide a loop-boundary jump. Tagged BT.709 is inspected through FFmpeg RGB decoding. [Validation](preview-validation.json), [analytic checks](analytic-validation.json), [cloud diagnostic](cloud-transport-validation.json), [colour samples](delivery-colour-validation.json).

The assistant inspected source detail, masks, temporal stills and colour-correct decoded event frames at normal composition size; continuous playback was not inspected. The [feedback record](user-feedback-2026-10-08.json) supersedes the immutable delivery record's pending-review status. Technical checks do not make this an approved final. See [implementation notes](inspection/implementation-notes.txt), including the corrected flat-red initial still and omitted precipitation.

## Source and reproduction

Source-v12.png is a byte-identical copy of the rebuilt native artwork: 1672 x 941, SHA-256 bbcb566dac5704b0a046c2c7769f3a73bd0f092851d723988489d627eb12e0b5. No new image generation or detail enhancement was used. Future 3840 x 2160 video will be upscaled from these native coordinates.

Run `python music/beneath-a-crimson-sky-animation-v2/render_crimson.py --stage samples`, `--stage analytic`, `--stage isolated` or `--stage preview` from the repository root. Existing MP4 destinations cannot be overwritten. The original v1 renderer and local effect dependencies are frozen in dependencies; the v2 subclass replaces source mapping, cloud renewal and new light events. Run finalize_records.py only after complete validation. The scene configuration is an immutable build snapshot; delivery-v2.json records current completion/review status.

After complete-preview acceptance, export and validate a matching sixty-second 4K master with the same motion. No 4K video, soundtrack or live broadcast was produced. The user subsequently requested commit/push of all work; see the backup record below. Current generic release copy remains in creative/live/skies-of-baal/release-v2. Unnumbered special after catalog 10; catalog 11 is unchanged. All authored scene and animation v1/v2 files, including historical/test MP4s and both repeated reviews, are selected for this requested backup. [Backup manifest](backup-manifest.json) records the exact scope; the subsequent local remote-backup-verification.json records actual remote restoration/hash checks. Two review files over 100 MiB use exact-path Git LFS. Regenerable Python bytecode and downloaded external references stay local.
