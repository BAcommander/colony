# Crater Rim Survey — complete minute, V2

Built 2026-11-05 in response to the user's barely-visible-motion verdict on V1 and request to create the full animation. This is the complete silent visual loop for playback review, at 1280×720, 30 fps. User acceptance and a 4K production master remain separate steps.

[Play the complete minute](Crater-Rim-Survey-v2-60s-loop.mp4) · [Three uninterrupted repetitions](Crater-Rim-Survey-v2-3-loops-180s.mp4)

The principal actions are forward cloud transport, three depths of broader basin haze and slow cloud shadows on the exterior terrain. The existing survey display has a rotating radar sweep, decaying returns, a telemetry read head and a moving map target. Three traced windows on the distant upper building have independent warm holds. The camera, ring, terrain geometry, window frames and survey equipment remain fixed. The room stays sheltered and does not receive the exterior shadow sweep.

The [scene plan](scene-plan.json) contains every route, speed, lifetime, mask and screen quadrilateral in the original 1672×941 artwork's coordinates. Haze reuses frozen copies of Saltline's local periodic gust transport; the final three source-space speeds are 5.6, 10.5 and 17 px/s. Plumes have different phases and hidden births/deaths. Source clouds use three staggered sky-only renewals, with bounded source sampling, rather than reversing the scene. This is a source-based 2D treatment; cloud renewal softness and haze character need a real playback verdict.

The scene's brighter daytime setting needs broad environmental changes that survive the full composition. V1 had measurable travel but failed the user's viewing test. V2 adds footprint, depth and local shading instead of treating a larger speed number as proof of quality. The display supports that environmental motion; it does not replace the terrain image with a new graphic.

[Cloud isolation](Crater-Rim-Survey-v2-clouds-8s.mp4) · [Haze isolation](Crater-Rim-Survey-v2-haze-8s.mp4) · [Shadow isolation](Crater-Rim-Survey-v2-shadows-8s.mp4) · [Survey display isolation](Crater-Rim-Survey-v2-survey-8s.mp4). Each isolation uses scene time 5–13 seconds, at actual speed and full composition.

The [validation record](delivery.json) binds the source, settings, renderer, transport dependencies and delivered videos by SHA-256. Checks cover safe interpolated sky samples, non-folding cloud maps, native protected pixels, every delivered frame and timestamp, direct native-to-encoded YUV controls, regional last-to-first steps against ordinary neighbors and exact decoded repetitions. Inspect [the mask overlay](inspection/mask-overlay.png) and the decoded temporal stills alongside playback. Stills and technical checks do not establish natural motion or user approval.

An internal first pass placed two small light masks on masonry; they were remapped to actual upper-building windows. The first full encode also exposed a snapping telemetry reset at the loop boundary. The corrected read head fades at both ends before restarting. Earlier internal settings/renderer/video remain in `history/`; the public links above point to the corrected candidate.

Reproduce from the repo root using the existing `.local/audio-analysis/Scripts/python.exe` environment, or Python with NumPy, Pillow, OpenCV and imageio-ffmpeg:

```powershell
python music/crater-rim-animation-v2/render_scene.py samples
python music/crater-rim-animation-v2/render_scene.py isolated
python music/crater-rim-animation-v2/render_scene.py full
python music/crater-rim-animation-v2/validate_delivery.py
python music/crater-rim-animation-v2/verify_isolations.py
```

Existing MP4 destinations are protected from overwriting; use an empty output checkout or retain prior candidates in a separate version folder. The three-loop review is stream-copied from the minute, not three minutes of unique animation. Diagnostic and repeated media stay local under the repository's storage policy. No music, new SFX, opening, paid service, upload, commit or push was part of this render. Native source detail remains 1672×941; later 3840×2160 delivery will be an upscale with these same accepted settings.
