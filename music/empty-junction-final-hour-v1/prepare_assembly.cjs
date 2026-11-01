const fs=require('fs'),path=require('path');
const home=__dirname,prior=path.join(home,'../spirewatch-final-two-hours-v1');
let a=fs.readFileSync(path.join(prior,'assemble_with_colony.py'),'utf8');
a=a.replace('Assemble Spirewatch','Assemble The Empty Junction')
.replace("R/'music/spirewatch-animation-v8/delivery-4k-v1/Spirewatch-v8-60s-4K-loop.mp4'","H/'masters/Empty-Junction-v6-cycle-180s-4K.mp4'")
.replace("R/'exports/spirewatch/Illuminated-Horizon-and-Stillness-2-Hours-v1.flac'","R/'exports/11-empty-junction/The-Empty-Junction-1-Hour-final-SFX-v3.flac'")
.replace("R/'exports/spirewatch';CACHE=EXPORT/'assembly-v1-cache'","R/'exports/11-empty-junction';CACHE=EXPORT/'video-v1-assembly-cache'")
.replace("EXPORT/'Spirewatch-2-Hours-4K-v1.mp4'","EXPORT/'The-Empty-Junction-1-Hour-4K-v1.mp4'");
const start=a.indexOf("    vd=json.loads(");const end=a.indexOf('    CACHE.mkdir',start);
if(start<0||end<0)throw Error('Source block not found');
a=a.slice(0,start)+`    validation=json.loads((H/'master-validation.json').read_text())
    assert validation['status']=='passed'
    vd=next(x for x in validation['files'] if x['file']==VIDEO.name)
    ar={'sha256':'84a773c68ca1a8d1115c76e2edcc914f8c955c5f60cb31436b1c5718b4982f09'}
    assert digest(VIDEO)==vd['sha256'] and digest(AUDIO)==ar['sha256']
`+a.slice(end);
a=a.replaceAll('7200','3600').replaceAll('216000','108000').replace('info.duration==60','info.duration==180')
.replace('str(VIDEO),60.0,info','str(VIDEO),180.0,info').replace("'unit_seconds':60","'unit_seconds':180")
.replace("IntroSettings('Spirewatch'","IntroSettings('The Empty Junction'")
.replace('>170*1024**3','>80*1024**3').replace('Only the opening minute is encoded.','Only the first three-minute unit is encoded.')
.replace('decoded source identity, opening stills','decoded source identity, opening stills');
fs.writeFileSync(path.join(home,'assemble_with_colony.py'),a);
let v=fs.readFileSync(path.join(prior,'verify_final.py'),'utf8');
v=v.replaceAll('Spirewatch','The Empty Junction').replaceAll('SPIREWATCH','THE EMPTY JUNCTION')
.replaceAll('7200','3600').replaceAll('216000','108000').replaceAll('345600000','172800000')
.replaceAll('/120 minutes','/60 minutes').replaceAll('two-hour','one-hour')
.replaceAll('7180','3580').replaceAll('7190','3590').replaceAll('7199','3599');
const vstart=v.indexOf('def verify_video():');const vend=v.indexOf('def verify_audio():',vstart);
let video=v.slice(vstart,vend).replaceAll('1800','5400').replace('count<3600','count<10800')
.replace('count//54000','count//18000').replaceAll("VIDEO,0,60","VIDEO,0,180")
.replaceAll('OUTPUT,0,60','OUTPUT,0,180').replaceAll('OUTPUT,60,60','OUTPUT,180,180')
.replaceAll('119_clean_minute','19_clean_three_minute').replaceAll('minute','three-minute');
v=v.slice(0,vstart)+video+v.slice(vend);
v=v.replace('progress=count//54000','progress=count//18000').replace('/60 three-minutes','/60 minutes')
.replace('19_clean_three_three-minute_payloads_identical','19_clean_three_minute_payloads_identical')
.replace('first_clean_three-minute_all_5400_decoded_yuv_frames_match_master','first_clean_cycle_all_5400_decoded_yuv_frames_match_master')
.replace('first_three-minute_after_22s_all_decoded_yuv_frames_match_master','opening_cycle_after_22s_all_decoded_yuv_frames_match_master')
.replace("'clean_loop_payloads_identical':119","'clean_loop_payloads_identical':19")
.replace('Source loop starts at phase zero and repeats every sixty seconds; opening adds no runtime','Source phase starts at zero; wind/quiet/quiet repeats every 180 seconds; opening adds no runtime');
fs.writeFileSync(path.join(home,'verify_final.py'),v);
console.log('Prepared actual Colony assembly and full-export validation scripts');
