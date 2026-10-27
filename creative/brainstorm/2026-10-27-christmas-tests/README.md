# Christmas somewhere you wish you could stay — ten clean tests

2026-10-27. User explicitly requests making all ten written seasonal ideas as a test. [Open the comparison gallery](gallery.html). Exact clean generated PNGs preserved with prompts and manifests; 1280×720 preview JPEGs are display copies, not designed thumbnails.

| Review ID | Scene | Influence |
| --- | --- | --- |
| X01 | [Christmas in the Time Machine Workshop](x01-time-machine/concept-v1.png) | Back to the Future |
| X02 | [Three Million Christmases from Home](x02-dwarf-christmas/concept-v1.png) | Red Dwarf |
| X03 | [Christmas on the Night Watch](x03-tos-lounge/concept-v1.png) | Star Trek TOS |
| X04 | [The Snowbound Gate Lodge](x04-gate-lodge/concept-v1.png) | Stargate SG-1 |
| X05 | [The Salvage Quarter Christmas Window](x05-salvage-window/concept-v1.png) | Andor |
| X06 | [The Freighter's Little Christmas](x06-freighter-christmas/concept-v1.png) | Alien 1979 |
| X07 | [Christmas with the Fleet](x07-fleet-christmas/concept-v1.png) | Battlestar Galactica 2004 |
| X08 | [The Belt's Christmas Canteen](x08-belt-canteen/concept-v1.png) | The Expanse |
| X09 | [Winter at the Rainward Keep](x09-rainward-winter/concept-v1.png) | Dune coastal strand |
| X10 | [Christmas Beneath the Rings](x10-ringfall-christmas/concept-v1.png) | Ambient Colony original / Ringfall identity |

## Scope and actual inspection

All ten generated using built-in imagegen, text-only inputs, one image per concept. generation-index.json records exact prompt, original returned path and intended brief. Each folder has generation-v1.txt, concept-v1.png, preview-v1.jpg and manifest-v1.json with byte sizes, native dimensions, SHA-256, actual concerns and acceptance state. Build script verifies original PNG bytes against returned source files, verifies decode and records prompt hashes. It exports display JPEGs via FFmpeg without changing the master PNGs.

Assistant inspected ten returned full-composition stills; not a crop-by-crop geometry audit. User approval pending for all. Original source influence is design context, not official affiliation or canon-accuracy certification. X01–X10 are review IDs, not release numbers. Existing Ringfall masters/art and all earlier concepts remain unchanged. No lettering, generated thumbnail design, masks, animation, audio or release packaging made.

## Learnings from actual outputs

- Small personal uses (meal, chair, blanket) carry refuge better than decoration alone, in assistant judgment. User verdict still needed.
- X01 DeLorean and X04 gate create recognizable sci-fi silhouettes immediately; X10 rings establish our own identity. X05 retains a community beyond the room.
- TOS X03 is more formal/clean than the worn other rooms, preserving a different era rather than adding generic grime.
- X06 tiny shelf tree and X07 wire tree preserve improvised crew Christmas; X08 citrus tree successfully varies the festive anchor.
- Generation still adds rugs, plants, parcels, dishes and warmer light beyond the restrained briefs. Record the deviation instead of assuming two/three-detail prompts enforced visual simplicity.
- X09 coastal keep feels convincing as shelter but can read as a terrestrial winter stronghold. X10 ring/planet relationship remains stylised; fire construction cannot be verified as electric simply from visible log-like flames.
- All car hardware, ring/portal geometry, doors/seals, hearth/flues, furniture and exterior supports need close inspection after scene selection. No motion mapping before the clean still is selected/frozen.

Initial editorial shortlist: X01 time machine, X04 gate lodge, X05 salvage flat, X10 rings. This is not user approval or CTR evidence.

User explicitly requests committing and pushing all ten tests and supporting records on the existing brainstorm branch. See [backup verification](backup-verification.json) for content commit, scope and remote evidence. The earlier receipt covers the preceding collection only. Backup authorization is separate from artistic approval.
