# Below the Snowline — native V6 production loop

Completed master: `masters/Snowline-v6-loop-120s-4K.mp4`, exact120s/3600frames,667,708,094bytes, SHA-256 `c1da088c92fcfdf65a54c3a63d9ab5252f0633b1b5551316bebc123c17339845`. The complete encoded validation passed; `master-validation.json` identifies the actual output and controls, and `visual-inspection.json` records the reviewed comparison/decoded stills. Rendering took272.6s; source artwork and approved V6 remain intact.

The approved V6 source artwork, configuration, geometry, shuttle RGBA master and renderer are frozen byte-for-byte in `source-snapshot/`; `source-manifest.json` records their original paths, sizes and SHA-256 hashes. The original V6 package is untouched. `render_native.py` renders the original **1672×941** artwork directly and the encoder scales those native RGB frames once to 3840×2160 with Lanczos. This retains detail absent from the earlier 1280×720 review; it does not invent native 4K artwork detail.

The final production loop is 120 seconds at 30fps. Its continuous weather and console motions are made periodic individually, without a whole-scene dissolve, reversal, pause, or alternate cloud source. The original shuttle passes, constant hull alpha, blue exhaust, physical cliff/frost occlusion, bridge walkers and cannon charge windows remain. Their invisible/zero states at the loop boundary avoid duplicated traffic or ghost vehicles.

`prepare_native.py` keeps every renderer adaptation explicit and fails if its expected approved-source expressions change. Geometry remains in original native artwork coordinates. Literal sizes previously expressed in 720p pixels—including shuttle width, exhaust, cloud displacement/reserve, fog scale and cannon bloom—are scaled to retain their apparent size. Physical lens RGB still comes from the source, the cloud map is still a single bounded continuous warp, and all flight effects share the approved supersampled occlusion mask.

Continuous angular frequencies are rounded to the nearest positive integer number of cycles over120s. Their phases are aligned to the approved48s frame. Very slow cloud motions consequently become one full smooth cycle per120s (original main horizontal sine period194.78s and vertical232.48s); the smaller horizontal term becomes two cycles instead of original81.68s. Fog texture transport makes one traversal per120s for original speeds1.2/1.6/2.3/3.0 texture pixels/sec, and two for4.4; the old phase is retained at48s. These are gentle production timing adjustments to make a true loop. Tiny radar contacts likewise use integer orbital cycles. Pulse periods change37→40s,19→20s,17→120/7s and43→40s; beacon periods use the closest divisor of120s.

Snow keeps the same seeded particle population and forward/downward direction. Each particle traverses an integer number of padded spatial torus widths/heights per120s; its small sinusoidal gust/flutter is also periodic. Wraps occur beyond the visible/faded region, with positive directional velocity verified. The wind envelope repeats the existing8–80s and108–169s events, including periodic copies: the second gust carries naturally through the boundary into the next cycle. This provides a continuous repeating visual weather pattern; it is not a claim that every visual gust matches the independent two-hour audio event schedule.

Reproduce from this directory with the installed Python environment:

```powershell
python prepare_native.py
python production.py samples
python production.py benchmark
python production.py parallel-render
python verify_master.py
```

The first two steps freeze/check inputs and generate native safety/seam/appearance evidence. The benchmark protects existing output files and uses a two-second4K sample. `parallel-render` runs six20s segments with four workers, global native timestamps, H.264 QP0, two encoder threads each, no B frames, fixed60-frame GOPs and explicit BT.709 TV tags, then copies their packets into one120s master. Lossless encoding prevents inter-segment quantization resets. `verify_master.py` decodes all3600 pictures, checks every PTS/DTS/duration, compares direct native-to-4K YUV reference hashes at all segment/loop joins and selected details, and measures actual decoded join motion. Existing output files are not overwritten by rendering.

The main soundtrack, Colony opening and full two-hour assembly are owned by the parent production package. This visual unit is silent and contains no title graphics or audio gain/fade operations. `master-validation.json` is only written with `status: passed` after the encoded checks succeed. Its hash identifies the exact unit used for assembly. Continuous playback and user approval of the production adaptation are not inferred from numeric checks; the approved V6 treatment and separately inspected production stills remain distinct evidence.

The installed FFmpeg initially omitted H.264 primary/transfer tags despite the explicit encoder flags. `repair_color_tags.py` adds the four BT.709/limited-range SPS fields without re-encoding and compares every decoded frame/timestamp before and after. The original untagged master remains in the cache. The production encoder and concatenation command now include the same `h264_metadata` bitstream filter for reproducible future outputs; `metadata-repair.json` records the actual first-run repair.
