"""Decode every 4K master picture, check timestamps, exact native controls and joins."""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
from PIL import Image,ImageDraw
import production as p

H=p.H;MASTER=p.MASTER;FF=p.FF;CACHE=p.CACHE

def rows(path):
    return [[x.strip() for x in line.split(',')] for line in path.read_text().splitlines() if line and not line.startswith('#')]

def main():
    begin=time.time();receipt=json.loads((H/'encode-receipt.json').read_text());assert receipt['sha256']==p.sha(MASTER)
    controls=json.loads((H/'native-validation.json').read_text())
    assert controls['source_and_renderer_hashes']['render_native.py']==p.sha(H/'render_native.py')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_packets','-show_entries','packet=pts,dts,duration:stream=codec_name,width,height,pix_fmt,r_frame_rate,time_base,nb_frames,duration,color_range,color_space,color_transfer,color_primaries,has_b_frames','-of','json',str(MASTER)]))
    stream=probe['streams'][0];packets=probe.pop('packets')
    assert stream['width']==3840 and stream['height']==2160 and stream['r_frame_rate']=='30/1' and stream['has_b_frames']==0
    assert stream['color_space']=='bt709' and stream['color_primaries']=='bt709' and stream['color_transfer']=='bt709' and stream['color_range']=='tv'
    assert stream['pix_fmt']=='yuv420p' and len(packets)==3600
    a,b=map(int,stream['time_base'].split('/'));step=b//(30*a);assert step*30*a==b
    for i,packet in enumerate(packets):assert packet['pts']==i*step and packet['dts']==i*step and packet['duration']==step,(i,packet)
    allhash=CACHE/'master-4K.framemd5'
    repair_path=H/'metadata-repair.json'
    if repair_path.exists():
        repair=json.loads(repair_path.read_text());assert repair['status']=='passed' and repair['after_sha256']==p.sha(MASTER) and repair['master_framemd5_sha256']==p.sha(allhash)
    else:subprocess.run([FF,'-v','error','-y','-i',str(MASTER),'-map','0:v:0','-an','-f','framemd5',str(allhash)],check=True)
    decoded=rows(allhash);assert len(decoded)==3600
    for i,line in enumerate(decoded):assert int(line[1])==i and int(line[2])==i and int(line[3])==1,(i,line)
    boundaries=[0,600,1200,1800,2400,3000]
    indices=sorted(set([825,1200,1440,2901]+[(i+k)%3600 for i in boundaries for k in [-2,-1,0,1]]))
    scene=p.n.Scene();expect=CACHE/'native-controls-4K.framemd5'
    cmd=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf','scale=3840:2160:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-f','framemd5',str(expect)]
    encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for index in indices:encoder.stdin.write(scene.frame(index/30).tobytes())
    finally:encoder.stdin.close()
    assert encoder.wait()==0
    expected=rows(expect);assert len(expected)==len(indices)
    for row,index in zip(expected,indices):assert row[-1]==decoded[index][-1],('Native picture mismatch',index,row[-1],decoded[index][-1])
    select='+'.join(f'eq(n\\,{i})' for i in indices)
    raw=subprocess.check_output([FF,'-v','error','-i',str(MASTER),'-vf',f'select={select},scale=1280:720:flags=area','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
    pictures=np.frombuffer(raw,np.uint8).reshape(len(indices),720,1280,3);frames=dict(zip(indices,pictures))
    metrics=[]
    regions={'full':(0,0,1280,720),'sky':(727,31,1148,130),'console':(0,153,165,467),'bridge':(612,298,1072,337)}
    for boundary in boundaries:
        a,b,c,d=[(boundary+k)%3600 for k in [-2,-1,0,1]];result={'join_frame':boundary,'regions':{}}
        for name,(x0,y0,x1,y1) in regions.items():
            def diff(q,r):return np.abs(frames[q][y0:y1,x0:x1].astype(float)-frames[r][y0:y1,x0:x1].astype(float))
            before,join,after=diff(a,b),diff(b,c),diff(c,d);normal=max(float(before.mean()),float(after.mean()),.02)
            result['regions'][name]={'join_mean_absolute_rgb_change':float(join.mean()),'before':float(before.mean()),'after':float(after.mean()),'ratio_to_larger_neighbour':float(join.mean()/normal)}
            assert join.mean()<normal*2.2+.08,(boundary,name,result)
        metrics.append(result)
    display=[0,825,1200,1440,2901,3599];sheet=Image.new('RGB',(1280,1080))
    draw=ImageDraw.Draw(sheet)
    for i,index in enumerate(display):
        image=Image.fromarray(frames[index]);image.save(CACHE/f'decoded4K-{index:04d}-720p.png')
        sheet.paste(image.resize((640,360)),((i%2)*640,(i//2)*360));draw.text(((i%2)*640+8,(i//2)*360+8),f'Decoded4K {index/30:.3f}s',fill='white')
    sheet.save(CACHE/'decoded4K-contact-sheet.jpg',quality=94)
    report={'status':'passed','output':str(MASTER),'sha256':p.sha(MASTER),'bytes':MASTER.stat().st_size,'seconds':120,'dimensions':[3840,2160],'native_dimensions':[1672,941],'fps':30,'frames':3600,'full_4K_decode':True,'all_pts_dts_durations_exact':True,'bt709_tv':True,'lossless_native_to_4k_yuv_control_frames_exact':indices,'all_five_part_joins_and_loop_boundary_checked':True,'decoded_join_metrics':metrics,'probe':probe,'raw_frame_hashes':str(allhash),'native_validation':'native-validation.json','source_snapshot':'source-manifest.json','renderer_sha256':p.sha(H/'render_native.py'),'production_script_sha256':p.sha(H/'production.py'),'verification_script_sha256':p.sha(Path(__file__)),'verification_seconds':time.time()-begin,'inspection':'Technical decoding/native controls; decoded still inspection separately reported; no continuous playback claim'}
    p.save('master-validation.json',report);print(json.dumps({k:report[k] for k in ['status','output','seconds','frames','bytes','sha256','verification_seconds']},indent=2),flush=True)

if __name__=='__main__':main()
