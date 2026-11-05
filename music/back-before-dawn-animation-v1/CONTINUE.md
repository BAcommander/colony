# Continue Back Before Dawn

The clean source is the original H1 artwork, native1672×941. Camera, hero body/wheels/door and fixed workshop hardware stay fixed. A generated sedan supplies the distant pass. The generated tree backfill remains as rejected history: its cutout revealed sky at an internal canopy boundary. Final foliage uses bounded original-source deformation with fixed boundaries. Exact executed built-in prompts, raw PNGs, working sprites, measured headlamp positions and asset hashes remain under `assets/`.

## Restore on another PC

From the repository root on `main`, with Git LFS installed:

```powershell
git pull --ff-only
git lfs pull --include="music/back-before-dawn-animation-v1/*.mp4" --exclude=""
```

Open [the review page](review.html) for the two-minute preview, four detail crops and the loop join. See the [backup inventory](backup-manifest.json) for the exact files and hashes. To continue rendering on a clean Windows machine, install Python 3.13 and run this once from the repository root:

```powershell
py -3.13 -m venv .local/back-before-dawn
.local/back-before-dawn/Scripts/python.exe -m pip install -r music/back-before-dawn-animation-v1/requirements.txt
```

## Check and resume rendering

Run `verify_resume.py` before extending this checkpoint. It compares the renderer, source, configuration and asset hashes in `continuation-checkpoint.json` and checks 15 frozen native RGB states across both clock modes. An existing `.local/audio-analysis` environment can also be used if it has the same pinned dependencies.

```powershell
.local/back-before-dawn/Scripts/python.exe music/back-before-dawn-animation-v1/verify_resume.py
.local/back-before-dawn/Scripts/python.exe music/back-before-dawn-animation-v1/render.py --seconds 12 --start 53 --output workshop-new-street-review.mp4
.local/back-before-dawn/Scripts/python.exe music/back-before-dawn-animation-v1/render.py --attention-mode production600 --seconds 600 --output workshop-production600-first-audition.mp4
```

The renderer refuses to overwrite an existing output. Its default is the120second review schedule. `--only rain,road` or another comma-separated subset of `Scene.effect_groups` gives an unamplified isolated visual proof with the same timeline. Use different output names for changed settings; do not rewrite the current review or original source.

The physical environment has a60second period; rare actions use an independent120second review or600second production clock. Production600 is implemented and native-audited, including actual cue peaks, but its full playback and user acceptance remain pending. Keep the absolute time when rendering later chunks. Do not replace the60second physical period with600 or restart rare events on every minute.

Review-scale motion and lighting must remain identical at later4K delivery. The code currently exports720p only; a production encoder must take the same native frames and upscale once to3840×2160 with disclosed upscaling and explicit BT.709 conversion. Bind the new master to the accepted review's source/settings/code/asset hashes, then check full decode, timestamps, protected pixels, direct native-to-YUV controls and actual regional/chunk joins. Do not treat this note as a delivered4K master.

Select/audition the score and SFX separately. Use the exact gust and passing-car cues in `documentation/cue-sheet.json`; a parked time machine is not an excuse for continuous warning beeps or invented machinery exhaust. No SFX gains or soundtrack were accepted in this visual build. Keep the clean animation free of opening graphics; the current Colony opening belongs once in final assembly.

Store long delivery files and reproducible repeats and caches under ignored local locations per `EXPORTS.md`. This backup keeps the sources, verification evidence, settings, feedback and short review videos needed to continue. Visual approval remains pending.
