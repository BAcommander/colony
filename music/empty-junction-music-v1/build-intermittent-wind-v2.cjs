// Preserve the reviewed dry arrangement; revise only the wind's schedule.
// Node built-ins + FFmpeg. Existing outputs refuse overwrite.
const fs=require('node:fs');
const path=require('node:path');
const cp=require('node:child_process');
const crypto=require('node:crypto');
const root=__dirname, rate=48000, duration=450, frames=rate*duration;
const review=path.join(root,'review'), cache=path.join(root,'.cache');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const run=args=>cp.execFileSync('ffmpeg',['-v','error','-nostdin',...args],{maxBuffer:300000000});
const decode=p=>{const b=run(['-i',p,'-map','0:a:0','-ar',String(rate),'-ac','2','-f','f32le','pipe:1']);return new Float32Array(b.buffer,b.byteOffset,b.length/4);};
const previous=JSON.parse(fs.readFileSync(path.join(root,'mix-recipe.json'),'utf8'));
const priorValidation=JSON.parse(fs.readFileSync(path.join(root,'validation.json'),'utf8'));
const dryPath=path.join(review,'Empty-Junction-A-B-dry-v1.flac');
const dryExpected=priorValidation.outputs.find(o=>o.file==='review/Empty-Junction-A-B-dry-v1.flac').sha256;
const windPath=path.join(root,'sources',previous.sources[2].file);
if(sha(dryPath)!==dryExpected || sha(windPath)!==previous.sources[2].sha256)throw Error('Input hash mismatch');
const dry=decode(dryPath), wind=decode(windPath);
if(dry.length!==frames*2 || wind.length<29*rate*2)throw Error('Unexpected source duration');
const period=24*rate, loop=new Float32Array(period*2), windGain=Math.pow(10,previous.wind_gain_db/20);
for(let frame=0;frame<period;frame++)for(let ch=0;ch<2;ch++){
  let x;
  if(frame<20*rate)x=wind[(5*rate+frame)*2+ch];
  else{const t=frame-20*rate,p=t/(4*rate)*Math.PI/2;x=wind[(25*rate+t)*2+ch]*Math.cos(p)+wind[(rate+t)*2+ch]*Math.sin(p);}
  loop[frame*2+ch]=x*windGain;
}
const windows=[[0,60],[180,240],[360,420]], offWindows=[[60,180],[240,360],[420,450]];
const mixed=new Float32Array(dry.length);
for(let frame=0;frame<frames;frame++){
  const t=frame/rate, local=t%180;
  // Fade time belongs inside each one-minute window. Two complete minutes off.
  let envelope=0;
  if(local<60){const f=frame%(180*rate);envelope=Math.max(0,Math.min(1,f/(5*rate),(60*rate-1-f)/(8*rate)));}
  for(let ch=0;ch<2;ch++)mixed[frame*2+ch]=dry[frame*2+ch]+loop[(frame%period)*2+ch]*envelope;
}
const raw=path.join(cache,'Empty-Junction-A-B-intermittent-wind-v2.f32');
if(fs.existsSync(raw))throw Error('Refusing to overwrite '+raw);
fs.writeFileSync(raw,Buffer.from(mixed.buffer,mixed.byteOffset,mixed.byteLength),{flag:'wx'});
const outputs=[], measurementLogs={};
for(const ext of ['flac','mp3']){
  const file='Empty-Junction-A-B-intermittent-wind-v2.'+ext, dest=path.join(review,file);
  if(fs.existsSync(dest))throw Error('Refusing to overwrite '+dest);
  run(['-n','-f','f32le','-ar',String(rate),'-ac','2','-i',raw,'-map_metadata','-1',
    ...(ext==='flac'?['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24']:['-c:a','libmp3lame','-b:a','192k']),dest]);
  const restored=decode(dest);
  if(restored.length!==mixed.length)throw Error('Wrong decoded frame count');
  let peak=0,maxError=0,signal=0,error=0;
  for(let i=0;i<restored.length;i++){
    const x=restored[i];if(!Number.isFinite(x)||Math.abs(x)>=1)throw Error('Non-finite or clipped sample');
    peak=Math.max(peak,Math.abs(x));const e=x-mixed[i];maxError=Math.max(maxError,Math.abs(e));error+=e*e;signal+=mixed[i]*mixed[i];
  }
  const comparison={all_decoded_samples_compared:true,max_absolute_error:maxError,snr_db:10*Math.log10(signal/error)};
  if(ext==='flac'&&maxError>2.4e-7)throw Error('Lossless recipe mismatch');
  if(ext==='mp3'&&comparison.snr_db<20)throw Error('Unexpected MP3 deviation');
  const offChecks=offWindows.map(([start,end])=>{
    let max=0;for(let i=start*rate*2;i<end*rate*2;i++)max=Math.max(max,Math.abs(restored[i]-dry[i]));
    if(ext==='flac'&&max!==0)throw Error('Wind present during off window');
    return {start_seconds:start,end_seconds:end,max_difference_from_dry:max,exact_dry_identity:ext==='flac'?max===0:null};
  });
  const result=cp.spawnSync('ffmpeg',['-hide_banner','-nostdin','-i',dest,'-af','loudnorm=I=-23:TP=-1:LRA=11:print_format=json','-f','null','NUL'],{encoding:'utf8',maxBuffer:5000000});
  if(result.status!==0)throw Error(result.stderr);
  const m=JSON.parse(result.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)[0]);
  measurementLogs[ext]=result.stderr;
  if(Number(m.input_tp)>=-1)throw Error('Insufficient headroom');
  outputs.push({file:'review/'+file,sha256:sha(dest),bytes:fs.statSync(dest).size,decoded_frames:restored.length/2,
    seconds:restored.length/2/rate,all_samples_finite:true,full_scale_samples:0,sample_peak_dbfs:20*Math.log10(peak),
    integrated_lufs:Number(m.input_i),true_peak_dbtp:Number(m.input_tp),lra_lu:Number(m.input_lra),recipe_comparison:comparison,
    wind_off_window_checks:offChecks});
}
if(sha(dryPath)!==dryExpected||sha(windPath)!==previous.sources[2].sha256)throw Error('Input changed');
const recipe={date:'2026-10-31',duration_seconds:duration,sample_rate:rate,channels:2,
  base_music:{file:'review/Empty-Junction-A-B-dry-v1.flac',sha256:dryExpected,note:'Reviewed dry arrangement retained; quantized to the existing 24-bit FLAC.'},
  wind_source:{file:'sources/'+previous.sources[2].file,sha256:previous.sources[2].sha256},wind_gain_db:previous.wind_gain_db,
  wind_period_seconds:24,wind_source_trim_seconds:[1,29],wind_tail_head_overlap_seconds:4,wind_tail_head_curve:'equal-power cosine/sine',
  wind_windows_seconds:windows,wind_off_windows_seconds:offWindows,
  wind_fade_in_seconds:5,wind_fade_out_seconds:8,wind_fades_are_inside_active_windows:true,
  music_handover_seconds:[212,224],radio_included:false,
  feedback:'User prefers roughly one minute wind / two minutes off; prior music/wind preview sounded good so far. Radio v2 too static-focused; v3 station prompt adds varied purposeful equipment activity.',
  approval:'New wind timing and radio v3 prompt await listening/generation; no final approval inferred.',
  assistant_review:'Full technical decode/sample checks only, no assistant listening verdict.',
  paid_generation_performed:false};
fs.writeFileSync(path.join(root,'mix-recipe-v2.json'),JSON.stringify(recipe,null,2)+'\n');
fs.writeFileSync(path.join(root,'validation-v2.json'),JSON.stringify({status:'passed',source_files_unchanged:true,outputs},null,2)+'\n');
fs.writeFileSync(path.join(root,'measurement-logs-v2.json'),JSON.stringify(measurementLogs,null,2)+'\n');
console.log(JSON.stringify({status:'passed',duration_seconds:duration,outputs},null,2));
