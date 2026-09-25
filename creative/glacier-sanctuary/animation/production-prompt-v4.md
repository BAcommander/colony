# Glacier Sanctuary v4 — calmer water and visible exterior lighting

Feedback: distant fog now good; water too strong; exterior lights still not readable. Preserve approved v3 fog, snow and v2 roof exhaust. Sampled isolated-layer comparisons confirm no changes to fog, snow, smoke or existing annex event.

Water: halve moving-highlight strength13 to6.5 and reflection phase speed12 to6. Reduce displacement4.5 to2.8px horizontally and1.7 to.85px vertically. Preserve broken crests, fixed ice and shoreline masks. Review calm readable motion without the previous dominant shimmer.

Exterior lighting: widen existing-lamp halos to17–25 source pixels, increase local amber intensity, and use a12% added-light floor for a visible slow cycle. Four lamps remain staggered on ten-second cycles, with no core blackout or strobe. Add elliptical warm snow pools around(278,643) and(650,637), constrained to hand-mapped ground polygons and synchronized to their respective lamps. Preserve texture and geometry; no global exposure changes. Judge at full-frame size, especially the nearest path lamp at left of the stairs.

Eight-second720p/30fps study, not seamless or final. Isolated water and exterior-light clips plus combined. Existing accepted effects are not rerendered separately unnecessarily. Next loop stage requires consistent snow/mist lifecycle as well as light periods; do not label this preview seamless.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v4.json --output creative/glacier-sanctuary/animation/review-v4
