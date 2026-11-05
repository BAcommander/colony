"""Composite only source-confined generated cleanup patches; retain every original."""
from pathlib import Path
import hashlib,json,sys
import cv2
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'music/scene-animation-core'))
from core import polygon_mask,roi_slice,sha

def save(name,array):Image.fromarray(np.uint8(np.clip(np.rint(array),0,255))).save(HERE/name)

def main():
    original=np.asarray(Image.open(ROOT/'creative/brainstorm/2026-10-27-three-worlds/e1-gate-camp/concept-v1.png').convert('RGB'))
    generated=np.asarray(Image.open(HERE/'gate-clean-backplate.png').convert('RGB'))
    assert generated.shape==original.shape
    roi=[280,600,321,680];m=polygon_mask(roi,[[[288,608],[318,608],[320,675],[286,675]]],3,0)
    repaired=original.copy();r=roi_slice(roi);repaired[r]=np.uint8(np.rint(original[r]+(generated[r].astype(np.float32)-original[r])*m[...,None]))
    allowed=np.zeros(original.shape[:2],bool);allowed[r]=m>0;assert np.array_equal(original[~allowed],repaired[~allowed])
    target=ROOT/'music/gate-camp-animation-v3/artwork-v2-mug-repair.png';Image.fromarray(repaired).save(target)
    city=np.asarray(Image.open(ROOT/'final/16-cyberpunk-apartment/artwork-v3.png').convert('RGB'))
    clean=city.copy();roi=[125,300,425,545];clean[roi_slice(roi)]=np.asarray(Image.open(HERE/'plant-clean-backplate.png').convert('RGB').resize((300,245),Image.Resampling.LANCZOS))
    Image.fromarray(clean).save(HERE/'city-plant-background-aligned.png')
    plant_polys=[[[129,357],[140,349],[157,346],[174,350],[194,360],[211,377],[229,398],[223,405],[208,398],[187,388],[165,382],[146,375],[132,367]],[[300,379],[315,372],[337,373],[359,382],[380,391],[399,408],[401,419],[384,413],[364,401],[351,399],[356,412],[347,410],[336,396],[327,394],[331,407],[319,403],[310,391],[299,388]]]
    masks=[]
    for i,poly in enumerate(plant_polys):
        m=polygon_mask(roi,[poly],1.1);rgb=city[roi_slice(roi)].astype(np.float32)
        green=np.clip((rgb[...,1]-.72*rgb[...,0]+2)/8,0,1)*np.clip((rgb[...,1]-1.12*rgb[...,2]+2)/8,0,1)
        m*=green;Image.fromarray(np.uint8(np.rint(m*255))).save(HERE/f'city-leaf-{i+1}-mask.png');masks.append(m)
    # Retain a source-space clean field for only the thin rope and selected scrub footprint.
    Image.fromarray(generated).save(HERE/'gate-motion-background.png')
    rope_roi=[517,280,576,623];rope=np.zeros((343,59),np.uint8)
    cv2.line(rope,(528-517,285-280),(565-517,618-280),255,5,cv2.LINE_AA)
    rope=cv2.GaussianBlur(rope,(0,0),.6);Image.fromarray(rope).save(HERE/'gate-rope-mask.png')
    scrub_roi=[737,535,810,594];scrub=polygon_mask(scrub_roi,[[[748,562],[751,550],[765,541],[780,542],[791,552],[800,569],[796,581],[779,585],[758,580]]],3)
    Image.fromarray(np.uint8(scrub*255)).save(HERE/'gate-scrub-mask.png')
    rover=Image.open(HERE/'expedition-rover-raw.png').convert('RGBA');alpha=np.asarray(rover)[:,:,3];assert alpha.min()==0 and alpha.max()>240
    ys,xs=np.where(alpha>16);box=(max(0,int(xs.min())-8),max(0,int(ys.min())-8),min(rover.width,int(xs.max())+9),min(rover.height,int(ys.max())+9));rover.crop(box).save(HERE/'expedition-rover-sprite.png')
    spec={'gate_original':'creative/brainstorm/2026-10-27-three-worlds/e1-gate-camp/concept-v1.png','gate_repaired':target.relative_to(ROOT).as_posix(),'mug_patch_roi':[280,600,321,680],'mug_original_pixels_outside_patch_exact':True,'city_leaf_roi':[125,300,425,545],'city_leaf_anchors':[[229,401],[302,383]],'gate_rope_roi':rope_roi,'gate_rope_anchor':[565,618],'gate_scrub_roi':scrub_roi,'gate_scrub_anchor':[775,584],'rover_raw_alpha_range':[int(alpha.min()),int(alpha.max())],'rover_crop_xyxy':box,'generated_images_used':'Built-in image_gen; exact requests in *_generation.json files. Only confined cleanup/element footprints consume backplates.','assets':[]}
    for p in sorted(HERE.glob('*.png')):spec['assets'].append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'dimensions':list(Image.open(p).size)})
    (HERE/'asset-preparation.json').write_bytes((json.dumps(spec,indent=2)+'\n').encode())
    # Review composites are diagnostics, not alternate source assets.
    Image.fromarray(repaired).crop((275,585,415,685)).resize((700,500)).save(HERE/'mug-repair-review.png')
    print('Prepared source-confined mug repair, clean movable-element backplates and RGBA rover',flush=True)

if __name__=='__main__':main()
