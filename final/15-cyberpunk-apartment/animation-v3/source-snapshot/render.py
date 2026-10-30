from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math, subprocess, json, sys, time
from concurrent.futures import ThreadPoolExecutor
from collections import deque

R=Path(__file__).resolve().parent
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
W,H=1920,1080
FPS=60; DURATION=10; N=FPS*DURATION; TAU=2*math.pi
SX,SY=W/1672,H/941
rng=np.random.default_rng(9324)
baseim=Image.open(R/'clean-apartment.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
base=np.asarray(baseim,dtype=np.float32)
Y,X=np.mgrid[:H,:W].astype(np.float32)
x=X/SX;y=Y/SY

def matte(polygons,feather=0):
    im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
    for p in polygons:d.polygon([(a*SX,b*SY) for a,b in p],fill=255)
    if feather:im=im.filter(ImageFilter.GaussianBlur(feather*SX))
    return np.asarray(im,dtype=np.float32)/255

glass=matte([
 [(428,73),(664,43),(664,613),(594,609),(590,544),(428,528)],
 [(694,37),(1253,0),(1253,646),(694,616)],
 [(1280,0),(1671,0),(1671,441),(1609,451),(1590,504),(1567,548),(1521,597),(1519,661),(1280,650)]
],.6)
water=matte([
 [(701,475),(743,477),(740,495),(707,499)],
 [(1080,476),(1237,478),(1237,561),(1190,533),(1142,545),(1100,519),(1082,518)],
 [(1282,499),(1323,505),(1350,527),(1393,542),(1419,562),(1424,638),(1384,640),(1381,589),(1325,575),(1282,551)]
],3)*glass
wy,wx=np.where(water>0.0001)
water_box=(int(wx.min()),int(wy.min()),int(wx.max()+1),int(wy.max()+1))
floor=matte([[(886,693),(1018,697),(1520,726),(1520,778),(1341,767),(1305,760),(1048,752),(921,748)]],8)
floor*=np.clip((base[:,:,2]-base[:,:,0]+10)/50,0,1)*np.clip((base.max(2)-35)/80,0,1)
sign_response=water*np.exp(-((x-1134)**2/1800+(y-515)**2/2600))+.3*floor*np.exp(-((x-1035)**2/14000))

# Mist lives in the gaps between structures and in the existing cloud banks.
fog=matte([
 [(705,135),(783,156),(838,197),(873,208),(911,239),(904,269),(861,248),(805,239),(757,211),(705,221)],
 [(904,288),(924,265),(942,245),(961,226),(974,251),(963,288),(935,318),(901,330)],
 [(1024,303),(1052,279),(1103,276),(1118,293),(1099,309),(1062,312)],
 [(1283,337),(1315,328),(1345,350),(1378,364),(1396,383),(1390,399),(1347,390),(1300,370),(1283,367)],
 [(1482,134),(1520,112),(1568,91),(1579,139),(1554,163),(1509,199),(1488,217)]
],12)*glass
fog_color=np.array([130,171,203],np.float32)

# Brightness masks select only existing lit material. No lights are placed in empty sky.
luma=base.max(2)
lit=np.clip((luma-62)/130,0,1)
local_luma=np.asarray(Image.fromarray(luma.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5)),dtype=np.float32)
# Only small existing luminous features qualify as windows. Soft mist and sky do not.
window_detail=np.clip((luma-local_luma-12)/35,0,1)*np.clip((luma-85)/100,0,1)
neons=[]
neon_specs=[
 (1024,163,1045,246,0.2,1),(1026,315,1044,386,1.5,2),
 (1124,312,1141,394,2.6,1),(1155,546,1179,590,3.1,2),
 (1348,220,1366,274,4.3,1),(1473,257,1486,324,5.1,2),
 (1526,440,1538,499,1.2,1),(546,493,570,532,2.4,2),
 (969,361,982,392,3.8,1),(1187,332,1204,361,5.5,3)]
for x0,y0,x1,y1,p,f in neon_specs:
    m=matte([[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]],1.2)*lit*glass
    # Cropped masks keep per-frame work small.
    box=(max(0,int((x0-5)*SX)),max(0,int((y0-5)*SY)),min(W,int((x1+5)*SX)),min(H,int((y1+5)*SY)))
    a,b,c,d=box
    neons.append((box,m[b:d,a:c],p,f,y[b:d,a:c]))

window_layers=[]
for k in range(12):
    im=Image.new('L',(W,H));draw=ImageDraw.Draw(im)
    buildings=[(830,320,877,495),(927,416,950,549),(976,403,1027,546),(1400,377,1419,466),(1584,27,1668,407),(359,91,491,464),(1137,177,1159,307)]
    for bx0,by0,bx1,by1 in buildings:
        for _ in range(6):
            a=rng.uniform(bx0,bx1-4);b=rng.uniform(by0,by1-6)
            draw.rectangle((a*SX,b*SY,(a+rng.uniform(2,6))*SX,(b+rng.uniform(3,11))*SY),fill=255)
    im=im.filter(ImageFilter.GaussianBlur(.7))
    m=np.asarray(im,dtype=np.float32)/255*window_detail*glass
    window_layers.append((m,float(rng.uniform(0,TAU)),int(rng.choice([1,2,3]))))
window_coefficients={i:[np.zeros((H,W),np.float32),np.zeros((H,W),np.float32)] for i in range(1,6)}
for m,p,f in window_layers:
    for frequency,amplitude in [(f,.28),(f+2,.12)]:
        window_coefficients[frequency][0]+=m*(amplitude*math.cos(p))
        window_coefficients[frequency][1]+=m*(amplitude*math.sin(p))
del window_layers

# Road routes follow the original perspective. Vehicles pass behind nearby towers.
traffic_visibility=glass.copy()
occluders=matte([
 [(831,310),(866,312),(888,353),(888,498),(831,498)],
 [(957,388),(985,382),(1039,399),(1047,548),(960,548)],
 [(1397,305),(1421,306),(1423,493),(1397,493)],
 [(1513,406),(1547,410),(1548,567),(1513,567)]
])
traffic_visibility*=1-occluders
roads=[
 ([(876,331),(1010,354),(1150,380),(1275,402),(1400,424),(1537,452)],12,1,(173,223,248),0.9),
 ([(876,334),(1010,357),(1150,383),(1275,405),(1400,427),(1537,455)],10,-1,(255,111,127),0.8),
 ([(681,454),(814,458),(963,463),(1120,466),(1265,469)],14,1,(186,230,247),0.75),
 ([(681,458),(814,462),(963,467),(1120,470),(1265,473)],11,-1,(250,106,112),0.65),
 # Near roads continue beyond the visible glazing: vehicles leave behind the sill/mullion.
 ([(1080,568),(1114,579),(1154,596),(1203,616),(1266,641),(1500,752),(1770,884)],20,1,(180,228,249),1.2),
 ([(1080,572),(1114,583),(1154,600),(1203,620),(1266,645),(1460,738),(1700,850)],17,-1,(251,103,125),1.1),
]
routes=[]
for pts,count,direction,color,exposure in roads:
    pts=np.array(pts,dtype=np.float32)*np.array([SX,SY])
    lengths=np.sqrt(((pts[1:]-pts[:-1])**2).sum(1));cum=np.r_[0,np.cumsum(lengths)];total=cum[-1]
    # All identities traverse one full route in ten seconds. Unique random headways,
    # individual appearances and small independent velocity variations replace the V2 tile.
    minimum=.034
    gaps=minimum+rng.dirichlet(np.full(count,.45))*(1-count*minimum)
    offsets=np.mod(np.r_[0,np.cumsum(gaps[:-1])]+rng.random(),1)
    vehicles=[]
    for offset in offsets:
        vehicles.append(dict(offset=float(offset),phase=float(rng.uniform(0,TAU)),
            length=float(rng.uniform(1.8,5.5)),intensity=float(rng.uniform(.52,1.05))*exposure,
            color=np.clip(np.array(color)+rng.uniform(-20,16,3),0,255),amplitude=float(rng.uniform(.002,.005))))
    routes.append((pts,cum,total,count,direction,vehicles))

def point(route,distance):
    pts,cum,total,*_=route
    q=np.searchsorted(cum,distance,side='right')-1;q=max(0,min(len(pts)-2,q))
    u=(distance-cum[q])/(cum[q+1]-cum[q])
    return pts[q]*(1-u)+pts[q+1]*u

rain=[]
for count,lo,hi,opacity,cycles,width in [(1400,5,24,(16,60),(5,7,9,10),1),(160,17,39,(20,58),(3,4,5),1)]:
    for _ in range(count):
        rain.append((float(rng.uniform(-80,W+150)),float(rng.uniform(0,H+140)),float(rng.uniform(lo,hi)),int(rng.integers(*opacity)),int(rng.choice(cycles)),width,float(rng.uniform(.05,.115))))
drops=[(float(rng.uniform(440,1640)*SX),float(rng.uniform(0,1)),float(rng.uniform(30,90)*SY),float(rng.uniform(4,12)),float(rng.uniform(.4,1))) for _ in range(28)]

# Steam is drawn locally above the existing cup. Nothing in the furniture is warped.
steam_box=(int(565*SX),int(631*SY),int(651*SX),int(727*SY))
stx0,sty0,stx1,sty1=steam_box
steam_y,steam_x=np.mgrid[sty0:sty1,stx0:stx1].astype(np.float32)
steam_h=np.clip((723*SY-steam_y)/(85*SY),0,1)
steam_envelope=np.maximum(0,np.sin(math.pi*steam_h))**1.2
steam_envelope*=np.clip((723*SY-steam_y)/7,0,1)

def vehicle_distance(route,vehicle,t):
    total,direction=route[2],route[4]
    q=(vehicle['offset']+direction*t+vehicle['amplitude']*math.sin(TAU*t+vehicle['phase']))%1
    return q*total

def frame(index,debug=False):
    t=(index%N)/N
    a=TAU*t
    out=base.copy()
    # Water alone receives tiny, flowing horizontal refraction and travelling highlights.
    wx0,wy0,wx1,wy1=water_box
    wm=water[wy0:wy1,wx0:wx1];cx=x[wy0:wy1,wx0:wx1];cy=y[wy0:wy1,wx0:wx1]
    displacement=(1.0*np.sin(cy*.23-a*2)+.45*np.sin(cy*.43+cx*.015-a*3))*wm
    sample_x=np.clip(X[wy0:wy1,wx0:wx1]+displacement,0,W-1)
    xl=sample_x.astype(np.int32);xr=np.minimum(xl+1,W-1);frac=(sample_x-xl.astype(np.float32))[:,:,None]
    yi=np.arange(wy0,wy1)[:,None]
    refracted=base[yi,xl]*(1-frac)+base[yi,xr]*frac
    out[wy0:wy1,wx0:wx1]+=(refracted-base[wy0:wy1,wx0:wx1])*wm[:,:,None]
    shimmer=(.13*np.sin(y*.37+x*.013-a*2)+.055*np.sin(y*.83-x*.025-a*3))*water
    out+=base*shimmer[:,:,None]
    # Correlated color reflection moves over the existing polished floor reflection.
    reflected=(.075*np.sin(x*.018-a+1.8)+.045*np.sin(y*.12+x*.023-a*3))*floor
    out+=base*reflected[:,:,None]
    reflected_sign_gain=0
    for ni,(box,m,p,f,cy) in enumerate(neons):
        x0,y0,x1,y1=box
        if ni in (1,2,5):
            # Luminous bands travel inside existing vertical signs only.
            q=((cy-cy.min())/max(1,float(cy.max()-cy.min()))+t*f+p/TAU)%1
            band=np.exp(-((q-.46)/.16)**2)
            gain=-.18+.78*band+.055*math.sin(a+p)
        elif ni in (3,4,7):
            gain=.30*np.sin(cy*.115-a*f+p)+.11*np.sin(cy*.047+a*(f+1)+p)
        else:
            gain=.18*math.sin(a*f+p)+.08*math.sin(a*(f+2)+p)
        out[y0:y1,x0:x1]+=base[y0:y1,x0:x1]*(m*gain)[:,:,None]
        if ni==2:reflected_sign_gain=float(np.sum(m*gain)/max(.001,float(m.sum())))
    out+=base*(sign_response*reflected_sign_gain*.4)[:,:,None]
    gain=np.zeros((H,W),np.float32)
    for frequency,(s,c) in window_coefficients.items():
        gain+=s*math.sin(a*frequency)+c*math.cos(a*frequency)
    out+=base*gain[:,:,None]
    # Translating multi-scale fog patterns; integer temporal frequencies guarantee periodicity.
    field=.5+.22*np.sin(x*.023+y*.013-a)+.15*np.sin(x*.041-y*.028-a*2)+.10*np.sin(x*.089+y*.04-a*3)
    fog_alpha=fog*np.clip(field,0,1)*.16
    out=out*(1-fog_alpha[:,:,None])+fog_color*fog_alpha[:,:,None]
    # Render traffic with small heads, directionally correct tail trails, and restrained bloom.
    lights=Image.new('RGB',(W,H));ld=ImageDraw.Draw(lights)
    for route in routes:
        pts,cum,total,count,direction,vehicles=route
        for vehicle in vehicles:
            distance=vehicle_distance(route,vehicle,t)
            px,py=point(route,distance)
            endfade=min(1,distance/10,(total-distance)/10)
            if endfade<=0:continue
            depth=np.clip((py/SY-290)/380,.25,1)
            length=vehicle['length']*(.7+.6*depth)
            color=vehicle['color']*vehicle['intensity']
            for z in range(5,0,-1):
                back=distance-direction*z*length/5
                if back<0 or back>total:continue
                tx,ty=point(route,back)
                c=tuple(int(min(255,v*endfade*(1-z/7)*.8)) for v in color)
                ld.line((tx,ty,px,py),fill=c,width=1 if depth<.5 else 2)
            c=tuple(int(min(255,v*endfade)) for v in color)
            radius=.6+depth*.65
            ld.ellipse((px-radius,py-.55,px+radius,py+.55),fill=c)
    la=np.asarray(lights,dtype=np.float32)
    bloom=np.asarray(lights.filter(ImageFilter.GaussianBlur(3.2)),dtype=np.float32)
    out+=(la*.88+bloom*.65)*traffic_visibility[:,:,None]
    rainim=Image.new('RGBA',(W,H));rd=ImageDraw.Draw(rainim)
    for rx,y0,length,alpha,cycles,width,slant in rain:
        ry=(y0+t*cycles*(H+140))%(H+140)-70
        xx=rx-ry*slant
        light=float(luma[min(H-1,max(0,int(ry))),min(W-1,max(0,int(xx)))])/255
        rain_alpha=int(alpha*(.62+.45*light))
        rd.line((xx,ry,xx-length*slant,ry+length),fill=(166,203,231,rain_alpha),width=width)
    # Slow beads develop and slide a short distance, then fade; phases are staggered.
    for dx,phase,travel,length,weight in drops:
        q=(t+phase)%1
        dy=(phase*941%600)*SY+travel*q
        opacity=int(95*weight*math.sin(math.pi*q)**2)
        dx2=dx+math.sin(q*5+phase)*.5
        rd.line((dx2,dy-length,dx2,dy),fill=(171,211,237,opacity//3),width=2)
        rd.ellipse((dx2-.8,dy-1.5,dx2+.8,dy+1.5),fill=(199,227,247,opacity))
    ra=np.asarray(rainim,dtype=np.float32);alpha=ra[:,:,3]/255*glass
    out=out*(1-alpha[:,:,None])+ra[:,:,:3]*alpha[:,:,None]
    # Two faint, irregular vapor filaments. Density travels upward and dissipates,
    # with a ten-second turbulence period rather than a repeated five-second clip.
    vapor=np.zeros(steam_h.shape,np.float32)
    for k in range(2):
        cx=(605+k*3)*SX+steam_h*(5*np.sin(a+steam_h*4.1+k*2)+4*np.sin(a*2-steam_h*7.3+k))
        width=(.9+steam_h*2.5)*SX
        density=.55+.22*np.sin(steam_h*19-a*3+k)+.16*np.sin(steam_h*31-a*5+k)
        vapor+=np.exp(-((steam_x-cx)/width)**2)*steam_envelope*density*.13
    vapor=np.clip(vapor,0,.18)
    foreground=out[sty0:sty1,stx0:stx1]
    out[sty0:sty1,stx0:stx1]=foreground*(1-vapor[:,:,None])+np.array([202,198,185],np.float32)*vapor[:,:,None]
    return np.clip(out,0,255).astype(np.uint8)

def parallel_frames(count,rate):
    # All scene data is read-only. Bound prefetch to four frames to limit memory use.
    with ThreadPoolExecutor(max_workers=2) as pool:
        queue=deque(pool.submit(frame,i*FPS/rate) for i in range(min(4,count)))
        for i in range(count):
            result=queue.popleft().result()
            if i+4<count:queue.append(pool.submit(frame,(i+4)*FPS/rate))
            yield result

def render():
    preview='--draft' in sys.argv
    rate=15 if preview else FPS
    count=rate*DURATION
    filename='Preview-Draft.mp4' if preview else 'Cyberpunk-Apartment-V3-4K.mp4'
    vf='format=yuv420p' if preview else 'scale=3840:2160:flags=lanczos,format=yuv420p'
    cmd=[FF,'-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(rate),'-i','pipe:0','-vf',vf,'-an','-c:v','libx264','-preset','fast' if preview else 'slow','-crf','16' if preview else '11','-g','120','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(R/filename)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    first=frame(0);previous=first;steps=[];begin=time.time()
    for i,f in enumerate(parallel_frames(count,rate)):
        if i:steps.append(float(np.abs(f.astype(np.int16)-previous.astype(np.int16)).mean()))
        if i in (0,count//4,count//2,3*count//4,count-1):Image.fromarray(f).save(R/f'frame-{i:03}.jpg',quality=95)
        p.stdin.write(f.tobytes());previous=f
        if i%30==0:print(f'{i}/{count} frames, {time.time()-begin:.1f}s',flush=True)
    p.stdin.close()
    if p.wait():raise RuntimeError('FFmpeg failed')
    seam=float(np.abs(first.astype(np.int16)-previous.astype(np.int16)).mean())
    report={'duration':DURATION,'fps':rate,'frames':count,'source_dimensions':[1672,941],'export_dimensions':[W,H] if preview else [3840,2160],'upscaled':True,'exact_periodic_match':bool(np.array_equal(frame(N),first)),'is_not_five_second_repeat':bool(not np.array_equal(frame(N//2),first)),'mean_adjacent_frame_difference':float(np.mean(steps)),'maximum_adjacent_frame_difference':max(steps),'seam_difference':seam,'seconds_to_render':round(time.time()-begin,1)}
    (R/('draft-report.json' if preview else 'quality-report.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':render()
