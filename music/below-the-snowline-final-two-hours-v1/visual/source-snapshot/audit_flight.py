"""Independent cliff-occlusion, engine-colour and unchanged-layer checks for V6."""
from pathlib import Path
import importlib.util
import inspect
import json
import hashlib
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'below-the-snowline-animation-v5'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    oldmod = module(OLD / 'render_v5.py', 'flight_audit_v5')
    newmod = module(HERE / 'render_v6.py', 'flight_audit_v6')
    old, new = oldmod.Scene(), newmod.Scene()
    # Trace was independently drawn against source.png at 6x/10x magnification;
    # use rock INTERIOR, two native pixels left of the visible snowy boundary.
    # This list is deliberately not loaded from V6's production geometry.
    trace = np.array([[708,56],[707,60],[706,64],[705,68],[705,72],
        [704,76],[702,80],[702,84],[701,88],[698,92],[698,96],
        [699,100],[699,104],[706,108],[711,112],[714,116],[719,120],
        [720,124],[720,128],[722,132],[725,136],[728,140],
        [729,144],[733,148],[733,152],[735,156],[739,160],
        [739,164],[743,168]], dtype=float)
    yy, xx = np.mgrid[:newmod.HEIGHT, :newmod.W]
    nx, ny = xx / newmod.S[0], yy / newmod.S[1]
    cliff_x = np.interp(ny, trace[:,1], trace[:,0])
    rock = (nx >= 640) & (nx <= cliff_x-2) & (ny >= 65) & (ny <= 135)
    observed = {'v5': {'max_rgb_change':0., 'changed_pixels_max':0},
                'v6': {'max_rgb_change':0., 'changed_pixels_max':0}}
    ranges = [(27,30,-5,70,False,50), (96,98,70,118,True,40)]
    tested = 0
    for a,b,start,end,reverse,width in ranges:
        for t in np.arange(a, b+1/60, 1/30):
            tested += 1
            for label, scene in [('v5',old),('v6',new)]:
                frame = scene.base.astype(np.float32)
                before = frame.copy()
                scene.shuttle_pass(frame,float(t),start,end,reverse,width)
                delta = np.max(np.abs(frame-before),axis=2)
                observed[label]['max_rgb_change'] = max(observed[label]['max_rgb_change'],float(delta[rock].max()))
                observed[label]['changed_pixels_max'] = max(observed[label]['changed_pixels_max'],int(np.count_nonzero(delta[rock]>1e-4)))
    assert observed['v5']['max_rgb_change']>1, 'Positive control failed to reproduce the old defect'
    assert observed['v6']['max_rgb_change']==0, 'New shuttle modifies protected rock interior'

    endpoints=[]
    for start,end,reverse,width in [(-5,70,False,50),(70,118,True,40)]:
        for t in [start+1/30,end-1/30]:
            frame=new.base.astype(np.float32);before=frame.copy()
            new.shuttle_pass(frame,t,start,end,reverse,width)
            changed=int(np.count_nonzero(np.any(frame!=before,axis=2)))
            endpoints.append({'time':t,'reverse':reverse,'changed_pixels':changed})
            assert changed==0, 'Flight endpoint still visible'

    # Blank only sprite imagery IN MEMORY, leaving production nozzle/plume math
    # and geometry untouched, so emitted colours can be measured independently.
    engine=[]
    for scene,label in [(old,'v5'),(new,'v6')]:
        keep=scene.ship_sprites
        scene.ship_sprites={key:np.zeros_like(value) for key,value in keep.items()}
        try:
            for t,start,end,reverse,width in [(40,-5,70,False,50),(90,70,118,True,40)]:
                frame=np.zeros_like(scene.base,dtype=np.float32)
                scene.shuttle_pass(frame,t,start,end,reverse,width)
                total=frame.sum(axis=(0,1),dtype=np.float64)
                engine.append({'version':label,'reverse':reverse,'emission_rgb_sum':total.tolist()})
                if label=='v6':assert total[2]>total[1]>total[0], 'Exhaust is not predominantly blue'
        finally:scene.ship_sprites=keep

    non_shuttle=[]
    old_pass,new_pass=old.shuttle_pass,new.shuttle_pass
    old.shuttle_pass=lambda *args:None
    new.shuttle_pass=lambda *args:None
    try:
        for t in [0,27.5,48,97,108]:
            a,b=old.frame(t),new.frame(t)
            changed=int(np.count_nonzero(np.any(a!=b,axis=2)))
            non_shuttle.append({'time':t,'changed_pixels':changed})
            assert changed==0, 'A non-shuttle layer changed'
    finally:old.shuttle_pass,new.shuttle_pass=old_pass,new_pass

    # Paired identical-time crops show both passage edges and blue engine change.
    times=[27,28,29,30,96,97,98,40]
    box=(int(635*newmod.S[0]),int(60*newmod.S[1]),int(825*newmod.S[0]),int(145*newmod.S[1]))
    out=Image.new('RGB',(1160, len(times)*290),(18,20,25))
    draw=ImageDraw.Draw(out)
    for i,t in enumerate(times):
        start,end,reverse,width=(-5,70,False,50) if t<70 else (70,118,True,40)
        for j,scene in enumerate([old,new]):
            frame=scene.base.astype(np.float32)
            scene.shuttle_pass(frame,t,start,end,reverse,width)
            crop=Image.fromarray(np.uint8(np.rint(np.clip(frame,0,255)))).crop(box)
            if t==40:
                x,y=scene.shuttle_pose(t,start,end,reverse)
                box2=(int((x-75)*newmod.S[0]),int(60*newmod.S[1]),int((x+115)*newmod.S[0]),int(145*newmod.S[1]))
                crop=Image.fromarray(np.uint8(np.rint(np.clip(frame,0,255)))).crop(box2)
            out.paste(crop.resize((580,260),Image.Resampling.NEAREST),(j*580,i*290+25))
            draw.text((j*580+8,i*290+6),f'{"V5" if j==0 else "V6"}  {t:.1f}s (isolated shuttle over unchanged source)',fill='white')
    out.save(HERE/'flight-occlusion-contact-sheet.png')

    unchanged={name:sha(OLD/name)==sha(HERE/name) for name in ['source.png','Snowline-V6-review-audio-2min.flac','assets/lambda-shuttle-master.png','assets/shuttle-prompt.txt','audio-recipe.json','v2-scene.json']}
    assert all(unchanged.values())
    old_events=json.loads((OLD/'events.json').read_text(encoding='utf-8'))
    new_events=json.loads((HERE/'events.json').read_text(encoding='utf-8'))
    prior_event_fields_equal=all(new_events.get(key)==value for key,value in old_events.items())
    added_event_fields=sorted(new_events.keys()-old_events.keys())
    assert prior_event_fields_equal and added_event_fields==['shuttle_revision']
    same_pose=inspect.getsource(oldmod.Scene.shuttle_pose)==inspect.getsource(newmod.Scene.shuttle_pose)
    same_traffic=inspect.getsource(oldmod.Scene.traffic)==inspect.getsource(newmod.Scene.traffic)
    assert same_pose and same_traffic
    result={'status':'passed','checks':'independent targeted native-source geometry and isolated rendering; not continuous video playback',
        'source_trace_native_xy':trace.tolist(),'rock_interior_margin_native_px':2,
        'protected_rock_pixels':int(rock.sum()),'crossing_frames_per_version':tested,
        'cliff_crossing_windows_seconds':[[27,30],[96,98]],'protected_rock_changes':observed,
        'old_mask_positive_control_detected':True,'flight_endpoints':endpoints,
        'emission_colour_checks':engine,'non_shuttle_frame_checks':non_shuttle,
        'source_inputs_unchanged':unchanged,'pose_unchanged':same_pose,'flight_schedule_unchanged':same_traffic,
        'event_metadata':{'all_preexisting_fields_semantically_equal':prior_event_fields_equal,'added_provenance_fields':added_event_fields,'byte_identical':sha(OLD/'events.json')==sha(HERE/'events.json')},
        'contact_sheet':'flight-occlusion-contact-sheet.png',
        'visual_review':'Source/V5/V6 paired stills inspected at 27,28,29,30,96,97,98 and40 seconds. V6 follows the snowy cliff edge and both engine directions appear blue-white. No continuous playback performed.',
        'limits':'Mask edge follows a manually inspected source with a soft 1-2 native-pixel snowy lip. Numeric zero-change checks cover conservative rock interior; inspect the diagnostic edge images for artistic appearance.'}
    (HERE/'repair-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'crossing_frames_per_version':tested,'protected_rock_changes':observed,'non_shuttle_frame_checks':non_shuttle},indent=2))


if __name__=='__main__':
    main()
