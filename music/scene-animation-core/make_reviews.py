"""Actual encoded-frame detail crops and tail-to-head review, with provenance."""
from pathlib import Path
import argparse,json,subprocess
from core import FFMPEG,sha
from validate_review import load,framehash,ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('scene',choices=['city','gate']);args=p.parse_args();scene,media=load(args.scene);folder=media.parent;fps=scene.fps
    # Crops are specified in the native source space, mapped once to the encoded frame.
    specs=([('City-neon-and-traffic',10,16,[817,145,1558,550]),('City-cup-lamp-and-leaves',18,10,[122,300,788,846]),('City-ferry-and-glass',37,12,[1015,465,1250,560])] if args.scene=='city' else [('Gate-water-and-steps',4,14,[1025,32,1490,553]),('Gate-canopy-and-wind',8,16,[1,0,950,626]),('Gate-rover-approach',7,20,[1080,530,1670,817])])
    results=[]
    for label,start,seconds,roi in specs:
        a,b,c,d=roi;x=round(a*1280/1672)//2*2;y=round(b*720/941)//2*2;w=round((c-a)*1280/1672)//2*2;h=round((d-b)*720/941)//2*2
        out=folder/f'{label}-detail.mp4';assert not out.exists()
        subprocess.run([FFMPEG,'-v','error','-n','-ss',str(start),'-i',str(media),'-t',str(seconds),'-an','-vf',f'crop={w}:{h}:{x}:{y},scale=iw*2:ih*2:flags=lanczos','-c:v','libx264','-qp','0','-preset','veryfast','-threads','3','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-movflags','+faststart',str(out)],check=True)
        text,rows=framehash(out);assert len(rows)==round(seconds*fps);results.append({'path':out.name,'sha256':sha(out),'source_sha256':sha(media),'scene_start_seconds':start,'seconds':seconds,'decoded_frames':len(rows),'encoded_crop_xywh':[x,y,w,h],'display_scale':2,'time_or_effect_strength_altered':False})
    # Read the source twice without copying a full repeated review to disk.
    listing=folder/'loop-review-input.txt';listing.write_text("file '"+media.name+"'\nfile '"+media.name+"'\n")
    out=folder/('City-loop-join-10s.mp4' if args.scene=='city' else 'Gate-loop-join-10s.mp4');assert not out.exists()
    subprocess.run([FFMPEG,'-v','error','-n','-f','concat','-safe','0','-i',str(listing),'-ss','55','-t','10','-an','-c:v','libx264','-qp','0','-preset','veryfast','-threads','3','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-movflags','+faststart',str(out)],check=True)
    _,join=framehash(out);_,original=framehash(media);assert len(join)==10*fps
    expected=original[55*fps:]+original[:5*fps];assert [r[-1].strip() for r in join]==[r[-1].strip() for r in expected]
    results.append({'path':out.name,'sha256':sha(out),'seconds':10,'decoded_frames':len(join),'exact_encoded_picture_sequence':'scene55-60 then0-5','all_decoded_yuv_hashes_match_source':True})
    (folder/'detail-review-validation.json').write_text(json.dumps({'source':media.name,'reviews':results},indent=2)+'\n');print(args.scene,'detail and join reviews validated')
if __name__=='__main__':main()
