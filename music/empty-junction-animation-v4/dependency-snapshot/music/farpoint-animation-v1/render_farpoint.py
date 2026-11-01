"""Farpoint source-specific adapter; fixed geology with separated cloud radiance.

Run from repository root: python music/farpoint-animation-v1/render_farpoint.py
--stage samples|isolated|preview. Existing video exports are never overwritten.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from ambient_effects import smoothstep, event_amount, polygon_mask
from render_floodplain import encode, digest

cv2.setNumThreads(4)


def save_json(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def byte_image(a):
    return np.rint(np.clip(a, 0, 255)).astype(np.uint8)


class Farpoint:
    def __init__(self):
        self.path = HERE / 'scene-plan-v1.json'
        self.config = json.loads(self.path.read_text(encoding='utf-8'))
        c = self.config
        assert digest(ROOT / c['source']['path']) == c['source']['sha256']
        self.base = np.array(Image.open(ROOT / c['source']['path']).convert('RGB'))
        self.h, self.w = self.base.shape[:2]
        assert [self.w, self.h] == c['source']['dimensions']
        self.duration = c['duration']
        self.shape = (self.h, self.w)
        self.y, self.x = np.mgrid[:self.h, :self.w].astype(np.float32)
        self.masks = {}
        self.prepare_planet()
        self.prepare_habitation()
        self.layer_masks = {k: v > 0 for k, v in self.masks.items()}
        self.layer_masks['habitation'] = np.logical_or.reduce(
            [self.layer_masks[k] for k in ('windows', 'screen', 'lamp')])
        self.active = np.logical_or.reduce(list(self.layer_masks.values()))

    def poly(self, points, feather=2):
        scale=4
        mask=np.zeros((self.h*scale,self.w*scale),np.uint8)
        for p in points:
            cv2.fillPoly(mask,[np.rint(np.array(p)*scale).astype(np.int32)],255)
        dist=cv2.distanceTransform(mask,cv2.DIST_L2,5)
        mask=smoothstep(dist/(feather*scale))
        return cv2.resize(mask,(self.w,self.h),interpolation=cv2.INTER_AREA)

    def prepare_planet(self):
        pc = self.config['planet']
        a, b, z, d = pc['roi']
        self.planet_roi = (a, b, z, d)
        self.plate = self.base[b:d, a:z].astype(np.float32)
        self.py, self.px = self.y[b:d, a:z], self.x[b:d, a:z]
        cx, cy = pc['center']
        self.rad = np.hypot(self.px - cx, self.py - cy)
        self.angle = np.arctan2(self.py - cy, self.px - cx)
        safe = self.poly([pc['window_polygon']], 12)[b:d, a:z]
        safe *= smoothstep((pc['radius'] - pc['limb_protection_pixels'] - self.rad) / 18)
        safe *= smoothstep((self.px-a)/12)*smoothstep((z-1-self.px)/12)
        safe *= smoothstep((self.py-b)/12)*smoothstep((d-1-self.py)/12)
        domain = self.poly(pc['cloud_polygons'], 18)[b:d, a:z] * safe
        e = pc['extraction']
        red, blue = self.plate[..., 0], self.plate[..., 2]
        chroma = smoothstep((blue-e['blue_red_ratio']*red-e['blue_offset']) / e['blue_range'])
        chroma *= smoothstep((red-e['red_floor'])/e['red_range'])
        selected = chroma * domain
        holes = np.uint8(selected > .12)*255
        holes = cv2.dilate(holes, np.ones((5,5), np.uint8))
        terrain = cv2.inpaint(self.plate.astype(np.uint8), holes, e['inpaint_radius'], cv2.INPAINT_TELEA).astype(np.float32)
        # Only pale positive cloud radiance is transported. Signed rock relief,
        # craters and all texture outside the selected atmosphere stay fixed.
        gate = cv2.GaussianBlur(np.float32(holes > 0), (0,0), 1.2) * domain
        cloud = np.maximum(self.plate - terrain, 0)
        cloud = cv2.GaussianBlur(cloud, (0,0), e['blur_sigma']) * gate[...,None]
        self.cloud = cloud
        self.clean = self.plate - cloud
        self.safe = safe
        support = cv2.dilate(np.uint8(np.max(cloud,axis=2) > .15), np.ones((49,49),np.uint8))
        support = smoothstep(cv2.distanceTransform(support,cv2.DIST_L2,5)/8)*safe
        support[support < .002] = 0
        self.pm = support
        self.veil = cv2.GaussianBlur(cloud,(0,0),pc['veil']['sigma'])
        central = smoothstep((self.py - 290)/100)
        transport = pc['transport']
        speed = transport['upper_pixels_per_second']*(1-central)+transport['central_pixels_per_second']*central
        # Travel lies tangent to the protected limb and is foreshortened near it.
        speed *= .5+.5*smoothstep((pc['radius']-self.rad)/155)
        self.omega = speed / np.maximum(self.rad,1)
        self.offset = transport['local_phase_spread']*(self.px-a)/(z-a)+(self.py-b)/1700
        for key in ['clouds','veil']:
            m = np.zeros(self.shape,np.float32)
            m[b:d,a:z] = support
            self.masks[key] = m
        self.selection = selected
        self.holes = holes

    def transported(self, texture, t, omega, offset):
        pc = self.config['planet']
        cx, cy = pc['center']
        a,b,_,_ = self.planet_roi
        out = np.zeros_like(texture)
        for phase in [0., .5]:
            age = (t/self.duration+offset+phase)%1
            weight = np.sin(np.pi*age)**2
            theta = self.angle - omega*self.duration*(age-.5)
            mx = (cx+self.rad*np.cos(theta)-a).astype(np.float32)
            my = (cy+self.rad*np.sin(theta)-b).astype(np.float32)
            moved = cv2.remap(texture,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
            out += moved*weight[...,None]
        return out

    def crop(self,m):
        yy,xx = np.where(m>0)
        a,b,z,d = int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
        return (a,b,z,d),m[b:d,a:z]

    def prepare_habitation(self):
        warm = smoothstep((self.base[...,0].astype(np.float32)-self.base[...,2]-12)/65)
        self.windows = []
        union = np.zeros(self.shape,np.float32)
        for lc in self.config['habitat_windows']:
            aperture = self.poly(lc['panes'],.9)
            # Warm divider reflections belong to the light pool; the dark
            # frame remains geometrically fixed and retains its texture.
            surround = self.poly([lc['inner_aperture']],1.1)*.65
            aperture=np.maximum(aperture,surround)
            cx,cy = lc['spill_center'];rx,ry = lc['spill_radius']
            spill = np.exp(-((self.x-cx)/rx)**2-((self.y-cy)/ry)**2)*warm*.12
            # Confine incidental spill to the local window surround.
            spill[(abs(self.x-cx)>rx*1.35)|(abs(self.y-cy)>ry*1.35)] = 0
            m = np.maximum(aperture,spill);m[m<.004]=0
            self.windows.append((lc,self.crop(m)))
            union=np.maximum(union,m)
        self.masks['windows']=union
        sc=self.config['screen'];sw,sh=sc['size'];quad=np.float32(sc['quad'])
        self.screen_matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[sw-1,0],[sw-1,sh-1],[0,sh-1]]),quad)
        self.screen_inverse=np.linalg.inv(self.screen_matrix)
        self.screen_original=cv2.warpPerspective(self.base,self.screen_inverse,(sw,sh)).astype(np.float32)
        self.masks['screen']=self.poly([sc['quad']],1.5)
        # Screen is partially occluded by the chair at the lower-left edge.
        self.masks['screen']*=1-self.poly([[[215,470],[242,479],[252,523],[270,587],[216,590]]],.5)
        self.screen_box,self.screen_mask=self.crop(self.masks['screen'])
        lc=self.config['lamp'];core=self.poly([lc['core_polygon']],1.6)
        cx,cy=lc['spill_center'];rx,ry=lc['spill_radius']
        spill=self.poly([lc['spill_polygon']],18)*np.exp(-((self.x-cx)/rx)**2-((self.y-cy)/ry)**2)*warm*.44
        halo=np.exp(-((self.x-408)/48)**2-((self.y-617)/12)**2)*warm*.22
        halo[(self.x<362)|(self.x>451)|(self.y<601)|(self.y>639)]=0
        lamp=np.maximum.reduce([core,spill,halo]).astype(np.float32);lamp[lamp<.003]=0
        self.masks['lamp']=lamp
        self.lamp=self.crop(lamp)

    def amount(self,t,events):
        return max((float(event_amount(t,self.duration,e['start'],e['hold'],e['transition']))*e['depth'] for e in events),default=0.)

    def dim(self,f,local,value):
        (a,b,z,d),mask=local
        f[b:d,a:z]*=1-mask[...,None]*value

    def screen(self,f,t):
        sc=self.config['screen'];sw,sh=sc['size'];phase=t/sc['period']
        canvas=np.zeros((sh,sw,3),np.float32)
        route=np.float32(sc['route']);lengths=np.linalg.norm(np.diff(route,axis=0),axis=1)
        at=phase*sum(lengths);idx=min(int(np.searchsorted(np.cumsum(lengths),at)),len(lengths)-1)
        part=(at-sum(lengths[:idx]))/lengths[idx]
        pos=route[idx]*(1-part)+route[idx+1]*part
        yy,xx=np.mgrid[:sh,:sw].astype(np.float32)
        marker=np.exp(-((xx-pos[0])**2+(yy-pos[1])**2)/7)
        marker*=float(smoothstep(phase/.06)*smoothstep((1-phase)/.06))
        canvas+=marker[...,None]*np.float32(sc['color'])
        for j,node in enumerate(route[[0,2,3,5]]):
            pulse=float(event_amount(t,self.duration,1.1+j*4.1,2.8,.5))
            ring=np.exp(-((np.hypot(xx-node[0],yy-node[1])-4)/1.1)**2)*pulse
            canvas+=ring[...,None]*np.float32([25,64,73])
        x0,y0,x1,y1=sc['log_rect'];patch=self.screen_original[y0:y1,x0:x1]
        gy,gx=np.mgrid[:y1-y0,:x1-x0].astype(np.float32)
        moved=cv2.remap(patch,gx,((gy+phase*(y1-y0))%(y1-y0)).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
        edge=smoothstep(gy/5)*smoothstep((y1-y0-1-gy)/5)*smoothstep(gx/3)*smoothstep((x1-x0-1-gx)/3)
        canvas[y0:y1,x0:x1]+=(moved-patch)*edge[...,None]*.8
        a,b,z,d=self.screen_box
        mat=self.screen_matrix.copy();mat[0]-=a*mat[2];mat[1]-=b*mat[2]
        warp=cv2.warpPerspective(canvas,mat,(z-a,d-b),flags=cv2.INTER_LINEAR)
        f[b:d,a:z]+=warp*self.screen_mask[...,None]

    def frame_float(self,t,only=None):
        t=float(t)%self.duration
        f=self.base.astype(np.float32)
        a,b,z,d=self.planet_roi
        if only in (None,'clouds'):
            moved=self.transported(self.cloud,t,self.omega,self.offset)
            f[b:d,a:z]+=(moved-self.cloud)*self.pm[...,None]*self.config['planet']['transport']['gain']
        if only in (None,'veil'):
            vc=self.config['planet']['veil']
            moved=self.transported(self.veil,t,vc['speed_pixels_per_second']/self.rad,self.offset+.23)
            f[b:d,a:z]+=(moved-self.veil)*self.pm[...,None]*vc['gain']
        if only in (None,'windows','habitation'):
            for lc,local in self.windows:self.dim(f,local,self.amount(t,lc['events']))
        if only in (None,'screen','habitation'):self.screen(f,t)
        if only in (None,'lamp','habitation'):self.dim(f,self.lamp,self.amount(t,self.config['lamp']['events']))
        assert np.isfinite(f).all()
        return f

    def frame(self,t,only=None,prototype=False):
        f=byte_image(self.frame_float(t,only))
        mask=self.active if only is None else self.layer_masks[only]
        assert np.array_equal(f[~mask],self.base[~mask]),'Protected source pixels changed'
        return f

    def fingerprint(self):
        paths=[self.config['source']['path'],'music/farpoint-animation-v1/render_farpoint.py','scripts/render_floodplain.py','scripts/water_surface.py','scripts/ambient_effects.py']
        return {'config_sha256':digest(self.path),'files':{p:digest(ROOT/p) for p in paths},'masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()},'versions':{'numpy':np.__version__,'opencv':cv2.__version__}}


def samples(s):
    (HERE/'masks').mkdir(exist_ok=True)
    overlay=s.base.astype(np.float32)
    colors={'clouds':[40,200,255],'veil':[40,200,255],'windows':[255,80,50],'screen':[80,255,100],'lamp':[255,200,20]}
    for k,m in s.masks.items():
        cv2.imwrite(str(HERE/'masks'/f'{k}.png'),byte_image(m*255))
        if k=='veil':continue
        alpha=m[...,None]*.36;overlay=overlay*(1-alpha)+np.float32(colors[k])*alpha
    Image.fromarray(byte_image(overlay)).save(HERE/'mask-review.png')
    Image.fromarray(byte_image(s.clean)).save(HERE/'reconstructed-terrain-crop.png')
    Image.fromarray(byte_image(s.cloud*2)).save(HERE/'cloud-extraction-diagnostic-x2.png')
    cv2.imwrite(str(HERE/'cloud-selection.png'),byte_image(s.selection*255))
    for t in [0,2,5,8,12.95,16,19+29/30]:
        Image.fromarray(s.frame(t)).save(HERE/f'sample-{t:06.3f}s.png')
    for name,box in [('habitat',(370,213,600,298)),('monitor',(237,471,390,591)),('lamp',(290,600,555,737)),('clouds',(960,210,1609,440))]:
        frames=[Image.fromarray(s.frame(t)).crop(box) for t in [0,5,8,12.95]]
        w,h=frames[0].size;sheet=Image.new('RGB',(w*2,h*2))
        for j,im in enumerate(frames):sheet.paste(im,((j%2)*w,(j//2)*h))
        sheet.save(HERE/f'{name}-temporal.png')
    forced=s.base.astype(np.float32)
    for lc,local in s.windows:s.dim(forced,local,.88)
    Image.fromarray(byte_image(forced)).crop((365,214,603,309)).resize((952,380)).save(HERE/'forced-dark-window-review.png')
    checks={}
    for key,m in s.layer_masks.items():
        f0=s.frame(0,key);assert np.array_equal(f0,s.frame(s.duration,key))
        vals=[]
        for t in [-1/30,0,2,3.5,5,8,12.73,12.95,13.2,16,17.8,19]:
            vals.append(float(np.abs(s.frame(t+1/30,key)[m].astype(float)-s.frame(t,key)[m]).mean()))
        assert vals[0]<=max(vals[1:])*1.1+.01,(key,vals)
        eps=1/300
        left=(s.frame_float(0,key)-s.frame_float(-eps,key))[m]/eps
        right=(s.frame_float(eps,key)-s.frame_float(0,key))[m]/eps
        checks[key]={'endpoint_exact':True,'seam_mae':vals[0],'ordinary_max_sampled':max(vals[1:]),'velocity_boundary_difference_mae':float(np.abs(left-right).mean()),'pass':True}
    assert not np.array_equal(s.frame(0),s.frame(s.duration-1/30))
    save_json('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':checks,'protected_pixels':'Exact outside active source masks, asserted for every rendered frame; reconstruction only inside mapped cloud areas.','user_approved':False})
    print('Samples, mask diagnostics and analytic checks saved',flush=True)


def verify(s,path,count,loop):
    cap=cv2.VideoCapture(str(path));assert cap.get(cv2.CAP_PROP_FPS)==s.config['fps']
    masks={k:cv2.resize(m.astype(np.uint8),tuple(s.config['preview_size']),interpolation=cv2.INTER_NEAREST) for k,m in {**s.layer_masks,'combined':s.active}.items()}
    first=prev=None;maximum={k:0. for k in masks};hashes=[];i=0
    while True:
        ok,f=cap.read()
        if not ok:break
        assert f.shape==(720,1280,3)
        assert abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/s.config['fps'])<.0001
        hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
        if first is None:first=f.copy()
        else:
            diff=cv2.absdiff(f,prev)
            for k,m in masks.items():maximum[k]=max(maximum[k],sum(cv2.mean(diff,mask=m)[:3])/3)
        if i in (0,240,388) and count==600:cv2.imwrite(str(HERE/f'decoded-preview-{i:04d}.png'),f)
        prev=f;i+=1
    cap.release();assert i==count,(i,count);checks={}
    if loop:
        assert hashes[0]!=hashes[-1]
        diff=cv2.absdiff(prev,first)
        for k,m in masks.items():
            value=sum(cv2.mean(diff,mask=m)[:3])/3
            assert value<=maximum[k]*1.1+.01,(k,value,maximum[k])
            checks[k]={'seam_mae':value,'ordinary_max_mae':maximum[k],'pass':True}
    return {'frames':i,'fps':30,'full_decode':True,'sequential_timestamps':True,'encoded_seam':checks},hashes


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True)
    args=p.parse_args();s=Farpoint()
    if args.stage=='samples':samples(s);return
    clips=[]
    if args.stage=='isolated':
        for layer in s.config['isolated_layers']:
            out=HERE/f'{layer}-isolated-v1-8s.mp4'
            item=encode(s,out,8,layer);item['validation'],_=verify(s,out,240,False);clips.append(item)
            print(layer,'isolated passed',flush=True)
    else:
        out=HERE/'farpoint-station-v1-preview-20s.mp4'
        item=encode(s,out,s.duration);item['validation'],hashes=verify(s,out,600,True);clips.append(item)
        repeat=HERE/'farpoint-station-v1-three-loops-60s.mp4';assert not repeat.exists()
        subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
        validation,repeated=verify(s,repeat,1800,True);assert repeated==hashes*3
        clips.append({'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
    save_json(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Source, masks, reconstruction, temporal and decoded stills; continuous playback not claimed.'})
    print(args.stage,'checks passed',flush=True)


if __name__=='__main__':main()
