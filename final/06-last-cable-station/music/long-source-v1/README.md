# Mineral Valley Transit - source and loop auditions

2026-10-03: user supplied the longer export after selecting Colony Cableway Transit. Requested generation was seven minutes; decoded source is 480 seconds (eight minutes), preserved byte-identically in exports/06-last-cable-station/source/. Exact generation settings and actual prompt were not observed.

- [66-second join audition](../../../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-join-v1.mp3): the overlap runs from 0:25 to 0:41.
- [Three repetitions, 20:43](../../../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-three-repeats-v1.mp3): overlaps at 6:49-7:05 and 13:38-13:54.

Candidate retains source 0:38-7:43 (425 seconds). Sixteen-second sine/cosine equal-power overlap gives a 409-second repeat interval. Fixed -7 dB gain brings the approximately -13.1 LUFS source near the preceding release's listening level, with no compression. The short audition has 0.15/0.3-second edge fades; the three-repeat preview has a single 5-second opening/10-second closing fade.

Candidate selection uses measured level and coarse stereo spectrum similarity; these do not prove harmonic compatibility. Listen for a change in harmony, a swell/dip, or an obvious restart through the overlap. User accepted the audio/transition on 2026-10-03: "the audio sounds good enough". Full long-form listening is not implied. Full audition decode/sample counts and loudness/peak measurements passed; see audition-v1.json. Assistant did not listen.

Reproduction: analyze.py preserves and analyzes the original; make-auditions-v1.py refuses to overwrite existing exports. Hashes, cut points, gain, curves and technical checks are saved. Originals and v1/v2/v3 prompts remain intact. User confirmed two hours and accepted v3 animation. The [two-hour MP3](../../../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3) and combined 4K Colony video are now delivered. See two-hour-delivery-v1.json: same cut/overlap/gain, single ten-second opening/twenty-second closing fades, exact 7200-second decoded duration, -20.4 LUFS and -9.6 dBTP. Reproduce with ../../../../music/cable-animation-v3/make-two-hours-v1.py. Full combined review and listening remain pending. No credits spent, no upload, commit or push; ignored media remain local only.
