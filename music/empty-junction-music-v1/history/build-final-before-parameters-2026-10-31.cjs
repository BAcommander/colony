// Requested final combination: existing music/wind/train plus supplied grit.
// Also retains a separate SFX-only stem and three exact in-context excerpts.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const {createVerifier,fileHash}=require('../audio-verify.cjs');
const root=__dirname,parent=path.dirname(root),rate=48000,seconds=3600,totalFrames=rate*seconds;
const media=path.join(root,'media'),cache=path.join(parent,'.cache');for(const d of [media,cache])fs.mkdirSync(d,{recursive:true});
const raw=path.join(cache,'Empty-Junction-final-SFX-full-v1.f32'),stemRaw=path.join(cache,'Empty-Junction-final-SFX-stem-v1.f32');
const ff=args=>cp.execFileSync('ffmpeg',['-v','error','-nostdin',...args],{maxBuffer:30000000});
const smallHash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const decode=p=>{const b=ff(['-i',p,'-map','0:a:0','-ar',String(rate),'-ac','2','-f','f32le','pipe:1']);return new Float32Array(b.buffer,b.byteOffset,b.length/4);};
const oldHour=JSON.parse(fs.readFileSync(path.join(parent,'delivery-hour-v1/mix-recipe.json'),'utf8'));
const trainRecipe=JSON.parse(fs.readFileSync(path.join(parent,'delivery-hour-train-option-v1/mix-recipe.json'),'utf8'));
const priorValidation=JSON.parse(fs.readFileSync(path.join(parent,'delivery-hour-train-option-v1/delivery-validation.json'),'utf8'));
const baseRecord=priorValidation.outputs.find(o=>o.file.endsWith('.flac'));
const base=path.join(parent,'delivery-hour-train-option-v1',baseRecord.file);
const newName='Fine_dry_mineral_gri_#2-1793489678825.mp3',original=path.join('C:/Users/jazzs/Downloads',newName),source=path.join(parent,'sources',newName),gritHash=smallHash(original);
if(fs.existsSync(source)){if(smallHash(source)!==gritHash)throw Error('Existing source differs');}else fs.copyFileSync(original,source,fs.constants.COPYFILE_EXCL);
if(smallHash(source)!==gritHash)throw Error('Grit copy hash mismatch');
const grit=decode(source),gritFrames=grit.length/2;
if(gritFrames!==12*rate)throw Error('Unexpected grit duration');
const windPath=path.join(parent,'sources',oldHour.sources[2].file),trainPath=path.join(parent,'sources',path.basename(trainRecipe.train.file));
if(smallHash(windPath)!==oldHour.sources[2].sha256||smallHash(trainPath)!==trainRecipe.train.sha256)throw Error('Prior SFX hash mismatch');
const wind=decode(windPath),train=decode(trainPath);
const gritStarts=[198,226,374,747,916,938,1282,1453,1479,1831,1996,2021,2367,2534,2899,2924,3088,3437,3460];
const gritEvents=gritStarts.map(s=>({start_seconds:s,end_seconds:s+12,start_frame:s*rate}));
for(const e of gritEvents){if(e.start_seconds%180>=60||e.start_seconds%180+12>60)throw Error('Grit outside wind minute');
 for(const t of trainRecipe.train.events)if(e.start_seconds<t.end_seconds&&e.end_seconds>t.start_seconds)throw Error('Grit overlaps train');}
const gritGainDb=4.2,gritGain=Math.pow(10,gritGainDb/20),trainGain=Math.pow(10,trainRecipe.train.gain_db/20),windGain=Math.pow(10,oldHour.wind.gain_db/20);
const period=24*rate,windLoop=new Float32Array(period*2);
for(let f=0;f<period;f++)for(let ch=0;ch<2;ch++){
 let x;if(f<20*rate)x=wind[(5*rate+f)*2+ch];else{const t=f-20*rate,p=t/(4*rate)*Math.PI/2;x=wind[(25*rate+t)*2+ch]*Math.cos(p)+wind[(rate+t)*2+ch]*Math.sin(p);}
 windLoop[f*2+ch]=x*windGain;
}
const examples=[
 {id:'01-wind',label:'Wind with music, then wind fades out',start:15,duration:60,events_at_excerpt_seconds:{wind:[0,45]},file:'Empty-Junction-check-01-wind-60s-v1.mp3'},
 {id:'02-train',label:'Train with music, wind absent',start:105,duration:60,events_at_excerpt_seconds:{train:[[20,45]]},file:'Empty-Junction-check-02-train-60s-v1.mp3'},
 {id:'03-grit',label:'Wind and grit with music',start:185,duration:60,events_at_excerpt_seconds:{grit:[[13,25],[41,53]],wind:[0,55]},file:'Empty-Junction-check-03-grit-and-wind-60s-v1.mp3'},
];
async function render(){
 if(await fileHash(base)!==baseRecord.sha256)throw Error('Base file hash mismatch');
 if(fs.existsSync(raw)||fs.existsSync(stemRaw))throw Error('Refusing to overwrite PCM');
 const wetFd=fs.openSync(raw,'wx'),stemFd=fs.openSync(stemRaw,'wx');
 let frames=0,carry=Buffer.alloc(0),stderr='',problem,maxOutside=0,outsideSamples=0,peak=0,stemPeak=0,offSilentChecked=0,offSilentMax=0;
 const proc=cp.spawn('ffmpeg',['-v','error','-nostdin','-i',base,'-map','0:a:0','-ar',String(rate),'-ac','2','-f','f32le','pipe:1']);
 proc.stderr.on('data',b=>stderr+=b.toString());
 proc.stdout.on('data',chunk=>{
  if(problem)return;
  try{
   let b=carry.length?Buffer.concat([carry,chunk]):chunk;const n=b.length-b.length%8;carry=Buffer.from(b.subarray(n));b=b.subarray(0,n);
   const input=b.byteOffset%4===0?new Float32Array(b.buffer,b.byteOffset,n/4):null,wet=new Float32Array(n/4),stem=new Float32Array(n/4);
   for(let j=0;j<n/8;j++){
    const f=frames+j,windLocal=f%(180*rate);let windEnv=0;
    if(windLocal<60*rate)windEnv=Math.max(0,Math.min(1,windLocal/(5*rate),(60*rate-1-windLocal)/(8*rate)));
    let ge,te;for(const e of gritEvents)if(f>=e.start_frame&&f<e.start_frame+gritFrames){ge=e;break;}
    for(const e of trainRecipe.train.events)if(f>=e.start_frame&&f<e.start_frame+train.length/2){te=e;break;}
    const gl=ge?f-ge.start_frame:0,tl=te?f-te.start_frame:0;
    const gEnv=ge?Math.max(0,Math.min(1,gl/rate,(gritFrames-1-gl)/(2.5*rate)))*windEnv:0;
    const tEnv=te?Math.max(0,Math.min(1,tl/(3*rate),(train.length/2-1-tl)/(6*rate))):0;
    for(let ch=0;ch<2;ch++){
     const at=j*2+ch,before=input?input[at]:b.readFloatLE(at*4),g=ge?grit[gl*2+ch]*gritGain*gEnv:0;
     wet[at]=before+g;
     stem[at]=windLoop[(f%period)*2+ch]*windEnv+(te?train[tl*2+ch]*trainGain*tEnv:0)+g;
     if(!ge){outsideSamples++;maxOutside=Math.max(maxOutside,Math.abs(wet[at]-before));}
     if(windLocal>=60*rate&&!te){offSilentChecked++;offSilentMax=Math.max(offSilentMax,Math.abs(stem[at]));}
     if(!Number.isFinite(wet[at])||!Number.isFinite(stem[at])||Math.abs(wet[at])>=1||Math.abs(stem[at])>=1)throw Error('Non-finite/clipped render');
     peak=Math.max(peak,Math.abs(wet[at]));stemPeak=Math.max(stemPeak,Math.abs(stem[at]));
    }
   }
   fs.writeSync(wetFd,Buffer.from(wet.buffer));fs.writeSync(stemFd,Buffer.from(stem.buffer));frames+=n/8;
  }catch(e){problem=e;proc.kill();}
 });
 const code=await new Promise((resolve,reject)=>{proc.on('error',reject);proc.on('close',resolve);});fs.closeSync(wetFd);fs.closeSync(stemFd);
 if(problem)throw problem;if(code||carry.length||frames!==totalFrames||maxOutside!==0||offSilentMax!==0)throw Error('Full render validation failed '+stderr);
 return {frames,all_samples_finite:true,full_scale_samples:0,full_mix_peak_dbfs:20*Math.log10(peak),sfx_stem_peak_dbfs:20*Math.log10(stemPeak),
  outside_grit_samples_checked:outsideSamples,outside_grit_max_difference_from_previous_mix:0,
  sfx_silent_gap_samples_checked:offSilentChecked,sfx_silent_gap_max_absolute_sample:0};
}
(async()=>{
 console.log('Rendering final mix and separate SFX stem');const renderChecks=await render();
 const recipe={date:'2026-10-31',duration_seconds:seconds,sample_rate:rate,channels:2,
  base:{file:base,sha256:baseRecord.sha256,recipe:'../delivery-hour-train-option-v1/mix-recipe.json'},
  grit:{file:'../sources/'+newName,original_path:original,sha256:gritHash,source_frames:gritFrames,source_seconds:gritFrames/rate,
   source_measurements:{integrated_lufs:-41.2,lra_lu:4.2,true_peak_dbtp:-20.9,method:'FFmpeg ebur128 analysis'},
   gain_db:gritGainDb,nominal_isolated_lufs_before_fades:-37,fade_in_seconds:1,fade_out_seconds:2.5,also_follows_wind_envelope:true,events:gritEvents},
  wind:oldHour.wind,train:trainRecipe.train,
  music_and_existing_effects:'Previous lossless one-hour train-option mix retained; only grit is added. Original music gains/handovers and twenty-second closing fade remain.',
  sfx_stem:'Separate one-hour wind + train + grit stem, at the same gains/envelopes. No music. Do not add it to the already combined full mix.',
  added_eq_compression_limiting_pitch_shift_time_stretch:false,additional_opening_or_closing_fade:false,radio_or_compressor_included:false,
  examples,authorization:'User requests final SFX combination using the supplied sources, and example sections containing each effect to check.',
  approval:'Final requested combination delivered for user balance checks; artistic/full-session approval pending.',
  actual_generation_settings_and_prompt:'Supplied audio; exact generation controls, model and prompt not verified.',paid_generation_performed:false,assistant_listening_performed:false};
 fs.writeFileSync(path.join(root,'mix-recipe.json'),JSON.stringify(recipe,null,2)+'\n');
 const verifyWet=createVerifier({root,raw,rate,seconds}),verifyStem=createVerifier({root,raw:stemRaw,rate,seconds});
 const excerptResults=[];
 for(const ex of examples){
  const dest=path.join(parent,'review',ex.file);if(fs.existsSync(dest))throw Error('Refusing to overwrite '+dest);
  ff(['-n','-f','f32le','-ar',String(rate),'-ac','2','-ss',String(ex.start),'-i',raw,'-t',String(ex.duration),'-c:a','libmp3lame','-b:a','192k',dest]);
  excerptResults.push({...ex,validation:await verifyWet(dest,ex.start,ex.duration)});
 }
 fs.writeFileSync(path.join(root,'example-sections.json'),JSON.stringify(excerptResults,null,2)+'\n');console.log('All three 60-second check clips ready and verified');
 const outputs=[];
 for(const item of [{file:'The-Empty-Junction-1-Hour-final-SFX-v1.flac',input:raw,kind:'full mix'},
  {file:'The-Empty-Junction-1-Hour-final-SFX-v1.mp3',input:raw,kind:'full mix'},
  {file:'The-Empty-Junction-1-Hour-SFX-only-v1.flac',input:stemRaw,kind:'SFX-only stem'}]){
  const dest=path.join(media,item.file);if(fs.existsSync(dest))throw Error('Refusing to overwrite '+dest);const lossless=item.file.endsWith('.flac');
  console.log('Encoding '+item.file);
  ff(['-n','-f','f32le','-ar',String(rate),'-ac','2','-i',item.input,'-map_metadata','-1',
   ...(lossless?['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24']:['-c:a','libmp3lame','-b:a','192k']),dest]);
  console.log('Checking entire '+item.file);const result=await(item.input===raw?verifyWet:verifyStem)(dest);outputs.push({...result,kind:item.kind});console.log(JSON.stringify(result));
 }
 if(smallHash(source)!==gritHash||smallHash(original)!==gritHash||smallHash(windPath)!==oldHour.sources[2].sha256||smallHash(trainPath)!==trainRecipe.train.sha256||await fileHash(base)!==baseRecord.sha256)throw Error('Input changed');
 fs.writeFileSync(path.join(root,'delivery-validation.json'),JSON.stringify({status:'passed',duration_seconds:seconds,source_hashes_unchanged:true,
  render_checks:renderChecks,outputs,examples:excerptResults,assistant_listening_performed:false,user_balance_and_full_length_approval:false},null,2)+'\n');
 console.log('PASS: full-hour mix, separate SFX stem and three check clips.');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
