# Gate Camp portal motion test

[Eight-second preview](Gate-Camp-portal-v1-8s.mp4) from the original E1 artwork. Three crossing ripple fields and a slow drift move the source texture inside a traced aperture. The map tapers near the metal rim and the stairs. This applies the same source-and-destination protection used in the Crater Rim sky test to a two-dimensional warp.

All 240 decoded frames are distinct and sequential. The source taps remained inside the aperture, the warp stayed positive, and the pixels outside the active mask matched the source before resizing and encoding. The first internal warp was too strong near the edges and failed the deformation check. A wider taper and lower displacement passed. Sampled decoded frames show visible texture change, and playback review is pending. [Delivery checks](delivery.json)

Use `python music/gate-camp-animation-v1/render_portal.py` with NumPy, OpenCV, Pillow and imageio-ffmpeg in the existing audio-analysis environment. Keep the output path free before rerendering. [Editable settings](scene-plan.json) · [Release brief](../../final/17-gate-camp/README.md)
