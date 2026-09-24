"""Prepare a protected planet crop and composite a local Wan motion candidate."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'creative/ringfall/animation/planet-pass'
SOURCE = ROOT / 'creative/ringfall/04-laptop-refined.png'
CROP = [900, 80, 1412, 400]

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    src = np.array(Image.open(SOURCE).convert('RGB'))
    conf = json.loads((ROOT / 'creative/ringfall/animation/scene-v6.json').read_text())['planet']
    mask = np.zeros(src.shape[:2], np.uint8)
    cv2.fillPoly(mask, [np.array(conf['surface_polygon'])], 255)
    protected = np.zeros_like(mask)
    cv2.fillPoly(protected, [np.array(conf['protected_rings_polygon'])], 255)
    protected = cv2.dilate(protected, np.ones((9,9),np.uint8))
    mask[protected>0] = 0
    _,labels,stats,_=cv2.connectedComponentsWithStats(mask)
    mask=(labels==(1+np.argmax(stats[1:,cv2.CC_STAT_AREA]))).astype(np.uint8)*255
    distance = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    alpha = np.clip((distance-3)/10,0,1)
    Image.fromarray((alpha*255).astype(np.uint8)).save(OUT/'atmosphere-mask.png')
    x0,y0,x1,y1=CROP
    Image.fromarray(src[y0:y1,x0:x1]).resize((768,480),Image.Resampling.LANCZOS).save(OUT/'planet-input.png')
    overlay=src.copy()
    overlay[alpha>0] = (overlay[alpha>0]*0.5 + np.array([40,230,100])*0.5).astype(np.uint8)
    Image.fromarray(overlay[y0:y1,x0:x1]).resize((1024,640)).save(OUT/'mask-review.png')
    brief=(ROOT/'creative/ringfall/animation/next-planet-pass-prompt.md').read_text(encoding='utf8')
    pos=brief.split('## Positive prompt for Wan — planet crop only')[1].split('## Negative prompt')[0].strip()
    neg=brief.split('## Negative prompt')[1].split('## Important boundary')[0].strip()
    (OUT/'positive.txt').write_text(pos,encoding='utf8')
    (OUT/'negative.txt').write_text(neg,encoding='utf8')
    cfg={'source':str(SOURCE.relative_to(ROOT)), 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'crop_xyxy':CROP,'generation_size':[768,480],'scale':1.5,'padding':0,
         'mask_method':'v6 polygons, rings dilated 4px, inner distance feather 3..13px',
         'active_pixels':int((alpha>0).sum()),'registration':'none; reject significant generated drift'}
    (OUT/'config.json').write_text(json.dumps(cfg,indent=2))

def encoder(path,size):
    return subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error',
        '-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','24','-i','-',
        '-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)

def composite(video):
    src=np.array(Image.open(SOURCE).convert('RGB'))
    alpha=np.array(Image.open(OUT/'atmosphere-mask.png')).astype(np.float32)/255
    x0,y0,x1,y1=CROP
    a=alpha[y0:y1,x0:x1,None]
    cap=cv2.VideoCapture(str(video)); count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    stem=video.stem
    preview=encoder(OUT/f'{stem}-preview.mp4',(1280,720))
    comparison=encoder(OUT/f'{stem}-comparison.mp4',(1920,540))
    original=cv2.resize(src,(960,540),interpolation=cv2.INTER_AREA)
    snapshots=[]; change=[]; outside_max=0
    for i in range(count):
        ok,frame=cap.read()
        if not ok: raise RuntimeError('Incomplete video')
        patch=cv2.resize(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)
        result=src.copy()
        result[y0:y1,x0:x1]=np.round(src[y0:y1,x0:x1]*(1-a)+patch*a).astype(np.uint8)
        outside_max=max(outside_max,int(np.abs(result.astype(np.int16)-src)[alpha==0].max()))
        change.append(float(np.abs(result.astype(float)-src)[alpha>0].mean()))
        preview.stdin.write(cv2.resize(result,(1280,720),interpolation=cv2.INTER_AREA).tobytes())
        joined=np.concatenate([original,cv2.resize(result,(960,540),interpolation=cv2.INTER_AREA)],axis=1)
        cv2.putText(joined,'ORIGINAL',(20,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),1)
        cv2.putText(joined,'PLANET MOTION TEST',(980,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),1)
        comparison.stdin.write(joined.tobytes())
        if i in [0,count//4,count//2,3*count//4,count-1]:
            snapshots.append(Image.fromarray(result[y0:y1,x0:x1]))
    for proc in [preview,comparison]:
        proc.stdin.close()
        if proc.wait(): raise RuntimeError('Encoding failed')
    sheet=Image.new('RGB',(512*len(snapshots),320))
    for i,snapshot in enumerate(snapshots): sheet.paste(snapshot,(512*i,0))
    sheet.save(OUT/f'{stem}-samples.jpg')
    report={'frames':count,'fps':24,'duration_seconds':count/24,'outside_mask_max_difference_pre_encode':outside_max,
            'masked_mean_absolute_source_difference':change,'loop_claim':False,'artistic_review':'pending',
            'raw_video':str(video),'preview':f'{stem}-preview.mp4','comparison':f'{stem}-comparison.mp4'}
    (OUT/f'{stem}-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='masked_mean_absolute_source_difference'}))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--video',type=Path); args=p.parse_args()
    if args.video: composite(args.video)
    else: prepare()
