# Ambient practice → Ambient Colony's November prompts

Researched 2026-10-30. User confirms the next four queued videos: The Empty Junction, Deepwell Station, Below the Snowline and Crater Rim Survey. This research informs **proposed** prompts; it does not establish their generated quality or explain Ambient Outpost's production method.

## Evidence we already have

[First listening ratings](../reference-analysis/comparison-2026-10-30/feedback-2026-10-30/README.md) put WINTER WATCH, Rainline and Shoreless at 4/5, both Ringfall versions and Basalt at 3.5, Spirewatch at 3. Your note says Spirewatch feels too fast and rain adds interest on Rainline. These are short personal trials, with missing distraction scores, not population evidence or long-session approval.

[Signal comparison](../reference-analysis/comparison-2026-10-30/README.md) distinguishes low-frequency balance, level movement and channel similarity. Spirewatch's coarse tonal resemblance did not predict your preference. Ringfall's measured bass discrepancy did not yield a higher score after the tested shelf. Those findings prevent using a numerical spectrum/width/loudness target as a musical recipe. The reference's short exact repetition remains unconfirmed, despite strong detection of our known recorded repeats.

## Practitioner research

### 1. A continuous setting with optional attention

In a first-person [ABC interview](https://www.abc.net.au/listen/programs/musicshow/brian-eno/3125602), Brian Eno distinguishes music that tells a developing story from a consistent sonic setting. His account allows small ongoing variation while the listener's attention comes and goes. Sound texture is central to his approach.

**Our inference:** keep an established sound family; avoid writing a small dramatic story into every generated piece. Reducing foreground replies does not require freezing the sound. This is an artistic model that fits our stated use, not a scientific definition of every ambient work.

### 2. Change can come from density, space and internal motion

In an interview on [Robert Rich's own site](https://robertrich.com/media/interviews/questions-from-tomasz-kowalczyk/), he describes gradual flow, listening in context, environmental sound as a sense of location and depth extending beyond left/right positioning. He also notes that too much activity can make a piece less interesting, while melodic lead voices can draw attention.

**Our inference:** test whether a single layer slowly receding or changing colour supplies enough interest before adding more notes. Front/back depth and quiet texture are candidates; a low correlation number alone is not a goal. His methods describe his practice, not verified properties of WINTER WATCH.

### 3. Atmospheric does not have to mean static

Steve Roach's [official Long Thoughts notes](https://www.steveroach.com/product/long-thoughts/) describe developing a long-form work through extended listening and evolving harmonic/sound-design relationships. That is useful process evidence, not independent verification of the page's wellbeing language.

**Our inference:** retain internal movement and evaluate the actual long export in repeated ordinary listening. Do not prescribe completely even intensity or pretend a one-minute test proves an hour works. We do not adopt medical, sleep-cycle or physiological claims from artist publicity.

### 4. Environmental detail and musical space can be composed together

In [KMRU's Ableton interview](https://www.ableton.com/en/blog/kmru-spaces/), he discusses texture-based work without the grid, quiet environmental recordings and processing a sound while retaining its original layer. [Patricia Wolf's first-person interview](https://www.ableton.com/en/blog/patricia-wolf-natural-synthesis/) describes choosing sounds for a particular filmed place and refining layers through editing and mixing.

**Our inference:** scene identity can come from the room/environment as well as instrument choice. Keep musical and environmental sources separately adjustable. Choose a source appropriate to the viewpoint, rather than adding generic rain to all four scenes. Generate/record intelligible environmental detail and set its depth and level in the mix; our earlier muffled-water brief lost too much useful detail. Neither interview proves that adding any field recording improves retention.

## What experimental research can and cannot tell us

[Kiss and Linnell's original study](https://link.springer.com/article/10.1007/s00426-020-01400-6) tested 40 students using preferred music and silence during a low-demand sustained-attention task. Preferred music changed reported attentional states, but did not significantly improve overall reaction time/variability. Its duration and task do not establish a recipe for all-day listening, programming work or a specific ambient palette.

**Application:** use the listener's preferences and normal work context in evaluation. Do not advertise these prompts as scientifically proven focus/sleep music. No study here validates 69% bass, a particular BPM, a fixed note, a stereo-correlation target or our proposed event density.

## Current ElevenLabs implementation

Checked against official [best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), [composition API](https://elevenlabs.io/docs/api-reference/music/compose), [composition plans](https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans) and [References](https://elevenlabs.io/blog/introducing-references-sound-control-for-music-v2).

The product supports musical/production descriptions, instrumental direction and structured arrangements. Text prompts and composition plans are alternatives. Music v2/v2.5 plans use chunks; API prompt generations can reach ten minutes, while the actual UI controls must be checked. Style reference and exact preservation/continuation are different capabilities. Use a short **owned dry generation** as reference after choosing it; no competitor audio upload is part of this pack. Current reference-length descriptions differ across official pages, so use the actual interface rather than a memorized limit. Seeded plans can aid consistency but are not a reproducibility guarantee.

The new text prompts omit invented LUFS/percentage demands, a mandatory key/BPM, artist/channel names and requests for guaranteed seamless looping. Free-time is our chosen direction in response to feedback, not a definition that excludes all rhythmic ambient music. Prompt instructions are requests: the export still needs checking.

## Audit of the previous four briefs

| Previous request | Why reconsider it | V3 proposal |
| --- | --- | --- |
| Piano-like figures and answering voices in 11/12/14 | May create identifiable musical events and a remembered sequence; not proven to have caused any existing score | Sustained sound colour, sparse voicing drift and changing depth |
| Bring in a voice at 1:00, figures from 1:30–3:30, one last reply | Builds a narrated arrival/departure pattern that can recur at every loop | Continuity without a required section change at a fixed timestamp |
| Even level throughout | Can be interpreted as static when our goal is gentle internal movement | Stable overall atmosphere, shallow independent slow changes |
| Very long cold tail / bowed-metal-like texture | Can become shrill, vocal-like or over-resonant; risk rather than observed V2 failure | Diffuse, restrained upper texture with a warm near layer |
| Scene narrative and adjectives | Can overpower useful production instructions or invite effects | One scene-mood sentence; explicit sonic roles |

V1/V2 prompts were not generated for these four packages. These are prospective wording risks, not a diagnosis of unheard V2 audio. All previous prompt files are preserved.

## Decision rules for November

1. Begin with two variants of a two-minute music pilot. For the first scene, compare against a duration-matched V2 control if budget allows; replicated results reduce one lucky/unlucky generation driving the conclusion.
2. Choose on comfortable matched-volume listening. Record perceived pace, foreground intrusions, bass pressure, boredom and willingness to keep playing. Blank means unknown, not a perfect score.
3. Extend only the chosen owned dry sound. Assess the full export; an attractive beginning does not approve the rest.
4. Audition music alone and the **same music** with quiet scene ambience, matching overall loudness. This tests ambience separately from a different composition. Include the sustained SFX plateau and quieter music passages.
5. Review the actual join and three repetitions; mark recurring attention-grabbing moments. An outer loop can be suitable even when material repeats. Do not introduce constantly changing layers merely to avoid repetition.
6. Listen for 30–60 minutes during normal work, then a longer session. Match playback conditions and keep the accepted version/recipe. Our goal is a preferred place to remain, not the lowest event count or closest spectrum.

No paid generation, audio upload or publication occurred during this research step. All V3 prompts and mixing ideas remain untested proposals.
