// Preserve built-in generated masters, export JPEGs and assemble review sheets.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=__dirname,project=path.resolve(root,'../..'),release=path.join(project,'final/11-empty-junction');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const ff=args=>cp.execFileSync('ffmpeg',['-v','error','-nostdin',...args],{maxBuffer:30000000});
const dimensions=p=>JSON.parse(cp.execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',p],{encoding:'utf8'})).streams[0];
const copy=(a,b)=>{if(fs.existsSync(b)){if(sha(a)!==sha(b))throw Error('Existing different file '+b);}else fs.copyFileSync(a,b,fs.constants.COPYFILE_EXCL);if(sha(a)!==sha(b))throw Error('Copy mismatch');};
const genDir='C:/Users/jazzs/.codex/generated_images/01a192a2-705f-7391-80a2-74e52ec3e7ea';
const generated=[
 ['exec-69c9684b-d571-4e2b-8f5b-98db55c84c9a.png','artwork-v3.png','prompts/artwork-v3.txt',[path.join(release,'artwork-v2.png')]],
 ['exec-88698694-7882-4f84-a04c-a4e05fa3e7ea.png','original-art-junction-master.png','prompts/thumbnail-junction.txt',[path.join(release,'artwork-v2.png'),path.join(project,'final/01-ringfall-observatory/thumbnail-v1.png')]],
 ['exec-57ff77fe-3e44-4c13-ad02-09c8bf91c9b8.png','revised-art-junction-master.png','prompts/thumbnail-junction.txt',[path.join(root,'artwork-v3.png'),path.join(project,'final/01-ringfall-observatory/thumbnail-v1.png')]],
];
generated.forEach(([from,to])=>copy(path.join(genDir,from),path.join(root,to)));
copy(path.join(release,'artwork-v2.png'),path.join(root,'original-art-scene-master.png'));
copy(path.join(release,'thumbnail-v1.jpg'),path.join(root,'original-branded-control.jpg'));
for(const file of ['youtube-title.txt','README.md','manifest.json'])copy(path.join(release,file),path.join(root,'previous-release-'+file));
const variants=[
 {id:'A',label:'Original scene',master:'original-art-scene-master.png',file:'thumbnail-original-scene-v1.jpg'},
 {id:'B',label:'Original + JUNCTION',master:'original-art-junction-master.png',file:'thumbnail-original-junction-v1.jpg'},
 {id:'C',label:'Revised scene',master:'artwork-v3.png',file:'thumbnail-revised-scene-v1.jpg'},
 {id:'D',label:'Revised + JUNCTION',master:'revised-art-junction-master.png',file:'thumbnail-revised-junction-v1.jpg'},
];
for(const v of variants){const dest=path.join(root,v.file);if(!fs.existsSync(dest))ff(['-n','-i',path.join(root,v.master),'-vf','scale=1280:720:flags=lanczos','-frames:v','1','-q:v','2',dest]);
 const d=dimensions(dest);if(d.width!==1280||d.height!==720||fs.statSync(dest).size>=2000000)throw Error('JPEG delivery check failed');
 ff(['-i',dest,'-f','null','NUL']);
}
const rgb=p=>ff(['-i',p,'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1']);
function drift(base,title){
 const p=path.join(root,base),q=path.join(root,title),d=dimensions(p),e=dimensions(q);
 if(d.width!==e.width||d.height!==e.height) return {same_dimensions:false,pixel_identical_outside_title:false};
 const a=rgb(p),b=rgb(q);let n=0,changed=0,sum=0,squared=0,baseL=0,titleL=0;
 for(let y=0;y<d.height;y++)for(let x=0;x<d.width;x++){
  if(x>=d.width*.35&&x<d.width*.75&&y>=d.height*.02&&y<d.height*.20)continue;
  const at=(y*d.width+x)*3;let any=false;
  for(let c=0;c<3;c++){const diff=b[at+c]-a[at+c];sum+=Math.abs(diff);squared+=diff*diff;n++;if(diff)any=true;}
  if(any)changed++;baseL+=.2126*a[at]+.7152*a[at+1]+.0722*a[at+2];titleL+=.2126*b[at]+.7152*b[at+1]+.0722*b[at+2];
 }
 return {same_dimensions:true,excluded_normalized_rectangle:[.35,.02,.75,.20],pixel_identical_outside_title:changed===0,
  changed_pixel_fraction_outside_title:changed/(n/3),mean_absolute_rgb_difference_8bit:sum/n,
  psnr_db:10*Math.log10(255*255/(squared/n)),outside_region_mean_luma:[baseL/(n/3),titleL/(n/3)],
  note:'Generated title edits are visual candidates, not a strictly controlled typography-only experiment.'};
}
const font=path.join(project,'creative/brand/fonts/BarlowCondensed-SemiBold.ttf').replaceAll('\\','/').replace(':','\\:');
function sheet(file,w,h,pad,label){
 const inputs=variants.flatMap(v=>['-i',path.join(root,v.file)]);
 const streams=variants.map((v,i)=>`[${i}:v]scale=${w}:${h}:flags=lanczos,pad=${w}:${h+label}:0:${label}:color=0x151a20,drawtext=fontfile='${font}':text='${v.id}  ${v.label}':fontcolor=0xF3EBDD:fontsize=${label-7}:x=8:y=3[v${i}]`).join(';');
 const stack=`[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|${w+pad}_0|0_${h+label+pad}|${w+pad}_${h+label+pad}:fill=0x151a20[out]`;
 const dest=path.join(root,file);if(!fs.existsSync(dest))ff(['-n',...inputs,'-filter_complex',streams+';'+stack,'-map','[out]','-frames:v','1',dest]);
}
sheet('comparison-phone-size.png',240,135,16,25);
sheet('comparison-large.png',640,360,16,38);
const assets=fs.readdirSync(root).filter(f=>/\.(png|jpg|txt|cjs)$/.test(f)&&!f.startsWith('previous-')).map(file=>{
 const p=path.join(root,file),entry={file,bytes:fs.statSync(p).size,sha256:sha(p)};
 if(/\.(png|jpg)$/.test(file))entry.dimensions=dimensions(p);return entry;
});
const manifest={date:'2026-10-31',scene:'The Empty Junction',catalog_number:11,
 generator:'built-in image_gen',new_generation_count:3,paid_api_used:false,
 generated:generated.map(([original,file,prompt,references])=>({file,original_generated_path:path.join(genDir,original),prompt,
  original_bytes_preserved:sha(path.join(genDir,original))===sha(path.join(root,file)),
  references:references.map(p=>({path:p,sha256:sha(p)}))})),
 variants,assets,
 title:fs.readFileSync(path.join(root,'youtube-title.txt'),'utf8').trim(),
 typography_drift:{original:drift('original-art-scene-master.png','original-art-junction-master.png'),revised:drift('artwork-v3.png','revised-art-junction-master.png')},
 review:{method:'Full returned stills and local phone-size/contact sheets inspected by assistant; user review pending.',
  artwork_candidate:'New complete-cabin composition, fewer near gravel areas and larger exposed mineral skyline. Warm cabin and freight hall retained. Some bright minor yard practicals remain. Rail turnout geometry and fine fittings need review before animation.',
  title_candidates:'JUNCTION correctly spelled; no header, logo, subtitle, number or underline. Scene details can drift during generated title edits.',
  historical_assets_preserved:true,new_art_user_approved:false,new_thumbnails_user_approved:false,
  animation:'Existing v3 animation still uses original artwork. New composition requires fresh mask mapping; not remapped or rendered by this request.',
  audio:'Existing one-hour delivery unchanged.',performance:'No CTR lift, native test result or visual acceptance inferred.'},
 validation:{all_four_jpegs_decoded:true,all_four_jpegs_1280x720:true,all_four_jpegs_under_2MB:true},
 prompts:['prompts/artwork-v3.txt','prompts/thumbnail-junction.txt'].map(file=>({file,sha256:sha(path.join(root,file))}))};
fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({variants,typography_drift:manifest.typography_drift,jpeg_checks:manifest.validation},null,2));
