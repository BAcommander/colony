# Regional planetary motion experiment

The selected source stays intact. This experiment uses a 512x320 crop at source coordinates `[900,80,1412,400]`, scaled uniformly 1.5x to 768x480 for local Wan inference. No padding or aspect distortion. The source hash and crop data are saved in config.json.

The mask reuses visually inspected v6 surface/ring polygons, dilates ring exclusions by four source pixels, retains the largest connected atmospheric area, and feathers inward from 3 to 13 pixels. It intentionally excludes the narrow area below the foreground rings. mask-review.png shows the permitted region in green. The room, landscape, rings and planetary edge remain original pixels.

## Reproduce

Start the local server with scripts/start_comfy.ps1. From the repository root:

```powershell
python scripts/planet_pass.py
.local/comfy-env/Scripts/python.exe scripts/run_wan_test.py --name ringfall-planet01 --width 768 --height 480 --frames 81 --input creative/ringfall/animation/planet-pass/planet-input.png --positive-file creative/ringfall/animation/planet-pass/positive.txt --negative-file creative/ringfall/animation/planet-pass/negative.txt
python scripts/planet_pass.py --video creative/ringfall/animation/wan-tests/ringfall-planet01_00001_.mp4
```

Use a new name for each generation. Candidate02 uses positive02.txt, negative02.txt and seed 24092027. Both use 20 uni_pc/simple steps, CFG 5, shift 8, 81 frames at 24fps. API graphs/results live in ../wan-tests; model hashes and dependency lock are reused from that folder. The generation environment runs the model; the existing system Python runs the OpenCV/Pillow compositor and bundled imageio-ffmpeg encoder.

Outputs: a 1280x720 preview and a 1920x540 original-versus-animated comparison, plus five temporal samples and a pre-encoding mask-leak report. Videos remain local, excluded from Git. They are 3.375-second diagnostic clips, not seamless loops or 4K finals.

## Review

Candidate01 completed in 196.20 seconds. Six sampled raw frames at 0/16/32/48/64/80 show framing drift and a dark blotch forming by the end. Rejected for artistic quality. A diagnostic composite was rendered to test preservation: maximum difference outside the mask is exactly zero before encoding. This technical success does not make the generated atmospheric motion acceptable.

Candidate02 simplifies the instruction to continuous horizontal flow of existing stripes, excludes new storm spots, and uses a different recorded seed. Review completed below; both candidates failed the artistic gate.

No registration correction has been applied. Significant changes of geometry/scale should be rejected rather than silently hidden. Only two generation candidates belong to this initial experiment.

## Completed review

Candidate02 completed in 200.846 seconds. Raw temporal samples show scale/position drift and horizontal artifacts in rings/terrain. Re-decoding the identical cached latent with untiled VAEDecode completed in 25.340 seconds; history confirms nodes 1-9 were cached, so this was not a third generation. Artifacts persist, so tiling alone does not explain them.

The second candidate's untiled output was composited for diagnosis. Full-scene frames 0/16/32/48/64/80 and five crop samples were inspected. Room, rings, terrain and planet silhouette remain fixed; outside-mask maximum source difference is zero before encoding. However, the drifting generated bright limb enters the upper atmosphere mask, creating an edge/texture mismatch. This fails the artistic gate. No continuous playback review was performed; no seamless-loop claim is made. Both candidates remain rejected experiments.

Best diagnostic comparison: ringfall-planet02-full-decode_00001_-comparison.mp4. Preview: ringfall-planet02-full-decode_00001_-preview.mp4. Both are local-only. Decoded preview verified: 1280x720,81 frames,24fps,3.375 seconds.

Learning: cropping plus a static mask successfully protects unrelated image geometry, but does not constrain movement inside the generated region. A future test should avoid feeding a moving planetary silhouette into the accepted cloud area: generate a cloud texture without the planet/rings and map it with fixed geometry and illumination, or use a controllable atmospheric simulation. This is an untested proposal, not an established solution. Do not continue enlarging the mask or fading the effect until defects are hidden.
