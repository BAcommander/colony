// Apply only the requested title and current candidate/delivery pointers.
// Historical artwork, thumbnail, animation and metadata snapshots are preserved.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=__dirname,project=path.resolve(root,'../..'),release=path.join(project,'final/11-empty-junction');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const f of ['youtube-title.txt','README.md','manifest.json']){
 if(sha(path.join(release,f))!==sha(path.join(root,'previous-release-'+f)))throw Error('Release file changed since snapshot: '+f);
}
const protectedFiles=['artwork-v2.png','thumbnail-v1.png','thumbnail-v1.jpg'];
const protectedHashes=Object.fromEntries(protectedFiles.map(f=>[f,sha(path.join(release,f))]));
const titlePath=path.join(release,'youtube-title.txt'),title=fs.readFileSync(path.join(root,'youtube-title.txt'));
const m=JSON.parse(fs.readFileSync(path.join(release,'manifest.json'),'utf8'));
const artManifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const titleText=title.toString('utf8').trim();if(titleText.length>100)throw Error('Title exceeds 100 characters');
m.status='Original approved artwork/thumbnail retained; revised composition and thumbnail candidates prepared 2026-10-31; one-hour audio delivered; original-plate animation remains work in progress.';
m.youtube_metadata.status='User-requested narrative title saved locally; publication not performed.';
m.youtube_metadata.title_sha256=crypto.createHash('sha256').update(title).digest('hex');
m.youtube_metadata.title_characters=titleText.length;
m.youtube_metadata.title_updated='2026-10-31';
m.youtube_metadata.previous_title_record='music/empty-junction-visual-revision-v1/previous-release-youtube-title.txt';
m.visual_revision={date:'2026-10-31',package:'music/empty-junction-visual-revision-v1/README.md',manifest:'music/empty-junction-visual-revision-v1/manifest.json',
 artwork_candidate:'music/empty-junction-visual-revision-v1/artwork-v3.png',artwork_candidate_sha256:sha(path.join(root,'artwork-v3.png')),
 thumbnail_candidates:artManifest.variants.map(v=>({id:v.id,path:'music/empty-junction-visual-revision-v1/'+v.file,sha256:sha(path.join(root,v.file))})),
 user_approved:false,status:'New returned artwork and thumbnails await visual selection; existing approved art/thumbnail are unchanged.',
 animation_note:'Current animation uses original artwork. New composition requires fresh mask mapping; not remapped or animated in this task.'};
const audioValidation=JSON.parse(fs.readFileSync(path.join(project,'music/empty-junction-music-v1/delivery-hour-v1/delivery-validation.json'),'utf8'));
if(audioValidation.status!=='passed')throw Error('Hour delivery not validated');
m.audio={status:'One-hour music and intermittent wind delivered locally; full listening approval not inferred.',duration_seconds:3600,
 recipe:'music/empty-junction-music-v1/delivery-hour-v1/mix-recipe.json',validation:'music/empty-junction-music-v1/delivery-hour-v1/delivery-validation.json',
 paths:'music/empty-junction-music-v1/delivery-hour-v1/delivery-paths.json',radio_included:false,user_full_length_approved:false};
if(m.music_preparation)m.music_preparation.status='Written prompt history retained; user-supplied long music variants and wind now have a separate one-hour delivery record. Actual supplied generation settings not verified.';
m.resolution_note='Original and new candidate artwork are native 1672x941. Existing 1280x720 v3 animation uses original artwork; new composition not animated. No 4K video delivery.';
let readme=fs.readFileSync(path.join(root,'previous-release-README.md'),'utf8').replaceAll('\r\n','\n');
const first='Prepared 2026-09-29.';
const firstIndex=readme.indexOf(first),paragraphEnd=readme.indexOf('\n\n',firstIndex);
if(firstIndex<0||paragraphEnd<0)throw Error('Unexpected README structure');
const intro='Current, 2026-10-31: [revised scene and thumbnail candidates](../../music/empty-junction-visual-revision-v1/README.md) and the requested narrative [video title](youtube-title.txt) are prepared. [One-hour music/wind ambience](../../music/empty-junction-music-v1/delivery-hour-v1/README.md) is delivered locally. The approved original art/thumbnail remain preserved; new visual selection is pending. Existing v3 animation still uses the original plate and remains a work in progress. The new composition has not been animated.';
readme=readme.slice(0,firstIndex)+intro+readme.slice(paragraphEnd);
readme=readme.replace('- Clean source:', '- Original approved clean source:');
readme=readme.replace('- [Music prompts and workflow](music/README.md): one-minute test and longer-piece briefs. No generation or credits spent here.',
 '- [Music prompt history](music/README.md) and [current one-hour delivery](../../music/empty-junction-music-v1/delivery-hour-v1/README.md). User-supplied sources, exact gains, wind schedule and validation are recorded in the delivery package.');
readme=readme.replace('Earlier versions preserved. No audio or assembly.','Earlier versions preserved. At that animation checkpoint no audio or assembly existed; the current separate one-hour soundtrack is linked above.');
fs.writeFileSync(titlePath,title);
fs.writeFileSync(path.join(release,'manifest.json'),JSON.stringify(m,null,2)+'\n');
fs.writeFileSync(path.join(release,'README.md'),readme);
for(const [f,digest]of Object.entries(protectedHashes))if(sha(path.join(release,f))!==digest)throw Error('Protected asset changed');
const receipt={date:'2026-10-31',status:'integrated locally',title:titleText,title_characters:titleText.length,
 modified_files:['youtube-title.txt','manifest.json','README.md'].map(f=>({path:'final/11-empty-junction/'+f,sha256:sha(path.join(release,f))})),
 original_art_and_thumbnail_unchanged:true,protected_hashes:protectedHashes,new_art_user_approved:false,
 existing_animation_unchanged:true,existing_hour_audio_unchanged:true,published:false,committed:false,pushed:false};
fs.writeFileSync(path.join(root,'release-integration.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify(receipt,null,2));
