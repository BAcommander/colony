"""Stream the approved two-track recipe into an exact two-hour audio delivery."""
from pathlib import Path
import subprocess,sys,json,hashlib,time
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import numpy as np
H=Path(__file__).resolve().parent
RATE=48000;SECONDS=7200;N=RATE*SECONDS;OVERLAP=8*RATE;CLOSING=20*RATE
ASOURCE=H.parent/'illuminated-horizon-slow-middle-v1'/'source-original.mp4'
BSOURCE=H.parent/'illuminated-stillness-long-v1'/'source-original.mp4'
REVIEW=H.parent/'illuminated-stillness-long-v1'/'delivery-review.json'
FLAC=H/'Illuminated-Horizon-and-Stillness-2-Hours-v1.flac'
MP3=H/'Illuminated-Horizon-and-Stillness-2-Hours-v1.mp3'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def decode(path):
    r=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn','-ar',str(RATE),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return np.frombuffer(r.stdout,dtype='<f4').reshape(-1,2).copy()
def prepare():
    review=json.loads(REVIEW.read_text())
    assert digest(ASOURCE)==review['original_sha256'] and digest(BSOURCE)==review['source_sha256']
    a=decode(ASOURCE);b=decode(BSOURCE)
    assert len(a)==510*RATE and len(b)==180*RATE
    ga=review['fixed_gain_db']['horizon'];gb=review['fixed_gain_db']['stillness']
    assert ga==-7.74 and gb==-7.08 and review['fixed_gain_db']['shared_headroom']==0
    a*=10**(ga/20);b*=10**(gb/20)
    t=np.linspace(0,np.pi/2,OVERLAP)
    ab=(a[-OVERLAP:]*np.cos(t)[:,None]+b[:OVERLAP]*np.sin(t)[:,None]).astype('<f4')
    ba=(b[-OVERLAP:]*np.cos(t)[:,None]+a[:OVERLAP]*np.sin(t)[:,None]).astype('<f4')
    # Each join uses precisely the same native recipe and gains as the accepted reviews.
    assert np.isfinite(ab).all() and np.isfinite(ba).all()
    pieces=[];tracks=[];joins=[];position=0
    def add(samples,kind,source_start):
        nonlocal position
        length=min(len(samples),N-position)
        if length<=0:return
        pieces.append({'start':position,'end':position+length,'samples':samples[:length],'kind':kind,'source_start_frame':source_start})
        position+=length
    add(a[:-OVERLAP],'Horizon',0)
    tracks.append({'track':'Illuminated Horizon','start_seconds':0,'source_duration_seconds':510})
    counter=0
    while position<N:
        incoming='Illuminated Stillness' if counter%2==0 else 'Illuminated Horizon'
        join=ab if counter%2==0 else ba
        current=b if counter%2==0 else a
        start=position
        joins.append({'from':'Illuminated Horizon' if counter%2==0 else 'Illuminated Stillness','to':incoming,'start_seconds':start/RATE,'end_seconds':min(start+OVERLAP,N)/RATE,'duration_seconds':min(OVERLAP,N-start)/RATE})
        tracks.append({'track':incoming,'start_seconds':start/RATE,'source_duration_seconds':len(current)/RATE})
        add(join,'A-to-B' if counter%2==0 else 'B-to-A',0)
        add(current[OVERLAP:-OVERLAP],incoming,OVERLAP)
        counter+=1
    assert position==N and len(tracks)==21 and len(joins)==20
    assert tracks[-1]['track']=='Illuminated Horizon' and tracks[-1]['start_seconds']==6740
    return a,b,pieces,tracks,joins
def chunks(pieces):
    for piece in pieces:
        for i in range(0,len(piece['samples']),RATE):
            offset=piece['start']+i
            chunk=piece['samples'][i:i+RATE].copy()
            if offset+len(chunk)>N-CLOSING:
                u=np.clip((np.arange(offset,offset+len(chunk))-(N-CLOSING))/(CLOSING-1),0,1)
                chunk*=((1+np.cos(np.pi*u))/2)[:,None]
            yield offset,chunk.astype('<f4',copy=False)
def main():
    assert not FLAC.exists() and not MP3.exists(),'Use a new version; keep previous delivery'
    began=time.time();a,b,pieces,tracks,joins=prepare()
    recipe={'date':'2026-10-25','user_request':'yeah those transitions sound good, can we make an 2-hour long version alternating between illuminated horizon and illuminated stillness?','approval_scope':'Both 45-second transition previews accepted; two-hour A/B audio requested. Full-length listening and final video remain separate.','sources':{'horizon':{'path':str(ASOURCE),'sha256':digest(ASOURCE),'audio_seconds':510},'stillness':{'path':str(BSOURCE),'sha256':digest(BSOURCE),'audio_seconds':180}},'accepted_review_record':{'path':str(REVIEW),'sha256':digest(REVIEW)},'sample_rate':RATE,'channels':2,'duration_seconds':SECONDS,'sample_frames':N,'gains_db':{'horizon':-7.74,'stillness':-7.08},'overlap_seconds':8,'overlap_curve':'outgoing cos / incoming sin, endpoints inclusive, matching accepted native review recipe','cycle_interval_seconds':674,'source_occurrences':{'horizon':11,'stillness':10},'tracks':tracks,'joins':joins,'end_treatment':{'last_track_start_seconds':6740,'last_track_source_used_seconds':460,'closing_fade_seconds':20,'closing_fade_curve':'half cosine, unity at 1:59:40, zero at final sample'},'opening':'No extra opening fade baked in. Apply once-only 0:05–0:20 entrance during later Colony video assembly. Original source entrance remains.','unchanged':'Source tempo, pitch, musical material and existing internal/source fades retained. No EQ, separation, synthetic pads, SFX or dynamic normalization.','outputs':[FLAC.name,MP3.name],'scope':'Audio-only local delivery. No new generation/spend, final video, commit or push.'}
    save('mix-recipe.json',recipe)
    (H/'track-timeline.tsv').write_text('start_seconds\ttrack\n'+''.join(f"{r['start_seconds']:.3f}\t{r['track']}\n" for r in tracks),encoding='utf-8')
    cmd=['ffmpeg','-hide_banner','-nostats','-v','warning','-n','-f','f32le','-ar',str(RATE),'-ac','2','-i','pipe:0','-map','0:a:0','-c:a','flac','-compression_level','5','-sample_fmt','s32','-bits_per_raw_sample','24',str(FLAC),'-map','0:a:0','-c:a','libmp3lame','-b:a','320k',str(MP3)]
    maximum=0.0;count=0
    with (H/'encode.log').open('wb') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
        try:
            for offset,chunk in chunks(pieces):
                maximum=max(maximum,float(np.max(abs(chunk))));assert np.isfinite(chunk).all() and maximum<1
                p.stdin.write(chunk.tobytes());count+=len(chunk)
                if count//(600*RATE)!=(count-len(chunk))//(600*RATE):print(f'Encoded input {count/RATE/60:.0f}/120 minutes',flush=True)
            p.stdin.close();code=p.wait()
            assert code==0 and count==N,code
        except BaseException:
            p.kill();p.wait();raise
    save('encode-result.json',{'sample_frames_sent':count,'input_peak_dbfs':20*np.log10(maximum),'encode_seconds':time.time()-began,'output_files':{q.name:{'bytes':q.stat().st_size,'sha256':digest(q)} for q in [FLAC,MP3]},'full_decode_validation':'Pending verify_delivery.py; encode completion alone is not final verification'})
    print('Encoding complete; full delivery verification next.',flush=True)
if __name__=='__main__':main()
