CYBERPUNK APARTMENT V3 — TEN SECOND LOOP

Delivery: 10 seconds, 60 fps, silent. 4K H.264 CRF 11, plus a smaller 1080p copy.
4K is upscaled from the original 1672 x 941 artwork, with no artificial sharpening.

Changes from V2:
- Four hovering vehicles removed using built-in image_gen edits. Only the repaired patches were composited into the original image, preserving all pixels outside those masks.
- Traffic uses unique vehicle headways, lengths, intensities and colors, plus small individual speed variations. Nearby routes move faster on screen. No three-car repeating tile.
- Traveling bands in three existing signs, scrolling gradients in three illuminated panels, and independent window groups. Strong sign changes subtly affect nearby reflections.
- Sparse steam filaments rise from the existing cup. The pot, leaves, furniture and camera remain stationary.
- Rain has varied length, opacity and slant, with brightness responding to its surroundings. Mist is restricted to gaps and cloud banks; water alone receives fine refraction.
- The full scene has a ten-second period, including traffic and steam. It is not V2 repeated twice or slowed down.

Preview-Draft.mp4 is a reduced-frame-rate motion study, not the final deliverable.
prepare_art.py reproduces the precision patch composite; render.py rebuilds the video. brief.txt contains the user's complete direction. art-prompts.txt documents the built-in imagegen repair prompts.

Verified: 600 frames decoded without errors, exactly 10 seconds at 60 fps and 3840 x 2160. The final 4K file was checked through four complete playback loops, with a direct V2 comparison and full-resolution crop inspection. Road headways remain above 18 pixels at 1080p throughout the cycle; checked unmoving foreground pixels remain unchanged before compression. The two five-second halves are distinct. A rectangular light-mask artifact found during review was corrected before the final export.
