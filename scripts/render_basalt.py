"""Config-driven Basalt scene. Reuses approved effect math and core encode/validation."""
import argparse,json,hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
import render_ringfall as core
from ambient_effects import polygon_mask,vent_density,event_amount,blend,TAU,smoothstep
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/basalt-transmission/animation'
CONFIG=OUT/'scene-plan-v1.json'

class Basalt:
    def __init__(self):
        self.config=json.loads(CONFIG.read_text())
        self.source=ROOT/self.config['source']['path']
        assert hashlib.sha256(self.source.read_bytes()).hexdigest()==self.config['source']['sha256']
        self.base=np.array(Image.open(self.source).convert('RGB'))
        self.duration=self.config['output']['loop_duration_seconds']
        self.active=np.zeros(self.base.shape[:2],bool)
        self.layer_masks={n:self.active.copy() for n in ['roof_exhaust','valley_haze','interior_lights']}
        self.vents=[]
        for c in self.config['effects']['vents']:
            x,y=c['anchor'];w=c['width'];h=c['height']
            roi=(x-2*w,y-h-3,x+2*w+c['drift']+1,y+1)
            x0,y0,x1,y1=roi;yy,xx=np.mgrid[y0:y1,x0:x1].astype(float)
            self.vents.append((c,roi,xx,yy))
            self.layer_masks['roof_exhaust'][y0:y1,x0:x1]=True
        c=self.config['effects']['haze'];self.haze_roi=tuple(c['roi'])
        x0,y0,x1,y1=self.haze_roi
        self.hy,self.hx=np.mgrid[y0:y1,x0:x1].astype(float)
        self.haze_mask=polygon_mask(self.hx.shape,[c['polygon']],(x0,y0),c['feather'])
        blockers=polygon_mask(self.hx.shape,c['blockers'],(x0,y0),1)
        # Inset from blockers to prevent any halo crossing the rocks.
        clear=cv2.distanceTransform(np.uint8(blockers==0),cv2.DIST_L2,5)
        self.haze_mask*=smoothstep((clear-1)/3)
        self.layer_masks['valley_haze'][y0:y1,x0:x1]=self.haze_mask>0
        self.windows=[]
        for c in self.config['effects']['windows']:
            pts=np.concatenate([np.array(p) for p in c['polygons']])
            x0,y0=pts.min(axis=0)-3;x1,y1=pts.max(axis=0)+4
            roi=(int(x0),int(y0),int(x1),int(y1))
            aperture=polygon_mask((y1-y0,x1-x0),c['polygons'],(x0,y0),1.3)
            spill=cv2.GaussianBlur(aperture,(0,0),1.6)*.1
            mask=np.clip(aperture+spill,0,1)
            self.windows.append((c,roi,mask))
            self.layer_masks['interior_lights'][y0:y1,x0:x1]|=mask>0
        self.active=np.logical_or.reduce(list(self.layer_masks.values()))
        self.effect_descriptions={'roof_exhaust':'Two source-anchored rising, right-drifting plumes','valley_haze':'Two depth bands of rightward material motion, rock-occluded','interior_lights':'Two smaller rooms with offset holds; main room steady'}
    def frame(self,t,output_size=True):
        p=TAU*(float(t)%self.duration)/self.duration
        f=self.base.copy()
        c=self.config['effects']['haze'];alpha=np.zeros_like(self.hx)
        for band in c['bands']:
            # Persistent low-frequency shapes with fine density traveling right.
            q=TAU*self.hx/band['wavelength']-p+band['phase']
            center=band['center_y']+2*np.sin(self.hx*.019)+1.4*np.sin(q*.0+self.hx*.034)
            ribbon=np.exp(-.5*((self.hy-center)/band['width'])**2)
            coarse=.50+.25*np.sin(self.hx*.015+band['phase'])+.15*np.cos(self.hx*.031)
            moving=.55+.28*np.sin(q+(self.hy-band['center_y'])*.23)+.17*np.sin(2*q+self.hy*.37)
            alpha+=ribbon*np.clip(coarse,0,1)*np.clip(moving,0,1)*band['opacity']
        blend(f,self.haze_roi,c['color'],alpha*self.haze_mask)
        for c,roi,x,y in self.vents:
            blend(f,roi,c['color'],vent_density(x,y,c,p))
        for c,roi,mask in self.windows:
            amount=event_amount(t,self.duration,c['start'],c['hold'],c['transition'])*c['strength']
            x0,y0,x1,y1=roi;patch=f[y0:y1,x0:x1].astype(float)
            # Retain texture in the dark aperture rather than a solid rectangle.
            dark=patch*.13+np.array([15,12,10])
            a=mask*amount
            f[y0:y1,x0:x1]=np.uint8(np.rint(np.clip(patch*(1-a[...,None])+dark*a[...,None],0,255)))
        return cv2.resize(f,core.SIZE,interpolation=cv2.INTER_LANCZOS4) if output_size else f
    def qa(self,stem):
        folder=OUT/'masks-v1';folder.mkdir(exist_ok=True)
        overlay=self.base.copy().astype(float)
        for (name,m),color in zip(self.layer_masks.items(),[(100,200,255),(100,255,150),(255,100,70)]):
            Image.fromarray(np.uint8(m)*255).save(folder/(name+'.png'))
            overlay[m]=overlay[m]*.6+np.array(color)*.4
        im=Image.fromarray(np.uint8(overlay));d=ImageDraw.Draw(im)
        for c,roi,x,y in self.vents:
            sx,sy=c['anchor'];d.ellipse((sx-3,sy-3,sx+3,sy+3),fill='red');d.text((sx+5,sy),c['name'],fill='white')
        im.save(folder/'mask-overlay.png')
        times=[0,2,5,9,13,17,19.9666667,20]
        sheet=Image.new('RGB',(1280,1440))
        for i,t in enumerate(times):
            im=Image.fromarray(self.frame(t,False)).resize((640,360));ImageDraw.Draw(im).text((10,10),f'{t:.2f}s',fill='white');sheet.paste(im,((i%2)*640,(i//2)*360))
        sheet.save(OUT/(stem+'-review.jpg'))
        Image.fromarray(self.frame(5)).save(OUT/(stem+'-poster.jpg'))
        checks={}
        a=self.frame(0,False);b=self.frame(20,False)
        assert np.array_equal(a,b)
        for name,m in self.layer_masks.items():
            steps=[];prev=a[m].astype(float)
            for t in [1/30,2,5,9,13,17,19+29/30]:
                f=self.frame(t,False);assert np.array_equal(f[~self.active],self.base[~self.active]);steps.append(float(np.abs(f[m].astype(float)-prev).mean()));prev=f[m].astype(float)
            checks[name]={'endpoint_identical':bool(np.array_equal(a[m],b[m])),'sample_step_changes':steps,'mask_pixels':int(m.sum())}
        assert not np.array_equal(a,self.frame(10,False))
        (OUT/(stem+'-layer-checks.json')).write_text(json.dumps(checks,indent=2))
        manifest={'config_sha256':hashlib.sha256(CONFIG.read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'effects_sha256':hashlib.sha256((ROOT/'scripts/ambient_effects.py').read_bytes()).hexdigest(),'source_sha256':self.config['source']['sha256'],'duration':self.duration,'effects':self.effect_descriptions,'inspection':'temporal samples; user review pending'}
        (OUT/(stem+'-settings.json')).write_text(json.dumps(manifest,indent=2))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['preview','final'],default='preview');ap.add_argument('--qa-only',action='store_true');args=ap.parse_args()
    anim=Basalt();core.SOURCE=anim.source;core.OUTPUT=OUT;core.DURATION=anim.duration;core.FPS=30
    core.SIZE=(1280,720) if args.stage=='preview' else (3840,2160)
    core.STEM='baseline-v1-preview' if args.stage=='preview' else 'baseline-v1-loop-4k-master'
    anim.qa(core.STEM)
    if not args.qa_only:
        path=OUT/(core.STEM+'.mp4')
        if path.exists():raise FileExistsError(path)
        core.render(anim,path);core.validate(anim,path)
if __name__=='__main__':main()
