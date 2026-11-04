# Skies of Baal: persistent storm audition

[Play the 60-second preview with sound](skies-of-baal-persistent-storm-audition-60s.mp4). Stronger sand moves just outside the opening throughout the minute. Low ribbons and faster grains travel behind the parapet, with stronger passages around 0:19 and 0:41. The close stone and the lantern frame the storm from shelter. The earlier [passing storm](../beneath-a-crimson-sky-sandstorm-test/README.md) remains available for comparison.

The original visual had three intracloud flashes and no thunder. This pass adds four flashes, two of them with visible forks: **0:26.4 and 0:50.6**. Six original synthesized thunder rolls arrive 1.8–3.3 seconds after their flashes. Listen at **0:28.2 and 0:52.5** for the closer rolls. The effects audition contains no music or rain. Thunder has soft tails of 9–12 seconds and the underlying wind stays up between events.

- [Thunder stem](rolling-thunder.wav) · [Wind and grit stem](storm-wind-grit.wav) · [Full PCM effects mix](storm-audition-mix.wav)
- [Picture checks](visual-checks.json) · [Sound levels and cues](sound-checks.json) · [Delivery checks](delivery.json)

`render_visual.py` uses the previous passing storm as its picture source. `design_sound.py` reuses the library wind and grit and builds a new deterministic thunder stem. Both run in the existing audio-analysis environment. The render verifies all 1,800 frames and the dust loop states. The PCM stems are exactly 60 seconds and thunder tails carry across the minute boundary. The compressed review file is for judging intensity; mix stems separately and vary the audible thunder schedule for long playback.
