"""Reusable deterministic scene effects, independent of source image coordinates."""
import cv2
import numpy as np
TAU=2*np.pi

def smoothstep(v):
    v=np.clip(v,0,1)
    return v*v*(3-2*v)

def polygon_mask(shape, polygons, origin=(0,0), feather=2):
    m=np.zeros(shape,np.uint8)
    for poly in polygons:
        cv2.fillPoly(m,[np.asarray(poly,np.int32)-np.asarray(origin,np.int32)],255)
    return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/feather)

def event_amount(t,duration,start,hold,transition):
    age=(t%duration-start)%duration
    return smoothstep(age/transition)*smoothstep((hold-age)/transition)

def vent_density(x,y,c,phase):
    sx,sy=c['anchor'];h=(sy-y)/c['height']
    density=np.zeros_like(h)
    for j in range(3):
        flow=18*h-3*phase+c['phase']+j*1.7
        center=sx+c['drift']*h+h*(3*np.sin(flow)+2*np.sin(31*h-5*phase+j))+(j-1)*h*c['width']*.25
        spread=1+c['width']*h*.4
        ribbon=np.exp(-.5*((x-center)/np.maximum(spread,.1))**2)
        detail=.55+.27*np.sin(29*h-5*phase+c['phase']+j)+.18*np.cos(49*h-7*phase+(x-sx)*.25+j)
        density+=ribbon*np.maximum(detail,0)*c['opacity']
    envelope=np.maximum(0,np.sin(np.pi*np.clip(h,0,1)))**.8
    density*=envelope*np.clip(h*30,0,1)*(h<1)*(h>0)
    edge=smoothstep((x-x.min())/6)*smoothstep((x.max()-x)/6)
    return np.clip(cv2.GaussianBlur(density*edge,(0,0),.7),0,.62)

def blend(frame,roi,color,alpha):
    x0,y0,x1,y1=roi
    patch=frame[y0:y1,x0:x1].astype(np.float32)
    frame[y0:y1,x0:x1]=np.uint8(np.rint(np.clip(patch*(1-alpha[...,None])+np.asarray(color)*alpha[...,None],0,255)))
