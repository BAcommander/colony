# Ambient Colony: lessons to carry into the next video

Updated 2026-11-02. Start here for decisions; follow the linked records for exact prompts, assets, measurements and feedback. Covers the September/October production work, November 1 follow-ups and November 2 reference investigation. This guide consolidates learning, not release approval or a new production schedule.

The aim is a convincing place someone wants to stay, with sound they want to keep playing. A scene needs a distinct identity, readable motion and a comfortable mix. None of those is established by a technical pass alone.

## Where the detailed learning lives

| Area | Working document | What it retains |
| --- | --- | --- |
| Music and sound | [Music workflow](MUSIC_WORKFLOW.md) | Generation lessons, accepted source-specific balances, joins and listening checks |
| Listening evidence | [October 30 ratings](music/reference-analysis/comparison-2026-10-30/feedback-2026-10-30/README.md) | Exact scores, comments and what remains unknown |
| Reference sound analysis | [Analysis index](music/reference-analysis/README.md) and [November 2 texture investigation](music/reference-analysis/nonmusical-2026-11-02/README.md) | Source provenance, measured results, inspection tools and interpretation limits |
| Latest cross-branch production feedback | [November 1 prompt/SFX checkpoint](https://github.com/BAcommander/colony/blob/aa62e427e3f6386217e90229c063820c8f54ccae/music/prompt-learnings-2026-11-01/README.md) | Junction/Deepwell outcomes, duration/fade lessons, reusable SFX and review drafts |
| Visual motion | [Animation knowledge bank](ANIMATION_KNOWLEDGE_BANK.md) | Accepted examples, rejected approaches and scene-specific refinements |
| Production method | [Animation workflow](ANIMATION_WORKFLOW.md) and [next-scene runbook](NEXT_SCENE_RUNBOOK.md) | Freeze, preview, review, render, validate and assemble |
| Believable worlds | [Art-direction guide](concepts/ALIEN_COLONY_ART_DIRECTION.md) | Physical realism, alien identity, source atmosphere and prompt corrections |
| Thumbnail identity | [Thumbnail style](../final/THUMBNAIL_STYLE.md) | Approved series identity and its history; newer sparse-text tests are separate candidates |
| Exploration | [Brainstorm collection](brainstorm/README.md) and [Christmas tests](brainstorm/2026-10-27-christmas-tests/README.md) | Exact concepts, prompts, images, concerns and selection state |
| November music | [Brief pack](music/november-2026/README.md) | Preserved V3 briefs and preparation-stage tracker; see the status correction below |
| Production status | [Production tracker](../PRODUCTION_PIPELINE.md) and scene records | Delivery/approval scope; check the branch and date before using a status |

### Branch and document drift found in this audit

This checkout is on `codex/concept-brainstorms-2026-10-27`. Newer production records also exist in fetched `origin/codex/empty-junction-backup-2026-11-01` at `aa62e427e3f6386217e90229c063820c8f54ccae`. They record supplied music, accepted mixes and exports for Junction/Deepwell, and an approved nine-minute Snowline pair. The local November tracker still contains the earlier ungenerated preparation checkpoint. **Do not use that old status to regenerate accepted work.** Exact later state belongs to the later scene records; completed export does not imply publication or full-session approval.

This audit reads the newer Git records without merging their large production/media tree or switching branches. Commit-pinned links above remain reproducible. [Audit provenance](learning-audit-2026-11-02.json) identifies inspected sources. The older root README also said no music had been produced; that stale statement has been removed.

## Music: what the evidence changes

| Lesson | Evidence and scope | What to do next time |
| --- | --- | --- |
| Listening preference outranks numerical resemblance. | WINTER WATCH, Rainline and Shoreless scored 4/5. Spirewatch scored 3/5 and felt too fast despite coarse spectral similarity. One short rating pass, not all-day acceptance. | Use the preferred owned recordings as listening anchors. Judge perceived pace directly. |
| Slower does not mean a motionless drone. | Early Ringfall was too constrained/droney; revised tests with more internal musical life received positive feedback. Later pace feedback favours less foreground activity. | Retain slow changes of colour, voicing and depth without making every layer follow a tune or pulse. Test the balance. |
| There is no universal bass, width or dynamics correction. | Ringfall's bass-shelf experiment did not improve its score. Later Deepwell/Snowline sources have very little sub-bass. Whole-source fades can inflate LRA. | Inspect the actual source and an interior window. Do not automatically cut bass, widen or compress to copy the reference. |
| Environment can add interest, but its contribution needs a controlled test. | User explicitly valued Rainline's rain. The public-mix comparison did not hold the dry music constant. | Compare the same dry bed with and without the proposed ambience at matched full-mix loudness. |
| Quiet must still be useful and audible in context. | Rainline rain and Shoreless water needed reductions; later Junction wind needed +3 dB, and other effects needed separate reductions. | Review the loudest sustained event and quiet music passages. Change gain, frequency and event duration independently. |
| Choose sounds for their place. | November 1 records say Junction radio/static and a compressor direction did not work; train/quieter grit and Deepwell pump were more useful. | Consult the accepted-source library and the listener viewpoint. A rejected source in one scene is not a ban on that source family everywhere. |
| Prompt wording is not proof of generation behaviour. | Supplied four-minute files differed from the prepared two-minute briefs; exact executed wording/settings remain unconfirmed. Ending fades occurred despite requests. | Record actual prompt/model/duration/cost/export. Keep duration in settings where appropriate; inspect the resulting fades. Duration-free V4 review drafts are proposals, not adopted replacements. |
| Separate the time quantities. | An eight-second wind fade was mistaken for a 60-second event. More frequent Junction events were a separate request from louder events. | Store source duration, prepared repeat period, event duration, fade-in/out, spacing and music repeat interval separately. |
| An hour can be technically seamless and still become repetitive. | Deepwell dry music recurs every 388 seconds. Independent SFX timing changes the combined texture, not that music recurrence. | Review the music join, three repeats, then normal-work listening. Unequal periods are an experiment, not proof of non-repetition. |
| A processing shortcut may remove the quality the user likes. | Newer Spirewatch records preserve rejection of whole-mix slowing and spectral reconstruction; separation experiments did not cleanly isolate the intended part. | Preserve the original. Prefer a new musical source or deliberate arrangement over claiming a successful stem extraction from a failed test. |

The [November 1 checkpoint](https://github.com/BAcommander/colony/blob/aa62e427e3f6386217e90229c063820c8f54ccae/music/prompt-learnings-2026-11-01/README.md) and [later music workflow](https://github.com/BAcommander/colony/blob/aa62e427e3f6386217e90229c063820c8f54ccae/creative/MUSIC_WORKFLOW.md) contain these newer production observations. They do not prove that canonical V3 wording caused the accepted results.

## What today's radio/static investigation adds

The user's listening description is radio-like static, indistinct chatter and a rising/lowering tone. That observation concerns a processed inspection clip boosted by 12 dB, approximately four times its same-gain amplitude. It is not an original SFX balance measurement or proof of physical radio/voice provenance.

The new tool distinguishes candidate narrow-tone frequency motion from level motion. One candidate near 131 Hz has substantial spectral-level variation with little frequency variation; it may be a musical partial, and has not been matched to the particular sound the user means. No level-envelope rate passes the current consistency screen in the inspected minute. Neither result establishes a loop or identifies the static.

Carry forward the **testable design idea**: a separate texture can make a place feel active while the musical bed remains patient. Try it only where the source belongs. Radio texture is an optional experiment for an appropriate scene, not a new house style and not a change to Junction's accepted mix. Establish that the desired detail is audible in the original before treating a filtered artefact as the reference target. Keep level movement, pitch movement, filter movement and intermittent events as separate controls.

**Snowline follow-up, 2026-11-02:** user explicitly selects this scene for original receiver experiments. [Current design/feedback](music/sound-design/receiver-2026-11-02/README.md) preserves rejection of a static-heavy noise prototype, acceptance of V3 voice blur but rejection of its frequency/continuous hiss, and the current V4 gated audition. Reuse accepted voice character while revising event density and switching. Hold per-event gain fixed when spacing events farther apart; whole-effect RMS normalization can otherwise make the remaining bursts louder. V4 has three transmissions, clicks, two acknowledgements and real silent gaps; overall/mix approval remains pending. The approved nine-minute Snowline pair has been restored from LFS with its approved hash unchanged.

**Full-session follow-up:** the user then requests the complete nine minutes with more random spacing. A new 540-second radio score now uses fourteen different phonetic phrases once each, independently made receiver packets, five acknowledgements and 18–58-second quiet gaps. It does not tile the 67-second audition. Full-session listening remains pending. The current clean artwork was restored/inspected: a warm monitoring room looking through closed glazing at a snowy exterior base. [Additional-layer proposals](music/sound-design/receiver-2026-11-02/ice-planet-layer-plan.md) prioritise exterior wind and visible room ventilation; natural atmospheric-receiver signals are an optional original timbral influence, not outdoor sound or reused reference audio.

**Environment audition:** user subsequently selects exterior wind plus quiet ventilation. A separate full nine-minute version now adds four slowly changing, sheltered wind passages and a low-level non-tonal room-air stem, preserving the radio/music parent. The original wind recording is reused; its 24-second source texture still repeats inside the longer gusts. Ventilation is newly synthesized as a complete nine-minute source. Keep environmental source-loop length, passage length, fades and quiet gaps distinct. Full output/recipe checks pass; final balance and long-session comfort remain user listening decisions.

The user finds this first atmosphere balance too quiet. V2 raises only wind/ventilation by 3 dB; source character, scheduling and music/radio remain fixed. User then says **“Enough—keep this level”**: retain the [accepted Snowline atmosphere preset](music/sound-design/receiver-2026-11-02/snowline-ambience-preset-current.json). A source gain reused from another scene plus a new distance filter did not establish audibility here; checking the plateau led to a useful scene-specific revision. Approval covers the combined atmosphere balance, not a universal gain or a full-session listening verdict.

User then authorizes a [wind/settling-detail test](music/sound-design/receiver-2026-11-02/wind-and-creaks-test.md). A preserves approved V2; B varies the sole original wind through unequal overlapping sections and matches passage RMS; C adds only two procedural creaks at1:31/5:38. Four sampled lag24 wind correlations drop from >.9994 to absolute<.016, demonstrating reduced recurrence at those positions, not an artistic win. Full decoded comparisons isolate both changes exactly; selection is pending. Preserve the difference between derived source variations, genuinely new recordings, measured recurrence and user preference.

User says the creak needs work and suggests ElevenLabs. Do not promote C or infer that B won. A concise one-source steel-frame SFX prompt and manual4-second/non-looping test are prepared, ungenerated. A subsequent question about snow is resolved by separating thermal/frame context from a snow-grain source: name an audible action rather than only scenery, and keep layers independently adjustable. No evidence yet that generated foley beats the procedural source.

## Art and atmosphere

- Start with the place's function, camera position, construction and access. Follow doors, steps, supports, paths and services before adding decorative detail. The Brineward entrance correction is a concrete reminder.
- Let one large environmental feature and a consistent engineering/ecological response establish alien identity. A small extra moon does not rescue an otherwise terrestrial scene.
- Use shared weather and illumination to organise colour and depth. Muted colour, a narrow hue range and low detail competition are different choices; blanket desaturation is not a realism recipe.
- Keep quiet areas. Concentrate wear where weather, handling and runoff would produce it. Every surface need not be wet, bright or intricately textured.
- Preserve the specific architecture, technology era, material language, light and everyday story that give a source its atmosphere. The user rejected abstraction that lost the IP vibe; research alone did not make those outputs successful.
- Finish and select the clean scene before typography and animation. Generative thumbnail edits can change geometry and lighting. Preserve both outputs and remap if the animation plate changes.
- Seasonal direction is **“Christmas somewhere you wish you could stay.”** Shelter and believable personal use carry the brief; decorations stay part of the physical scene. The ten seasonal tests are generated candidates, not ten approved releases.

These are user-directed design judgments and documented observations, not measured CTR improvements. Exact examples and unresolved geometry risks remain in the art guide and brainstorm records.

## Animation and final assembly

- Freeze the exact source/hash. Reuse rendering methods, then remap every mask and occluder to that source.
- Prove readable motion at normal viewing size: actual cloud/snow/water transport before small glints or LED activity. More opacity and more particles are not universal improvements.
- Couple light sources to their attached spill and reflections. Independently held habitation events work better as a starting method than synchronised whole-scene breathing.
- Make longer loops genuinely varied across their full duration. Keep established transport speed; do not merely slow a short cycle or call repeated clips a unique long animation.
- Check isolated changed effects, the complete preview and the encoded loop boundary. Technical continuity and source protection do not establish artistic approval.
- Render the accepted short master once and preserve its pictures/colour through long assembly. Disclose source resolution/upscaling and verify final audio/video, timestamps and repetition.
- Apply the current opening once during assembly; keep clean loop masters. Preserve the 0:05–0:20 audio entrance without stacking it over an old baked fade. The current visual opening needs its full 22-second budget. For streams it sits outside the repeating playlist.

## Packaging and performance

The approved branded thumbnails remain an identity reference. Later scene-only/one-word candidates test a different presentation; they do not automatically replace approved releases. Use the current final-scene plate, preserve important planet/location cues, and check at phone size. If image, lighting and text all change, call it a package comparison rather than a typography-only test.

Public view counts, a screenshot and attractive new art cannot diagnose why viewers do not click or stay. Use impressions, CTR by traffic source, retention, watch duration and comparable upload age when available. Separate the discovery question from the listening-comfort question. The [dated channel research](https://github.com/BAcommander/colony/blob/aa62e427e3f6386217e90229c063820c8f54ccae/creative/music/channel-research-2026-10-30/README.md) contains hypotheses and a proposed plan; its dates, thresholds and pending tasks are not current performance findings or an automatically active schedule.

## How to use this on the next actual soundtrack decision

1. Check the latest scene/branch status and accepted sources first. Do not restart Junction/Deepwell or overwrite the accepted Snowline pair because an older plan says “ungenerated.”
2. Review the existing music brief and actual generation record. Use short variants for an unapproved direction; do not prescribe the old two/eight-minute proposals as mandatory settings. Keep four different scene identities.
3. With one chosen dry musical bed held fixed, prepare a comparison: A dry, B with a scene-appropriate environment source, optionally C with the same environment plus a restrained receiver-like texture if it fits that scene. This is a proposed experiment, not generated audio or permission to spend credits.
4. Use constant gain to match whole-mix audition loudness; retain originals and exact recipes. Our -23 LUFS trial setup is a comparison convention, not a universal publication target. Inspection boosts stay clearly labelled and out of preference tests.
5. Record comfort, willingness to keep playing, perceived pace and any distracting event/timestamp. Blank answers remain unknown. Compare the maximum effect level as well as its entrance.
6. Take the preferred version through a join/three-repeat review, 30–60 minutes of ordinary work, and then a longer session. A three-minute score cannot establish the all-day goal.
7. Carry only supported improvements into the following scene. If a condition loses, retain the rejection and revise the specific variable instead of making it the default.

## Keep the learning usable

For each meaningful test or user correction, record **date/scene → exact evidence → decision → scope → next unresolved check**. Update the existing relevant workflow and link its source record; add only the reusable consequence here. Preserve rejected versions and superseded reasoning.

Keep these states separate: proposed, generated, technically checked, user accepted, assembled, published, and remotely backed up. A push does not approve the art, and a code push does not back up ignored media. October 30 research/prompt backup has its own [receipt](music/reference-analysis/backup-2026-10-30.json); November 2 analysis/tools and this guide are currently local/uncommitted.
