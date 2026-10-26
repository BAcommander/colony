"""Validate the actual branded final file, copied loops and entire audio mix."""
from assemble_with_colony import *
from colony import intro as opening
import re,math
import numpy as np
from PIL import Image,ImageDraw
V=H/'verification-cache';V.mkdir(exist_ok=True)
FF=render.get_ffmpeg_path();PROBE=shutil.which('ffprobe')
def run(args,**kwargs):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,**kwargs)
def framedigests(path,start,seconds,label):
    args=[FF,'-v','error']
    if start:args+=['-ss',str(start)]
    args+=['-i',str(path),'-t',str(seconds),'-map','0:v:0','-an','-f','framemd5','pipe:1']
    result=run(args).stdout.decode();(V/(label+'-frames.md5')).write_text(result)
    return [row.rsplit(',',1)[-1].strip() for row in result.splitlines() if row and not row.startswith('#')]
def verify_video():
    assert OUTPUT.exists()
    print('Checking every encoded packet and video timestamp...',flush=True)
    intro_rows=[];base=[];count=0;tb=None;progress=-1
    log=V/'packet-read.log'
    with log.open('wb') as err:
        p=subprocess.Popen([FF,'-v','error','-i',str(OUTPUT),'-map','0:v:0','-c:v','copy','-f','framehash','-hash','sha256','pipe:1'],stdout=subprocess.PIPE,stderr=err,text=False)
        with (V/'all-video-packets.sha256').open('wb') as records:
            for raw in p.stdout:
                records.write(raw);line=raw.decode().strip()
                if line.startswith('#tb 0:'):
                    n,d=map(int,line.split(':',1)[1].strip().split('/'));tb=n/d
                elif line and not line.startswith('#'):
                    fields=[v.strip() for v in line.split(',')];assert tb is not None
                    dts,pts=int(fields[1])*tb,int(fields[2])*tb
                    assert abs(pts-count/30)<1e-5 and abs(dts-count/30)<1e-5,(count,dts,pts)
                    if count<1800:intro_rows.append(fields[5])
                    elif count<3600:base.append(fields[5])
                    else:assert fields[5]==base[count%1800],('Changed clean loop payload',count)
                    count+=1
                    if count//18000>progress:
                        progress=count//18000;print(f'Packet/timestamp scan: {count/30/60:.1f}/120 minutes',flush=True)
        assert p.wait()==0
    assert count==216000 and len(base)==len(intro_rows)==1800
    print('Comparing decoded master, branded first minute and clean minute...',flush=True)
    original=framedigests(VIDEO,0,60,'master')
    first=framedigests(OUTPUT,0,60,'branded-first-minute')
    second=framedigests(OUTPUT,60,60,'first-clean-minute')
    assert len(original)==len(first)==len(second)==1800
    assert second==original,'First clean minute differs from verified source'
    assert first[660:]==original[660:],'Pictures changed after opening clears'
    assert any(first[i]!=original[i] for i in range(660)),'Intro missing'
    probe=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(OUTPUT)]).stdout)
    video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['r_frame_rate'])==(3840,2160,'30/1')
    assert int(video['nb_frames'])==216000 and abs(float(probe['format']['duration'])-7200)<.04
    assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000 and audio['channels']==2
    save('video-validation.json',{'status':'passed','packet_count':count,'frames':216000,'all_pts_dts_exact_30fps':True,'119_clean_minute_payloads_identical':True,'first_clean_minute_all_1800_decoded_yuv_frames_match_master':True,'first_minute_after_22s_all_decoded_yuv_frames_match_master':True,'opening_detected_in_first_22s':True,'dimensions':[3840,2160],'fps':30,'probe':probe})
def verify_audio():
    print('Checking full AAC audio against Colony fade/mix reference...',flush=True)
    graph=opening.audio_graph(render.build_audio_graph([0.0],0,first_input=0),IntroSettings('Spirewatch',True))
    base=[FF,'-v','error']
    with (V/'expected-audio.log').open('wb') as e1,(V/'final-audio.log').open('wb') as e2:
        p=subprocess.Popen(base+['-i',str(AUDIO),'-filter_complex',graph,'-map','[aout]','-t','7200','-ac','2','-ar','48000','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=e1)
        q=subprocess.Popen(base+['-i',str(OUTPUT),'-vn','-t','7200','-ac','2','-ar','48000','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=e2)
        count=0;maxpeak=0.0;sxx=syy=sxy=error=0.0;first=0.0;windows=[]
        for second in range(7200):
            ar=p.stdout.read(48000*2*4);br=q.stdout.read(48000*2*4)
            assert len(ar)==len(br)==48000*2*4,(second,len(ar),len(br))
            a=np.frombuffer(ar,dtype='<f4').astype(float);b=np.frombuffer(br,dtype='<f4').astype(float)
            assert np.isfinite(a).all() and np.isfinite(b).all()
            maxpeak=max(maxpeak,float(np.max(abs(b))));assert maxpeak<1
            if second<4:first=max(first,float(np.max(abs(b))))
            ax=float(a@a);by=float(b@b);xy=float(a@b)
            sxx+=ax;syy+=by;sxy+=xy;error+=float(np.sum((a-b)**2));count+=48000
            if second in [4,5,10,15,19,20,501,505,510,673,677,682,7180,7190,7199]:
                windows.append({'second':second,'expected_rms':math.sqrt(ax/len(a)),'aac_rms':math.sqrt(by/len(b)),'correlation':xy/math.sqrt(max(ax*by,1e-30))})
            if second%1800==1799:print(f'AAC audio verified {(second+1)/60:.0f}/120 minutes',flush=True)
        assert not p.stdout.read(1) and not q.stdout.read(1)
        assert p.wait()==q.wait()==0 and count==345600000
    corr=sxy/math.sqrt(sxx*syy);gain=10*math.log10(syy/sxx);snr=10*math.log10(sxx/error)
    assert first<1e-6 and corr>.995 and abs(gain)<.15 and snr>25,(first,corr,gain,snr)
    save('audio-validation.json',{'status':'passed','valid_audio_seconds':7200,'sample_frames':count,'all_samples_finite':True,'no_full_scale_samples':True,'sample_peak_dbfs':20*math.log10(maxpeak),'source_expected_graph':graph,'first_four_seconds_peak':first,'opening_audio_silence_to_5s_then_hsin_fade_to_20s':True,'full_track_correlation_with_expected_mix':corr,'whole_mix_gain_difference_db':gain,'lossy_encoding_snr_db':snr,'diagnostic_windows':windows,'note':'Exact sample count over declared 7200-second interval; compare AAC with the full FLAC passed through the same Colony graph. No claim of lossy waveform identity or assistant listening.'})
def stills():
    print('Extracting opening review stills...',flush=True)
    frames=[30,180,390,480,570,690]
    selection='+'.join(f'eq(n\\,{i})' for i in frames)
    run([FF,'-v','error','-n','-i',str(OUTPUT),'-vf',f'select={selection},scale=1280:720:flags=lanczos','-frames:v','6','-fps_mode','vfr',str(H/'opening-%02d.png')])
    sheet=Image.new('RGB',(1280,1170),'#11151b');draw=ImageDraw.Draw(sheet)
    labels=['1s: dark opening','6s: channel, logo and PRESENTS','13s: SPIREWATCH and invitation','16s: invitation held','19s: invitation still held','23s: clean scene']
    for i,label in enumerate(labels):
        image=Image.open(H/f'opening-{i+1:02d}.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
        x=(i%2)*640;y=(i//2)*390;sheet.paste(image,(x,y));draw.text((x+10,y+367),label,fill='#F3EBDD')
    sheet.save(H/'opening-contact-sheet.jpg',quality=94)
    save('visual-review.json',{'stills':'opening-contact-sheet.jpg','times_seconds':[1,6,13,16,19,23],'inspection':'Prepared for assistant visual inspection; continuous playback not claimed','source_phase':'Source loop starts at phase zero and repeats every sixty seconds; opening adds no runtime'})
def finish():
    v=json.loads((H/'video-validation.json').read_text());a=json.loads((H/'audio-validation.json').read_text());c=json.loads((H/'colony-export.json').read_text());assert v['status']==a['status']=='passed' and c['verification']['full_decode'] and c['verification']['passed']
    settings=json.loads((H/'assembly-settings.json').read_text())
    assert digest(VIDEO)==settings['video']['sha256'] and digest(AUDIO)==settings['audio']['sha256']
    if (H/'container-hash.json').exists():
        container=json.loads((H/'container-hash.json').read_text());stat=OUTPUT.stat()
        assert container['bytes']==stat.st_size and container['mtime_ns']==stat.st_mtime_ns
        finalhash=container['sha256']
    else:
        print('Hashing finished final video...',flush=True);finalhash=digest(OUTPUT)
    save('delivery-validation.json',{'status':'passed','output':str(OUTPUT),'bytes':OUTPUT.stat().st_size,'sha256':finalhash,'duration_seconds':7200,'dimensions':[3840,2160],'fps':30,'frames':216000,'native_source_dimensions':[1672,941],'upscale':'Previously verified native-to-4K Lanczos master, unchanged in assembly','colony_full_video_audio_decode':True,'video_validation':'video-validation.json','audio_validation':'audio-validation.json','opening':'Actual Colony v3, public title Spirewatch, once; pictures clear by 22s; sound silence to5/fade to20','source_hashes_unchanged':True,'clean_loop_payloads_identical':119,'full_combined_user_review':'pending','assistant_inspection':'Decoded temporal stills, technical checks; not continuous playback or full listening','remote_backup':False})
    print('Final two-hour Spirewatch delivery technically verified.',flush=True)
def container_hash():
    assert not (H/'container-hash.json').exists()
    before=OUTPUT.stat();h=hashlib.sha256();total=0;last=0
    with OUTPUT.open('rb') as stream:
        for block in iter(lambda:stream.read(16*1024**2),b''):
            h.update(block);total+=len(block)
            if total-last>=8*1024**3:
                print(f'Final-file hash read: {total/1024**3:.1f}/{before.st_size/1024**3:.1f} GiB',flush=True);last=total
    after=OUTPUT.stat();assert before.st_size==after.st_size==total and before.st_mtime_ns==after.st_mtime_ns
    save('container-hash.json',{'path':str(OUTPUT),'bytes':total,'mtime_ns':after.st_mtime_ns,'sha256':h.hexdigest(),'stable_during_read':True})
    print('Final-file SHA-256 complete.',flush=True)
if __name__=='__main__':
    choice=sys.argv[1:]
    if '--hash' in choice:container_hash()
    if not choice or '--video' in choice:verify_video()
    if not choice or '--audio' in choice:verify_audio()
    if not choice or '--stills' in choice:stills()
    if not choice or '--finish' in choice:finish()
