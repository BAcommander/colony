# Beneath a Crimson Sky: passing sandstorm test

[Watch the silent 60-second sandstorm candidate](beneath-a-crimson-sky-sandstorm-test-60s.mp4) and compare it with the [V3 dry-gust preview](../beneath-a-crimson-sky-animation-v3/beneath-a-crimson-sky-v3-dry-gusts-60s.mp4). The storm grows after 0:12, moves across the middle of the minute and clears by 0:51. The test asks whether one stronger gust makes the sheltered terrace feel more inviting.

The distant dust bank advances more slowly than two lower streamers. Sparse grains appear in the stronger gust. The cliff, nearby rocks and parapet hold out the dust. The existing fortress lights, sky and near terrace retain their V3 motion and colour. The storm falls away before the loop boundary, with no added audio.

If this intensity works, audition a rise in the exterior wind and a brief grit pass. Over a long video, vary when the stronger pass occurs instead of making it happen every minute. Use the [weather and SFX plan](../../final/15-beneath-a-crimson-sky/weather-and-sfx.md) for thunder as a separate cue.

Reproduce with `python music/beneath-a-crimson-sky-sandstorm-test/render_sandstorm.py` in the same environment as V3. The script checks the source hash, all decoded frames, frame spacing and the clear start/end against V3. See [delivery checks](delivery.json). This is a separate candidate for playback review.
