"""Render a quiet, silent ten-second channel graphic. No generated image edits."""
import argparse,hashlib,json,math,subprocess
from pathlib import Path
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,COUNT=3840,2160,30,300
IVORY='#F3EBDD';AMBER='#E7A83E';PANEL='#141B21'
FONT=ROOT/'creative/brand/fonts'

def smooth(x):
    x=max(0,min(1,x));return x*x*x*(x*(x*6-15)+10)

def lettering(draw,xy,text,font,fill,spacing=0):
    x,y=xy
    for char in text:
        draw.text((x,y),char,font=font,fill=fill,anchor='lt')
        x+=draw.textlength(char,font=font)+spacing

def card(t):
    # Native graphics on a transparent canvas, drawn at delivery resolution.
    s=2;im=Image.new('RGBA',(1120*s,156*s));d=ImageDraw.Draw(im)
    d.rounded_rectangle((1,1,2238,310),radius=32,fill=PANEL,outline='#475058',width=2)
    d.rounded_rectangle((2,76,8,236),radius=3,fill=AMBER)
    d.ellipse((78,78,234,234),outline=IVORY,width=5)
    angle=-math.pi/4+max(0,min(7.4,t-1.4))*.09
    cx=156+78*math.cos(angle);cy=156+78*math.sin(angle)
    d.ellipse((cx-11,cy-11,cx+11,cy+11),fill=IVORY)
    d.line((288,84,288,228),fill=AMBER,width=5)
    title=ImageFont.truetype(str(FONT/'BarlowCondensed-SemiBold.ttf'),92)
    body=ImageFont.truetype(str(FONT/'BarlowCondensed-Regular.ttf'),58)
    button=ImageFont.truetype(str(FONT/'BarlowCondensed-SemiBold.ttf'),66)
    lettering(d,(348,69),'AMBIENT COLONY',title,IVORY,4)
    d.text((350,184),'Stay a while and listen.',font=body,fill='#C6C5C1',anchor='lt')
    d.rounded_rectangle((1630,94,2144,220),radius=16,fill=AMBER)
    d.text((1868,155),'SUBSCRIBE',font=button,fill=PANEL,anchor='mm')
    d.line((2075,143,2088,156,2075,169),fill=PANEL,width=4)
    return im

def overlay(t):
    im=Image.new('RGBA',(W,H))
    if t<.4 or t>=9.8:return im
    enter=smooth((t-.4)/1.0);leave=smooth((t-8.8)/1.0)
    y=round(1664+(1-enter)*530+leave*530)
    im.alpha_composite(card(t),(800,y))
    return im

def pipe(path,alpha):
    codec=['-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-alpha_bits','16','-threads','8'] if alpha else ['-c:v','libx264','-preset','medium','-crf','10','-pix_fmt','yuv420p','-movflags','+faststart']
    return subprocess.Popen([FF,'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgba' if alpha else 'rgb24','-s','3840x2160','-r','30','-i','-','-an',*codec,str(path)],stdin=subprocess.PIPE)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='final/channel-assets/subscribe-v1');p.add_argument('--still-only',action='store_true');a=p.parse_args()
    out=ROOT/a.output;out.mkdir(parents=True,exist_ok=True)
    plate=Image.open(ROOT/'creative/ringfall/04-laptop-refined.png').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
    sample=overlay(4);sample.save(out/'subscribe-v1-still.png')
    plate.alpha_composite(sample);plate.convert('RGB').resize((1280,720),Image.Resampling.LANCZOS).save(out/'preview-still.jpg',quality=94)
    if a.still_only:return
    alpha=out/'subscribe-v1-10s-4k-alpha.mov';green=out/'subscribe-v1-10s-4k-green.mp4';preview=out/'subscribe-v1-preview.mp4'
    assert not any(x.exists() for x in [alpha,green,preview])
    ap=pipe(alpha,True);gp=pipe(green,False)
    try:
        for i in range(COUNT):
            frame=overlay(i/FPS);ap.stdin.write(frame.tobytes())
            keyed=Image.new('RGB',(W,H),(0,255,0));keyed.paste(frame,mask=frame.getchannel('A'));gp.stdin.write(keyed.tobytes())
            if i%60==0:print(f'Rendered {i}/300',flush=True)
    finally:ap.stdin.close();gp.stdin.close()
    assert ap.wait()==0 and gp.wait()==0
    # Preview uses actual accepted Ringfall footage; neither source master is edited.
    subprocess.run([FF,'-hide_banner','-loglevel','error','-n','-i',str(ROOT/'final/01-ringfall-observatory/video-4k.mp4'),'-i',str(alpha),'-filter_complex','[0:v][1:v]overlay=0:0:shortest=1,scale=1280:720:flags=lanczos[v]','-map','[v]','-an','-t','10','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(preview)],check=True)
    outputs=[]
    for path,size in [(alpha,(W,H)),(green,(W,H)),(preview,(1280,720))]:
        cap=cv2.VideoCapture(str(path));assert cap.get(cv2.CAP_PROP_FPS)==30
        n=0
        while True:
            ok,f=cap.read()
            if not ok:break
            assert f.shape[:2]==(size[1],size[0]);n+=1
        cap.release();assert n==COUNT
        probe=subprocess.run([FF,'-hide_banner','-i',str(path)],capture_output=True,text=True).stderr
        assert 'Audio:' not in probe and 'Video:' in probe
        outputs.append({'file':path.name,'dimensions':list(size),'fps':30,'frames':n,'seconds':10,'audio_stream':False,'bytes':path.stat().st_size,'sha256':sha(path)})
    # Decode alpha separately: endpoints empty, exterior transparent, panel opaque.
    alpha_checks=[]
    for t in [0,4,299/30]:
        raw=subprocess.check_output([FF,'-hide_banner','-loglevel','error','-ss',str(t),'-i',str(alpha),'-frames:v','1','-vf','alphaextract','-pix_fmt','gray','-f','rawvideo','-'])
        aa=np.frombuffer(raw,np.uint8).reshape(H,W)
        if t==4:assert aa[1800,1000]>=254 and aa[0,0]==0 and aa.min()==0
        else:assert aa.max()==0
        alpha_checks.append({'time':t,'min':int(aa.min()),'max':int(aa.max())})
    report={'status':'v1 rendered and technically checked; user visual review pending','outputs':outputs,'alpha_checks':alpha_checks,'timing':{'blank_start':[0,.4],'entrance':[.4,1.4],'hold':[1.4,8.8],'exit':[8.8,9.8],'blank_end':[9.8,10]},'green_rgb':[0,255,0],'alpha':'straight alpha, ProRes 4444','renderer':'scripts/render_subscribe_banner.py','renderer_sha256':sha(Path(__file__)),'inspection':'Full decode/count/no-audio/alpha checks and sampled stills; no continuous assistant playback claim','font':'Barlow Condensed, SIL OFL, bundled under creative/brand/fonts'}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
