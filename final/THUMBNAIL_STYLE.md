# Ambient Colony - approved thumbnail style v1

Approved 2026-09-25. User feedback: "man they look awesome". The three finished PNGs in this directory are the visual authority. This guide records the reusable direction; it is not a promise of identical results from a fresh generation.

## Identity

Make the scene feel like an inviting place to spend time. Use the actual video artwork, a short destination title and one evocative caption. Keep the architecture, environment and strongest visual feature recognizable. Aim for a quiet cinematic science-fiction series with clear titles at small sizes.

- Main lettering: very bold condensed uppercase sans serif, warm ivory approximately `#F3EBDD`. Clean engineered letterforms; no distressed horror type. The lettering is generated, not a verified named font. Use the approved Ringfall thumbnail as the visual typography reference.
- Brand header: a fine ivory orbital circle with one small satellite dot, an amber vertical separator, then widely spaced `AMBIENT COLONY`.
- Accent: restrained amber approximately `#E7A83E`, repeated as a short horizontal rule before the caption.
- Main title: two lines, dominant at thumbnail scale. Fit long second lines without losing readability. No glow, thick cartoon outlines, giant boxes or excessive effects.
- Caption: one brief uppercase phrase, smaller and widely spaced. Secondary to the destination name.
- Catalog number: small ivory two-digit number in the top corner opposite the title. It is a series identifier, not a duration.
- Background: preserve scene identity; modest cinematic tonal separation and local shadow behind lettering. Warm shelter against cool or dark surroundings. Generated thumbnails are marketing adaptations, not exact video frames.
- Composition: target roughly 5% outer safe margins, protect the focal subject and leave the bottom-right duration area clear. Titles may switch sides to suit the scene.
- No invented duration, music claim, 4K badge, people, spacecraft, platform UI, neon or border.

## Approved set

| No. | Main title | Caption | Title placement |
| --- | --- | --- | --- |
| 01 | RINGFALL / OBSERVATORY | LUNAR NIGHT WATCH | Upper left; keep planet and rings visible |
| 02 | BASALT / TRANSMISSION | SIGNAL FROM THE EDGE | Upper right; keep station and antenna visible |
| 03 | GLACIER / SANCTUARY | SHELTER FROM THE STORM | Upper right; keep dome and warm annex visible |

## Repeat the workflow

1. Read this guide and inspect `01-ringfall-observatory/thumbnail-v1.png` as the established identity. Inspect the new video's actual source artwork too.
2. Use the built-in image-generation tool; no API key, paid plugin or external video service. Supply the new scene as image 1 (edit target), and the approved Ringfall thumbnail as image 2 (style only). One call per thumbnail.
3. Reuse the exact prompts saved beside each thumbnail. Specify every word verbatim, the scene's protected focal point, left/right title placement and the next catalog number. Do not import the reference scene's planet, furniture or landscape.
4. Inspect spelling, series consistency, legibility and the focal subject. Generated text and geometry can drift; judge the actual result. Save revisions as v2/v3 instead of overwriting approved assets.
5. Save the original generated PNG inside its final folder immediately. Export a JPEG at 1280x720 with FFmpeg, retaining the master PNG. This set uses Lanczos scaling and JPEG quality 2; each exported JPEG is below 2 MB. This export step changes file format/size, not the creative design.
6. Record exact prompt, source artwork, reference image, user feedback, dimensions and file hashes in `manifest.json`. Commit/push thumbnails and notes alongside the approved video, and verify remote media availability.

Prompt scaffold:

> Create one finished 16:9 Ambient Colony thumbnail. Image 1 is the actual scene and edit target; image 2 is the approved channel identity reference only. Preserve [scene and protected focal subject]. Match image 2's bold condensed ivory typography, orbital circle with satellite dot, amber separators and spaced brand header. Exact title: "[LINE 1]" / "[LINE 2]". Caption: "[SHORT CAPTION]". Brand: "AMBIENT COLONY". Catalog number: "[NN]". Place title [chosen side] in available negative space, readable when small, without obscuring [hero subject]. Preserve photographic materials and cinematic lighting. Keep bottom right clear. No additional text, fake duration, badges, people, spacecraft, border or platform UI. Output the finished thumbnail, not a mockup.

## Storage

Each scene package contains `video-4k.mp4`, `thumbnail-v1.png`, `thumbnail-v1.jpg`, `thumbnail-prompt-v1.md`, `manifest.json` and a short README. Final video copies must match their original approved master hashes. Historical render paths stay valid; these folders are a convenient release collection. Video masters are silent loops; music and long-form publishing assembly are separate work.
