"""Make a two-repeat review file and verify every decoded repeated frame."""
import hashlib,json,subprocess
from pathlib import Path
import cv2,imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/glacier-sanctuary/animation/final-v11'

def frames(path):
    cap=cv2.VideoCapture(str(path));result=[]
    while True:
        ok,frame=cap.read()
        if not ok:break
        result.append(hashlib.sha256(frame.tobytes()).hexdigest())
    cap.release()
    return result

def main():
    src=OUT/'glacier-sanctuary-v11-60s-720p.mp4'
    dst=OUT/'glacier-sanctuary-v11-two-loop-check-720p.mp4'
    assert src.exists() and not dst.exists()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-n',
        '-stream_loop','1','-i',str(src),'-map','0:v:0','-an','-c','copy','-t','120',
        '-movflags','+faststart',str(dst)],check=True)
    original=frames(src);repeated=frames(dst)
    assert len(original)==1800 and len(repeated)==3600
    assert repeated==original*2
    report={'path':dst.relative_to(ROOT).as_posix(),'decoded_frames':len(repeated),
        'duration_seconds':120,'unique_timeline_seconds':60,'join_at_seconds':60,
        'decoded_repetitions_identical':True,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
        'bytes':dst.stat().st_size,'inspection':'All decoded frame hashes compared; no continuous visual playback claimed'}
    (OUT/'repeat-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
