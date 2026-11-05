# Workshop sound and shared cues

The first animation review is silent. This file records a future sound direction and its relationship to the visual build; no new audio, gain, generation prompt result or balance approval is implied.

## Listening position

The viewer is inside the open garage, close to quiet workbench equipment and the parked car. Exterior rain should sound outside that shelter. The street and small electrical details provide gentle variation without demanding attention every few seconds.

| Layer | Intended role | Visual relationship | Review constraint |
|---|---|---|---|
| Equipment/room air | A low, maintained workshop bed. | Mostly independent of display changes; no need to make each light audible. | Avoid a strong mains tone or broad static that masks the score. |
| Exterior rain | Continuous weather with restrained natural density variation. | Follow the same exterior weather/gust envelope as the animation. | Audition against the same music at the intended listening perspective, not as an isolated loud rain demo. |
| Relay/servo detail | Rare, soft signs of live equipment. | Attach only to a chosen attention event supported by visible hardware. | Sparse events with varied spacing; do not create a short repeated beep loop. |
| Distant road wash | A brief soft exterior movement. | Use the implemented sedan path, visibility and shared headlamp/body state. | No sharp horn, near engine or sound while the vehicle is absent. |
| Tree/wind texture | Occasional outdoor movement. | Use the same gust as the fixed-boundary original-canopy deformation and exterior rain/road response. | Do not add persistent flapping or storm force to a calm workshop. |

## Timing handoff

The environment uses a continuous 60-second periodic phase, while the first complete visual review has an independent 120-second attention schedule. [cue-sheet.json](cue-sheet.json) exports the actual current settings, source hash and both schedule arrays for later sound work. Regenerate it whenever the renderer settings change.

The renderer also implements `--attention-mode production600`. Its sparse attention schedule is available for the longer build, but full ten-minute visual review and music/SFX balance remain pending. Carry its absolute clock across rendered chunks so the same cue is not restarted at every minute boundary. Keep the60s physical fields unchanged while widening rare-event intervals.

The120s visual review has gust onsets9/65/104s; lamp dips27.4/27.76/94.2s; six bank starts12/34/45/76/87/102s; diagnostic78–90s; and a19s sedan pass starting54s. The600s mode has gust onsets45/194/361/521s; lamp143.4/143.76/436.2s; banks72/153/248/327/418/507s; diagnostic382–394s; and sedan starts214/489s. Those are visual cues, not instructions to make every lamp or panel change audible.

## Lessons from the listening work

The user reduced Snowline chatter frequency and auditioned wind, creak and snow in context. Carry forward the process: change one variable, compare the same music section, hear event peaks rather than only fades, then record the user's actual verdict. Do not transplant those source-specific gains or frequencies into the workshop. Quiet electronics should not become an uninterrupted static bed or a constant warning beep.

The Hoth music method is a starting approach for a later composition: slow tonal/harmonic movement with room for separate environmental layers. It is not authorization to reuse an iconic film theme or assert an ungenerated prompt has solved long-session listening. Keep original music and SFX sources, provenance, gains, timing and joins separate in the delivery recipe.

## Fields still pending

- Original music and SFX assets or new generation decisions.
- Contextual audition gains, event frequencies, fades and user listening feedback.
- Long runtime, accepted attention schedule and once-only Colony opening/closing assembly settings.
