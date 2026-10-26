"""Deliver the unchanged v8 native scene as a clean 60-second 4K loop."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys, subprocess, json, hashlib, time, re
import numpy as np
import cv2
from PIL import Image

D = Path(__file__).resolve().parent
H = D.parent
sys.path.insert(0, str(H))
from render_spirewatch import Spirewatch, sha, old
W, HEIGHT, FPS, COUNT = 3840, 2160, 30, 1800
MASTER = D / 'Spirewatch-v8-60s-4K-loop.mp4'

def save(name, value):
    (D/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

def scene():
    s = Spirewatch()
    expected = json.loads((H/'delivery-v8.json').read_text())['fingerprint']
    assert s.fingerprint() == expected, 'Preview fingerprint changed'
    return s

def worker(index):
    s = scene()
    s.config['preview_size'] = [W, HEIGHT]
    original = s.frame
    s.frame = lambda t, only=None: original(t+index*15, only)
    path = D/'parts'/f'part-{index:02d}.mp4'
    old.encode(s, path, 15)
    return {'index':index, 'start_seconds':index*15, 'sha256':sha(path)}

def render():
    assert not MASTER.exists(), 'Preserve existing master'
    s = scene()
    samples=[]
    for t in [0,4,12,24,40,59.97]:
        # The last saved still is named 59.97 but represents 59 + 29/30.
        exact=59+29/30 if t==59.97 else t
        p=H/f'review-{t:05.2f}.png'
        assert np.array_equal(s.frame(exact), np.array(Image.open(p).convert('RGB'))), str(p)
        samples.append(exact)
    # Two extra storm stills predate the finishing adjustments; the delivered
    # preview, rather than those exploratory PNGs, is authoritative at these times.
    ff=s.config['ffmpeg']; indices=[552,1296]; selection='+'.join('eq(n\\,%d)'%i for i in indices)
    decoded=subprocess.check_output([ff,'-v','error','-i',str(H/'spirewatch-v8-preview-60s.mp4'),'-vf','select='+selection,'-vsync','0','-pix_fmt','yuv420p','-f','rawvideo','-'])
    size=1280*720*3//2
    assert len(decoded)==len(indices)*size
    for j,i in enumerate(indices):
        expected=subprocess.run([ff,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{s.w}x{s.h}','-r','30','-i','pipe:0','-frames:v','1','-vf','scale=1280:720:flags=lanczos:out_color_matrix=bt709:out_range=tv','-pix_fmt','yuv420p','-f','rawvideo','-'],input=s.frame(i/FPS).tobytes(),stdout=subprocess.PIPE,check=True).stdout
        assert expected==decoded[j*size:(j+1)*size],('Delivered preview mismatch',i)
    save('source-verification.json', {'fingerprint':s.fingerprint(), 'exact_native_saved_samples':samples,'exact_delivered_preview_storm_frames':indices,'excluded_exploratory_stills':['review-18.40.png','review-43.20.png'],
        'authorization':'sure make a 60s 4k loop', 'source_detail':'1672x941 native artwork; native frames upscaled directly with Lanczos, not the 720p preview',
        'unchanged_effects':True, 'opening_titles':False, 'audio':False})
    (D/'parts').mkdir(exist_ok=True)
    results=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for job in as_completed([pool.submit(worker,i) for i in range(4)]):
            results.append(job.result());print('4K chunk complete',results[-1]['index'],flush=True)
    results.sort(key=lambda r:r['index'])
    concat=D/'parts/concat.txt'
    concat.write_text(''.join("file 'part-%02d.mp4'\n"%i for i in range(4)))
    subprocess.run([s.config['ffmpeg'],'-v','error','-n','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(MASTER)],check=True)
    save('render.json', {'chunks':results,'master_sha256':sha(MASTER),'script_sha256':sha(__file__)})

def verify():
    s=scene(); ff=s.config['ffmpeg']; framebytes=W*HEIGHT*3
    masks={}
    for k,m in {**s.layer_masks,'combined':s.active}.items():
        full=cv2.resize(m.astype(np.uint8),(W,HEIGHT),interpolation=cv2.INTER_NEAREST)
        yy,xx=np.where(full); a,b,z,d=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
        masks[k]=(a,b,z,d,full[b:d,a:z].copy())
    maximum={k:0. for k in masks}; near={k:0. for k in masks}
    first=prev=None; hashes=[]; count=0
    with (D/'decode.log').open('wb') as log:
        p=subprocess.Popen([ff,'-hide_banner','-nostats','-i',str(MASTER),'-map','0:v:0','-vf','showinfo,scale=in_color_matrix=bt709:out_range=full','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=log)
        while True:
            raw=p.stdout.read(framebytes)
            if not raw:break
            assert len(raw)==framebytes
            f=np.frombuffer(raw,np.uint8).reshape(HEIGHT,W,3)
            hashes.append(hashlib.sha256(raw).hexdigest())
            if first is None:first=f.copy()
            else:
                diff=cv2.absdiff(f,prev)
                for k,(a,b,z,d,m) in masks.items():
                    value=sum(cv2.mean(diff[b:d,a:z],mask=m)[:3])/3
                    maximum[k]=max(maximum[k],value)
                    if count<15 or count>=1785:near[k]=max(near[k],value)
            if count in [0,450,552,1296,1799]:Image.fromarray(f).save(D/f'decoded-{count:04d}.jpg',quality=95)
            prev=f.copy();count+=1
            if count%150==0:print('Full 4K decode/seam checks',count,'/',COUNT,flush=True)
        assert p.wait()==0 and count==COUNT
    text=(D/'decode.log').read_text()
    timestamps=re.findall(r'\bn:\s*(\d+)\s+pts:\s*\d+\s+pts_time:([\d.]+)',text)
    assert len(timestamps)==COUNT,len(timestamps)
    assert all(int(n)==i and abs(float(t)-i/FPS)<.00006 for i,(n,t) in enumerate(timestamps))
    assert '3840x2160' in text and 'Audio:' not in text
    diff=cv2.absdiff(prev,first);checks={}
    for k,(a,b,z,d,m) in masks.items():
        value=sum(cv2.mean(diff[b:d,a:z],mask=m)[:3])/3
        assert value<=maximum[k]*1.1+.012,(k,value,maximum[k])
        assert value<=near[k]*1.25+.012,(k,'quiet-neighbour',value,near[k])
        checks[k]={'seam_mae':value,'ordinary_max':maximum[k],'neighbour_max':near[k],'pass':True}
    assert hashes[0]!=hashes[-1] and len({hashes[i] for i in [0,600,1200]})==3
    # All join-adjacent pictures plus lightning/endpoints must equal direct native renders.
    indices=[0,449,450,552,899,900,1296,1349,1350,1799]
    selection='+'.join('eq(n\\,%d)'%i for i in indices)
    actual=subprocess.check_output([ff,'-v','error','-i',str(MASTER),'-vf','select='+selection,'-vsync','0','-pix_fmt','yuv420p','-f','rawvideo','-'])
    size=W*HEIGHT*3//2;assert len(actual)==size*len(indices)
    for j,i in enumerate(indices):
        expected=subprocess.run([ff,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{s.w}x{s.h}','-r','30','-i','pipe:0','-frames:v','1','-vf',f'scale={W}:{HEIGHT}:flags=lanczos:out_color_matrix=bt709:out_range=tv','-pix_fmt','yuv420p','-f','rawvideo','-'],input=s.frame(i/FPS).tobytes(),stdout=subprocess.PIPE,check=True).stdout
        assert actual[j*size:(j+1)*size]==expected,('Native picture mismatch',i)
    save('delivery-validation.json',{'master':MASTER.name,'sha256':sha(MASTER),'bytes':MASTER.stat().st_size,'dimensions':[W,HEIGHT],'fps':FPS,'seconds':60,'frames':COUNT,'audio':False,'codec':'H.264 lossless QP0 yuv420p BT.709','native_source_dimensions':[s.w,s.h],'upscale':'Lanczos from native frames','fingerprint':s.fingerprint(),'full_decode':True,'all_timestamps_checked':True,'no_duplicate_endpoint':True,'distinct_0_20_40':True,'regional_and_composite_seams':checks,'exact_native_yuv_frame_checks':indices,'assistant_continuous_playback':False,'new_commit_or_push':False})
    print('PASS: complete 4K minute, regional seams and direct native picture identity',flush=True)

if __name__=='__main__':
    if '--verify-only' not in sys.argv:render()
    verify()
