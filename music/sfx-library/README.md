# Ambient Colony — SFX library

[Open the searchable listening library](index.html). Seven original sources: exterior wind, gentle water, distant freight, mineral grit, circulation pump, sheltered rain and the supplied painted-steel frame creak.

Original bytes live in `assets/`, with SHA-256, duration, provenance, related briefs, scene-specific gains and feedback in [catalog.json](catalog.json). Six source/preview pairs were imported exactly from production commit `aa62e427e3f6386217e90229c063820c8f54ccae`; its larger production tree was not merged. The new four-second [creak original](assets/creak-painted-steel-frame-01.mp3) matches the supplied MP3 exactly, SHA-256 `8d126f0c72a3b2e991ba7e56347da2364d191823c12077d0e61d3eccf77f8ea6`.

The six earlier sources retain their recorded scene acceptance. The creak and later Snowline wind settings were selected for the two-hour V5 render; full-session listening remains pending. No universal favourite or gain default is inferred. One source reused with two balances remains one take. Material descriptions record intended use, not assistant identification of the recording.

Previews use constant gain toward −24 LUFS with peak headroom. They are browsing aids, not mix presets. Source and preview files are included for portable listening. Use the original and consult the scene recipe before mixing. Refresh the existing catalogue page with `python music/sfx-library/build_library.py --refresh`; `--validate` checks original/preview/prompt hashes. The default importer and its historical snapshot describe the initial six-source build and should not be rerun over the catalogue.

Before reusing a source:

1. Match the location, listener viewpoint and distance.
2. Audition full sustained peaks and quiet music, preserving the comparison's whole-mix gain.
3. Separate source length, prepared repeat period, event duration, fades, spacing and gain.
4. Arrange useful quiet gaps without normalizing sparse events louder.
5. Check an existing source before generating another; keep the complete take and natural tail.

[Snowline's reusable notes](../../creative/music/sound-design/receiver-2026-11-02/REUSE.md) record the final radio/wind/creak balance and exact gain chain. The related ElevenLabs prompt is a prepared brief; executed prompt/model/settings/cost were not supplied. Add those details only when confirmed.

[Portable session backup](../snowline-sound-design-2026-11-03/RESUME.md) includes the full audio history and restore commands. Actual remote evidence belongs in its `backup-verification.json`; catalogue presence alone does not establish remote backup.
