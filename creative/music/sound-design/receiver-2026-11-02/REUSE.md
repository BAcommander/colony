# Snowline sound design: settings and lessons to reuse

Updated 2026-11-03. The user requested the selected minute-test settings across the full two-hour V5. Full-session listening remains pending. These are source-specific settings, not universal ambient mix defaults.

## Current mix

| Layer | Current arrangement | Current level / source treatment |
| --- | --- | --- |
| Music | Approved 540-second Shelter/Outpost pair repeats through two hours. | Unchanged source at unity stem gain. This remains a repeating musical source. |
| Radio | 47 calls; voice entrances 122–176 seconds apart. Fourteen existing blurred phonetic packets reused in varied orders. | −1.5 dB versus V4, tested as −1 dB then −0.5 dB. Chatter, clicks, gated static, tuning/carrier and acknowledgements move together. Original packet gain 0.24984153 becomes analytically 0.21021545. |
| Exterior wind | 80 passages; 22–31 seconds fully off between passages; 69.89% scheduled coverage including fades. | +2 dB to the whole wind stem versus V4. Retains the earlier up-to-10% crest lift near full outer envelope, unequal overlapping 9–14-second sections and 1800 Hz sheltered-viewpoint filtering. One original 30-second recording; fragments recur. |
| Ventilation | Quiet interior air; existing 540-second source repeats. | Unchanged from the accepted environment V2 balance. |
| Frame creaks | 24 events across two hours, mostly roughly 4–6 minutes apart. One supplied four-second take with two existing right/left balances. | +4 dB versus two-hour V1; cumulative ×1.91772076 versus first supplied-creak placement. V5 retains V4 creaks. Original MP3 is preserved in the [SFX library](../../../../music/sfx-library/README.md). |

The effects have a complete two-hour schedule; the 18-minute composite is not tiled. Scheduling does not create new voice takes, wind recordings or music. See [current machine-readable settings](snowline-working-mix-current.json), [all event times](cue-sheet-two-hour-2026-11-03.txt) and [V5 full checks](two-hour-balanced-v5-2026-11-03.json).

The listening MP3 has fixed **+0.4 dB** overall gain, no baked opening and one 20-second closing fade. It measures −23.1 LUFS, 10.2 LU LRA and −7.5 dBTP. The separate lossless master is the unfaded unity-stem sum: apply +0.4 dB once to match the listening copy, and apply the current intro/closing once during assembly. The master already includes every SFX layer. Do not add them again.

## What changed through listening

The first receiver was too static-heavy. The later blurred voices were sufficiently indistinct, but occurred too often and the static was too consistent. Gating the receiver with opening/closing clicks, tails, carrier movement and occasional acknowledgements made a more specific experiment. These are original design choices, not verified sound-source detections from WINTER WATCH.

The first nine-minute score had 14 calls averaging about 37 seconds between voice entrances and only four wind passages, with 55–71-second off gaps. User feedback was less chatter and more wind. The final arrangement separates these decisions: radio every 2–3 minutes; wind returns after 22–31 seconds off. Keep that distinction when designing the next location.

The creak needed several contextual level revisions. The exact chain is **×1.1, ×1.1, +1 dB, +1 dB, +2 dB** relative to its first placement. Two-hour V1 already included both 10% steps. Consequently V4/V5 are +4 dB versus two-hour V1, not another two 10% increases on top of the current setting. “10% louder” was implemented as amplitude ×1.1 (+0.82785 dB), not a measured change in perceived loudness.

## Method for the next video

1. **Design for the listener's position.** Snowline is an enclosed monitoring room: wind outside closed glazing, quiet room air inside and occasional frame movement. Keep snow-grain/spindrift texture separate if it is ever selected; do not bake broad wind into a creak source.
2. **Separate character, density and gain.** Blurring voices does not fix excessive frequency. Varying wind fragments does not fix long silent gaps. Change source gain independently of duration, fades and event spacing.
3. **Keep per-event gain fixed when reducing density.** Whole-source RMS normalization can make sparse calls louder. Preserve source/event gain first; evaluate the new arrangement in context.
4. **Review sustained maxima and masking.** The first creak check at 1:31 was in a wind-off gap. It could not establish audibility during a wind maximum. Use the same window for a changed layer and its control, at the same whole-mix gain, without independently normalizing either clip.
5. **Record what the excerpt contains.** The wind/creak check covers 26:55–27:55, creak at 0:10, full wind envelope at 0:06–0:45, no radio. The radio check covers 3:15–4:15, voice at 0:10, full wind envelope at 0:07–0:46, no creak. A short clip with three calls and a long wind-off tail can bias an impression of the whole score.
6. **Check the changed component, not just whole-track LUFS.** The radio −1 and −1.5 dB clips both round to −22.2 LUFS overall. Full sample-level reconstruction confirms the receiver change while the musical bed dominates the meter.
7. **Arrange long effects independently of music.** Use a fixed seed and save the full cue sheet/packet choices. Sparse original takes still recur; longer timing alone does not prove an all-day, non-repetitive result.
8. **Preserve the actual source and uncertainty.** One supplied MP3 is one take, even when balanced two ways. The executed ElevenLabs prompt/model/settings/cost are unknown. Keep the prepared prompt as a related brief, not proof of the generation settings.
9. **Keep a single current state.** V5 has the selected gains applied; its pending-adjustment object is empty. Do not reapply gains mentioned in historical audition records. A request for the full version selects render settings; it is not a full two-hour listening verdict.

Original sources and every November 3 export, including earlier mixes/tests, are covered by the [portable backup and restore guide](../../../../music/snowline-sound-design-2026-11-03/RESUME.md). The [case history](README.md) retains exact feedback, recipes and technical evidence. No assistant listening, new paid generation, video assembly or publication is claimed.
