# Research: independent motion overlays

User feedback: the planet pass looks no better than the original subtle steam. User requests online research into overlays/ComfyUI. Research only this turn; no additional model or custom node installation and no new render.

## Findings from primary sources

1. ComfyUI core ImageCompositeMasked overlays a source onto a destination with position and mask. The installed implementation accepts image batches; RepeatImageBatch can repeat the original still for the sequence. These nodes already exist locally. Compositing is therefore available without installing another video-generation model. [Official node documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageCompositeMasked/en.md).
2. ComfyUI Simple Video Effects documents a Video Overlay node with per-pixel alpha, batch alignment and placement/scale controls. This is an optional open-source third-party package, not installed or tested here. It does not solve generation quality itself. [Maintainer repository](https://github.com/scofano/ComfyUI-Simple-video-effects).
3. FFmpeg supports screen/addition blend modes and an overlay filter. Bright elements on black can be screen-composited; this is not equivalent to physically correct alpha for opaque objects or dark smoke. Use true alpha/foreground masks for opaque subjects. [Official filter documentation](https://ffmpeg.org/ffmpeg-filters.html#blend_002c-tblend).
4. VACE takes source video, masks and optional reference images during generation. This differs from our Wan2.2 image-to-video runs, where masks were applied only afterward. ComfyUI supplies a VACE inpainting workflow. It is an alternative for changes that must interact with scene content, not an automatic guarantee of clean edges or exact preservation. Restore the untouched source outside the final mask. [ComfyUI tutorial](https://docs.comfy.org/tutorials/video/wan/vace), [official VACE project](https://github.com/TMCADV/VACE).
5. VACE has 1.3B and 14B variants; official examples list roughly 81x480x832 and 81x720x1280 respectively. We have not benchmarked either on this 8GB GPU. Do not transfer Wan2.2 5B's observed memory/runtime to VACE or promise the 14B version fits. The existing Wan2.2 TI2V checkpoint is not a VACE checkpoint.
6. ComfyUI-layerdiffuse documents SDXL/SD1.5 support for transparent-image workflows. It is not a drop-in native-alpha Wan2.2 video solution. [Maintainer README](https://github.com/huchenlei/ComfyUI-layerdiffuse).

## Proposed workflow

Original still -> repeated background frames.
Independent motion element -> actual alpha/matte or suitable black-background screen blend -> transform and grade -> foreground occlusion mask -> composite over original -> final encode.

Save element RGBA sequences or separate RGB/mask sequences for reuse; do not expect ordinary H.264 MP4 to carry the transparency. Match light direction, perspective, color and sharpness. Window frames and furniture can be restored as foreground occluders. Lighting/reflections/shadows, when needed, are explicit additional layers rather than a license to regenerate the whole image. Process final 4K composites in bounded batches/streaming instead of loading 300 float frames onto the 8GB GPU.

For luminous wisps/steam/glows, generate or render the element alone on black and test a screen blend, with black-level cleanup and edge inspection. For a rigid moving subject, prefer an authored 2D/3D asset and a keyframed path; another AI video can still deform the subject. Exact ten-second loops require deliberate trajectories and temporal review, not merely a loop prompt. Exit/reentry must be offscreen or occluded with a matching state; never teleport a visible asset.

## Recommendation and creative distinction

The earlier work already used overlays/masked compositing. Moving the same subtle effects into ComfyUI would not improve them. The next meaningful change is the motion asset and choreography: one clearly readable main action, with steam/screens as supporting elements. Do not resume planetary stripe experiments by default.

For Ringfall, a proposed example is a maintenance craft moving outside the window along a controlled path, correctly occluded by the window frame, with restrained navigation lights and optional matched reflections. This is a new creative element, not user-approved content. A lunar craft should be thruster-driven, not a propeller drone, and should not produce atmospheric beams or windblown dust. A rover is another option but must be large/near enough to read; a tiny distant light will repeat the old failure.

Recommendation: prototype one independently animated main element over the original before adding further effects. Native ComfyUI compositing is sufficient; VACE remains a secondary research option for scene-integrated edits. No quality outcome is established until a real preview passes review.
