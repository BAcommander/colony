# Glacier Sanctuary v3 — distant fog, exterior halos, readable water

Feedback: smoke and snow good; push distant fog; add exterior light halos/pulses; water still invisible. Preserve v2 snow and roof exhaust exactly. Isolated sampled-frame comparisons verify both, including existing room-light event.

Fog: widen moving valley banks 15%, increase their vertical scale45%, cool pale color194/210/229, density cap.56. Preserve coherent rightward transport. Allow mountains to show through and inspect for blanket fog obscuring the composition. No shifting mountain silhouettes.

Exterior lights: source anchors(277,588),(634,578),(776,586),(125,404). Add soft amber halos with radii13–17 source pixels and localized additive spill. Each halo has a steady floor and slow10/12-second sinusoidal breathing with staggered phase. Lamp cores remain present; no blackouts, flashing, global exposure modulation or added fixtures. Keep dome glow steady.

Water: 4.5px horizontal and1.7px vertical source-texture ripple. Introduce broader broken reflection crests traveling through the open-water mask at approximately20 source px/s. Brightness strength13, crest/trough asymmetry and irregular horizontal breakup. Preserve ice exclusion and shoreline fade. Review at full-frame1x for visible water motion without uniform stripes, an electric shimmer or warped ice.

Render eight-second720p/30fps silent study with isolated mist, water, exterior_lights and combined. Not seamless:12-second lamp periods and linear mist/snow travel need a common final timeline after visual approval. No twenty-minute or4K render yet.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v3.json --output creative/glacier-sanctuary/animation/review-v3
