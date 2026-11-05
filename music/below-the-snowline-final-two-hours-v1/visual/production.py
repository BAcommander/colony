"""Native scene samples, independent seam/safety checks and continuous 4K encoding."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, subprocess, time
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import numpy as np
from PIL import Image, ImageDraw
import render_native as n

H=Path(__file__).resolve().parent
CACHE=H/'cache'
MASTER=H/'masters'/'Snowline-v6-loop-120s-4K.mp4'
FF='ffmpeg'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value):
    (H/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
def mod(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def controls():
    CACHE.mkdir(exist_ok=True);s=n.Scene();started=time.time()
    raw=np.array(Image.open(n.H/'source.png').convert('RGB'))
    assert np.array_equal(s.base,raw),'Native base detail changed'
    # The real backward-map Jacobian and every contributing bilinear source
    # corner are checked independently of the renderer's clearance multiplier.
    x0,y0,x1,y1=s.skyroi;dest=s.sky[y0:y1,x0:x1]>1e-5
    dist=cv2.distanceTransform((s.cloud_safe>0).astype(np.uint8),cv2.DIST_L2,5)
    safe=dist>2*n.R;minimum_j=1e9;minimum_clear=1e9;max_motion=0
    for t in np.arange(0,120.01,.5):
        mx,my=s.cloud_maps(float(t));dyx,dxx=np.gradient(mx.astype(float));dyy,dxy=np.gradient(my.astype(float))
        jac=dxx*dyy-dyx*dxy;minimum_j=min(minimum_j,float(jac[dest].min()))
        fx=np.floor(mx).astype(int);fy=np.floor(my).astype(int);dx=mx-fx;dy=my-fy
        for ox,oy in [(0,0),(1,0),(0,1),(1,1)]:
            weight=(dx if ox else 1-dx)*(dy if oy else 1-dy);keep=dest&(weight>1e-6)
            xx,yy=(fx+ox)[keep],(fy+oy)[keep]
            assert ((xx>=0)&(xx<n.W)&(yy>=0)&(yy<n.HEIGHT)).all()
            assert safe[yy,xx].all(),('Cloud source touches protected silhouette',t)
            minimum_clear=min(minimum_clear,float(dist[yy,xx].min()))
        nx,ny=s.cloud_maps(float(t+1/30));max_motion=max(max_motion,float(np.hypot(nx-mx,ny-my)[dest].max()))
    assert minimum_j>.3 and max_motion<.15
    # Independent V6 cliff traces are loaded only from the accepted audit code.
    # Fixed explicit guard regions below protect the interior of both rock/frost.
    trace=np.array([[708,56],[707,60],[706,64],[705,68],[705,72],[704,76],[702,80],[702,84],[701,88],[698,92],[698,96],[699,100],[699,104],[706,108],[711,112],[714,116],[719,120],[720,124],[720,128],[722,132],[725,136],[728,140],[729,144],[733,148],[733,152],[735,156],[739,160],[739,164],[743,168]],float)
    yy,xx=np.mgrid[:n.HEIGHT,:n.W];boundary=np.interp(yy,trace[:,1],trace[:,0])
    rock=(xx>=640)&(xx<=boundary-2)&(yy>=65)&(yy<=135)
    protected=rock|((xx>=1620)&(yy>=40)&(yy<=145))
    count=0;endpoints=[]
    for a,b,start,end,reverse,width in [(27,30,-5,70,False,50),(96,98,70,118,True,40)]:
        for t in np.arange(a,b+1/60,1/30):
            f=s.base.astype(np.float32);s.shuttle_pass(f,float(t),start,end,reverse,width)
            assert np.array_equal(f[protected],s.base[protected]);count+=1
        for t in [start+1/30,end-1/30]:
            f=s.base.astype(np.float32);s.shuttle_pass(f,t,start,end,reverse,width)
            changed=int(np.any(f!=s.base,axis=2).sum());assert changed==0
            endpoints.append({'time':t,'changed_pixels':changed})
    # Keep emitter colour checks independent of the source hull image.
    old=s.ship_sprites;s.ship_sprites={k:np.zeros_like(v) for k,v in old.items()};engine=[]
    for t,start,end,reverse,width in [(40,-5,70,False,50),(90,70,118,True,40)]:
        f=np.zeros_like(s.base,dtype=np.float32);s.shuttle_pass(f,t,start,end,reverse,width)
        total=f.sum(axis=(0,1),dtype=np.float64);assert total[2]>total[1]>total[0];engine.append(total.tolist())
    s.ship_sprites=old
    # Positive lower bounds include maximum sinusoidal gust/flutter derivative.
    velocities=[]
    for sx,sy,vx,vy,r,opacity,p in s.flakes:
        rx=max(1,round(vx*1.08*120/(n.W+80*n.R)))*(n.W+80*n.R)/120
        ry=max(1,round(vy*120/(n.HEIGHT+50*n.RY)))*(n.HEIGHT+50*n.RY)/120
        velocities.append((rx-vx*2.2*abs(n.omega(1/13))-8*n.R*abs(n.omega(1/7)),ry-4*n.RY*abs(n.omega(1/5))))
    velocities=np.array(velocities);assert np.all(velocities>0),'Snow may reverse'
    # Native samples, including two actual adjacent frames on either side of
    # the repeat join. Exact120s periodicity alone cannot prove a smooth seam.
    times=[0,1/30,2/30,27.5,40,48,96.7,119.9,120-2/30,120-1/30]
    frames={t:s.frame(t) for t in times}
    for t in [0,27.5,40,48,96.7]:assert np.array_equal(frames[t],s.frame(t+120))
    assert np.array_equal(s.frame(120),frames[0])
    outside=s.full_active<1e-8
    for t,f in frames.items():assert np.array_equal(f[outside],s.base[outside]),('Static outside pixels changed',t)
    for t in [0,27.5,40,48,96.7,120-1/30]:Image.fromarray(frames[t]).save(CACHE/f'native-{t:07.3f}.png')
    regions={'full':(0,0,n.W,n.HEIGHT),'sky':(950,40,1500,170),'console':(0,200,215,610),'bridge':(800,390,1400,440),'weather':(450,220,1500,780)}
    seam={}
    for name,(a,b,z,d) in regions.items():
        def diff(x,y):return np.abs(frames[x][b:d,a:z].astype(float)-frames[y][b:d,a:z].astype(float))
        before=diff(120-2/30,120-1/30);join=diff(120-1/30,0);after=diff(0,1/30)
        neighbour=max(before.mean(),after.mean(),.02)
        seam[name]={'mean_abs_join':float(join.mean()),'mean_abs_before':float(before.mean()),'mean_abs_after':float(after.mean()),'join_vs_neighbour':float(join.mean()/neighbour),'p99_join':float(np.percentile(join,99))}
        assert join.mean()<neighbour*2.2+.06,(name,seam[name])
    # Preserve material size and crisp native detail without comparing a
    # downscaled preview as if it contained native resolution.
    approved=mod(n.H/'render_v6.py','approved_v6').Scene()
    original=approved.frame(48);candidate=cv2.resize(frames[48],(1280,720),interpolation=cv2.INTER_AREA)
    Image.fromarray(original).save(CACHE/'approved-v6-48s.png');Image.fromarray(candidate).save(CACHE/'native-downsampled-48s.png')
    boxes={'cannon-shuttle':(700,65,1320,225),'left-cliff':(650,60,815,180),'console':(0,250,200,610)}
    sheet=Image.new('RGB',(1280,720),(15,18,24));sheet.paste(Image.fromarray(original).resize((640,360)),(0,0));sheet.paste(Image.fromarray(candidate).resize((640,360)),(640,0))
    draw=ImageDraw.Draw(sheet);draw.text((8,8),'Approved V6 at48s',fill='white');draw.text((648,8),'Native periodic adaptation at48s',fill='white')
    for i,(name,box) in enumerate(boxes.items()):
        a,b,z,d=box;oldbox=tuple(round(v*(1280/1672 if k%2==0 else 720/941)) for k,v in enumerate(box))
        tile=Image.fromarray(original).crop(oldbox);tile.thumbnail((400,160));sheet.paste(tile,(i*426,390));draw.text((i*426,370),name+' approved',fill='white')
        tile=Image.fromarray(frames[48]).crop(box);tile.thumbnail((400,160));sheet.paste(tile,(i*426,555));draw.text((i*426,535),name+' native',fill='white')
    sheet.save(CACHE/'appearance-control.jpg',quality=95)
    join=Image.new('RGB',(n.W,4*240),(0,0,0))
    for i,t in enumerate([120-2/30,120-1/30,0,1/30]):join.paste(Image.fromarray(frames[t]).crop((0,0,n.W,240)),(0,i*240))
    join.save(CACHE/'seam-upper-scene.png')
    periodic={}
    for name,fn in [('interior',s.interior),('sky',s.sky_layer),('traffic',s.traffic),('hardware',s.hardware)]:
        a=s.base.astype(np.float32);b=a.copy();fn(a,0);fn(b,120)
        delta=float(np.max(np.abs(a-b)));assert delta<.002,(name,delta);periodic[name]=delta
    # Fog/plumes/snow and shadow also enter the end-to-start regional check.
    report={'status':'passed','scope':'Native sampled analytic/source/occlusion/seam checks; final encoded review separate','native_source_exact':True,'native_dimensions':[n.W,n.HEIGHT],'period_seconds':120,'independent_map_samples':241,'minimum_backward_jacobian':minimum_j,'minimum_bilinear_source_clearance_native_pixels':minimum_clear,'maximum_map_one_frame_motion_native_pixels':max_motion,'cliff_crossing_frames':count,'protected_rock_exact':True,'traffic_endpoints':endpoints,'engine_rgb_sums':engine,'snow_positive_velocity_lower_bound_native_px_s':velocities.min(axis=0).tolist(),'raw_layer_periodicity_max_rgb_error':periodic,'seam_metrics':seam,'outside_active_pixels_exact':True,'source_and_renderer_hashes':{str(p.relative_to(H)):sha(p) for p in [H/'render_native.py',H/'prepare_native.py',H/'source-manifest.json']},'seconds_to_audit':time.time()-started,'artistic_approval':'Approved V6 treatment retained; production adaptation technical and image review only'}
    save('native-validation.json',report);print(json.dumps(report,indent=2),flush=True)

def encoder(output,seconds):
    return [FF,'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{n.W}x{n.HEIGHT}','-r','30','-i','pipe:0','-an','-vf','scale=3840:2160:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-preset','veryfast','-qp','0','-bf','0','-threads','8','-g','60','-keyint_min','60','-sc_threshold','0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bsf:v','h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1','-movflags','+faststart',str(output)]

def encode(benchmark=False):
    seconds=2 if benchmark else 120
    path=CACHE/'benchmark-final-2s-4K.mp4' if benchmark else MASTER;path.parent.mkdir(parents=True,exist_ok=True)
    assert not path.exists(),path
    assert json.loads((H/'native-validation.json').read_text())['status']=='passed'
    scene=n.Scene();cmd=encoder(path,seconds);p=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time();render_time=0
    try:
        for i in range(seconds*30):
            before=time.time();frame=scene.frame((48 if benchmark else 0)+i/30);render_time+=time.time()-before;p.stdin.write(frame.tobytes())
            if i%150==0:print(json.dumps({'frame':i,'total':seconds*30,'elapsed':round(time.time()-start,1)}),flush=True)
    finally:p.stdin.close()
    assert p.wait()==0
    elapsed=time.time()-start
    report={'status':'encoded-awaiting-decoded-validation','output':str(path),'seconds':seconds,'frames':seconds*30,'dimensions':[3840,2160],'fps':30,'elapsed_seconds':elapsed,'native_frame_render_seconds':render_time,'bytes':path.stat().st_size,'sha256':sha(path),'command':cmd,'projected_full_render_minutes':elapsed/seconds*2,'projected_full_master_gib':path.stat().st_size/seconds*120/2**30}
    save('benchmark.json' if benchmark else 'encode-receipt.json',report);print(json.dumps(report,indent=2),flush=True)

def encode_part(index):
    scene=n.Scene();path=CACHE/f'part-{index:02d}.mp4';assert not path.exists(),path
    cmd=encoder(path,20);cmd[cmd.index('-threads')+1]='2'
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
    try:
        for frame in range(600):p.stdin.write(scene.frame(index*20+frame/30).tobytes())
    finally:p.stdin.close()
    assert p.wait()==0
    return {'part':index,'output':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'elapsed_seconds':time.time()-start,'command':cmd}

def parallel_render():
    assert json.loads((H/'native-validation.json').read_text())['status']=='passed'
    assert not MASTER.exists();MASTER.parent.mkdir(exist_ok=True);start=time.time();parts=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(encode_part,i) for i in range(6)]):
            result=future.result();parts.append(result);print(json.dumps({k:v for k,v in result.items() if k!='command'}),flush=True)
    parts.sort(key=lambda v:v['part']);listing=CACHE/'native-parts.concat.txt'
    listing.write_text(''.join("file '"+v['output'].replace('\\','/')+"'\n" for v in parts),encoding='utf-8')
    cmd=[FF,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-c','copy','-an','-bsf:v','h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(MASTER)]
    subprocess.run(cmd,check=True)
    save('encode-receipt.json',{'status':'encoded-awaiting-decoded-validation','output':str(MASTER),'seconds':120,'frames':3600,'dimensions':[3840,2160],'fps':30,'elapsed_seconds':time.time()-start,'bytes':MASTER.stat().st_size,'sha256':sha(MASTER),'parts':parts,'concat_command':cmd})
    print('Master encoded; decoded validation pending',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['samples','benchmark','render','parallel-render']);a=p.parse_args()
    if a.stage=='samples':controls()
    elif a.stage=='parallel-render':parallel_render()
    else:encode(a.stage=='benchmark')
