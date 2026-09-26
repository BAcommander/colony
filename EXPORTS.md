# Local exports and media storage

Long finished video/audio and local source-audio copies live under `exports/`, which is ignored by Git. This folder remains on this computer but will not appear after cloning. No export was deleted or transcoded during the move; hashes were verified before and after.

- `exports/01-ringfall-observatory/`: Ringfall video and one-hour soundtrack, plus original generated audio/video under `source/`.
- `exports/02-basalt-transmission/`: Basalt video and two-hour soundtrack, plus original generated audio/video under `source/`.
- `exports/previews/`: local review clips.

Tracked inventory: `final/local-export-inventory.json` records paths, sizes and SHA-256. Keep a separate external-drive/cloud backup of these files, especially generated soundtrack originals, which cannot be recreated identically by rerunning a prompt. No separate backup has been performed in this task. Git push does not upload ignored files.

Keep code, prompts, settings, thumbnails, descriptions, feedback, validation and inventories in Git. Existing approved short visual masters retain their exact Git/LFS rules and paths under `creative/` and `final/`. The small restored green-screen subscribe MP4 is explicitly tracked as a draft asset; that is backup status, not creative approval. Large repeated deliveries do not need LFS.

For future final deliveries use `exports/<scene>/`. Keep tracked manifests beside scene documentation under `final/<scene>/`. A moved export must be selected again if an editor still references its old path. The existing `final` folders now contain production packages and short masters, not the long upload files.
