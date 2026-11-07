"""Place the new audio audition over two unchanged copies of the existing V5 minute."""
from build_mix import H,R,C,FF,sha,run,save,validate
from pathlib import Path
import json,shutil

def packets(path):
    data=run([FF,'-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','framehash','-hash','sha256','pipe:1']).stdout.decode()
    rows=[];tb=None
    for line in data.splitlines():
        if line.startswith('#tb 0:'):
            a,b=map(int,line.split(':',1)[1].strip().split('/'));tb=a/b
        elif line and not line.startswith('#'):
            x=[y.strip() for y in line.split(',')];rows.append({'pts':int(x[2])*tb,'hash':x[5]})
    return rows

def main():
    d=json.loads((H/'delivery-validation.json').read_text(encoding='utf-8'));assert d['status']=='passed'
    source=R/'music/crater-rim-animation-v5/Crater-Rim-Survey-v5-60s-loop.mp4'
    before=sha(source)
    raw=C/'Crater-Rim-music-wind-room-air-check-2min-v1.f32'
    out=H/'review/Crater-Rim-V5-with-music-and-SFX-2min-v1.mp4'
    run([FF,'-v','error','-xerror','-n','-stream_loop','1','-i',str(source),'-f','f32le','-ar','48000','-ac','2','-i',str(raw),
         '-map','0:v:0','-map','1:a:0','-t','120','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)])
    original=packets(source);actual=packets(out)
    assert len(original)==1800 and len(actual)==3600
    assert all(row['hash']==original[i%1800]['hash'] and abs(row['pts']-i/30)<1e-5 for i,row in enumerate(actual))
    run([FF,'-v','error','-xerror','-err_detect','explode','-i',str(out),'-f','null','-'])
    audio=validate(out,raw,120,False)
    assert sha(source)==before
    save(H/'scene-review-validation.json',{'status':'passed','output':str(out),'bytes':out.stat().st_size,'sha256':sha(out),
         'seconds':120,'frames':3600,'dimensions':[1280,720],'fps':30,'video_source':str(source),'video_source_sha256':before,
         'all_video_packets_identical_to_two_source_copies':True,'all_timestamps_checked':True,'full_decode':True,'audio':audio,
         'full_hour_audio_window_seconds':[20,140],'review_only_fades_seconds':[.5,2],
         'wind_enters_review_at_seconds':25,'first_wind_ends_review_at_seconds':90,
         'scope':'Existing V5 visual minute repeated for sound-balance audition. No new long animation, opening or final video export.',
         'assistant_continuous_playback_or_listening':False,'user_review':'pending'})
    print('Two-minute in-scene audio check passed: unchanged V5 video packets, full decode and AAC comparison.',flush=True)

if __name__=='__main__':main()
