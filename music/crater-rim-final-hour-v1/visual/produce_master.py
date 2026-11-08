"""Produce native-cached Crater Rim 600s clean master, preserving absolute timing."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,time
from fractions import Fraction
import cv2,numpy as np
from PIL import Image
import long_scene as n
H=Path(__file__).resolve().parent;PKG=H.parent;R=PKG.parents[1]
CACHE=R/'.local/crater-rim-final-hour-v1';OUT=R/'exports/14-crater-rim-survey/production-v1'
MASTER=OUT/'Crater-Rim-Survey-clean-600s-4K.mp4'
FF=shutil.which('ffmpeg');FP=shutil.which('ffprobe');FPS=30;SHAPE=(1800,941,1672,3)
RAW=CACHE/'weather-native.rgb'
S=None;MM=None

def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(cmd):return subprocess.run(cmd,capture_output=True,check=True)
def production_fingerprint():
    cache_info=json.loads((H/'weather-cache-validation.json').read_text())
    values={'renderer_sha256':sha(H/'long_scene.py'),'cache_sha256':cache_info['sha256'],'ffmpeg_sha256':sha(Path(FF)),'encoder_command_template':encoder(Path('OUTPUT'),1800)}
    return {**values,'sha256':hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()}
def init_worker(read_cache=False):
    global S,MM
    S=n.Scene()
    if read_cache:MM=np.memmap(RAW,dtype=np.uint8,mode='r',shape=SHAPE)
def cache_job(bounds):
    a,z=bounds;mm=np.memmap(RAW,dtype=np.uint8,mode='r+',shape=SHAPE)
    protected=~S.active;baseline=S.base[protected];rows=[];start=time.monotonic()
    for i in range(a,z):
        frame=S.weather_frame(i/FPS);assert np.array_equal(frame[protected],baseline),i
        mm[i]=frame;rows.append(hashlib.sha256(frame.tobytes()).hexdigest())
    mm.flush();del mm
    return {'start_frame':a,'end_frame':z,'sha256':rows,'elapsed':time.monotonic()-start}
def cache():
    CACHE.mkdir(parents=True,exist_ok=True)
    assert not RAW.exists(),'Existing cache must be verified or a new version used'
    with RAW.open('xb') as f:f.truncate(int(np.prod(SHAPE)))
    started=time.monotonic();rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3,initializer=init_worker) as pool:
        jobs=[pool.submit(cache_job,(i,min(1800,i+150))) for i in range(0,1800,150)]
        for job in concurrent.futures.as_completed(jobs):
            row=job.result();rows.append(row)
            print(json.dumps({'stage':'native-weather-cache','completed_frames':sum(x['end_frame']-x['start_frame'] for x in rows),'total':1800,'elapsed':round(time.monotonic()-started,1)}),flush=True)
    rows.sort(key=lambda x:x['start_frame']);frame_hashes=[h for x in rows for h in x['sha256']]
    assert len(frame_hashes)==1800
    receipt={'status':'passed','file':str(RAW),'shape':list(SHAPE),'bytes':RAW.stat().st_size,'sha256':sha(RAW),'frames':1800,'every_native_frame_source_protection_checked':True,'renderer_sha256':sha(H/'long_scene.py'),'elapsed':time.monotonic()-started,'frame_sha256':frame_hashes}
    save(H/'weather-cache-validation.json',receipt)

def encoder(path,frames,threads=3,size=(3840,2160)):
    return [FF,'-hide_banner','-v','error','-n','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-an','-vf',f'scale={size[0]}:{size[1]}:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-qp','0','-bf','0','-threads',str(threads),'-g','60','-keyint_min','60','-sc_threshold','0','-x264-params','open-gop=0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bsf:v','h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1','-movflags','+faststart',str(path)]

def benchmark():
    CACHE.mkdir(parents=True,exist_ok=True);s=n.Scene();path=CACHE/'benchmark-4K-2s.mp4'
    cmd=encoder(path,60);begun=time.monotonic();render_seconds=0
    with (CACHE/'benchmark-encode.log').open('wb') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(60):
                before=time.monotonic();frame=s.frame(52+i/30);render_seconds+=time.monotonic()-before;p.stdin.write(frame.tobytes())
        finally:p.stdin.close()
        assert p.wait()==0
    receipt={'elapsed':time.monotonic()-begun,'native_render_seconds':render_seconds,'frames':60,'bytes':path.stat().st_size,'command':cmd}
    save(H/'benchmark.json',receipt);print(json.dumps(receipt),flush=True)

def encode_part(index):
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/f'clean-minute-{index:02d}.mp4';partial=OUT/f'clean-minute-{index:02d}.partial.mp4'
    assert not path.exists() and not partial.exists()
    cmd=encoder(partial,1800);start=time.monotonic();protected=~S.active;baseline=S.base[protected];attention_count=0
    logpath=CACHE/f'encode-minute-{index:02d}.log'
    with logpath.open('wb') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(1800):
                t=(index*1800+i)/30;frame=MM[i]
                if S.attention_active(t):frame=S.apply_attention(frame,t);attention_count+=1
                assert np.array_equal(frame[protected],baseline),(index,i)
                p.stdin.write(frame.tobytes())
                if i%150==0:save(CACHE/f'progress-minute-{index:02d}.json',{'minute':index,'frame':i,'total':1800,'elapsed':time.monotonic()-start})
        finally:p.stdin.close()
        assert p.wait()==0,logpath.read_text()
    partial.rename(path)
    receipt={'minute':index,'path':str(path),'frames':1800,'absolute_time_window':[index*60,(index+1)*60],'attention_frames':attention_count,'every_native_frame_source_protection_checked':True,'bytes':path.stat().st_size,'sha256':sha(path),'elapsed':time.monotonic()-start,'command':cmd}
    receipt['production_fingerprint']=production_fingerprint()
    save(H/f'part-{index:02d}-receipt.json',receipt);return receipt

def render(workers):
    cache_path=H/'weather-cache-validation.json';cache_info=json.loads(cache_path.read_text());assert cache_info['status']=='passed'
    current_renderer=sha(H/'long_scene.py')
    if cache_info['renderer_sha256']!=current_renderer:
        recheck=json.loads((H/'renderer-validation.json').read_text())['weather_cache_after_lamp_correction']
        assert recheck['status']=='passed' and recheck['frames']==1800
        assert recheck['all_current_weather_and_stored_cache_frame_hashes_match_original_receipt']
        assert recheck['original_receipt_sha256']==sha(cache_path)
        assert recheck['original_receipt_renderer_sha256']==cache_info['renderer_sha256']
        assert recheck['current_renderer_sha256']==current_renderer
        assert recheck['raw_cache_sha256_from_original_receipt']==cache_info['sha256']
    native=json.loads((PKG/'audit/native-validation.json').read_text())
    assert native['status']=='passed' and native['renderer_sha256']==current_renderer
    assert RAW.stat().st_size==cache_info['bytes'] and sha(RAW)==cache_info['sha256']
    OUT.mkdir(parents=True,exist_ok=True)
    # Minutes 2 and 9 contain no attention events and share the exact 60s weather.
    s=n.Scene();assert not any(s.attention_active((j*1800+i)/30) for j in [2,9] for i in range(1800))
    started=time.monotonic();results=[]
    existing=[];needed=[]
    for i in range(9):
        receipt=H/f'part-{i:02d}-receipt.json';path=OUT/f'clean-minute-{i:02d}.mp4'
        if receipt.exists():
            row=json.loads(receipt.read_text());assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'];assert row['production_fingerprint']==production_fingerprint();results.append(row);existing.append(i)
        else:needed.append(i)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(True,)) as pool:
        jobs={pool.submit(encode_part,i):i for i in needed}
        for job in concurrent.futures.as_completed(jobs):
            row=job.result();results.append(row)
            print(json.dumps({'stage':'4K-clean-minutes','minute_finished':row['minute'],'complete':len(results),'total_unique_minutes':9,'elapsed':round(time.monotonic()-started,1)}),flush=True)
    a=OUT/'clean-minute-02.mp4';b=OUT/'clean-minute-09.mp4'
    if b.exists():assert sha(b)==sha(a)
    else:shutil.copy2(a,b)
    save(H/'part-09-receipt.json',{'minute':9,'path':str(b),'copied_exact_from_minute':2,'frames':1800,'attention_frames':0,'absolute_time_window':[540,600],'bytes':b.stat().st_size,'sha256':sha(b),'reason':'Both units have identical cached weather with all attention layers off; scheduler checked at all3600 relevant frames'})
    concat=CACHE/'clean-master.ffconcat';concat.write_text('ffconcat version 1.0\n'+''.join("file '"+(OUT/f'clean-minute-{i:02d}.mp4').as_posix()+"'\n" for i in range(10)),encoding='utf-8')
    cmd=[FF,'-v','error','-n','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(MASTER)]
    run(cmd);save(H/'master-encode-receipt.json',{'status':'encoded_awaiting_decode_controls','file':str(MASTER),'bytes':MASTER.stat().st_size,'sha256':sha(MASTER),'duration_seconds':600,'frames':18000,'dimensions':[3840,2160],'fps':30,'renderer_sha256':sha(H/'long_scene.py'),'elapsed_this_run':time.monotonic()-started,'resumed_verified_parts':existing,'exact_duplicate_units':{'9':2},'command':cmd})
    print('Clean 600s 4K master assembled.',flush=True)

def validate_master():
    probe=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(MASTER)]).stdout)
    stream=probe['streams'][0]
    assert stream['width']==3840 and stream['height']==2160 and stream['pix_fmt']=='yuv420p' and stream['r_frame_rate']=='30/1'
    assert stream['color_range']=='tv' and all(stream[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
    assert abs(float(probe['format']['duration'])-600)<.001
    assert stream['has_b_frames']==0 and int(stream['nb_frames'])==18000
    assert Fraction(stream['time_base'])*int(stream['duration_ts'])==600
    framehash=CACHE/'master-decoded-framehash.txt';log=CACHE/'master-decode.log'
    previous=CACHE/'master-decode-single-worker-incomplete.txt'
    if framehash.exists():
        assert not previous.exists(),'Preserve existing completed/repeated audit instead of replacing it'
        framehash.rename(previous)
        if log.exists():log.rename(CACHE/'master-decode-single-worker-incomplete.log')
    def chunk(index):
        path=CACHE/f'master-decoded-chunk-{index:02d}.txt';errors=CACHE/f'master-decoded-chunk-{index:02d}.log'
        cmd=[FF,'-v','error','-xerror','-err_detect','explode','-threads','2','-ss',str(index*120),'-i',str(MASTER),'-map','0:v:0','-an','-frames:v','3600','-fps_mode','passthrough','-threads','1','-f','framehash','-hash','sha256','-']
        with path.open('wb') as output,errors.open('wb') as error:
            q=subprocess.run(cmd,stdout=output,stderr=error)
        assert q.returncode==0 and errors.stat().st_size==0,errors.read_text()
        entries=[];unit_tb=None
        for line in path.read_text().splitlines():
            if line.startswith('#tb 0:'):unit_tb=Fraction(line.split(':',1)[1].strip())
            elif line and not line.startswith('#'):
                fields=[x.strip() for x in line.split(',')];i=len(entries)
                assert int(fields[1])*unit_tb==int(fields[2])*unit_tb==Fraction(i,30)
                assert int(fields[3])*unit_tb==Fraction(1,30) and int(fields[4])==12441600
                entries.append(fields[5])
        assert len(entries)==3600
        print(json.dumps({'stage':'4K-master-full-decode','chunk':index,'frames_passed':3600}),flush=True)
        return index,entries
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        decoded=dict(pool.map(chunk,range(5)))
    with framehash.open('w',encoding='utf-8') as output:
        output.write('#format: frame checksums\n#version: 2\n#hash: SHA256\n#tb 0: 1/30\n')
        for block in range(5):
            for local,value in enumerate(decoded[block]):
                i=block*3600+local;output.write(f'0, {i}, {i}, 1, 12441600, {value}\n')
    if previous.exists():
        old=[line.rsplit(',',1)[-1].strip() for line in previous.read_text().splitlines() if line and not line.startswith('#') and len(line.rsplit(',',1)[-1].strip())==64]
        all_hashes=[value for block in range(5) for value in decoded[block]]
        assert all_hashes[:len(old)]==old,'Parallel decode differs from previous sequential prefix'
    rows=[];tb=None
    for line in framehash.read_text().splitlines():
        if line.startswith('#tb 0:'):
            a,b=map(int,line.split(':',1)[1].split('/'));tb=a/b
        elif line and not line.startswith('#'):
            fields=[x.strip() for x in line.split(',')];rows.append({'pts':int(fields[2])*tb,'sha256':fields[5]})
    assert len(rows)==18000 and all(abs(x['pts']-i/30)<1e-6 for i,x in enumerate(rows))
    assert [x['sha256'] for x in rows[3600:5400]]==[x['sha256'] for x in rows[16200:18000]]
    packets=json.loads(run([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration','-of','json',str(MASTER)]).stdout)['packets']
    packet_tb=Fraction(stream['time_base']);assert len(packets)==18000
    for i,p in enumerate(packets):
        assert int(p['pts'])*packet_tb==int(p['dts'])*packet_tb==Fraction(i,30),i
        assert int(p['duration'])*packet_tb==Fraction(1,30),i
    info=json.loads((H/'master-encode-receipt.json').read_text());assert sha(MASTER)==info['sha256']
    receipt={**info,'status':'decode_passed_awaiting_independent_picture_audit','output':str(MASTER),'seconds':600,'full_decode':True,'full_4K_decode':True,'full_decode_method':'Five contiguous120s closed-GOP chunks; all18000 pictures decoded and hashed. Original MP4 PTS/DTS/durations checked independently. Complete final also gets continuous decode.','sequential_prefix_matches_parallel_decode_frames':len(old) if previous.exists() else None,'raw_frame_hashes':str(framehash),'raw_frame_hash_algorithm':'sha256','every_timestamp_checked':True,'all_original_packet_pts_dts_durations_exact':True,'decoded_frames':len(rows),'decoded_duplicate_minutes_exact':True,'decoded_framehash_file':str(framehash),'video_stream':stream}
    save(H/'master-decode-validation.json',receipt);print(json.dumps({'status':receipt['status'],'frames':len(rows),'bytes':MASTER.stat().st_size}),flush=True)

def approve_master():
    receipt=json.loads((H/'master-decode-validation.json').read_text());master_sha=sha(MASTER)
    assert receipt['sha256']==master_sha and receipt['renderer_sha256']==sha(H/'long_scene.py')
    native=PKG/'audit/native-validation.json';decoded=PKG/'audit/decoded-colour-validation.json'
    a=json.loads(native.read_text());b=json.loads(decoded.read_text())
    assert a['status']==b['status']=='passed'
    assert a['renderer_sha256']==b['renderer_sha256']==receipt['renderer_sha256']
    assert b['master_sha256']==master_sha and b['native_validation_sha256']==sha(native)
    assert b['all_selected_actual_decoded_frames_pixel_exact_yuv']
    receipt.update(status='passed',independent_native_audit_sha256=sha(native),independent_encoded_audit_sha256=sha(decoded),independent_encoded_controls=len(b['control_indices']))
    save(H/'master-validation.json',receipt);print('Master decode, original timestamps and independent picture audits all passed.',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['benchmark','cache','render','validate','approve']);ap.add_argument('--workers',type=int,default=3);args=ap.parse_args()
    if args.stage=='benchmark':benchmark()
    elif args.stage=='cache':cache()
    elif args.stage=='render':render(args.workers)
    elif args.stage=='validate':validate_master()
    else:approve_master()
