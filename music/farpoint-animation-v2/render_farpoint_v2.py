"""Forward transport prototype after the v1 visibility rejection.

No lifetime blend or wrap is used for the revised principal cloud layer.
These eight-second excerpts are NOT seamless loops.
"""
from pathlib import Path
import sys, json, hashlib
import cv2
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
V1=HERE.parent/'farpoint-animation-v1'
sys.path.insert(0,str(V1))
from render_farpoint import Farpoint, byte_image, encode, digest, smoothstep, verify


class ForwardFarpoint(Farpoint):
    def __init__(self):
        super().__init__()
        self.path=HERE/'scene-plan-v2.json'
        self.config=json.loads(self.path.read_text())
        assert digest(V1/'render_farpoint.py')==self.config['parent_renderer_sha256']
        # Rebuild the planet with the revised travel speeds; preserve the
        # source extraction and habitation implementations exactly.
        self.prepare_planet()
        # Convert extracted radiance to an optical cloud layer. Premultiplied
        # alpha compositing prevents a cloud crossing brighter ground from
        # adding its old ground contrast as an overexposed glowing patch.
        alpha=np.clip(np.max(self.cloud/np.maximum(245-self.clean,12),axis=2),0,.96)
        premultiplied=self.cloud+alpha[...,None]*self.clean
        self.optical_cloud=np.dstack([premultiplied,alpha]).astype(np.float32)
        support=cv2.dilate(np.uint8(np.max(self.cloud,axis=2)>.15),np.ones((121,121),np.uint8))
        self.pm=smoothstep(cv2.distanceTransform(support,cv2.DIST_L2,5)/12)*self.safe
        self.pm[self.pm<.002]=0
        a,b,z,d=self.planet_roi
        self.masks['clouds'][b:d,a:z]=self.pm
        self.layer_masks={k:v>0 for k,v in self.masks.items()}
        self.layer_masks['habitation']=np.logical_or.reduce([self.layer_masks[k] for k in ('windows','screen','lamp')])
        self.active=np.logical_or.reduce(list(self.layer_masks.values()))

    def forward_cloud(self,t):
        cx,cy=self.config['planet']['center'];a,b,_,_=self.planet_roi
        theta=self.angle-self.omega*t
        mx=(cx+self.rad*np.cos(theta)-a).astype(np.float32)
        my=(cy+self.rad*np.sin(theta)-b).astype(np.float32)
        return cv2.remap(self.optical_cloud,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)

    def frame_float(self,t,only=None):
        if only not in (None,'clouds'):
            return super().frame_float(t,only)
        f=super().frame_float(t,'habitation') if only is None else self.base.astype(np.float32)
        a,b,z,d=self.planet_roi
        moved=self.forward_cloud(t)
        cloud_delta=moved[...,:3]-moved[...,3,None]*self.clean-self.cloud
        f[b:d,a:z]+=cloud_delta*self.pm[...,None]*self.config['planet']['transport']['gain']
        if only is None:
            f+=super().frame_float(t,'veil')-self.base
        assert np.isfinite(f).all()
        return f

    def fingerprint(self):
        f=super().fingerprint()
        f['files']['music/farpoint-animation-v2/render_farpoint_v2.py']=digest(__file__)
        f['prototype']={'duration_seconds':8,'seamless':False,'loop_boundary_checked':False}
        return f


def main():
    s=ForwardFarpoint();old=Farpoint()
    for t in [0,2,4,6,8]:
        Image.fromarray(s.frame(t)).save(HERE/f'sample-{t:02d}s.png')
    (HERE/'masks').mkdir(exist_ok=True)
    for k,m in s.masks.items():cv2.imwrite(str(HERE/'masks'/f'{k}.png'),byte_image(m*255))
    reg={k:all(np.array_equal(s.frame(t,k),old.frame(t,k)) for t in [0,5,8,12.95,18]) for k in ['windows','screen','lamp','veil']}
    assert all(reg.values())
    movement={}
    for name,(x,y,r) in {'upper_cloud':(1186,263,13),'central_wisp':(978,367,13),'right_cloud':(1570,339,13)}.items():
        a,b,z,d=s.planet_roi;x-=a;y-=b
        start=s.forward_cloud(0).mean(2).astype(np.float32)
        end=s.forward_cloud(8).mean(2).astype(np.float32)
        template=start[y-r:y+r+1,x-r:x+r+1]
        xa,xb=max(0,x-r-12),min(end.shape[1],x+r+65)
        ya,yb=max(0,y-r-40),min(end.shape[0],y+r+25)
        match=cv2.matchTemplate(end[ya:yb,xa:xb],template,cv2.TM_CCOEFF_NORMED)
        _,score,_,pos=cv2.minMaxLoc(match)
        dx=pos[0]+xa-(x-r);dy=pos[1]+ya-(y-r)
        movement[name]={'template_correlation':score,'source_displacement_xy':[dx,dy],'preview_displacement_xy':[dx*1280/1672,dy*720/941]}
    (HERE/'sample-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'retained_layers_sampled_exact':reg,'template_tracking_diagnostic':movement,'scope':'Supporting measurement only; normal-speed visibility requires user playback review.'},indent=2)+'\n')
    if '--samples-only' in sys.argv:return
    clips=[]
    for layer,filename in [('clouds','farpoint-v2-planet-motion-test-8s.mp4'),(None,'farpoint-v2-full-scene-motion-test-8s.mp4')]:
        item=encode(s,HERE/filename,8,layer,prototype=True)
        item['validation'],_=verify(s,HERE/filename,240,False)
        item['seamless']=False;clips.append(item)
    cap=cv2.VideoCapture(str(HERE/clips[1]['path'].split('/')[-1]))
    for n in [0,90,210]:
        cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok
        cv2.imwrite(str(HERE/f'decoded-{n:03d}.png'),f)
    cap.release()
    (HERE/'delivery-v2.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'stage':'forward motion proof; NOT a loop delivery','inspection':'Source, temporal and decoded stills; no continuous playback claim','v1_feedback':s.config['review']['user_feedback_on_v1']},indent=2)+'\n')
    print('Forward-motion clips decoded and timestamp checked. User visibility review pending.',flush=True)


if __name__=='__main__':main()
