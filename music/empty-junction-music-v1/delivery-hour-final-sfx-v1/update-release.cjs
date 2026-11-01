// Point release documentation to the now-validated requested SFX combination.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const version=process.argv.find(a=>a.startsWith('--version='))?.slice(10)||'v1';
if(!/^v[1-9][0-9]*$/.test(version))throw Error('Invalid delivery version');
const root=path.join(path.dirname(__dirname),'delivery-hour-final-sfx-'+version),project=path.resolve(root,'../../..'),release=path.join(project,'final/11-empty-junction');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const v=JSON.parse(fs.readFileSync(path.join(root,'delivery-validation.json'),'utf8'));
const delivery=JSON.parse(fs.readFileSync(path.join(root,'delivery-paths.json'),'utf8'));
const recipe=JSON.parse(fs.readFileSync(path.join(root,'mix-recipe.json'),'utf8'));
if(v.status!=='passed'||delivery.status!=='delivered'||delivery.outputs.length!==3)throw Error('Verified three-file delivery required');
const manifestPath=path.join(release,'manifest.json'),readmePath=path.join(release,'README.md');
const snapshots=['manifest.json','README.md'];
for(const f of snapshots)fs.copyFileSync(path.join(release,f),path.join(root,'previous-release-'+f),fs.constants.COPYFILE_EXCL);
const protectedFiles=['artwork-v2.png','thumbnail-v1.png','thumbnail-v1.jpg','youtube-title.txt'];
const before=Object.fromEntries(protectedFiles.map(f=>[f,sha(path.join(release,f))]));
const m=JSON.parse(fs.readFileSync(manifestPath,'utf8')),previous=m.audio;
m.audio={version:'one-hour-final-sfx-'+version,status:'User-requested full music + wind + distant train + mineral grit combination delivered; three in-context checks and separate SFX-only stem ready. Grit source gain '+recipe.grit.gain_db+' dB; other levels and timings retained. User balance/full-session approval pending.',
 grit_source_gain_db:recipe.grit.gain_db,grit_change_from_v1_db:recipe.grit.change_from_v1_db||0,
 duration_seconds:3600,recipe:'music/empty-junction-music-v1/delivery-hour-final-sfx-v1/mix-recipe.json',
 validation:'music/empty-junction-music-v1/delivery-hour-final-sfx-v1/delivery-validation.json',
 paths:'music/empty-junction-music-v1/delivery-hour-final-sfx-v1/delivery-paths.json',
 examples:'music/empty-junction-music-v1/delivery-hour-final-sfx-v1/example-sections.json',
 outputs:delivery.outputs,radio_included:false,compressor_included:false,user_balance_and_full_length_approved:false,
 previous_delivery:previous,earlier_option:'music/empty-junction-music-v1/delivery-hour-train-option-v1/README.md'};
for(const key of ['recipe','validation','paths','examples'])m.audio[key]=m.audio[key].replace('final-sfx-v1/','final-sfx-'+version+'/');
let readme=fs.readFileSync(readmePath,'utf8');
readme=readme.replace('[One-hour music/wind ambience](../../music/empty-junction-music-v1/delivery-hour-v1/README.md)',
 '[One-hour music with wind, train and grit](../../music/empty-junction-music-v1/delivery-hour-final-sfx-v1/README.md)');
readme=readme.replace('[current one-hour delivery](../../music/empty-junction-music-v1/delivery-hour-v1/README.md)',
 '[current one-hour mix and example checks](../../music/empty-junction-music-v1/delivery-hour-final-sfx-v1/README.md)');
if(version!=='v1')readme=readme.replaceAll('delivery-hour-final-sfx-v1/README.md','delivery-hour-final-sfx-'+version+'/README.md');
fs.writeFileSync(manifestPath,JSON.stringify(m,null,2)+'\n');fs.writeFileSync(readmePath,readme);
for(const[f,h]of Object.entries(before))if(sha(path.join(release,f))!==h)throw Error('Protected release asset changed');
fs.writeFileSync(path.join(root,'release-integration.json'),JSON.stringify({date:'2026-10-31',status:'current audio pointers updated locally',
 modified_files:['final/11-empty-junction/manifest.json','final/11-empty-junction/README.md'],original_art_thumbnail_and_title_unchanged:true,
 animation_unchanged:true,user_full_length_approval:false,published:false,committed:false,pushed:false},null,2)+'\n');
console.log('Release audio records now point to final SFX combination and check clips.');
