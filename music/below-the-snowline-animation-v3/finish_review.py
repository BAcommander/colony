"""Assemble and verify the Snowline V3 two-minute review."""
from pathlib import Path
import subprocess,json,hashlib,math
import numpy as np
import cv2
from PIL import Image
import render_v3 as renderer
H=Path(__file__).resolve().parent
OUT=H/'Below-the-Snowline-v3-with-V6-audio-2min.mp4'

def run(cmd):subprocess.run(cmd,check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],text=True))
def audio(p):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-acodec','pcm_f32le','-f','f32le','-'])
    return np.frombuffer(raw,'<f4').reshape(-1,2)

def main():
    parts=[H/'cache'/f'part-{i:02}.mp4' for i in range(6)]
    for p in parts:
        q=probe(p);assert abs(float(q['format']['duration'])-20)<1e-6
    playlist=H/'cache/concat.txt'
    playlist.write_text(''.join("file '"+p.as_posix()+"'\n" for p in parts),encoding='utf-8')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(playlist),'-i',str(H/'Snowline-V6-review-audio-2min.flac'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-bsf:v','h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','256k','-t','120','-movflags','+faststart',str(OUT)]
    run(cmd)
    q=probe(OUT);v=next(s for s in q['streams'] if s['codec_type']=='video');a=next(s for s in q['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1')
    assert v['color_space']=='bt709' and v['color_transfer']=='bt709' and v['color_primaries']=='bt709'
    assert abs(float(q['format']['duration'])-120)<.001 and a['sample_rate']=='48000' and a['channels']==2
    stamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(OUT)],text=True))
    ts=np.array([float(x['best_effort_timestamp_time']) for x in stamps['frames']]);assert len(ts)==3600 and np.max(np.abs(ts-np.arange(3600)/30))<1e-5
    scene=renderer.Scene();protected=scene.full_active<1e-6
    for t in [0,10,24.5,35,48,72,96,119.9]:
        native=scene.frame(t);assert np.array_equal(native[protected],scene.base[protected])
    # Decode every picture; compare continuous motion at worker/chunk joins.
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(OUT),'-map','0:v:0','-vf','scale=in_color_matrix=bt709:out_range=pc,format=rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
    samples={0:0,1050:35,1440:48,2160:72,2880:96,3599:3599/30};metrics={};previous=None;steps=[];roi_steps=[]
    i=0
    while True:
        raw=proc.stdout.read(1280*720*3)
        if not raw:break
        assert len(raw)==1280*720*3
        frame=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
        if previous is not None:
            delta=cv2.absdiff(frame,previous);steps.append(float(delta.mean()))
            roi_steps.append([float(delta[10:570,285:1260].mean()),float(delta[180:490,:170].mean()),float(delta[290:340,600:1100].mean())])
        if i in samples:
            Image.fromarray(frame).save(H/f'decoded-{i:04}.png')
            expected=scene.frame(samples[i]);diff=frame.astype(np.float32)-expected
            psnr=10*math.log10(255**2/max(1e-9,float((diff**2).mean())))
            assert psnr>34,(i,psnr)
            metrics[str(i)]={'native_to_decoded_psnr_db':psnr,'mean_absolute_error':float(np.abs(diff).mean())}
        previous=frame.copy();i+=1
    assert proc.wait()==0 and i==3600
    steps=np.array(steps);roi_steps=np.array(roi_steps);joins=[]
    for frame in range(600,3600,600):
        at=frame-1;neighbours=np.r_[steps[at-15:at],steps[at+1:at+16]]
        ratio=float(steps[at]/max(.001,neighbours.max()))
        assert ratio<1.6,(frame,ratio)
        regions=[]
        for k,name in enumerate(['exterior','controls','bridge']):
            near=np.r_[roi_steps[at-15:at,k],roi_steps[at+1:at+16,k]]
            assert roi_steps[at,k]<=max(near.max()*1.8+.03,.06),(frame,name)
            regions.append({'region':name,'join_mae':float(roi_steps[at,k]),'nearby_max_mae':float(near.max())})
        joins.append({'frame':frame,'join_vs_neighbour_max':ratio,'regions':regions})
    expected=audio(H/'Snowline-V6-review-audio-2min.flac');actual=audio(OUT)
    assert len(expected)==5760000 and len(actual)>=len(expected)
    actual=actual[:len(expected)];assert np.isfinite(actual).all() and np.max(np.abs(actual))<1
    err=actual.astype(np.float64)-expected
    snr=float(10*np.log10(np.sum(expected.astype(np.float64)**2)/np.sum(err**2)))
    corr=float(np.corrcoef(expected.ravel(),actual.ravel())[0,1]);assert corr>.995 and snr>22,(snr,corr)
    report={'video':OUT.name,'sha256':renderer.digest(OUT),'bytes':OUT.stat().st_size,'seconds':120,'decoded_frames':i,'timestamps_passed':True,'bt709':True,'protected_pixels_unchanged_at_checked_times':True,'native_picture_checks':metrics,'segment_joins':joins,'audio':{'source_master':'exports/13-below-the-snowline/audio-2h-v6/Below-the-Snowline-2-Hours-unfaded-master-v6.flac','source_start_seconds':180,'source_end_seconds':300,'gain_db':.4,'preview_fades_seconds':[.5,2],'all_six_layers_already_in_master':True,'decoded_expected_frames':len(expected),'aac_correlation':corr,'aac_snr_db':snr,'peak_linear':float(np.max(np.abs(actual)))},'review':'Decoded/temporal stills and technical checks; no continuous playback or listening verdict; new motion pending user review','loop_status':'Continuous 120 seconds; not a final seamless-loop claim','fingerprints':{n:renderer.digest(H/n) for n in ['source.png','v2-scene.json','render_v3.py','events.json','Snowline-V6-review-audio-2min.flac']}}
    renderer.save('delivery-validation.json',report)
    print(json.dumps({'path':str(OUT),'frames':i,'audio_snr_db':snr,'audio_correlation':corr,'checks':'passed'}),flush=True)

if __name__=='__main__':main()
