// Integrate the verified animation review candidate; preserve historical assets.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=__dirname,project=path.resolve(root,'../..'),release=path.join(project,'final/11-empty-junction');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const delivery=JSON.parse(fs.readFileSync(path.join(root,'delivery-v4.json'),'utf8'));
if(delivery.status!=='technically verified review candidate'||!delivery.source_unchanged||delivery.clips.length!==5)throw Error('Complete verified preview delivery required');
const prefix='music/empty-junction-animation-v4/';
const protectedPaths=[path.join(release,'artwork-v2.png'),path.join(release,'thumbnail-v1.png'),path.join(release,'thumbnail-v1.jpg'),
 path.join(project,'music/empty-junction-animation-v3/empty-junction-v3-preview-60s.mp4')];
const protectedHashes=Object.fromEntries(protectedPaths.map(p=>[p,sha(p)]));
const files=['final/11-empty-junction/manifest.json','final/11-empty-junction/README.md','AGENTS.md','PRODUCTION_PIPELINE.md','creative/ANIMATION_KNOWLEDGE_BANK.md'];
for(const rel of files){const dest=path.join(root,'history/records-before-v4',rel);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(project,rel),dest,fs.constants.COPYFILE_EXCL);}
const m=JSON.parse(fs.readFileSync(path.join(release,'manifest.json'),'utf8'));
const wind=delivery.clips.find(c=>c.file.includes('-wind-minute-'));
const cycle=delivery.clips.find(c=>c.file.includes('-scheduled-cycle-'));
const repeats=delivery.clips.find(c=>c.file.includes('-three-cycles-'));
const combined=delivery.clips.find(c=>c.file.includes('-with-approved-audio-'));
m.animation={version:'v4',status:'Revised-composition 720p motion and combined preview technically verified; user playback verdict pending.',
 source:'music/empty-junction-animation-v4/artwork-v3.png',source_sha256:delivery.fingerprint.source.sha256,
 record:prefix+'delivery-v4.json',preview:prefix+wind.file,preview_sha256:wind.sha256,
 duration_seconds:60,fps:30,dimensions:[1280,720],silent:true,delivery_cycle_seconds:180,
 scheduled_cycle:prefix+cycle.file,scheduled_cycle_sha256:cycle.sha256,repeat_review:prefix+repeats.file,
 combined_preview:prefix+combined.file,combined_preview_sha256:combined.sha256,combined_preview_seconds:240,
 source_protection_and_seam_checks_passed:true,user_approved:false,master_4k:null,previous_animation:m.animation};
if(m.audio){m.audio.user_current_mix_approved=true;m.audio.user_balance_approved=true;m.audio.full_hour_continuous_listening_reported=false;
 m.audio.approval_record='music/empty-junction-music-v1/delivery-hour-final-sfx-v3/user-approval-2026-10-31.json';
 m.audio.status='V3 music/wind/train/grit mix chosen by user after quieter-grit checks; locked for the new motion preview. Continuous full-hour listening not reported.';}
if(m.visual_revision){m.visual_revision.artwork_selected_for_animation_work=true;m.visual_revision.animation_candidate=prefix+'README.md';}
m.status='Original approved assets preserved. Revised-composition animation v4 and four-minute combined review delivered; V3 audio balance chosen; visual playback review pending.';
m.resolution_note='Source artwork 1672x941; v4 review 1280x720/30 fps. No native-4K claim or final hour-long video; 4K follows motion review.';
fs.writeFileSync(path.join(release,'manifest.json'),JSON.stringify(m,null,2)+'\n');
let readme=fs.readFileSync(path.join(release,'README.md'),'utf8');
const old='Existing v3 animation still uses the original plate and remains a work in progress. The new composition has not been animated.';
readme=readme.replace(old,'[Animation v4](../../music/empty-junction-animation-v4/README.md) now uses the revised clean plate, with wind/quiet units, a scheduled three-minute cycle and a four-minute approved-audio preview. V3 audio balance is chosen; new motion playback review is pending.');
readme=readme.replace('Current animation (2026-10-07):','Historical original-plate animation (2026-10-07):');
fs.writeFileSync(path.join(release,'README.md'),readme);
const agentsPath=path.join(project,'AGENTS.md');let agents=fs.readFileSync(agentsPath,'utf8');const newline=agents.indexOf('\n')+1;
const current='Current Empty Junction animation: user accepts V3 music/wind/train/grit balance (grit source gain -3.3 dB) and says "lets go" for the revised scene. music/empty-junction-animation-v4/ uses the new 1672x941 complete-cabin artwork v3, SHA-256 44bd1465510494ed91bc54c9461cb77da590179cb708c6dd21fcd6a6b51f8ba8. Every mask, route, aperture and occluder is freshly mapped. Genuine sixty-second wind/quiet units share cloud/mist, grille plume and independent lighting; only near powder differs. Wind/quiet/quiet gives the requested one-minute-on/two-minute-off visual cycle. Three scheduled cycles and a four-minute combined preview are verified. Initial pale sky-boundary artifact corrected by source-relative cloud differences; initial diagnostics retained. Full decode/timestamps, regional and quiet-neighbour seams, exact repeated/copied pictures, direct native-to-YUV controls and complete approved-source/AAC comparison passed. Assistant inspected temporal/decoded stills, not continuous playback. Audio balance chosen; new animation user verdict pending. No final 4K/hour video, paid generation, upload, commit, push or remote backup. Existing art/thumbnail/v1-v3/audio preserved. See v4 README and delivery-v4.json.';
agents=agents.slice(0,newline)+'\n'+current+'\n'+agents.slice(newline);fs.writeFileSync(agentsPath,agents);
const pipelinePath=path.join(project,'PRODUCTION_PIPELINE.md');let pipeline=fs.readFileSync(pipelinePath,'utf8');
pipeline=pipeline.replace(/^\| 11 \|[^\n]*/m,(line)=>'| 11 | [The Empty Junction](final/11-empty-junction/README.md) | Revised-art v4: wind/quiet sixty-second units, scheduled 180s cycle and four-minute combined 720p review technically verified | One-hour V3 music + wind/train/grit chosen; grit gain -3.3 dB | Review [v4 combined preview](music/empty-junction-animation-v4/README.md); then matching 4K and Colony final assembly |'+(line.match(/\r*$/)?.[0]||''));
pipeline=pipeline.replace(/^\| 11 Empty Junction \|[^\n]*/m,(line)=>'| 11 Empty Junction | V4 remaps all motion to the whole-cabin revised composition; powder follows the one-minute-on/two-minute-off wind schedule | Anchored grille plume, evolving sky/pass mist and independent room/practical lights; full technical checks passed, user motion review pending. |'+(line.match(/\r*$/)?.[0]||''));
fs.writeFileSync(pipelinePath,pipeline);
const bankPath=path.join(project,'creative/ANIMATION_KNOWLEDGE_BANK.md');let bank=fs.readFileSync(bankPath,'utf8');
const heading='### 11 The Empty Junction';const at=bank.indexOf(heading);if(at<0)throw Error('Junction knowledge section missing');const end=bank.indexOf('\n',at)+1;
const learning='\nCurrent revised-composition v4: [review delivery](../music/empty-junction-animation-v4/README.md). Remap every aperture/anchor/occluder to the new plate. The first normalized sky replacement produced pale bands at the conservative skyline boundary; applying source-relative transported cloud differences with a wider inward feather removed that artifact in inspected stills. Keep source and destination protection. Render wind and quiet minutes from the same native state in one pass, changing only powder; sequence wind/quiet/quiet to match the accepted SFX schedule while plume, clouds, mist and habitation continue. Do not infer natural motion from numeric checks: V4 is technically verified but user playback remains pending. Audio V3 balance is chosen.\n';
bank=bank.slice(0,end)+learning+bank.slice(end);bank=bank.replace('Empty Junction 11 has a technically checked v3 checkpoint that the user says still needs work.','Empty Junction 11 now has a revised-composition v4 motion/combined preview with full technical checks; user motion review remains pending and the V3 audio balance is chosen.');
fs.writeFileSync(bankPath,bank);
for(const[p,h]of Object.entries(protectedHashes))if(sha(p)!==h)throw Error('Protected asset changed');
fs.writeFileSync(path.join(root,'record-integration.json'),JSON.stringify({status:'current records updated locally',modified_files:files,
 protected_assets_unchanged:true,protected_hashes:protectedHashes,user_motion_approved:false,user_audio_current_mix_approved:true,
 final_4k_or_hour_video_created:false,published:false,committed:false,pushed:false},null,2)+'\n');
console.log('Current scene, tracker, knowledge and approval scope updated; original assets unchanged.');
