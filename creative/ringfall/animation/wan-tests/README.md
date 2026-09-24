# Ringfall: free local AI video experiments

Authorized September 24, 2026 after the manually composited v6 was rejected for insufficient visible motion. This experiment tests whether Wan produces more convincing scene-wide movement. It is not yet an approved final, a seamless loop, or native 4K.

## Setup

- Official ComfyUI clone: `C:/Colony/.local/ComfyUI`.
- Isolated Python 3.12 environment: `C:/Colony/.local/comfy-env`.
- ComfyUI initial revision: `1568e6cfd04586a4b3c4e1817ea7dde09b1bf9e7`.
- PyTorch `2.14.0+cu130`; CUDA operation verified on RTX 4060 8GB.
- Wan2.2 TI2V-5B FP16 diffusion weights, Wan2.2 VAE, UMT5 XXL scaled FP8 text encoder from Comfy-Org's official repackaged model repository.
- Local server only, paid API nodes disabled. No paid services or per-video credits.
- Runtime and model files are excluded from Git using `.local/`.

Official instructions: https://docs.comfy.org/tutorials/video/wan/wan2_2

## Repeat a test

From PowerShell in `C:/Colony`:

```powershell
./scripts/start_comfy.ps1
# In a separate terminal, after the server starts:
./.local/comfy-env/Scripts/python.exe scripts/run_wan_test.py
```

The runner copies the original reference into ComfyUI's input folder, saves an API workflow, queues it locally, and records completion/failure and elapsed time. Use a new `--name` for revisions. Default: 640x352, 49 frames at 24fps (~2 seconds), 20 steps, CFG 5, uni_pc/simple, shift 8, seed 24092026. Text encoding runs on CPU to leave GPU memory for video inference; VAE decoding is tiled.

The canonical test prompt is in `scripts/run_wan_test.py`, copied into each saved API workflow. Model-generated motion must be inspected for camera drift, distorted furniture, ring deformation, and whether background movement is actually visible. Only progress to longer clips and finishing after this feasibility test. Do not disguise a weak test with an upscale.

## Completed local AI tests — 2026-09-24

ComfyUI 0.37.0 is installed and working locally. All three model files passed SHA256 verification against official repository metadata; hashes are in model-manifest.json. Example-media packages were omitted to avoid unnecessary downloads; workflow JSON and frontend are installed. No paid service was used.

Test01: 640x352, 49 frames, 24fps, 20 steps, 91.84 seconds actual server execution. Technically successful; sampled frames 0/16/32/48 show an invented oversized light cone and scene drift. Rejected internally.

Test02: 832x480, 81 frames, 24fps, 20 steps, 215.04 seconds actual server execution. Revised prompt saved in test02-prompt.txt and ringfall-wan-test02-api.json. Sampled frames 0/16/32/48/64/80 show stronger visible changes, but rings distort, the laptop display changes radically, and steam originates near the lamp rather than cleanly from the mug. Not production quality. Sampled-frame review only; no claim of continuous playback review. Clip duration verified as 3.375 seconds. Neither test is a seamless loop or 4K deliverable.

Conclusion: local inference is feasible on this RTX4060 with memory offloading. Quality/control is the unresolved problem. Proposed next experiment is a regional motion pass composited into the preserved source, with explicit masks protecting rings and furniture; this has not been tested. Do not upscale either test and call it finished.
