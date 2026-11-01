// Local preview assembly, Node built-ins + FFmpeg only. No paid generation.
// Existing media are never overwritten. Run with `node build-review.cjs`.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const root = __dirname;
const rate = 48000, channels = 2, duration = 450;
const review = path.join(root, 'review');
const sources = path.join(root, 'sources');
const cache = path.join(root, '.cache');
for (const d of [review, sources, cache]) fs.mkdirSync(d, {recursive:true});
const inputs = [
  ['Signal_Cabin_Wait_2026-10-31T161557.mp4', -13.87, -2.13, 2.80],
  ['Quiet_Signal_Cabin_2026-10-31T161557.mp4', -13.24, -1.89, 1.80],
  ['Soft_wind_moving_thr_#4-1793463971195.mp3', -42.85, -24.68, 3.20],
];
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const run = (args, options={}) => cp.execFileSync('ffmpeg', ['-v','error','-nostdin',...args], {maxBuffer:300000000,...options});
const decode = p => {
  const b = run(['-i',p,'-map','0:a:0','-ac','2','-ar',String(rate),'-f','f32le','pipe:1']);
  return new Float32Array(b.buffer,b.byteOffset,b.length/4);
};
const originals = inputs.map(([name,lufs,tp,lra]) => {
  const from = path.join('C:/Users/jazzs/Downloads', name);
  const local = path.join(sources,name);
  const digest = hash(from);
  if (fs.existsSync(local)) {
    if (hash(local)!==digest) throw Error('Existing source differs: '+local);
  } else fs.copyFileSync(from,local,fs.constants.COPYFILE_EXCL);
  if (hash(local)!==digest) throw Error('Source copy hash mismatch');
  return {file:name,original_path:from,sha256:digest,bytes:fs.statSync(local).size,
    measured_input_lufs:lufs,measured_input_true_peak_dbtp:tp,measured_input_lra_lu:lra,
    measurement:'FFmpeg loudnorm analysis input statistics, 2026-10-31; analysis output discarded',local};
});
const [a,b,w] = originals.map(s => decode(s.local));
if(a.length!==240*rate*2 || b.length!==240*rate*2) throw Error('Unexpected music frame count');
if(w.length<29*rate*2) throw Error('Wind too short');
const gainA = -23-originals[0].measured_input_lufs;
const gainB = -23-originals[1].measured_input_lufs;
const gainWind = -35-originals[2].measured_input_lufs;
const amp = db => Math.pow(10,db/20);
const dry = new Float32Array(duration*rate*2);
// A 0:00-3:44, before its long generated fade; B 0:02-4:00.
// 12-second equal-power overlap at output 3:32-3:44. No time/pitch changes.
for(let frame=0;frame<224*rate;frame++) {
  const fade = frame<212*rate ? 1 : Math.cos((frame-212*rate)/(12*rate)*Math.PI/2);
  for(let ch=0;ch<2;ch++) dry[frame*2+ch] = a[frame*2+ch]*amp(gainA)*fade;
}
for(let frame=0;frame<238*rate;frame++) {
  const fade = frame<12*rate ? Math.sin(frame/(12*rate)*Math.PI/2) : 1;
  const dest=(212*rate+frame)*2, src=(2*rate+frame)*2;
  for(let ch=0;ch<2;ch++) dry[dest+ch] += b[src+ch]*amp(gainB)*fade;
}
// Make one 24-second steady-state wind period from source 0:01-0:29.
// Source 0:05-0:25, followed by a four-second tail/head crossfade.
// The last head sample joins continuously back to source 0:05 next period.
const period = 24*rate, overlap=4*rate;
const windLoop = new Float32Array(period*2);
for(let frame=0;frame<period;frame++) {
  for(let ch=0;ch<2;ch++) {
    let sample;
    if(frame<20*rate) sample=w[(5*rate+frame)*2+ch];
    else {
      const t=frame-20*rate, phase=t/overlap*Math.PI/2;
      sample=w[(25*rate+t)*2+ch]*Math.cos(phase)+w[(rate+t)*2+ch]*Math.sin(phase);
    }
    windLoop[frame*2+ch]=sample*amp(gainWind);
  }
}
const wet = new Float32Array(dry.length);
for(let frame=0;frame<duration*rate;frame++) {
  const envelope=Math.min(1,frame/(3*rate),(duration*rate-1-frame)/(10*rate));
  for(let ch=0;ch<2;ch++) wet[frame*2+ch]=dry[frame*2+ch]+windLoop[(frame%period)*2+ch]*Math.max(0,envelope);
}
const summary = data => {
  let peak=0,sum=0,nonfinite=0,fullscale=0;
  for(const x of data) {if(!Number.isFinite(x)) nonfinite++; peak=Math.max(peak,Math.abs(x));sum+=x*x;if(Math.abs(x)>=1) fullscale++;}
  return {frames:data.length/2,seconds:data.length/2/rate,all_samples_finite:nonfinite===0,
    full_scale_samples:fullscale,sample_peak_dbfs:20*Math.log10(peak),rms_dbfs:10*Math.log10(sum/data.length)};
};
const logs={};
function measure(p,label) {
  const res=cp.spawnSync('ffmpeg',['-hide_banner','-nostdin','-i',p,'-map','0:a:0','-af','loudnorm=I=-23:TP=-1:LRA=11:print_format=json','-f','null','NUL'],{encoding:'utf8',maxBuffer:5000000});
  if(res.status!==0) throw Error(res.stderr);
  logs[label]=res.stderr;
  const match=res.stderr.match(/\{\s*"input_i"[\s\S]*?\}/);
  if(!match) throw Error('Missing loudness statistics');
  const m=JSON.parse(match[0]);
  return {integrated_lufs:Number(m.input_i),true_peak_dbtp:Number(m.input_tp),lra_lu:Number(m.input_lra)};
}
const outputs=[];
function exportPair(label,data) {
  const raw=path.join(cache,label+'.f32');
  if(fs.existsSync(raw)) throw Error('Refusing to overwrite '+raw);
  fs.writeFileSync(raw,Buffer.from(data.buffer,data.byteOffset,data.byteLength),{flag:'wx'});
  for(const ext of ['flac','mp3']) {
    const file=label+'.'+ext, dest=path.join(review,file);
    if(fs.existsSync(dest)) throw Error('Refusing to overwrite '+dest);
    run(['-n','-f','f32le','-ar',String(rate),'-ac','2','-i',raw,
      '-map_metadata','-1',...(ext==='flac'?['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24']:['-c:a','libmp3lame','-b:a','192k']),dest]);
    const restored=decode(dest), stats=summary(restored);
    if(restored.length!==data.length || !stats.all_samples_finite || stats.full_scale_samples) throw Error('Output validation failure '+file);
    let maxError=0,err=0,signal=0;
    for(let i=0;i<data.length;i++){const e=restored[i]-data[i];maxError=Math.max(maxError,Math.abs(e));err+=e*e;signal+=data[i]*data[i];}
    const compare={all_decoded_samples_compared:true,max_absolute_error:maxError,snr_db:10*Math.log10(signal/err)};
    if(ext==='flac' && maxError>2.4e-7) throw Error('Lossless recipe mismatch');
    if(ext==='mp3' && compare.snr_db<20) throw Error('Unexpected MP3 deviation');
    const loudness=measure(dest,label+'-'+ext);
    if(loudness.true_peak_dbtp>=-1) throw Error('Insufficient true peak headroom');
    outputs.push({file:'review/'+file,bytes:fs.statSync(dest).size,sha256:hash(dest),...stats,...loudness,recipe_comparison:compare});
  }
}
exportPair('Empty-Junction-A-B-dry-v1',dry);
exportPair('Empty-Junction-A-B-soft-wind-v1',wet);
const excerpt=wet.slice(192*rate*2,252*rate*2);
exportPair('Empty-Junction-music-handover-60s-v1',excerpt);
const windBoundary=[];
for(let ch=0;ch<2;ch++) windBoundary.push(windLoop[ch]-windLoop[(period-1)*2+ch]);
const recipe={date:'2026-10-31',sample_rate:rate,channels:2,duration_seconds:duration,
  sources:originals.map(({local,...s})=>s),music_gain_db:[gainA,gainB],wind_gain_db:gainWind,
  nominal_isolated_targets_lufs:{music:-23,wind:-35},
  schedule:[{source:inputs[0][0],source_in_seconds:0,source_out_seconds:224,output_start_seconds:0},
    {source:inputs[1][0],source_in_seconds:2,source_out_seconds:240,output_start_seconds:212}],
  handover:{start_seconds:212,end_seconds:224,curve:'equal-power cosine/sine, 12 seconds',approval:'pending user listening'},
  source_fade_handling:'A long generated closing fade excluded; B two-second opening excluded. A opening and B final generated fade retained.',
  wind:{source_in_seconds:1,source_out_seconds:29,crossfade_seconds:4,period_seconds:24,
    curve:'equal-power cosine/sine',fade_in_seconds:3,fade_out_seconds:10,
    loop_boundary_sample_differences:windBoundary,note:'Repeating 30-second source; no claim of non-repetition or acoustic field-recording provenance.'},
  excerpt:{output_start_seconds:192,output_end_seconds:252,handover_at_excerpt_seconds:[20,32]},
  added_eq_compression_limiting_time_stretch_pitch_shift:false,
  radio_included:false,paid_generation_performed:false,
  approval:'Local audition only. User preferred earlier Signal Cabin Drift pilot; no approval inferred for either new long variant, handover or wind balance.',
  assistant_review:'Full technical decode/sample validation only; no assistant listening verdict.',
  generation_settings:'User supplied two four-minute variants and one wind export. Actual generation prompts, reference, settings and cost not verified.'};
for(const s of originals) if(hash(s.original_path)!==s.sha256 || hash(s.local)!==s.sha256) throw Error('Source changed');
fs.writeFileSync(path.join(root,'mix-recipe.json'),JSON.stringify(recipe,null,2)+'\n');
fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify({status:'passed',source_copies_hash_verified:true,source_files_unchanged:true,outputs},null,2)+'\n');
fs.writeFileSync(path.join(root,'measurement-logs.json'),JSON.stringify(logs,null,2)+'\n');
console.log(JSON.stringify({status:'passed',duration_seconds:duration,outputs},null,2));
