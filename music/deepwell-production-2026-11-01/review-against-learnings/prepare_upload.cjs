const fs=require('fs'),path=require('path'),crypto=require('crypto');
const h=__dirname,r=path.resolve(h,'../../..'),release=path.join(r,'final/12-deepwell-station');
const pack=path.join(release,'upload-2026-11-01'),history=path.join(pack,'previous-copy');
if(fs.existsSync(pack))throw Error('Preserve existing upload package');
fs.mkdirSync(history,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const n of ['youtube-title.txt','description.txt','youtube-tags.txt','manifest.json'])fs.copyFileSync(path.join(release,n),path.join(history,n));
const title='Deepwell Station — Water for a New World | 1 Hour Sci-Fi Ambient';
const description=`Every warm window on the ridge depends on this water.

Settle into the pump gallery at Deepwell Station, where pale mineral terraces step down into blue-grey channels and a pipeline follows the cliffs toward the colony. Beyond the window, an unfamiliar planet hangs over the waterworks.

One hour of sci-fi ambient music with gentle water, passing wind and distant circulation-pump sounds. Featuring Waterworks Gallery and Sheltered Replenishment, arranged into a continuous soundtrack for the animated scene. Presented in 4K.

Music, artwork and sound effects were created using AI tools. Animation, sound selection and the final mix were assembled for Ambient Colony.

Welcome to Ambient Colony. Stay a while and listen.

#SciFiAmbience #AlienPlanet #AmbientColony
`;
if(title.length>100)throw Error('Title too long');
fs.writeFileSync(path.join(release,'youtube-title.txt'),title+'\n');fs.writeFileSync(path.join(release,'description.txt'),description);
for(const n of ['youtube-title.txt','description.txt','youtube-tags.txt'])fs.copyFileSync(path.join(release,n),path.join(pack,n));
const thumb=path.join(release,'thumbnail-v1.jpg'),thumbHash=sha(thumb);fs.copyFileSync(thumb,path.join(pack,'thumbnail-current.jpg'));if(sha(path.join(pack,'thumbnail-current.jpg'))!==thumbHash)throw Error('Thumbnail copy mismatch');
const notes=`DEEPWELL STATION — UPLOAD PACKAGE (2026-11-01)

Video: G:/AI/colony/exports/12-deepwell-station/Deepwell-Station-1-Hour-4K-v1.mp4
Title: ${title}
Thumbnail: thumbnail-current.jpg (byte-identical copy of approved thumbnail-v1.jpg; 1280x720)
Description: description.txt
Tags: youtube-tags.txt
Suggested category: Music
AI use: Yes. AI-generated music is a disclosure example in current YouTube guidance. The description line supplements the Studio setting.
Source: https://support.google.com/youtube/answer/14328491

PACKAGING REVIEW
The existing thumbnail is readable and matches the established channel identity, but predates the latest review. Its large two-line title, brand, subtitle and catalogue number occupy much of the upper-left scene. It also omits the planet now visible in the final animation. These are visual/creative concerns, not demonstrated CTR defects.
Keep the current approved thumbnail available; no replacement was generated or silently selected. A scene-first candidate with only DEEPWELL, and a scene-only candidate, are sensible tests. Use consistent artwork/crop/brightness if the purpose is to isolate typography; changing the planet/art and text together tests the complete package, not text alone. No concurrent result or Studio CTR/retention data currently establishes the winner.
Native YouTube A/B testing can compare up to3 variants, where eligible; it evaluates watch time. Hold title steady for a thumbnail-only comparison.
Source: https://support.google.com/youtube/answer/16391400

The title and description have now been refreshed from the old preparation drafts to state the scene story, one-hour runtime, actual sound layers,4K output and AI creation. Previous bytes are under previous-copy/. Native art is1672x941, rendered then Lanczos upscaled to4K; no native4K artwork claim.

AUDIO REVIEW
G:/AI/colony/music/deepwell-production-2026-11-01/review-against-learnings/REPORT.md
No audio/video re-export or processing change was made. Both source analyses and equal160-second interior-window checks are saved. Full-session preference remains a listening question, not a number to optimize.

No account action, upload, paid generation, commit or push.
`;
fs.writeFileSync(path.join(pack,'upload-notes.txt'),notes);
const mp=path.join(release,'manifest.json');let m=JSON.parse(fs.readFileSync(mp,'utf8'));
m.youtube_metadata.status='Updated local upload copy for completed one-hour video; not published';
m.youtube_metadata.title_sha256=sha(path.join(release,'youtube-title.txt'));m.youtube_metadata.description_sha256=sha(path.join(release,'description.txt'));
m.youtube_metadata.description_words_before_hashtags=description.split('#SciFiAmbience')[0].trim().split(/\s+/).length;
m.youtube_metadata.guidance_checked='2026-11-01';m.youtube_metadata.sources=[...new Set([...m.youtube_metadata.sources,'https://support.google.com/youtube/answer/14328491','https://support.google.com/youtube/answer/16391400'])];
m.youtube_metadata.upload_package='final/12-deepwell-station/upload-2026-11-01';m.youtube_metadata.thumbnail_review='Current approved v1 retained. Large text/brand/subtitle/number and absence of final-scene planet noted; no measured CTR verdict or new thumbnail chosen.';
m.current_production.audio_learnings_review='music/deepwell-production-2026-11-01/review-against-learnings/REPORT.md';
fs.writeFileSync(mp,JSON.stringify(m,null,2)+'\n');
const record={date:'2026-11-01',title,title_characters:title.length,thumbnail_sha256:thumbHash,thumbnail_changed:false,canonical_upload_files_updated:true,old_files_preserved:'previous-copy/',files:Object.fromEntries(['youtube-title.txt','description.txt','youtube-tags.txt','thumbnail-current.jpg','upload-notes.txt'].map(n=>[n,sha(path.join(pack,n))])),soundtrack_unchanged:true,uploaded:false};
fs.writeFileSync(path.join(pack,'package.json'),JSON.stringify(record,null,2)+'\n');
const ap=path.join(r,'AGENTS.md');let a=fs.readFileSync(ap,'utf8'),end=a.indexOf('\n');
const note='Deepwell upload copy and audio review (2026-11-01): user asks for thumbnail/title/description and comparison of both tracks against this week’s learnings. final/12-deepwell-station/upload-2026-11-01/ holds refreshed narrative title, finished-runtime/sound-layer/AI description, unchanged tags and byte-exact approved thumbnail; prior copy preserved. Thumbnail remains text-heavy and lacks final-scene planet; no replacement or CTR winner inferred. Current YouTube AI-use and A/B guidance checked. Both original four-minute dry sources plus20–180s interior windows analysed using the same measurement functions as October30; job-local adapter only changes FFmpeg binary discovery. Waterworks sub80 0.0049%,250Hz–1kHz73.3%, correlation0.744, interior LRA4.4LU. Sheltered sub80 0.0063%,low-mid43.0%,correlation0.525; full LRA9.8 drops to3.2 in interior window, showing fade confound. Full mix remains−22.71LUFS/4.3LU/−9.41dBTP. No consistent strong internal-loop confirmation; actual dry A/B recipe repeats every388s after entrance, while SFX timing varies separately. No automatic EQ/widening or claim of improved pace/retention: prior preference ratings override spectral resemblance. User accepted balance; full-hour work-session verdict unrecorded. See music/deepwell-production-2026-11-01/review-against-learnings/REPORT.md and comparison.json. Audio/video unchanged; no paid generation, upload, commit or push.';
fs.writeFileSync(ap,a.slice(0,end+1)+'\r\n'+note+'\r\n\r\n'+a.slice(end+1));
console.log(JSON.stringify({package:pack,title,characters:title.length,thumbnail_sha256:thumbHash,description_words:m.youtube_metadata.description_words_before_hashtags}));
