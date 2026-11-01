// Optional train layer on the existing verified one-hour ambience.
// Local Node + FFmpeg; no generation, paid services or edits to the baseline.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=__dirname,parent=path.dirname(root),rate=48000,seconds=3600,totalFrames=rate*seconds;
const media=path.join(root,'media'),cache=path.join(parent,'.cache'),raw=path.join(cache,'Empty-Junction-1-Hour-train-option-v1.f32');
for(const d of [media,cache])fs.mkdirSync(d,{recursive:true});
const fileHash=p=>new Promise((resolve,reject)=>{const h=crypto.createHash('sha256'),s=fs.createReadStream(p);s.on('data',b=>h.update(b));s.on('error',reject);s.on('end',()=>resolve(h.digest('hex')));});
const smallHash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const ff=args=>cp.execFileSync('ffmpeg',['-v','error','-nostdin',...args],{maxBuffer:30000000});
const sourceName='Distant_freight_trai_#4-1793489393057.mp3';
const original=path.join('C:/Users/jazzs/Downloads',sourceName),source=path.join(parent,'sources',sourceName),sourceHash=smallHash(original);
if(fs.existsSync(source)){if(smallHash(source)!==sourceHash)throw Error('Existing source differs');}
else fs.copyFileSync(original,source,fs.constants.COPYFILE_EXCL);
if(smallHash(source)!==sourceHash)throw Error('Source copy mismatch');
const sourceBytes=ff(['-i',source,'-map','0:a:0','-ar',String(rate),'-ac','2','-f','f32le','pipe:1']);
const train=new Float32Array(sourceBytes.buffer,sourceBytes.byteOffset,sourceBytes.length/4),trainFrames=train.length/2;
if(trainFrames<24*rate||trainFrames>26*rate)throw Error('Unexpected source duration');
const starts=[125,622,1164,1697,2251,2782,3320],gainDb=4.5,gain=Math.pow(10,gainDb/20);
const events=starts.map(start=>({start_seconds:start,end_seconds:start+trainFrames/rate,start_frame:start*rate}));
for(const e of events)if(e.start_seconds%180<60||e.start_seconds%180+trainFrames/rate>180)throw Error('Train overlaps wind window');
const baseValidation=JSON.parse(fs.readFileSync(path.join(parent,'delivery-hour-v1/delivery-validation.json'),'utf8'));
const baseRecord=baseValidation.outputs.find(o=>o.file.endsWith('.flac'));
const base=path.join(parent,'delivery-hour-v1',baseRecord.file);
async function render(){
 if(await fileHash(base)!==baseRecord.sha256)throw Error('Base hash mismatch');
 if(fs.existsSync(raw))throw Error('Refusing to overwrite PCM');
 const fd=fs.openSync(raw,'wx');let frames=0,peak=0,maxOutsideDifference=0,outsideSamples=0,carry=Buffer.alloc(0),problem,stderr='';
 const proc=cp.spawn('ffmpeg',['-v','error','-nostdin','-i',base,'-map','0:a:0','-ar',String(rate),'-ac','2','-f','f32le','pipe:1']);
 proc.stderr.on('data',b=>stderr+=b.toString());
 proc.stdout.on('data',chunk=>{
  if(problem)return;
  try{
   let input=carry.length?Buffer.concat([carry,chunk]):chunk;const len=input.length-input.length%8;
   carry=Buffer.from(input.subarray(len));input=input.subarray(0,len);
   const out=new Float32Array(len/4),view=input.byteOffset%4===0?new Float32Array(input.buffer,input.byteOffset,len/4):null;
   for(let j=0;j<len/8;j++){
    const frame=frames+j;let event;
    for(const e of events)if(frame>=e.start_frame&&frame<e.start_frame+trainFrames){event=e;break;}
    let env=0,local=0;
    if(event){local=frame-event.start_frame;env=Math.max(0,Math.min(1,local/(3*rate),(trainFrames-1-local)/(6*rate)));}
    for(let ch=0;ch<2;ch++){
     const at=j*2+ch,before=view?view[at]:input.readFloatLE(at*4);
     const added=event?train[local*2+ch]*gain*env:0;out[at]=before+added;
     if(!event){outsideSamples++;maxOutsideDifference=Math.max(maxOutsideDifference,Math.abs(out[at]-before));}
     if(!Number.isFinite(out[at])||Math.abs(out[at])>=1)throw Error('Rendered non-finite/clipped sample');
     peak=Math.max(peak,Math.abs(out[at]));
    }
   }
   fs.writeSync(fd,Buffer.from(out.buffer));frames+=len/8;
  }catch(e){problem=e;proc.kill();}
 });
 const code=await new Promise((resolve,reject)=>{proc.on('error',reject);proc.on('close',resolve);});fs.closeSync(fd);
 if(problem)throw problem;if(code||carry.length||frames!==totalFrames)throw Error('Base decode failed '+stderr);
 if(maxOutsideDifference!==0)throw Error('Baseline changed outside train events');
 return {frames,peak_dbfs:20*Math.log10(peak),all_samples_finite:true,full_scale_samples:0,
  outside_train_event_samples_checked:outsideSamples,outside_train_event_max_difference_from_base:0};
}
async function validate(p,start=0,duration=seconds){
 const refFd=fs.openSync(raw,'r');let count=0,peak=0,maxError=0,error=0,signal=0,carry=Buffer.alloc(0),problem,stderr='';
 const proc=cp.spawn('ffmpeg',['-hide_banner','-nostdin','-nostats','-i',p,'-map','0:a:0','-af','ebur128=peak=true:framelog=verbose','-ar',String(rate),'-ac','2','-f','f32le','pipe:1']);
 proc.stderr.on('data',b=>stderr+=b.toString());
 proc.stdout.on('data',chunk=>{
  if(problem)return;
  try{
   let b=carry.length?Buffer.concat([carry,chunk]):chunk;const n=b.length-b.length%4;carry=Buffer.from(b.subarray(n));b=b.subarray(0,n);
   if(count+n/4>duration*rate*2)throw Error('Too many decoded samples');
   const ref=Buffer.allocUnsafe(n);let read=0;
   while(read<n){const done=fs.readSync(refFd,ref,read,n-read,start*rate*8+count*4+read);if(!done)throw Error('Reference EOF');read+=done;}
   const a=b.byteOffset%4===0?new Float32Array(b.buffer,b.byteOffset,n/4):null,r=new Float32Array(ref.buffer,ref.byteOffset,n/4);
   for(let i=0;i<n/4;i++){
    const x=a?a[i]:b.readFloatLE(i*4);if(!Number.isFinite(x)||Math.abs(x)>=1)throw Error('Decoded non-finite/clipped sample');
    peak=Math.max(peak,Math.abs(x));const e=x-r[i];maxError=Math.max(maxError,Math.abs(e));error+=e*e;signal+=r[i]*r[i];
   }
   count+=n/4;
  }catch(e){problem=e;proc.kill();}
 });
 const code=await new Promise((resolve,reject)=>{proc.on('error',reject);proc.on('close',resolve);});fs.closeSync(refFd);
 if(problem)throw problem;if(code||carry.length||count!==duration*rate*2)throw Error('Incorrect decoded duration');
 const summary=stderr.slice(stderr.lastIndexOf('Summary:'));
 const I=summary.match(/Integrated loudness:\s*I:\s*([-\d.]+) LUFS/),LRA=summary.match(/Loudness range:\s*LRA:\s*([-\d.]+) LU/),TP=summary.match(/True peak:\s*Peak:\s*([-\d.]+) dBFS/);
 if(!I||!LRA||!TP||Number(TP[1])>=-1)throw Error('Loudness/headroom validation failed');
 const snr=10*Math.log10(signal/error);
 if(p.endsWith('.flac')&&maxError>2.4e-7)throw Error('FLAC recipe mismatch');
 if(p.endsWith('.mp3')&&snr<20)throw Error('Unexpected MP3 deviation');
 fs.writeFileSync(path.join(root,path.basename(p)+'.decode-loudness.log'),stderr);
 return {file:path.relative(root,p).replaceAll('\\','/'),sha256:await fileHash(p),bytes:fs.statSync(p).size,
  decoded_frames:count/2,duration_seconds:count/2/rate,all_samples_finite:true,full_scale_samples:0,sample_peak_dbfs:20*Math.log10(peak),
  integrated_lufs:Number(I[1]),lra_lu:Number(LRA[1]),true_peak_dbtp:Number(TP[1]),
  full_sample_recipe_comparison:{performed:true,max_absolute_error:maxError,snr_db:snr}};
}
(async()=>{
 console.log('Rendering optional train layer');const renderChecks=await render();
 const recipe={date:'2026-10-31',option:'Occasional distant train over existing one-hour music/wind',duration_seconds:seconds,sample_rate:rate,channels:2,
  base:{file:base,sha256:baseRecord.sha256,recipe:'../delivery-hour-v1/mix-recipe.json'},
  train:{file:'../sources/'+sourceName,original_path:original,sha256:sourceHash,source_frames:trainFrames,source_seconds:trainFrames/rate,
   source_measurements:{integrated_lufs:-39.5,lra_lu:9.7,true_peak_dbtp:-20.3,method:'FFmpeg ebur128 analysis, not assistant listening'},
   gain_db:gainDb,nominal_isolated_lufs:-35,fade_in_seconds:3,fade_out_seconds:6,events},
  wind:'Existing one-minute-on/two-minute-off schedule unchanged; every train event lies wholly within a wind-off window.',
  added_eq_compression_limiting_pitch_shift_time_stretch:false,additional_opening_or_closing_fade:false,
  status:'Optional mix for listening comparison; original mix remains available. No artistic approval inferred.',
  actual_generation_settings_and_prompt:'Not verified; user supplied the file. Earlier proposed duration was 12 seconds; supplied file actually contains approximately 25 seconds.',
  paid_generation_performed:false,assistant_listening_performed:false};
 fs.writeFileSync(path.join(root,'mix-recipe.json'),JSON.stringify(recipe,null,2)+'\n');
 const preview=path.join(parent,'review/Empty-Junction-train-option-audition-90s-v1.mp3');
 if(fs.existsSync(preview))throw Error('Refusing to overwrite audition');
 ff(['-n','-f','f32le','-ar',String(rate),'-ac','2','-ss','95','-i',raw,'-t','90','-c:a','libmp3lame','-b:a','192k',preview]);
 const audition=await validate(preview,95,90);console.log('90-second audition ready.');
 const outputs=[];
 for(const ext of ['flac','mp3']){
  const dest=path.join(media,'The-Empty-Junction-1-Hour-train-option-v1.'+ext);if(fs.existsSync(dest))throw Error('Refusing to overwrite '+dest);
  console.log('Encoding '+ext.toUpperCase());
  ff(['-n','-f','f32le','-ar',String(rate),'-ac','2','-i',raw,'-map_metadata','-1',
   ...(ext==='flac'?['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24']:['-c:a','libmp3lame','-b:a','192k']),dest]);
  console.log('Checking entire '+ext.toUpperCase());const output=await validate(dest);outputs.push(output);console.log(JSON.stringify(output));
 }
 if(smallHash(original)!==sourceHash||smallHash(source)!==sourceHash||await fileHash(base)!==baseRecord.sha256)throw Error('Source changed');
 fs.writeFileSync(path.join(root,'delivery-validation.json'),JSON.stringify({status:'passed',duration_seconds:seconds,
  source_hashes_unchanged:true,render_checks:renderChecks,audition:{...audition,full_mix_range_seconds:[95,185],train_at_excerpt_seconds:[30,30+trainFrames/rate]},outputs,
  assistant_listening_performed:false,user_listening_approval:false},null,2)+'\n');
 console.log('PASS: exact one-hour train option; baseline preserved outside event windows.');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
