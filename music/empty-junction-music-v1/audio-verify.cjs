// Shared full-stream sample, duration and loudness verification for local audio.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const fileHash=p=>new Promise((resolve,reject)=>{const h=crypto.createHash('sha256'),s=fs.createReadStream(p);s.on('data',b=>h.update(b));s.on('error',reject);s.on('end',()=>resolve(h.digest('hex')));});
function createVerifier({root,raw,rate=48000,seconds=3600}){
 return async function validate(p,start=0,duration=seconds){
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
 };
}
module.exports={createVerifier,fileHash};
