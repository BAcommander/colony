"""Validate the ComfyUI export and create a side-by-side review video."""
import json
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/ringfall/animation/craft-overlay'
bg=np.array(Image.open(ROOT/'.local/ComfyUI/input/craft-test-background.png').convert('RGB'))
mid=np.array(Image.open(OUT/'comfy-midpoint.png').convert('RGB'))
matte=np.array(Image.open(OUT/'midpoint-matte.png'))
outside=np.abs(mid.astype(np.int16)-bg.astype(np.int16))[matte==0]
cap=cv2.VideoCapture(str(OUT/'craft-test-720p.mp4'))
fps=cap.get(cv2.CAP_PROP_FPS)
size=[int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error',
    '-f','rawvideo','-pix_fmt','rgb24','-s','1920x540','-r',str(fps),'-i','-',
    '-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',
    str(OUT/'craft-test-comparison.mp4')],stdin=subprocess.PIPE)
original=cv2.resize(bg,(960,540),interpolation=cv2.INTER_AREA)
count=0
while True:
    ok,bgr=cap.read()
    if not ok: break
    rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    comp=np.concatenate([original,cv2.resize(rgb,(960,540),interpolation=cv2.INTER_AREA)],axis=1)
    cv2.putText(comp,'ORIGINAL',(20,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),1)
    cv2.putText(comp,'INDEPENDENT CRAFT OVERLAY',(980,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),1)
    proc.stdin.write(comp.tobytes())
    if count==60: Image.fromarray(rgb).save(OUT/'decoded-midpoint.jpg')
    count+=1
proc.stdin.close()
assert proc.wait()==0
assert count==120 and fps==24 and size==[1280,720]
assert int(outside.max())==0,'Comfy PNG differs outside overlay matte'
report={'frames':count,'fps':fps,'size':size,'duration_seconds':count/fps,
        'lossless_comfy_midpoint_max_change_outside_matte':int(outside.max()),
        'source_unchanged':True,'silent':True,'loop':False,
        'review':'Six path samples, actual lossless Comfy midpoint and decoded MP4 midpoint; no continuous playback review.',
        'limits':'Rigid 2D cutout; no changing perspective, cast shadow or glass reflection. User artistic review pending.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
