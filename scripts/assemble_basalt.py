"""Encode once, repeat without generation, fully decode-check a long ambient delivery."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import cv2
import imageio_ffmpeg
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'creative/basalt-transmission/animation'
FF=imageio_ffmpeg.get_ffmpeg_exe()
PREFIX='baseline-v1b'
MASTER=OUT/'baseline-v1-loop-4k-master.mp4'
LOOP=OUT/f'{PREFIX}-loop-4k.mp4'
LONG=OUT/f'{PREFIX}-20min-4k.mp4'

def run(args):
    subprocess.run([FF,'-hide_banner','-loglevel','error','-n',*map(str,args)],check=True)

def encode():
    # CRF16 introduced an encoded seam outlier; preserve validated master pixels.
    run(['-i',MASTER,'-map','0:v:0','-an','-c:v','copy','-movflags','+faststart',LOOP])
    hashes=[]
    for path in [MASTER,LOOP]:
        r=subprocess.run([FF,'-hide_banner','-loglevel','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','streamhash','-hash','sha256','-'],capture_output=True,text=True,check=True)
        hashes.append(r.stdout.strip())
    assert hashes[0]==hashes[1], 'Remux changed the validated video stream'
    print('Delivery loop encoded',LOOP.stat().st_size,flush=True)

def compare():
    report={};a=cv2.VideoCapture(str(MASTER));b=cv2.VideoCapture(str(LOOP))
    # Compare matched decoded 4K frames in motion patches and overall.
    regions={'exhaust':(280,247,588,375),'haze':(1035,475,1672,560),'sky':(700,20,1300,180)}
    for i in [0,60,150,300,450,599]:
        a.set(cv2.CAP_PROP_POS_FRAMES,i);b.set(cv2.CAP_PROP_POS_FRAMES,i)
        oka,x=a.read();okb,y=b.read();assert oka and okb
        values={'overall_mae':float(np.abs(x.astype(float)-y.astype(float)).mean())}
        for name,(x0,y0,x1,y1) in regions.items():
            x0,x1=round(x0*3840/1672),round(x1*3840/1672);y0,y1=round(y0*2160/941),round(y1*2160/941)
            values[name+'_mae']=float(np.abs(x[y0:y1,x0:x1].astype(float)-y[y0:y1,x0:x1].astype(float)).mean())
        report[str(i)]=values
        if i==150:cv2.imwrite(str(OUT/f'{PREFIX}-delivery-decoded.jpg'),cv2.resize(y,(1280,720)))
    a.release();b.release()
    (OUT/f'{PREFIX}-encoding-check.json').write_text(json.dumps(report,indent=2))
    print('Encoding comparison',json.dumps(report),flush=True)

def assemble():
    run(['-stream_loop','59','-i',LOOP,'-map','0:v:0','-an','-c:v','copy','-t','1200','-movflags','+faststart',LONG])
    print('Twenty-minute delivery assembled',LONG.stat().st_size,flush=True)

def decode_hashes(path,output):
    # Every original-resolution frame is decoded, then scaled for compact hash evidence.
    run(['-threads','8','-i',path,'-map','0:v:0','-an','-vf','scale=32:18:flags=area','-fps_mode','passthrough','-f','framemd5',output])
    lines=output.read_text().splitlines()
    tb=next(line for line in lines if line.startswith('#tb'))
    assert tb.endswith('1/30'),tb
    records=[]
    for line in lines:
        if line.startswith('#') or not line.strip():continue
        fields=[v.strip() for v in line.split(',')]
        records.append((int(fields[1]),int(fields[2]),int(fields[3]),fields[5]))
    return records

def validate():
    cap=cv2.VideoCapture(str(LONG))
    metadata={'width':int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),'height':int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),'fps':cap.get(cv2.CAP_PROP_FPS),'container_frames':int(cap.get(cv2.CAP_PROP_FRAME_COUNT))};cap.release()
    assert metadata=={'width':3840,'height':2160,'fps':30.0,'container_frames':36000},metadata
    probe=subprocess.run([FF,'-hide_banner','-i',str(LONG)],capture_output=True,text=True)
    assert 'Audio:' not in probe.stderr
    loop_records=decode_hashes(LOOP,OUT/f'{PREFIX}-loop-decoded.framemd5')
    assert len(loop_records)==600
    print('Decoding all 36,000 delivery frames for timestamp and repeated-frame checks...',flush=True)
    records=decode_hashes(LONG,OUT/f'{PREFIX}-20min-decoded.framemd5')
    assert len(records)==36000,len(records)
    for i,(dts,pts,duration,h) in enumerate(records):
        assert dts==i and pts==i and duration==1,(i,dts,pts,duration)
        assert h==loop_records[i%600][3],f'Repeated frame mismatch at {i}'
    # Compare full-resolution decoded frames around early/middle/late joins.
    cap=cv2.VideoCapture(str(LONG));ref=cv2.VideoCapture(str(LOOP));joins={}
    for index in [599,600,17999,18000,35399,35400,35999]:
        cap.set(cv2.CAP_PROP_POS_FRAMES,index);ref.set(cv2.CAP_PROP_POS_FRAMES,index%600)
        ok,a=cap.read();ok2,b=ref.read();assert ok and ok2 and np.array_equal(a,b),index
        joins[str(index)]='full-resolution pixels equal to loop reference'
    cap.release();ref.release()
    report={'metadata':metadata,'decoded_frames':len(records),'duration_seconds':len(records)/30,'audio':False,'all_pts_dts_sequential':True,'all_repeated_frame_hashes_match':True,'full_resolution_join_checks':joins,'sha256':hashlib.sha256(LONG.read_bytes()).hexdigest(),'bytes':LONG.stat().st_size,'method':'Validated QP0 master loop repeated sixty times with stream copy; every delivery frame decoded and hashed after reduction','visual_review':'Temporal samples and decoded frames; no continuous playback review claimed','artistic_status':'awaiting user review','source_resolution_note':'4K export upscaled from 1672x941 artwork'}
    (OUT/f'{PREFIX}-20min-validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['encode','compare','assemble','validate']);p.add_argument('--version',choices=['v1b','v2'],default='v1b');a=p.parse_args()
    PREFIX='baseline-'+a.version
    MASTER=OUT/('baseline-'+('v1' if a.version=='v1b' else a.version)+'-loop-4k-master.mp4')
    LOOP=OUT/(PREFIX+'-loop-4k.mp4');LONG=OUT/(PREFIX+'-20min-4k.mp4')
    globals()[a.stage]()
