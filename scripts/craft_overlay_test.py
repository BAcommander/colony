"""Author rigid sprite motion locally; composite its RGB/matte sequences in ComfyUI."""
import hashlib
import json
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/ringfall/animation/craft-overlay'
INP=ROOT/'.local/ComfyUI/input'
MASTER=ROOT/'creative/ringfall/04-laptop-refined.png'
W,H,FPS,N=1280,720,24,120

def api(path,data=None):
    req=urllib.request.Request('http://127.0.0.1:8188'+path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as response: return json.load(response)

def writer(path):
    return subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error',
        '-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-an','-c:v','ffv1','-pix_fmt','bgr0',str(path)],stdin=subprocess.PIPE)

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    master=Image.open(MASTER).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    master.save(INP/'craft-test-background.png')
    asset=Image.open(OUT/'craft-source.png').convert('RGBA')
    bbox=asset.getchannel('A').getbbox()
    craft=asset.crop(bbox)
    arr=np.array(craft)
    arr[:,:,:3]=np.clip(arr[:,:,:3].astype(float)*np.array([.77,.78,.80]),0,255).astype(np.uint8)
    craft=Image.fromarray(arr)
    # Main window polygon in original source coordinates. The flight path remains
    # above the chair and close terrain; no pretend foreground-depth reconstruction.
    polygon=np.array([[624,35],[1671,0],[1671,574],[1455,541],[1240,510],
                       [1130,485],[1030,480],[970,485],[941,511],[624,505]],float)
    polygon*=np.array([W/1672,H/941])
    window=np.zeros((H,W),np.uint8)
    cv2.fillPoly(window,[np.round(polygon).astype(np.int32)],255)
    # Inset feather prevents edge spill onto the frame.
    window=np.clip(cv2.distanceTransform(window,cv2.DIST_L2,5)/1.5,0,1)
    Image.fromarray((window*255).astype(np.uint8)).save(OUT/'window-occlusion-mask.png')
    rgb_writer=writer(INP/'craft-test-rgb.mkv')
    mask_writer=writer(INP/'craft-test-matte.mkv')
    trajectory=[]
    stills=[]
    union=np.zeros((H,W),bool)
    for i in range(N):
        t=i/(N-1)
        # Constant forward travel. This five-second test is deliberately not looped.
        cx=(530+1080*t)*W/1672
        cy=(365+50*t-15*np.sin(np.pi*t))*H/941
        width=round((190-35*t)*W/1672)
        sprite=craft.resize((width,round(width*craft.height/craft.width)),Image.Resampling.LANCZOS)
        layer=Image.new('RGBA',(W,H))
        xy=(round(cx-width/2),round(cy-sprite.height/2))
        layer.paste(sprite,xy)
        rgba=np.array(layer)
        matte=np.round(rgba[:,:,3]*window).astype(np.uint8)
        rgb_writer.stdin.write(rgba[:,:,:3].tobytes())
        mask_writer.stdin.write(np.repeat(matte[:,:,None],3,axis=2).tobytes())
        union|=matte>0
        trajectory.append({'frame':i,'center':[cx,cy],'width':width,'visible_alpha_pixels':int((matte>0).sum())})
        if i in [0,24,48,72,96,119]:
            a=matte[:,:,None]/255
            composed=np.round(np.array(master)*(1-a)+rgba[:,:,:3]*a).astype(np.uint8)
            preview=cv2.resize(composed,(640,360))
            cv2.putText(preview,f'{i/FPS:.2f}s',(12,24),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1)
            stills.append(preview)
        if i==60: Image.fromarray(matte).save(OUT/'midpoint-matte.png')
    for proc in [rgb_writer,mask_writer]:
        proc.stdin.close()
        if proc.wait(): raise RuntimeError('Lossless element encode failed')
    Image.fromarray(np.concatenate([np.concatenate(stills[j:j+2],axis=1) for j in [0,2,4]],axis=0)).save(OUT/'path-review.jpg')
    Image.fromarray(union.astype(np.uint8)*255).save(OUT/'motion-union.png')
    config={'source_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),
            'asset_sha256':hashlib.sha256((OUT/'craft-source.png').read_bytes()).hexdigest(),
            'source':'creative/ringfall/04-laptop-refined.png','asset_crop':bbox,
            'fps':FPS,'frames':N,'size':[W,H],'duration':N/FPS,'loop':False,
            'asset_rgb_gain':[.77,.78,.80],'window_polygon_preview':polygon.tolist(),
            'trajectory':trajectory,'method':'rigid 2D sprite; native ComfyUI masked batch composite'}
    (OUT/'config.json').write_text(json.dumps(config,indent=2))

def submit():
    def node(kind,**inputs): return {'class_type':kind,'inputs':inputs}
    graph={
      '1':node('LoadImage',image='craft-test-background.png'),
      '2':node('RepeatImageBatch',image=['1',0],amount=N),
      '3':node('LoadVideo',file='craft-test-rgb.mkv'),
      '4':node('GetVideoComponents',video=['3',0]),
      '5':node('LoadVideo',file='craft-test-matte.mkv'),
      '6':node('GetVideoComponents',video=['5',0]),
      '7':node('ImageToMask',image=['6',0],channel='red'),
      '8':node('ImageCompositeMasked',destination=['2',0],source=['4',0],mask=['7',0],x=0,y=0,resize_source=False),
      '9':node('CreateVideo',images=['8',0],fps=float(FPS)),
      '10':node('SaveVideo',video=['9',0],filename_prefix='craft-overlay-test',format='mp4',
                 codec={'codec':'h264','encoding':{'encoding':'re-encode','crf':17}}),
      '11':node('ImageFromBatch',image=['8',0],batch_index=60,length=1),
      '12':node('SaveImage',images=['11',0],filename_prefix='craft-overlay-midpoint'),
    }
    (OUT/'comfy-api.json').write_text(json.dumps(graph,indent=2))
    response=api('/prompt',{'prompt':graph})
    (OUT/'queue.json').write_text(json.dumps(response,indent=2))
    print(response,flush=True)
    pid=response['prompt_id']
    while True:
        hist=api('/history/'+pid)
        if pid in hist:
            result=hist[pid]
            (OUT/'result.json').write_text(json.dumps(result,indent=2))
            print(result['status'],flush=True)
            if result['status']['status_str']!='success': raise RuntimeError('Comfy workflow failed')
            for key,dest in [('10','craft-test-720p.mp4'),('12','comfy-midpoint.png')]:
                item=result['outputs'][key]['images'][0]
                shutil.copy2(ROOT/'creative/ringfall/animation/wan-tests'/item['subfolder']/item['filename'],OUT/dest)
            return
        time.sleep(5)

if __name__=='__main__':
    prepare()
    submit()
