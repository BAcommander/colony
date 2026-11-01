const fs=require('fs'),path=require('path');
const H=__dirname,R=path.resolve(H,'../..');
const intake=JSON.parse(fs.readFileSync(path.join(H,'sample-intake.json'),'utf8'));
const rel=p=>path.relative(R,p).replaceAll('\\','/');
const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const sources=intake.sources.map(s=>({title:s.title,path:rel(s.source_copy),original_path:s.original_path,sha256:s.source_sha256,duration_seconds:s.decoded_seconds,audition:rel(s.audition.path)}));
const history=path.join(H,'history');fs.mkdirSync(history,{recursive:true});
for(const name of ['generation-record.json','README.md']){
 const source=path.join(R,'final/12-deepwell-station/music',name),dest=path.join(history,'before-samples-'+name);
 if(!fs.existsSync(dest))fs.copyFileSync(source,dest);
}
const gpath=path.join(R,'final/12-deepwell-station/music/generation-record.json');
const g=JSON.parse(fs.readFileSync(gpath,'utf8'));
g.status='Two user-supplied four-minute music candidates received and technically checked; selection pending';
g.received_date='2026-11-01';g.short_test_files=sources;g.actual_supplied_durations_seconds=sources.map(s=>s.duration_seconds);
g.measurements='music/deepwell-production-2026-11-01/sample-intake.json';g.selected_test=null;g.audio_approval=false;
g.actual_model=null;g.actual_cost_shown=null;g.actual_prompt_confirmed=false;
g.v3_status='Two samples supplied after the prepared pilot brief; actual generation prompt/settings unverified';
g.assistant_listening=false;write(gpath,g);
const mpath=path.join(R,'final/12-deepwell-station/manifest.json'),m=JSON.parse(fs.readFileSync(mpath,'utf8'));
m.status='Deepwell active: V4 visuals remain review candidate; two four-minute soundtrack candidates received, level-matched comparison prepared, selection pending';
m.current_production.music_status=g.status;m.current_production.sample_intake=g.measurements;
m.music_preparation.status=g.status;m.music_preparation.supplied_candidates=sources;write(mpath,m);
const sessionPath=path.join(H,'session-start.json'),session=JSON.parse(fs.readFileSync(sessionPath,'utf8'));
session.generation_status=g.status;session.sample_intake='sample-intake.json';session.actual_supplied_durations_seconds=sources.map(s=>s.duration_seconds);write(sessionPath,session);
const monthPath=path.join(R,'creative/music/november-2026/month-plan.json');
const month=JSON.parse(fs.readFileSync(monthPath,'utf8'));
function visit(o){if(!o||typeof o!=='object')return;if(o.catalog_id==='12'){o.status=g.status;o.generated_files=sources;o.actual_pilot_durations_seconds=sources.map(s=>s.duration_seconds);o.generation_provenance_note='Supplied by user; exact prompt/model/cost unverified';}for(const v of Object.values(o))if(typeof v==='object')visit(v);}
visit(month);write(monthPath,month);
const trackerPath=path.join(R,'PRODUCTION_PIPELINE.md');let tracker=fs.readFileSync(trackerPath,'utf8');
tracker=tracker.replace(/^\| 12 \|.*$/m,'| 12 | [Deepwell Station](final/12-deepwell-station/README.md) | V4 rolling steam and purple pipeline lights; preview review pending | Two four-minute candidates received: Waterworks Gallery / Sheltered Replenishment; matched-volume auditions ready | Choose music; then test separate water-circulation ambience. Intake: music/deepwell-production-2026-11-01/sample-intake.json |');fs.writeFileSync(trackerPath,tracker);
const note='Deepwell music samples received (2026-11-01): user supplies Waterworks_Gallery_2026-11-01T171541.mp4 and Sheltered_Replenishment_2026-11-01T171541.mp4. Both decode to exactly 240 seconds, stereo 48kHz. Originals copied and SHA-256 verified in music/deepwell-production-2026-11-01/sources/. Source integrated loudness −14.65/−16.20 LUFS; fixed −8.35/−6.80 dB gains make approximately −23 LUFS full-length audition MP3s under review/. All samples decoded, finite/unclipped audition and full gain-reference comparison passed. No EQ, compression, extra fades, SFX, joins, stretching or new generation. Actual prompt/model/cost unverified. Music choice/approval pending; no assistant listening verdict. Earlier proposed 120-second test is superseded by actual supplied 240-second durations, not evidence of incorrect files. V4 visuals and original thumbnail unchanged.';
for(const relative of ['AGENTS.md','final/12-deepwell-station/README.md','final/12-deepwell-station/music/README.md']){
 const p=path.join(R,relative),text=fs.readFileSync(p,'utf8');if(text.includes('Deepwell music samples received (2026-11-01):'))continue;
 const i=text.indexOf('\n')+1;fs.writeFileSync(p,text.slice(0,i)+'\n'+note+'\n\n'+text.slice(i));
}
write(path.join(H,'sample-record-update.json'),{status:'received and ready for listening selection',sources,selected:null,audio_approval:false,commit_or_push:false});
console.log('Deepwell sample intake and production records updated');
