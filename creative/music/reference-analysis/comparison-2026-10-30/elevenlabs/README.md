# ElevenLabs: measured development, not a promised prompt

These are **original candidate briefs**, not an identification of WINTER WATCH's instruments, notes, effects or production method. No music has been generated or uploaded during this investigation. Existing workflow keeps paid generations manual; no API key or credit purchase is needed for the analysis/test artifacts.

## Current priority after the first listening test

User ratings supersede the initial spectral starting point: Rainline and Shoreless tie with the reference at 4/5, while Spirewatch is 3/5 and feels too fast. [Exact verdict](../feedback-2026-10-30/README.md). Use [D: environment-first pilot](D-environment-first-after-ratings.txt) as the current ungenerated brief. The prior A/B/C prompts and API examples below remain preserved proposals, not executed or approved tests. Test a slow bed and environmental texture separately; do not assume reducing Ringfall bass improved preference (original and treatment both 3.5/5). The API long-form scaffold still needs a successful owned generation and longer listening acceptance.

## Why this direction

Spirewatch already approaches the reference's coarse tonal profile. Its smaller loudness range and greater channel similarity suggest testing dynamic movement and spatial independence separately. Ringfall's sub-heavy balance is a different, measurable problem. Do not roll all five tracks into a universal “more bass, less treble, less movement” instruction. Do the existing level-matched trials first; sound measurements alone cannot choose the preferred harmony, texture or atmosphere.

## Verified capabilities, 2026-10-30

- [Music composition API](https://elevenlabs.io/docs/api-reference/music/compose): text prompt or composition plan; current models include `music_v2_5`; prompt duration can be up to ten minutes. Seed is available with a composition plan, not the text-prompt route; repeatability is not guaranteed across model/system updates. `force_instrumental` is a prompt-route field, so the prepared plan examples instead specify instrumental style and exclude vocals.
- [Chunk composition plans](https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans): `music_v2`/`music_v2_5` use chunk lists, individual chunk duration 3–120 seconds and total duration up to ten minutes. High context adherence is intended for continuity. Prepared files use the current chunk schema, not the old v1 global/section schema.
- [References](https://elevenlabs.io/blog/introducing-references-sound-control-for-music-v2): condition on the style/feel of an existing track; intended for music you've made yourself. This page lists 10 seconds–5 minutes, while the [best-practices page](https://elevenlabs.io/docs/overview/capabilities/music/best-practices) mentions roughly 30 seconds. The actual UI limit needs checking; use a short owned excerpt. This is distinct from a 30-second inpainting conditioning slice. No competitor recording has been uploaded or prepared for upload.
- [Music inpainting](https://elevenlabs.io/docs/eleven-api/guides/how-to/music/inpainting): retain slices of stored music, regenerate sections and condition adjacent new sections. The documented loop method generates a bridge between kept audio slices. This is a potential repair step if a candidate join is difficult, not proof our candidate already loops cleanly.
- [Loop Studio](https://elevenlabs.io/blog/introducing-tools-on-elevenmusic) is presented around genre/BPM, drums, bass and a motif. That advertised workflow is not evidence it is the best route for this beatless, slowly evolving target. Start with Music composition and verified local assembly.

## Stage 1 — replicated palette and movement tests

Ready-to-paste text files:

1. [A: palette control](A-palette-control.txt).
2. [B: same brief plus spatial independence](B-spatial-independence.txt).
3. [C: same brief plus broader slow dynamics](C-slow-dynamic-movement.txt).

Use the same actual model, duration (two minutes), settings and export format for all conditions. Record the model exposed in the UI, rather than assuming a selector exists. Generate two independent results per condition to reduce the risk of selecting one lucky generation. This proposes twelve generated minutes if all six are run; check current displayed cost before spending. No old credit rate is assumed current.

For a future API workflow, the six prepared JSON bodies pin `music_v2_5`, pair the same two seeds across conditions and use 120-second chunks. These are request examples only; no caller executes them. Matched seeds can help consistency but do not isolate every musical detail when a prompt changes. The text-prompt route does not supply the same seed control. This is replicated experimentation with stochastic generation, not proof that a wording change alone caused an outcome.

Keep original exports and fill [test-matrix.json](test-matrix.json). Analyse the full export with our local tool. Treat the reference's measured profile as a comparison, not exact percentage/LUFS pass/fail rules. Reject obvious faults/vocals/foreground interruptions through listening. Match audition gain to −23 LUFS, compare without identifying labels and record preference and tiring moments. A candidate advances because it is preferred and remains comfortable, not because a fabricated similarity score says so.

If neither condition improves the user's preference, revise the palette/arrangement; do not keep rerolling the same brief indefinitely or infer that ElevenLabs cannot do it from one failure. This stage is a concrete test of current capabilities, not a guarantee of success.

## Stage 2 — keep a successful original sound while extending

Use a short excerpt of **our own preferred dry generation** as the reference, preserving the sound family. Keep rain/water and other SFX separate. The reference steers character, not exact continuation. Store the song ID if using API inpainting.

[Prepared eight-minute plan](long-form-8min-plan-api.json) uses four two-minute continuity chunks. The sound-family styles remain stable; only subtle thinning, receding and voicing directions change. This plan is a candidate scaffold and still needs the successful palette/reference added using the supported UI/API workflow. It does not automatically insert a reference, and no placeholder song ID pretends otherwise.

Audition the actual full export. Find usable material away from generated fades or cadences. Use local join reviews first; an inpainting bridge is another documented option if needed. Inspect and listen to three repetitions before making a long export. Do not assume a prompt saying “loopable” guarantees a seam.

## Stage 3 — the actual all-day acceptance test

Screen short candidates, then test the selected long source over 30–60 minutes while the user does normal work. Mark any moment that repeatedly draws attention or creates an urge to change the track. Repeat on a second session at the same playback level. This is the first direct evidence of sustained comfort; a short test cannot substitute for it.

If a short unit becomes obvious or tiring, try a coherent 20–40-minute assembly of several compatible original pieces before the outer repeat. This is our proposed production experiment, not a claim about how Ambient Outpost constructed its stream. If a single unit already works for hours, additional material is not automatically an improvement. Keep the recipe for the version the user actually prefers.

The honest unknowns are now explicit: preferred musical content, whether the prepared prompt conditions deliver it, and long-session acceptance. Current measurements, local matched trials and documented ElevenLabs capabilities narrow those unknowns; they do not erase the need to generate and listen.
