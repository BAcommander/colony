# Ambient Colony — SFX library

[Open the searchable listening library](index.html). Six source sounds: soft exterior wind, gentle water, distant freight, fine mineral grit, circulation pump and sheltered rain.

Original source files are byte-preserved in assets/. The library deduplicates identical source hashes, so the wind used in Junction and Deepwell is one sound with two usage records. Existing project sources remain untouched. The catalogue is local; no commit, push or remote backup is implied.

Preview copies are adjusted by constant gain toward −24 LUFS for browsing, with peak headroom. They are not mix presets. Use the original source and consult the scene-specific gain, fades, event duration, recipe and feedback. No new effect was generated and no original audio was processed in place.

Acceptance means the user accepted that source in a particular composition. It does not imply that every source works everywhere or has a universal favourite rating. Source descriptions reflect the intended use and saved brief, not assistant identification of every sound in the recording. Related briefs are preserved with exact hashes; the actual generator wording/model/settings remain unconfirmed where not documented.

Before reusing a sound, check:

1. Does the source belong to this location, viewpoint and distance?
2. Is it comfortable at its loudest point while the music is quiet?
3. Is the event long enough to be felt? Distinguish source duration, loop period, event duration and fade duration.
4. Does it need quiet gaps? Vary event placement separately from music, without claiming this removes musical repetition.
5. Can an existing accepted sound meet the need before generating another?

When adding a sound, preserve its original bytes, SHA-256, duration, provenance and any confirmed exact prompt. Separate related prompt drafts from verified generation prompts. Add scene-specific uses and exact feedback; keep candidate/rejected/accepted states distinct. Rejected approaches can be recorded without promoting their files into the accepted set. Do not silently update established project recipes when the library changes.

The current six sources are modest in size and are copied once for portability. Previews are regenerable and ignored by Git. Any future backup should explicitly verify both catalogue and original audio scope; nothing is remotely backed up merely because it appears here.
