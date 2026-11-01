// Requested one-hour audio: alternating own music and intermittent wind.
// Run: node build-hour.cjs. Optional --resume reuses existing deterministic PCM
// and exports only after matching the saved recipe fingerprint and file size.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=__dirname, parent=path.dirname(root),rate=48000,seconds=3600,totalFrames=rate*seconds;
const media=path.join(root,'media'),cache=path.join(parent,'.cache'),raw=path.join(cache,'Empty-Junction-1-Hour-v1.f32');
const resume=process.argv.includes('--resume');
for(const p of [media,cache])fs.mkdirSync(p,{recursive:true});
const prior=JSON.parse(fs.readFileSync(path.join(parent,'mix-recipe.json'),'utf8'));
const windPrior=JSON.parse(fs.readFileSync(path.join(parent,'mix-recipe-v2.json'),'utf8'));
const sourcePaths=prior.sources.map(s=>path.join(parent,'sources',s.file));
const smallHash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const fileHash=p=>new Promise((resolve,reject)=>{const h=crypto.createHash('sha256'),s=fs.createReadStream(p);s.on('data',b=>h.update(b));s.on('error',reject);s.on('end',()=>resolve(h.digest('hex')));});
const ff=args=>cp.execFileSync('ffmpeg',['-v','error','-nostdin',...args],{maxBuffer:200000000});
const decode=p=>{const b=ff(['-i',p,'-map','0:a:0','-ac','2','-ar',String(rate),'-f','f32le','pipe:1']);return new Float32Array(b.buffer,b.byteOffset,b.length/4);};
function checkSources(){sourcePaths.forEach((p,i)=>{if(smallHash(p)!==prior.sources[i].sha256)throw Error('Source hash mismatch '+p);});}
checkSources();
// First A retains its generated entrance. Every subsequent source starts at
// 0:02, and both generated closing fades are excluded before overlap.
const schedule=[];let start=0,index=0;
while(start<seconds){
  const which=index%2,sourceIn=index===0?0:2,sourceOut=which===0?224:230;
  const length=sourceOut-sourceIn;
  schedule.push({source_index:which,source:prior.sources[which].file,source_in_seconds:sourceIn,source_out_seconds:sourceOut,
    output_start_seconds:start,output_end_seconds:Math.min(seconds,start+length),natural_segment_end_seconds:start+length,
    fade_in_seconds:index===0?0:12,fade_out_seconds:start+length<seconds?12:0});
  start+=length-12;index++;
}
const windOn=[],windOff=[];
for(let t=0;t<seconds;t+=180){windOn.push([t,t+60]);windOff.push([t+60,Math.min(seconds,t+180)]);}
const recipe={date:'2026-10-31',duration_seconds:seconds,sample_rate:rate,channels:2,
  sources:prior.sources,music_gain_db:prior.music_gain_db,schedule,
  music_crossfade:{duration_seconds:12,curve:'equal-power cosine/sine',first_A_to_B:'Retains existing preview timing at 212–224 seconds',
    B_to_A:'New return join: B source 218–230 seconds overlaps A source 2–14 seconds. Both generated closing fades excluded for repeated playback.'},
  wind:{source_index:2,gain_db:prior.wind_gain_db,source_trim_seconds:[1,29],loop_period_seconds:24,
    tail_head_overlap_seconds:4,tail_head_curve:'equal-power cosine/sine',active_windows_seconds:windOn,off_windows_seconds:windOff,
    fade_in_seconds:5,fade_out_seconds:8,fades_inside_each_active_minute:true,
    note:'Wind timing runs on the global clock independently of music handovers; short wind source still repeats.'},
  opening:'Only the first music source generated entrance; no added production intro fade.',closing_fade_seconds:20,
  added_eq_compression_limiting_pitch_shift_time_stretch:false,radio_included:false,paid_generation_performed:false,
  authorization:'User requested one-hour ambience after provisional positive Junction feedback and one-minute-on/two-minute-off wind instruction. Radio experimentation stopped.',
  assistant_review:'Technical validation, no assistant listening verdict or full-length artistic approval.'};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(recipe)).digest('hex');
const recipePath=path.join(root,'mix-recipe.json');
if(fs.existsSync(recipePath)){
  const saved=JSON.parse(fs.readFileSync(recipePath,'utf8'));
  if(!resume||saved.recipe_fingerprint_sha256!==fingerprint)throw Error('Existing recipe; use a fresh version or explicit --resume with identical inputs.');
}else fs.writeFileSync(recipePath,JSON.stringify({...recipe,recipe_fingerprint_sha256:fingerprint},null,2)+'\n',{flag:'wx'});
if(fs.existsSync(raw)){
  if(!resume||fs.statSync(raw).size!==totalFrames*8)throw Error('Existing/incomplete PCM; refusing overwrite.');
  console.log('Resuming from existing full-length PCM.');
}else{
  const music=sourcePaths.slice(0,2).map(decode),w=decode(sourcePaths[2]);
  if(music.some(x=>x.length!==240*rate*2)||w.length<29*rate*2)throw Error('Unexpected source duration');
  const amps=prior.music_gain_db.map(db=>Math.pow(10,db/20)),windAmp=Math.pow(10,prior.wind_gain_db/20);
  const period=24*rate,loop=new Float32Array(period*2);
  for(let f=0;f<period;f++)for(let ch=0;ch<2;ch++){
    let x;if(f<20*rate)x=w[(5*rate+f)*2+ch];
    else{const t=f-20*rate,p=t/(4*rate)*Math.PI/2;x=w[(25*rate+t)*2+ch]*Math.cos(p)+w[(rate+t)*2+ch]*Math.sin(p);}
    loop[f*2+ch]=x*windAmp;
  }
  const fd=fs.openSync(raw,'wx'),chunkFrames=10*rate;
  let rawPeak=0,offSamplesChecked=0,maxOffDifference=0;
  try{
    for(let first=0;first<totalFrames;first+=chunkFrames){
      const count=Math.min(chunkFrames,totalFrames-first),block=new Float32Array(count*2);
      // Accumulate only the source occurrences that intersect this block.
      for(const seg of schedule){
        const segFirst=seg.output_start_seconds*rate,segEnd=seg.output_end_seconds*rate;
        const begin=Math.max(first,segFirst),end=Math.min(first+count,segEnd);
        for(let f=begin;f<end;f++){
          const local=f-segFirst,naturalLength=(seg.source_out_seconds-seg.source_in_seconds)*rate;
          let gain=amps[seg.source_index];
          if(seg.fade_in_seconds&&local<12*rate)gain*=Math.sin(local/(12*rate)*Math.PI/2);
          if(seg.fade_out_seconds&&local>=naturalLength-12*rate)gain*=Math.cos((local-naturalLength+12*rate)/(12*rate)*Math.PI/2);
          const out=(f-first)*2,src=(seg.source_in_seconds*rate+local)*2;
          block[out]+=music[seg.source_index][src]*gain;block[out+1]+=music[seg.source_index][src+1]*gain;
        }
      }
      for(let j=0;j<count;j++){
        const f=first+j,local=f%(180*rate),closing=Math.min(1,(totalFrames-1-f)/(20*rate));
        let windEnv=0;
        if(local<60*rate)windEnv=Math.max(0,Math.min(1,local/(5*rate),(60*rate-1-local)/(8*rate)));
        for(let ch=0;ch<2;ch++){
          const at=j*2+ch,before=block[at],addition=loop[(f%period)*2+ch]*windEnv;
          block[at]=(before+addition)*closing;
          if(local>=60*rate){offSamplesChecked++;maxOffDifference=Math.max(maxOffDifference,Math.abs(block[at]-Math.fround(before*closing)));}
          if(!Number.isFinite(block[at])||Math.abs(block[at])>=1)throw Error('Non-finite/clipped rendered sample');
          rawPeak=Math.max(rawPeak,Math.abs(block[at]));
        }
      }
      fs.writeSync(fd,Buffer.from(block.buffer));
      if((first+count)%(300*rate)===0)console.log('Rendered '+(first+count)/rate+' / 3600 seconds');
    }
  }finally{fs.closeSync(fd);}
  if(maxOffDifference!==0)throw Error('Wind present in off windows');
  fs.writeFileSync(path.join(root,'render-checks.json'),JSON.stringify({expected_frames:totalFrames,raw_sample_peak_dbfs:20*Math.log10(rawPeak),
    wind_off_samples_checked:offSamplesChecked,wind_off_max_difference_from_dry:0,raw_bytes:fs.statSync(raw).size},null,2)+'\n');
}
async function validate(p,expectedStart=0,expectedDuration=seconds){
  const expected=fs.openSync(raw,'r'),offset=expectedStart*rate*8,wanted=expectedDuration*rate*2;
  let sampleCount=0,peak=0,maxError=0,error=0,signal=0,carry=Buffer.alloc(0),stderr='',problem;
  const proc=cp.spawn('ffmpeg',['-hide_banner','-nostdin','-nostats','-i',p,'-map','0:a:0','-af','ebur128=peak=true:framelog=verbose',
    '-ar',String(rate),'-ac','2','-f','f32le','pipe:1'],{stdio:['ignore','pipe','pipe']});
  proc.stderr.on('data',b=>{stderr+=b.toString();});
  proc.stdout.on('data',chunk=>{
    if(problem)return;
    try{
      let buf=carry.length?Buffer.concat([carry,chunk]):chunk;
      const length=buf.length-buf.length%4;carry=Buffer.from(buf.subarray(length));buf=buf.subarray(0,length);
      if(sampleCount+length/4>wanted)throw Error('Too many decoded samples');
      const ref=Buffer.allocUnsafe(length);let done=0;
      while(done<length){const n=fs.readSync(expected,ref,done,length-done,offset+sampleCount*4+done);if(!n)throw Error('Unexpected reference EOF');done+=n;}
      const floats=buf.byteOffset%4===0?new Float32Array(buf.buffer,buf.byteOffset,length/4):null;
      const refs=new Float32Array(ref.buffer,ref.byteOffset,length/4);
      for(let i=0;i<length/4;i++){
        const x=floats?floats[i]:buf.readFloatLE(i*4),r=refs[i];
        if(!Number.isFinite(x)||Math.abs(x)>=1)throw Error('Non-finite/clipped decoded sample');
        peak=Math.max(peak,Math.abs(x));const e=x-r;maxError=Math.max(maxError,Math.abs(e));error+=e*e;signal+=r*r;
      }
      sampleCount+=length/4;
    }catch(e){problem=e;proc.kill();}
  });
  const code=await new Promise((resolve,reject)=>{proc.on('error',reject);proc.on('close',resolve);});
  fs.closeSync(expected);
  fs.writeFileSync(path.join(root,path.basename(p)+'.decode-loudness.log'),stderr);
  if(problem)throw problem;if(code!==0)throw Error('FFmpeg decode failed '+stderr.slice(-2000));
  if(carry.length||sampleCount!==wanted)throw Error('Incorrect decoded sample count');
  const summary=stderr.slice(stderr.lastIndexOf('Summary:'));
  const I=summary.match(/Integrated loudness:\s*I:\s*([-\d.]+) LUFS/),LRA=summary.match(/Loudness range:\s*LRA:\s*([-\d.]+) LU/),TP=summary.match(/True peak:\s*Peak:\s*([-\d.]+) dBFS/);
  if(!I||!LRA||!TP)throw Error('Loudness summary missing');
  if(Number(TP[1])>=-1)throw Error('Insufficient true-peak headroom');
  const snr=10*Math.log10(signal/error);
  if(p.endsWith('.flac')&&maxError>2.4e-7)throw Error('Lossless recipe comparison failed');
  if(p.endsWith('.mp3')&&snr<20)throw Error('MP3 recipe deviation unexpectedly high');
  return {file:path.relative(root,p).replaceAll('\\','/'),bytes:fs.statSync(p).size,sha256:await fileHash(p),decoded_frames:sampleCount/2,
    duration_seconds:sampleCount/2/rate,all_samples_finite:true,full_scale_samples:0,sample_peak_dbfs:20*Math.log10(peak),
    integrated_lufs:Number(I[1]),lra_lu:Number(LRA[1]),true_peak_dbtp:Number(TP[1]),
    full_sample_recipe_comparison:{performed:true,max_absolute_error:maxError,snr_db:snr}};
}
(async()=>{
  const outputs=[];
  for(const ext of ['flac','mp3']){
    const p=path.join(media,'The-Empty-Junction-1-Hour-v1.'+ext);
    if(fs.existsSync(p)){if(!resume)throw Error('Refusing to overwrite '+p);}
    else{
      console.log('Encoding '+ext.toUpperCase());
      ff(['-n','-f','f32le','-ar',String(rate),'-ac','2','-i',raw,'-map_metadata','-1',
        ...(ext==='flac'?['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24']:['-c:a','libmp3lame','-b:a','192k']),p]);
    }
    console.log('Validating entire '+ext.toUpperCase()+' and measuring loudness');
    const output=await validate(p);outputs.push(output);console.log(JSON.stringify(output));
  }
  const joinPath=path.join(parent,'review','Empty-Junction-B-to-A-return-join-60s-v1.mp3');
  if(!fs.existsSync(joinPath))ff(['-n','-f','f32le','-ar',String(rate),'-ac','2','-ss','408','-i',raw,'-t','60','-c:a','libmp3lame','-b:a','192k',joinPath]);
  const join=await validate(joinPath,408,60);
  checkSources();
  const validation={status:'passed',duration_seconds:seconds,expected_frames_per_channel:totalFrames,source_hashes_unchanged:true,
    recipe_fingerprint_sha256:fingerprint,render_checks:JSON.parse(fs.readFileSync(path.join(root,'render-checks.json'),'utf8')),
    outputs,return_join_excerpt:{...join,full_mix_range_seconds:[408,468],crossfade_at_excerpt_seconds:[20,32]},
    assistant_listening_performed:false,user_full_length_listening_approval:false};
  fs.writeFileSync(path.join(root,'delivery-validation.json'),JSON.stringify(validation,null,2)+'\n');
  console.log('PASS: exact one-hour MP3 and 24-bit FLAC; all samples decoded and compared.');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
