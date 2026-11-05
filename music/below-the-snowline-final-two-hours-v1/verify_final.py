"""Streamed validation of the full Snowline delivery and its once-only opening."""
from assemble_with_colony import *
from colony import intro as opening
import math
import numpy as np
from PIL import Image, ImageDraw
V=H/'verification-cache'; V.mkdir(exist_ok=True)
FF=render.get_ffmpeg_path(); PROBE=shutil.which('ffprobe')
SECONDS=7200; UNIT=120; FPS=30; FRAMES=216000; UNIT_FRAMES=3600

def run(args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)

def framedigests(path,start,seconds,label):
    if label=='master' and start==0 and seconds==UNIT:
        evidence=json.loads((H/'visual/master-validation.json').read_text(encoding='utf-8'))
        cached=Path(evidence['raw_frame_hashes'])
        assert evidence['status']=='passed' and evidence['full_4K_decode'] and digest(path)==evidence['sha256']
        if cached.exists():
            text=cached.read_text(encoding='utf-8')
            rows=[line.rsplit(',',1)[-1].strip() for line in text.splitlines() if line and not line.startswith('#')]
            assert len(rows)==UNIT_FRAMES
            (V/'master-frames.md5').write_text(text,encoding='utf-8')
            save('master-verification-reuse.json',{'master_sha256':evidence['sha256'],'framehash_source':str(cached),'framehash_sha256':digest(cached),'decoded_frames_reused':len(rows),'reason':'Reuse the completed full-master decode; final opening and clean unit are independently decoded below.'})
            return rows
    args=[FF,'-v','error']
    if start: args+=['-ss',str(start)]
    args+=['-i',str(path),'-t',str(seconds),'-map','0:v:0','-an','-f','framemd5','pipe:1']
    result=run(args).stdout.decode(); (V/(label+'-frames.md5')).write_text(result,encoding='utf-8')
    return [line.rsplit(',',1)[-1].strip() for line in result.splitlines() if line and not line.startswith('#')]

def verify_video():
    assert OUTPUT.exists()
    count=0; tb=None; first=[]; clean=[]
    with (V/'packets-error.log').open('wb') as err, (V/'all-video-packets.sha256').open('wb') as records:
        proc=subprocess.Popen([FF,'-v','error','-i',str(OUTPUT),'-map','0:v:0','-c:v','copy','-f','framehash','-hash','sha256','pipe:1'],stdout=subprocess.PIPE,stderr=err)
        for raw in proc.stdout:
            records.write(raw); line=raw.decode().strip()
            if line.startswith('#tb 0:'):
                n,d=map(int,line.split(':',1)[1].strip().split('/')); tb=n/d
            elif line and not line.startswith('#'):
                fields=[x.strip() for x in line.split(',')]; assert tb is not None
                dts,pts=int(fields[1])*tb,int(fields[2])*tb
                assert abs(pts-count/FPS)<1e-5 and abs(dts-count/FPS)<1e-5,(count,dts,pts)
                if count<UNIT_FRAMES:first.append(fields[5])
                elif count<2*UNIT_FRAMES:clean.append(fields[5])
                else:assert fields[5]==clean[count%UNIT_FRAMES],('clean payload changed',count)
                count+=1
                if count%18000==0:print(f'Video packets/timestamps {count/FPS/60:.0f}/120 minutes',flush=True)
        assert proc.wait()==0 and count==FRAMES
    assert len(clean)==len(first)==UNIT_FRAMES
    print('Comparing decoded master, opening unit and first clean unit',flush=True)
    native=framedigests(VIDEO,0,UNIT,'master')
    branded=framedigests(OUTPUT,0,UNIT,'opening')
    repeated=framedigests(OUTPUT,UNIT,UNIT,'first-clean')
    assert len(native)==len(branded)==len(repeated)==UNIT_FRAMES
    assert repeated==native
    assert branded[660:]==native[660:],'Source pictures changed after opening'
    assert any(a!=b for a,b in zip(branded[:660],native[:660])),'Intro missing'
    q=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(OUTPUT)]).stdout)
    v=next(x for x in q['streams'] if x['codec_type']=='video');a=next(x for x in q['streams'] if x['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'])==(3840,2160,'30/1')
    assert int(v['nb_frames'])==FRAMES and abs(float(q['format']['duration'])-SECONDS)<.04
    assert v['pix_fmt']=='yuv420p' and v['color_range']=='tv'
    assert all(v[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
    assert a['codec_name']=='aac' and int(a['sample_rate'])==48000 and a['channels']==2
    save('video-validation.json',{'status':'passed','frames':count,'all_pts_dts_exact_30fps':True,'clean_120s_units_identical':59,'first_clean_unit_all_decoded_frames_match_master':True,'opening_after22s_all_decoded_frames_match_master':True,'intro_present_once':True,'dimensions':[3840,2160],'fps':FPS,'probe':q})

def expected_audio_graph():
    graph=render.build_audio_graph([.4],0,first_input=0)
    assert '[a0]alimiter=' in graph
    graph=graph.replace('[a0]alimiter=','[a0]afade=t=out:st=7180:d=20:curve=tri[closing];[closing]alimiter=')
    return opening.audio_graph(graph,IntroSettings('Below the Snowline',True))

def verify_audio():
    assert json.loads((H/'audio-preparation-validation.json').read_text())['status']=='passed'
    graph=expected_audio_graph(); count=0; peak=0.; first=0.;sxx=syy=sxy=error=0.; windows=[]
    with (V/'expected-audio.log').open('wb') as e1,(V/'actual-audio.log').open('wb') as e2:
        p=subprocess.Popen([FF,'-v','error','-i',str(SOURCE_AUDIO),'-filter_complex',graph,'-map','[aout]','-t',str(SECONDS),'-ac','2','-ar','48000','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=e1)
        q=subprocess.Popen([FF,'-v','error','-i',str(OUTPUT),'-vn','-t',str(SECONDS),'-ac','2','-ar','48000','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=e2)
        for sec in range(SECONDS):
            ar=p.stdout.read(48000*2*4);br=q.stdout.read(48000*2*4)
            assert len(ar)==len(br)==48000*2*4,(sec,len(ar),len(br))
            a=np.frombuffer(ar,'<f4').astype(np.float64);b=np.frombuffer(br,'<f4').astype(np.float64)
            assert np.isfinite(a).all() and np.isfinite(b).all()
            peak=max(peak,float(np.max(abs(b))));assert peak<1
            if sec<4:first=max(first,float(np.max(abs(b))))
            ax=float(np.sum(a*a));by=float(np.sum(b*b));xy=float(np.sum(a*b))
            sxx+=ax;syy+=by;sxy+=xy;error+=float(np.sum((a-b)**2));count+=48000
            if sec in [4,5,10,15,19,20,180,224,498,7180,7190,7199]:
                local_gain=10*math.log10(max(by,1e-30)/max(ax,1e-30))
                local_corr=xy/math.sqrt(max(ax*by,1e-30))
                if sec>=5:
                    assert abs(local_gain)<.35 and local_corr>.98,(sec,local_gain,local_corr)
                windows.append({'second':sec,'expected_rms':math.sqrt(ax/len(a)),'aac_rms':math.sqrt(by/len(b)),'correlation':local_corr if ax>0 else None,'gain_difference_db':local_gain if ax>0 else None,'reference_silent':ax==0})
            if sec%900==899:print(f'Entire AAC compared {(sec+1)//60}/120 minutes',flush=True)
        assert not p.stdout.read(1) and not q.stdout.read(1)
        assert p.wait()==q.wait()==0 and count==345600000
    corr=sxy/math.sqrt(sxx*syy);gain=10*math.log10(syy/sxx);snr=10*math.log10(sxx/error)
    assert first<1e-6 and corr>.995 and abs(gain)<.15 and snr>25,(first,corr,gain,snr)
    save('audio-validation.json',{'status':'passed','seconds':SECONDS,'sample_frames':count,'all_samples_finite':True,'unclipped':True,'peak_dbfs':20*math.log10(peak),'expected_input':str(SOURCE_AUDIO),'expected_graph':graph,'gain_db_once':.4,'closing_fade_seconds_once':20,'opening_silence_to5_fade_to20_once':True,'first_four_seconds_peak':first,'full_track_correlation':corr,'gain_difference_db':gain,'aac_snr_db':snr,'diagnostic_windows':windows,'note':'Independent comparison to original unfaded master plus gain, closing and actual Colony opening/limiter. No full listening claim.'})

def stills():
    times=[1,6,13,16,19,23,28,48,97,119,120,121]
    sheet=Image.new('RGB',(1280,2340),'#11151b');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        target=H/f'final-still-{t:03}.png'
        if not target.exists():run([FF,'-v','error','-n','-ss',str(t),'-i',str(OUTPUT),'-frames:v','1','-vf','scale=1280:720:flags=lanczos',str(target)])
        im=Image.open(target).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
        x=(i%2)*640;y=(i//2)*390;sheet.paste(im,(x,y));draw.text((x+10,y+365),f'{t}s',fill='#F3EBDD')
    sheet.save(H/'final-contact-sheet.jpg',quality=94)
    save('visual-review.json',{'stills':'final-contact-sheet.jpg','times_seconds':times,'inspection':'Prepared for assistant inspection of opening, charge, flight and repeat boundary; continuous playback not claimed'})

def container_hash():
    before=OUTPUT.stat();h=hashlib.sha256();size=0;mark=0
    with OUTPUT.open('rb') as f:
        for b in iter(lambda:f.read(16*1024**2),b''):
            h.update(b);size+=len(b)
            if size-mark>=8*1024**3:print(f'Final file hash {size/1024**3:.1f}GiB',flush=True);mark=size
    after=OUTPUT.stat();assert before.st_size==after.st_size==size and before.st_mtime_ns==after.st_mtime_ns
    save('container-hash.json',{'path':str(OUTPUT),'bytes':size,'mtime_ns':after.st_mtime_ns,'sha256':h.hexdigest(),'stable_during_read':True})

def finish():
    v=json.loads((H/'video-validation.json').read_text());a=json.loads((H/'audio-validation.json').read_text());c=json.loads((H/'colony-export.json').read_text());m=json.loads((H/'visual/master-validation.json').read_text())
    assert v['status']==a['status']==m['status']=='passed' and c['verification']['full_decode'] and c['verification']['passed']
    h=json.loads((H/'container-hash.json').read_text());st=OUTPUT.stat();assert h['bytes']==st.st_size and h['mtime_ns']==st.st_mtime_ns
    assert digest(VIDEO)==m['sha256']
    assert digest(SOURCE_AUDIO)=='6c46365081e88d55b198387ea0b53259b7a90b12181e279ddb6dc12e8f474257'
    save('delivery-validation.json',{'status':'passed','completed_date':'2026-11-05','started_date':'2026-11-04','output':str(OUTPUT),'bytes':st.st_size,'sha256':h['sha256'],'seconds':SECONDS,'frames':FRAMES,'dimensions':[3840,2160],'fps':FPS,'native_artwork_dimensions':[1672,941],'native_render_then_upscale':'Native scene rendering followed by Lanczos4K; see visual/master-validation.json','colony_full_video_audio_decode':True,'video_validation':'video-validation.json','audio_validation':'audio-validation.json','opening':'Actual Colony v3, Below the Snowline; once, graphics clear by22s, silence to5/fade to20','closing_audio_fade_seconds':20,'clean_units':59,'source_audio_unchanged':True,'approved_visual_basis':'V6 two-minute preview','longform_motion':'Periodic production adaptation described and checked in visual/','full_combined_user_review':'pending','assistant_review':'Technical checks and decoded temporal stills; no continuous playback or full listening','remote_backup':False})
    print('Final two-hour Snowline4K delivery verified',flush=True)

if __name__=='__main__':
    choices=sys.argv[1:]
    if '--video' in choices:verify_video()
    if '--audio' in choices:verify_audio()
    if '--stills' in choices:stills()
    if '--hash' in choices:container_hash()
    if '--finish' in choices:finish()
