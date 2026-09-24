"""V9: vent exhaust, scheduled existing windows, tangential ring material."""
import argparse,json,hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
import render_ringfall as core
from render_ringfall_v7 import AmbientRingfall
from render_ringfall_v8 import ExtendedRingfall

class ColonyRingfall(ExtendedRingfall):
    def __init__(self):
        super().__init__()
        self.lamps=[] # Replace inherited additive breathing windows with real states.
        self.effect_descriptions.pop('distance',None)
        self.effect_descriptions['colony']='Two surface light pools, scheduled windows and mast beacon'
        self.vents=[(1336,433,68,20,0.0),(1508,433,48,14,2.1)]
        self.windows=[(1276,452,4,6,1,6),(1327,448,3,7,7,6),
                      (1376,449,7,7,11,5),(1497,455,3,7,16,6)]
        for x,y,h,w,p in self.vents:self.active[y-h-3:y+1,x-w*2:x+w*2+1]=True
        for x,y,rx,ry,s,d in self.windows:self.active[y-ry-5:y+ry+6,x-rx-6:x+rx+7]=True
        dx=self.rx-1060;dy=self.ry-280
        u=.94*dx-.342*dy;v=.342*dx+.94*dy
        self.theta=np.arctan2(v/85,u/640)
        self.radius=np.sqrt((u/640)**2+(v/85)**2)
        self.effect_descriptions.update(exhaust='Two directed expanding vapor plumes at existing roof vents',
          windows='Four existing windows with staggered off holds and local spill reduction',
          rings='Coherent angular material field transported through fixed band mask; artistic speed')

    def frame(self,t,output_size=True):
        p=self.phase(t)
        f=AmbientRingfall.frame(self,t,False)
        x0,y0,x1,y1=self.ring_box
        # Two-scale angular texture travels forward along elliptical material coordinates.
        q=13*self.theta-p*2+9*self.radius
        texture=.20*np.sin(q)+.10*np.sin(2*q+5*self.radius)+.045*np.cos(5*q-7*self.radius)
        patch=self.base[y0:y1,x0:x1].astype(float)
        f[y0:y1,x0:x1]=np.uint8(np.rint(np.clip(patch*(1+self.ring_mask[...,None]*texture[...,None]),0,255)))
        for x,y,rx,ry,start,duration in self.windows:
            xa,xb=x-rx-6,x+rx+7;ya,yb=y-ry-5,y+ry+6
            yy,xx=np.mgrid[ya:yb,xa:xb]
            age=(t%20-start)%20
            a=np.clip(age/.45,0,1);b=np.clip((duration-age)/.45,0,1)
            off=(a*a*(3-2*a))*(b*b*(3-2*b))
            aperture=np.exp(-.5*(((xx-x)/rx)**6+((yy-y)/ry)**6))
            spill=np.exp(-.5*(((xx-x)/(rx+3))**2+((yy-y)/(ry+3))**2))
            patch=f[ya:yb,xa:xb].astype(float)
            # Preserve dark frames and wall details while suppressing original emission.
            warm=np.clip((patch[:,:,0]-patch[:,:,2]-12)/55,0,1)
            mask=off*np.clip(.98*aperture+.15*spill*warm,0,.99)
            dark=np.minimum(patch,np.array([43,36,29]))
            f[ya:yb,xa:xb]=np.uint8(np.rint(patch*(1-mask[...,None])+dark*mask[...,None]))
        for x,y,height,width,offset in self.vents:
            xa,xb=x-width*2,x+width*2+1;ya,yb=y-height-3,y+1
            yy,xx=np.mgrid[ya:yb,xa:xb].astype(float)
            h=(y-yy)/height
            density=np.zeros_like(h)
            for j in range(3):
                flow=18*h-3*p+offset+j*1.7
                center=x+h*(3*np.sin(flow)+2*np.sin(31*h-5*p+j))+ (j-1)*h*width*.25
                spread=1.0+width*h*.40
                ribbon=np.exp(-.5*((xx-center)/spread)**2)
                detail=.55+.27*np.sin(29*h-5*p+offset+j)+.18*np.cos(49*h-7*p+(xx-x)*.25+j)
                density+=ribbon*np.maximum(detail,0)*.32
            env=np.maximum(0,np.sin(np.pi*np.clip(h,0,1)))**.8
            density*=env*np.clip(h*30,0,1)*(h<1)*(h>0)
            density*=np.clip((xx-xa)/5,0,1)*np.clip((xb-1-xx)/5,0,1)
            alpha=np.clip(cv2.GaussianBlur(density,(0,0),.65),0,.55)
            patch=f[ya:yb,xa:xb].astype(float)
            color=np.array([184,180,169])
            f[ya:yb,xa:xb]=np.uint8(np.rint(patch*(1-alpha[...,None])+color*alpha[...,None]))
        return cv2.resize(f,core.SIZE,interpolation=cv2.INTER_LANCZOS4) if output_size else f

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['preview','final'],default='preview');parser.add_argument('--qa-only',action='store_true');a=parser.parse_args()
    core.DURATION=20;core.SIZE=(1280,720) if a.stage=='preview' else (3840,2160);core.STEM='ringfall-ambient-v9b-20s-'+a.stage
    anim=ColonyRingfall()
    sheet=Image.new('RGB',(1280,1080))
    for i,t in enumerate([0,2,5,9,13,17]):
        im=Image.fromarray(anim.frame(t,False)).resize((640,360));ImageDraw.Draw(im).text((10,10),str(t)+'s',fill='white');sheet.paste(im,((i%2)*640,(i//2)*360))
    sheet.save(core.OUTPUT/(core.STEM+'-review.jpg'))
    Image.fromarray(anim.frame(5)).save(core.OUTPUT/(core.STEM+'-poster.jpg'))
    settings={'source_sha256':hashlib.sha256(core.SOURCE.read_bytes()).hexdigest(),'duration':20,'fps':30,'vents':anim.vents,'windows':anim.windows,'ring_box':anim.ring_box,'method':'local procedural independent layers','prompt':'ambient-v9-final-brief.md','artistic_status':'awaiting user review'}
    (core.OUTPUT/(core.STEM+'-settings.json')).write_text(json.dumps(settings,indent=2))
    if not a.qa_only:
        dest=core.OUTPUT/(core.STEM+'.mp4')
        if dest.exists():raise FileExistsError(dest)
        core.render(anim,dest);core.validate(anim,dest)
if __name__=='__main__':main()
