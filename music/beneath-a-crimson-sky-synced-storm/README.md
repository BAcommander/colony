# Skies of Baal: synced storm review

[Play the minute with sound](skies-of-baal-synced-storm-60s.mp4). The user found the [previous full-opening version](../beneath-a-crimson-sky-full-storm/README.md) an improvement and asked for clearer depth, hidden lightning origins and coordinated weather. This new version is for review before a 4K build or music mix.

The far bank, middle sheets and near dust ribbons travel at roughly 36, 89 and 180 preview pixels per second. Finer grains pass the opening faster. The camera stays still. The lightning starts inside the cloud, which glows above the place where the lower channel becomes visible. The bolts keep their roughly three-second re-strike sequences.

| Squall | Wind and dust build | Strike and peak gust | Close thunder | Eases by |
| --- | --- | --- | --- | --- |
| 1 | 0:21.7 | 0:26.4 | 0:28.2 | 0:34.5 |
| 2 | 0:46.3 | 0:50.6 | 0:52.5 | 0:59.1 |

The same envelope drives dust and the wind/grit level. The latter rises from −0.6 dB to +2.6 dB relative to the previous stem. The original [synthesized thunder](../beneath-a-crimson-sky-persistent-storm/rolling-thunder.wav) retains its delays and decay. The [revised effects mix](synced-storm-effects.wav) has no score.

To restore the preview after pulling with LFS smudge disabled, run `git lfs pull --include="music/beneath-a-crimson-sky-synced-storm/skies-of-baal-synced-storm-60s.mp4,music/beneath-a-crimson-sky-persistent-storm/rolling-thunder.wav"`. To rebuild, restore the three LFS inputs named in [the backup manifest](backup-manifest.json), keep the output paths free and run `python music/beneath-a-crimson-sky-synced-storm/render_synced.py` in the existing audio-analysis environment. The noise tiles and their curl wrap together; the added dust changes by about the same amount across the loop join as between nearby frames. [Editable settings](settings.json) · [Delivery checks](delivery.json).
