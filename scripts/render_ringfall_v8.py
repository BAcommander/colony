"""20-second Ringfall extension: fixed ring geometry, fine ring light drift, colony sequence."""
import argparse
import json
import hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
import render_ringfall as core
from render_ringfall_v7 import AmbientRingfall

class ExtendedRingfall(AmbientRingfall):
    def __init__(self):
        super().__init__()
        self.ring_box=(1348,90,1655,292)
        x0,y0,x1,y1=self.ring_box
        self.ry,self.rx=np.mgrid[y0:y1,x0:x1].astype(float)
        # Conservative visible right-hand ring arc; avoids planetary silhouette.
        poly=np.array([[1360,144],[1470,119],[1564,100],[1610,100],[1639,106],
          [1650,116],[1640,136],[1593,169],[1518,213],[1420,260],[1360,282],
          [1357,259],[1446,218],[1522,177],[1568,147],[1576,134],[1564,129],
          [1530,129],[1455,144],[1364,164]])-[x0,y0]
        m=np.zeros((y1-y0,x1-x0),np.uint8); cv2.fillPoly(m,[poly.astype(np.int32)],255)
        distance=cv2.distanceTransform(m,cv2.DIST_L2,5)
        patch=self.base[y0:y1,x0:x1].astype(float)
        # Modulate only existing lit ring material, not dark sky between bands.
        lum=patch.mean(axis=2)
        self.ring_mask=np.clip((distance-2)/6,0,1)*np.clip((lum-48)/28,0,1)
        self.active[y0:y1,x0:x1]|=self.ring_mask>0
        self.ring_angle=np.arctan2((self.ry-235)*3.4,self.rx-1160)
        self.sequence=[(1225,444),(1271,446),(1368,449),(1473,449),(1526,458)]
        for x,y in self.sequence:self.active[y-5:y+6,x-8:x+9]=True
        self.effect_descriptions.update(rings='Fine existing ring brightness/texture drift in a protected right-arc mask; fixed geometry',
          distance='Five phased points of service-light activity at the colony; no added moving objects')

    def steam(self,phase):
        # Keep natural rise speed while the overall composition gains a longer cycle.
        return super().steam(2*phase)*(.92+.08*np.sin(phase+.5))

    def frame(self,t,output_size=True):
        phase=self.phase(t)
        frame=super().frame(t,False)
        x0,y0,x1,y1=self.ring_box
        # Moving illumination texture, not rotating/repainting the ring ellipse.
        drift=.065*np.sin(8*self.ring_angle-phase)+.025*np.sin(19*self.ring_angle-2*phase)
        patch=self.base[y0:y1,x0:x1].astype(float)
        frame[y0:y1,x0:x1]=np.rint(np.clip(patch*(1+self.ring_mask[:,:,None]*drift[:,:,None]),0,255)).astype(np.uint8)
        for i,(x,y) in enumerate(self.sequence):
            yy,xx=np.mgrid[y-5:y+6,x-8:x+9]
            alpha=np.exp(-.5*(((xx-x)/2.2)**2+((yy-y)/1.4)**2))
            pulse=(.5+.5*np.cos(phase-i*.8))**6
            patch=frame[y-5:y+6,x-8:x+9].astype(float)
            frame[y-5:y+6,x-8:x+9]=np.rint(np.clip(patch+alpha[:,:,None]*pulse*np.array([35,23,9]),0,255)).astype(np.uint8)
        return cv2.resize(frame,core.SIZE,interpolation=cv2.INTER_LANCZOS4) if output_size else frame

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['preview','final'],default='preview');a=p.parse_args()
    core.DURATION=20;core.SIZE=(1280,720) if a.stage=='preview' else (3840,2160)
    core.STEM='ringfall-ambient-v8-20s-'+a.stage
    anim=ExtendedRingfall();sheet=Image.new('RGB',(1280,1080))
    for i,t in enumerate([0,4,8,12,16,19.967]):
        im=Image.fromarray(anim.frame(t,False)).resize((640,360));ImageDraw.Draw(im).text((10,10),str(t)+'s',fill='white');sheet.paste(im,((i%2)*640,(i//2)*360))
    sheet.save(core.OUTPUT/(core.STEM+'-review.jpg'))
    x0,y0,x1,y1=anim.ring_box
    crop=anim.base[y0:y1,x0:x1].astype(float);m=anim.ring_mask[:,:,None]*.5
    overlay=np.uint8(crop*(1-m)+np.array([50,220,100])*m)
    Image.fromarray(overlay).resize((921,606)).save(core.OUTPUT/'ringfall-v8-ring-mask-review.png')
    settings={'duration':20,'fps':30,'source_sha256':hashlib.sha256(core.SOURCE.read_bytes()).hexdigest(),
      'ring_box':anim.ring_box,'ring_drift_amplitudes':[.065,.025],'colony_sequence':anim.sequence,
      'baseline':'v7b','method':'v7 inherited layers plus ring material drift and colony service-light sequence',
      'steam':'10-second upward transport with20-second density envelope','artistic_status':'pending user review'}
    (core.OUTPUT/(core.STEM+'-settings.json')).write_text(json.dumps(settings,indent=2))
    dest=core.OUTPUT/(core.STEM+'.mp4')
    if dest.exists():raise FileExistsError(dest)
    core.render(anim,dest);core.validate(anim,dest)

if __name__=='__main__':main()
