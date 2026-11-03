# Snowline: other sounds that belong in this scene

2026-11-02. User selects **exterior wind and quiet ventilation**. User found V1 too quiet, then accepts [V2's +3 dB atmosphere balance](environment-v2-balance-approval.json) with “Enough—keep this level.” Retain these scene-specific settings. Other layers below remain proposals. The earlier radio-only mix and V1 are preserved for comparison; full-session listening is a separate review.

## Establish the listening position

The restored current artwork shows a warm enclosed monitoring room, closed frosted glazing, equipment, heater/ventilation grilles beneath the window and a snowy base beyond an enclosed bridge. The dish and cannon are exterior structures. Use the room's perspective rather than an unprotected microphone in a blizzard or an underwater ice recording.

Source: `aa62e427e3f6386217e90229c063820c8f54ccae:final/13-below-the-snowline/ice-planet-retheme-v3/artwork-v5.png`, restored locally for inspection at `exports/restored-snowline-2026-11-02/artwork-v5.png`, SHA-256 `2007d8121670a25c44e93caedec2bf1d80f7c5a8ef8ee6bd03e3579b1568516f`. Assistant inspected the complete current image. Earlier underground ice-vault art is historical.

## Recommended order

| Priority | Layer | Placement and behaviour | Listening risk to check |
| --- | --- | --- | --- |
| First | Exterior wind with occasional blowing-snow texture | Beyond the sealed glass; broad, slowly changing gusts, with quieter intervals. Preserve enough source detail to feel like weather, then set its distance/level in the mix. | A loud constant howl or foreground hiss can overwhelm both refuge and radio. |
| First | Quiet ventilation/heater circulation | The visible under-window grilles give it a specific source. Soft, rounded room air with only gentle level drift. | Additional bass drone, an obvious motor pulse, or another constant layer as bright as radio static. |
| Later | Small thermal/structural settling sounds | Very occasional short ticks/creaks in the warm frame or distant building, with a consistent room distance. | Repeated clicks can sound like a faulty mix; dramatic cracks suggest danger and attract attention. |
| Later | Distant base utility activity | One restrained airlock closure or brief equipment servo, heard through the building/enclosed bridge. | Foreground storytelling, rhythmic machinery and too many competing activity cues. |
| Alternative receiver colour | Sparse atmospheric-receiver whistlers | Brief, low-level descending shapes coming from a scientific receiver, replacing a few carrier gestures rather than adding a new continuous track. | Piercing sci-fi beeps; suggesting that radio emissions are directly audible outdoors. |

Start with wind and quiet ventilation as a separate comparison against the current radio-only mix. Add rare details only if those two layers leave useful space. No cannon fire or battle sequence is proposed for the depicted idle base. These choices are artistic interpretations, not measurements of actual ice-planet acoustics.

## Reuse and evidence

The newer branch already contains a Snowline wind-in-scene audition at `music/below-the-snowline-wind-review-2026-11-02/`. It used the untouched library original `music/sfx-library/assets/wind-soft-exterior-01.mp3`, hash `324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34`, with +4.85 dB source gain, 60-second events and 120-second gaps. That gain came from Deepwell as a starting point; Snowline wind acceptance remains pending in the source record. Do not assume an approved universal preset or silently reuse its regular schedule as a new random one.

The source wind LFS object has now been fetched/hash-verified and used with a glazing filter and newly scheduled long passages. Original source bytes are unchanged; the library's gain-adjusted preview is not used. Quiet ventilation is newly synthesized and saved separately. V2's atmosphere balance is accepted; full-session acceptance is not inferred. Two procedural frame/pipe settling details now exist in the optional test below; no distant door/servo or receiver-whistler layer has been made.

Primary-source research gives useful inspiration without supplying audio for this mix:

- [British Antarctic Survey: Sounds of Space](https://www.bas.ac.uk/project/sounds-of-space/) describes VLF signals received at Halley and converted to audio, including descending whistlers and brief spheric cracks. These require a receiver; they are electromagnetic signals, not free-air sounds. This supports an original scientific-equipment colour for our fictional dish/radio station. No BAS audio is downloaded or reused.
- [Ben Burtt's Empire sound-design interview](https://www.starwars.com/news/empire-at-40-ben-burtt-interview) discusses building believable worlds from manipulated real-world source recordings and maintaining a reusable sound library. Our practical interpretation is to give each layer a physical source and useful role before adding more effects. It does not provide a validated all-day listening recipe or approval of our synthetic textures.

Both sources checked 2026-11-02. The exact added sources, gains, placement and full-session feedback should be recorded before promoting an environmental version.

## Included-layer audit and next refinement candidates

User asks whether all the ambient-style SFX are included, and what else could improve the mix. The current V2 deliberately includes fourteen distinct blurred transmissions, receiver opening/closing clicks, gated static and carrier movement, five acknowledgement events, four broad exterior-wind passages and continuous quiet ventilation. These are the layers actually built. A complete effect inventory of the earlier external reference was never established; this is not a certified recreation of that recording.

The user's accepted V2 wind/ventilation balance remains the baseline. Two frame/pipe creaks are now included in optional test C only. Distant utility/door activity, dedicated snow/ice-detail recordings and atmospheric-receiver whistlers remain proposals; their presence in this planning document does not make them part of the approved audio.

Recommended next tests, in order:

1. **Wind source variety.** The known 24-second wind-source cycle can recur several times within one passage. It is the clearest remaining short-source repetition risk in the recipe, not a defect established by assistant listening. Try a small pool of genuinely different wind takes with unequal starts/overlaps and longer changing gust shapes, holding the accepted broad balance. Merely changing the entry phase of one source does not produce a new wind recording.
2. **Viewpoint/space review.** Check that the receiver reads as the left console, ventilation as the under-window grilles, and wind as weather beyond the closed glazing. The existing render already uses a near-mono receiver and placement filtering; refine those relationships if listening warrants it rather than assuming they are missing. This may add depth without extra event density.
3. **Sparse building detail.** As a separate candidate, test two quiet frame/pipe settling creaks across nine minutes, or one distant service-door/servo event. Choose a consistent source and distance; preserve room for the existing radio. No new effects are generated by this audit.
4. **Full-session attention check.** During normal work, log any event that pulls attention, whether a voice becomes too foregrounded, and whether a wind repetition is recognizable. The plateau approval establishes the accepted atmosphere balance, not every later event or long-session comfort.

[Apple's sound-design session](https://developer.apple.com/videos/play/wwdc2023/10271/) discusses overall ambient backgrounds, localized foreground/midground sounds and randomized timing. It supplies general spatial/layering principles, not evidence that any particular change improves this music video. Our scene placements and proposed event counts above are design judgments; listener results decide whether a candidate replaces the accepted baseline. No audio, gain, source, schedule or approval changed in this audit.

## Authorized follow-up test

User subsequently says “ok lets do the test.” [Wind variation plus two settling details](wind-and-creaks-test.md) now has A/B/C comparisons. There is still only one original wind file: B/C use differently overlapped original-rate sections, not new independent wind recordings. B changes wind alone; C adds two quiet procedural creaks to B. Known lag24 waveform matches fall substantially at four sampled positions, and passage RMS is matched, but preference remains untested. Supplied 90-second comparisons and full nine-minute B/C versions await selection; approved V2 stays current.
