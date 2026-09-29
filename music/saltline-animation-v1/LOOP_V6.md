# Saltline Receiver — twenty-second loop v6

Requested on 2026-09-29: “could the loop be 20 seconds?”. The user previously accepted the v5 twelve-second look. V5 media, renderer, config and manifest remain untouched.

Current preview: `saltline-v6-loop-20s.mp4`, 1280×720/30 fps, 600 frames, silent. Join review: `saltline-v6-three-loops-60s.mp4`, three stream-copied cycles. These new periodic outputs await user review; v5 acceptance is not relabelled as acceptance of v6.

`scene-plan-v6.json` sets one twenty-second scene duration. The accepted v5 adapter supplies source mapping, masks, light apertures and events. `render_saltline_loop.py` adds the periodic timeline; `periodic_transport.py` renews local dust bodies with zero-weight births/resets and matched seam states. Cloud transport uses the established staggered source-texture method. The sunlight patch travels forward and resets only at zero opacity. Foreground dust remains disabled. Camera, terrain, equipment, sun and exposure remain fixed.

Motion rates are unchanged: clouds 2.5 source pixels/s, far dust 20 pixels/s and localized sunlight shadow 28 pixels/s. Dust shape, colour, optical depth, cap and masks are unchanged; renewal phases and local fades are now periodic rather than the finite prototype schedule. Light timings/holds/fades are the same twenty-second schedules used by v5. The new cloud blend and dust lifetime overlaps require visual seam review despite exact mathematical periodicity.

`v6-analytic-validation.json` checks periodic endpoints and individual layer steps, and samples dust coverage across all twenty seconds. `v6-delivery-validation.json` fully decodes 600/1,800 frames, checks sequential timestamps and encoded last-to-first changes for each layer region and composite, and verifies three identical decoded payloads. No duplicate endpoint, reversed motion or full-frame dissolve. Source pixels outside active masks are asserted unchanged for every generated frame. Still inspection and user artistic acceptance are recorded separately.

Reproduce from repository root with the existing Python/OpenCV/NumPy/Pillow and FFmpeg:

```text
python music/saltline-animation-v1/render_saltline_loop.py --stage samples
python music/saltline-animation-v1/render_saltline_loop.py --stage preview
```

Existing video destinations are protected against overwrite. V6 review media remain local ignored files until accepted. Native artwork is 1672×941; no 4K output is claimed by this 720p review package. After the full-loop look/join review, export the short 4K master from the same timing/config and revalidate.
