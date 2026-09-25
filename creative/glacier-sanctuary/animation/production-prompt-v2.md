# Glacier Sanctuary v2 — readable atmosphere, water and lighting

User feedback: snow good; mist and water hard to see; roof plume needs more presence; requested light activity. Preserve accepted snowfall seed, trajectories, sizes, speeds, mask and opacity exactly. Four sampled-time pixel comparisons verify unchanged snow.

Mist: replace broad weak density with three more defined moving banks over the mountain valleys, widths 95/120/110 source pixels, heights 24/26/20 and rightward speeds 14/16/17 px/s. Pale cool density capped at .48, with advected internal structure. Keep mountain geometry fixed and boundaries confined to the arch opening. Judge against excessive opaque fog in normal playback.

Water: increase source-texture ripple displacement to 3.4px horizontal/1.1px vertical and add low-amplitude broken traveling reflection highlights. Keep ice and shoreline masks fixed; no ice warping or full-lake brightness pulsing. Review whether highlights read as water rather than regular stripes.

Roof: retain source anchor (730,451); height105, width23, drift29, opacity .56. Broader coherent rising plume, with smooth dissipation. Never detach from the roof outlet or move the equipment.

Lights: slowly dim the two right-hand annex window panes starting at1.8s, using1.1s transitions and a4.7s event, returning by6.5s. Preserve structural mullions and visible interior texture. Dome entrance, main-room left windows and exterior lamps stay steady. This is localized bay lighting, not a global exposure change or flashing beacon.

Eight-second 720p/30fps silent motion study, not a final seamless loop. Isolated mist, water, roof/lights and combined previews. Visual acceptance pending. Preserve all originals; do not export long/4K media until the look has been reviewed.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v2.json --output creative/glacier-sanctuary/animation/review-v2
