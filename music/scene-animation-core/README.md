# Shared scene16/17 first-draft helpers

`core.py` contains ROI masks, bounded source-cloud transport, toroidal moving noise, seeded vapour, original-cutout motion over generated backfill, premultiplied sprite scaling and native-first encoding. It uses the imageio-ffmpeg binary and explicit BT.709/TV conversion/tags. The city and Gate Camp renderers own their source geometry and creative settings.

From the repo root, use the existing `.local/audio-analysis/Scripts/python.exe`. Pinned packages are in `requirements.txt`. Run each scene renderer with a new `--output` name. Output is silent720p; there is no4K/full-length renderer or production600s attention schedule in this checkpoint. The60s attention events are deliberately compressed for review.

`validate_review.py city` and `validate_review.py gate` fully decode/timestamp-check the minute, compare15 exact native-to-YUV controls, test241 independent native source/warp states and compare actual encoded regional loop joins with nearby frame steps. The encoder also checks protected native pixels on every frame. These gates cannot establish natural-looking motion or artistic approval.

`make_reviews.py city|gate` creates enlarged actual-video detail crops and an exact55–60/0–5s join review, with provenance. It refuses overwrites. `build_delivery_pack.py` connects verified results to the paired local review page, scene briefs/catalog/tracker and shared learnings; it is a once-per-checkpoint updater, not an idempotent general publishing tool. It does not commit, push, upload or generate audio.
