# Spirewatch v4 — connected digital city

Delivered 2026-10-21. Technically verified; user animation and thumbnail review pending. Earlier versions preserved.

- **Watch:** [complete sixty-second preview](spirewatch-v4-preview-60s.mp4).
- **Join review:** [three exact repetitions, 180 seconds](spirewatch-v4-three-loops-180s.mp4).
- **Thumbnail:** [1280x720 JPEG](thumbnail-v1.jpg), [native generated PNG](thumbnail-v1.png), [exact generation prompt](thumbnail-prompt-v1.txt).
- **Music:** [eight-minute prompt](music-prompt-eight-minutes.txt). User is generating the track; no new audio was received or evaluated in this pass.

The main spire charges near its base, sends staggered light up existing channels (3–17s), holds near its crown, then sends a later return downward (37–53s). Six cyan districts respond with delays. Three bridge passages (4–20s cyan, 25–42s amber, 45–59s cyan) have attached trails and broken water reflections. The original monitor map has transit tracking and small acknowledgements; warm windows have slower independent holds. Two local cloud storms peak around 28.6 and 54.6 seconds. A faint lamp reflection follows its local lighting state.

The exact same 1672x941 source is retained. Eight weather/water/lamp layers match v3 exactly at five sampled times. New light reflections do not increase water displacement. Geometry stays fixed; thumbnail pixels never enter animation. The generated thumbnail has brighter marketing lighting and some fine-geometry differences from the clean scene.

Validated all native layer endpoints/source protection, all 1800/5400 decoded frames and timestamps, regional/composite and quiet-neighbour seams, exact three-cycle identity, and all six contiguous-render boundary pictures. Details: analytic-validation.json, preview-validation.json, repeat-validation.json, chunk-join-validation.json, delivery-v4.json. The assistant inspected native/decoded stills and temporal crops, not continuous playback.

No 4K, long combined video or music sync yet. Lighting has an activity control for the eventual eight-minute energy arc; actual timings await the supplied music. No commit/push in this session; new files are local.

Reproduction: use the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. The versioned package already contains its source/config/dependency snapshot; do not rerun setup_v4.py. Check with check_v4.py; render with render_parallel.py; verify with render_spirewatch.py --stage verify and check_chunk_joins.py. Render destinations must be absent; preserve previous outputs before any deliberate revision.
