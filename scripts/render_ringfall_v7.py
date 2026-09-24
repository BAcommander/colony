"""Independent atmosphere/steam/light layers; fixed master scene, no video diffusion."""
import argparse
import json
import hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
import render_ringfall as core
from render_ringfall_v6 import LivingRingfall

OUT=core.OUTPUT

class AmbientRingfall(LivingRingfall):
    def __init__(self):
        super().__init__(['coffee_steam','laptop_scan','mast_beacon','colony_work_lights'])
        self.steam_box=(202,337,306,516)
        self.active[337:516,202:306]=True
        self.active|=self.layer_masks['planet_atmosphere']
        self.lamps=[(1255,440,7,4,0.0),(1320,449,5,3,1.8),(1390,451,6,5,3.4),(1481,454,5,3,4.8)]
        for x,y,rx,ry,p in self.lamps: self.active[y-ry*3:y+ry*3+1,x-rx*3:x+rx*3+1]=True
        self.effect_descriptions={
          'steam':'Layered rising wisps with advected density and widening turbulent path',
          'planet':'Independent procedural cloud bands, fixed master lighting and protected rings',
          'colony':'Two moving textured surface light pools, four phased windows and mast beacon',
          'laptop':'Original display retained with scan sector and telemetry'}
        self.config['colony']['lights'][0].update(width=[48,10],gain=2.8,travel=[175,7])
        self.config['colony']['lights'][1].update(width=[38,9],gain=2.4,travel=[108,12])

    def steam(self,phase):
        x0,y0,x1,y1=self.steam_box
        y,x=np.mgrid[y0:y1,x0:x1].astype(np.float32)
        h=np.clip((515-y)/175,0,1)
        # Phase travels upward: for constant noise phase, h increases with time.
        flow=13*h-2*phase
        cx=250+6*h+13*h*np.sin(flow)+4*h*np.sin(25*h-3*phase)
        density=np.zeros_like(h)
        for j in range(4):
            center=cx+(j-1.5)*(1+6*h)+3*h*np.sin(18*h-2*phase+j)
            width=1.2+2.7*h+1.1*h*np.sin(22*h-3*phase+j)**2
            filament=np.exp(-.5*((x-center)/width)**2)
            # Two scales of advected detail break up a coherent plume.
            texture=.52+.28*np.sin(32*h-4*phase+j*1.9)+.16*np.sin(63*h-7*phase+(x-250)*.15+j)
            density+=filament*np.maximum(texture,0)*.27
        envelope=np.maximum(0,np.sin(np.pi*h))**.85
        density*=envelope*np.clip((515-y)/8,0,1)
        density*=np.clip((x-x0)/8,0,1)*np.clip((x1-1-x)/8,0,1)
        return np.clip(cv2.GaussianBlur(density,(0,0),.7),0,.42)

    def frame(self,t,output_size=True):
        phase=self.phase(t)
        frame=super().frame(t,False)
        x0,y0,x1,y1=self.rois['planet_atmosphere']
        x,y=self.grids['planet_atmosphere']
        # Independent material-like cloud detail. Geometry is never resampled.
        bend=2.0*np.sin(x*.024-phase)+1.0*np.sin(x*.055-2*phase+y*.012)
        clouds=(np.sin((y+bend)*.31+x*.024-phase)*.65+
                np.sin((y+bend)*.56-x*.037+2*phase)*.24+
                np.sin(y*.92+x*.06-3*phase)*.11)
        patch=self.base[y0:y1,x0:x1].astype(np.float32)
        light=np.clip(patch.mean(axis=2)/175,.15,1)
        alpha=self.masks['planet_atmosphere']
        delta=clouds*10*light*alpha
        frame[y0:y1,x0:x1]=np.rint(np.clip(patch+delta[:,:,None]*np.array([1.0,.92,.78]),0,255)).astype(np.uint8)
        # Dim activity confined to pre-existing warm windows, no moving objects.
        for x,y,rx,ry,offset in self.lamps:
            x0,y0,x1,y1=x-rx*3,y-ry*3,x+rx*3+1,y+ry*3+1
            yy,xx=np.mgrid[y0:y1,x0:x1]
            a=np.exp(-.5*(((xx-x)/rx)**2+((yy-y)/ry)**2))
            power=(.5+.5*np.sin(phase+offset))**3
            patch=frame[y0:y1,x0:x1].astype(float)
            frame[y0:y1,x0:x1]=np.rint(np.clip(patch+a[:,:,None]*power*np.array([28,15,4]),0,255)).astype(np.uint8)
        # Radar-like scan over the existing moon display, inset within screen edges.
        x0,y0,x1,y1=self.screen_box
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(float)
        u=xx/95; v=(yy-457+.078*xx)/(144-.17*xx)
        angle=np.arctan2((v-.5)*1.1,u-.32)
        radius=np.sqrt(((v-.5)*1.1)**2+(u-.32)**2)
        angular=np.mod(angle-phase,core.TAU)
        a=np.exp(-angular/.20)*np.clip((.48-radius)/.12,0,1)*.16
        a*=(v>.08)&(v<.86)&(u<.83)&(u>0)
        patch=frame[y0:y1,x0:x1].astype(float)
        frame[y0:y1,x0:x1]=np.rint(patch*(1-a[:,:,None])+np.array([148,187,176])*a[:,:,None]).astype(np.uint8)
        return cv2.resize(frame,core.SIZE,interpolation=cv2.INTER_LANCZOS4) if output_size else frame

def main():
    p=argparse.ArgumentParser(); p.add_argument('--stage',choices=['preview','final'],default='preview')
    p.add_argument('--qa-only',action='store_true'); p.add_argument('--version',default='v7b'); args=p.parse_args()
    core.SIZE=(1280,720) if args.stage=='preview' else (3840,2160)
    core.STEM='ringfall-ambient-'+args.version+'-'+args.stage
    anim=AmbientRingfall()
    sheet=Image.new('RGB',(1280,1080))
    for i,t in enumerate([0,2,4,6,8,9.967]):
        im=Image.fromarray(anim.frame(t,False)).resize((640,360))
        ImageDraw.Draw(im).text((12,12),f'{t}s',fill='white')
        sheet.paste(im,((i%2)*640,(i//2)*360))
    sheet.save(OUT/(core.STEM+'-review.jpg'))
    core.make_qa(anim)
    (OUT/(core.STEM+'-settings.json')).write_text(json.dumps({'config':anim.config,'source_sha256':hashlib.sha256(core.SOURCE.read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'prompt':'ambient-v7-prompt.md','procedural_seed':'deterministic trigonometric fields; no random state'},indent=2))
    if not args.qa_only:
        dest=OUT/(core.STEM+'.mp4')
        if dest.exists(): raise FileExistsError(dest)
        core.render(anim,dest)
        core.validate(anim,dest)

if __name__=='__main__': main()
