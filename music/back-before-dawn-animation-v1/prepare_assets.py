"""Keep generated originals and prepare a small premultiplied-alpha street insert."""
from pathlib import Path
import json,sys
import numpy as np,cv2
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'dependencies'))
from core import sha
def main():
    folder=HERE/'assets';path=folder/'passing-sedan-raw.png';image=Image.open(path).convert('RGBA');rgba=np.array(image);alpha=rgba[...,3]
    assert alpha.min()==0 and alpha.max()>240,'Expected genuine transparent RGBA'
    ys,xs=np.where(alpha>16);box=[max(0,int(xs.min())-8),max(0,int(ys.min())-8),min(image.width,int(xs.max())+9),min(image.height,int(ys.max())+9)]
    crop=rgba[box[1]:box[3],box[0]:box[2]];target=folder/'passing-sedan.png';Image.fromarray(crop).save(target)
    h,w=crop.shape[:2];yy,xx=np.indices((h,w));r,g,b=crop[...,:3].astype(np.float32).transpose(2,0,1)
    warm=np.uint8((r>170)&(g>135)&(b<r*.96)&(xx<w*.4)&(yy>h*.4)&(yy<h*.83)&(crop[...,3]>200))
    count,labels,stats,centers=cv2.connectedComponentsWithStats(warm,8)
    candidates=sorted([(int(stats[i,cv2.CC_STAT_AREA]),centers[i]) for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>40],key=lambda v:-v[0])
    assert len(candidates)>=2,[(a,c.tolist()) for a,c in candidates]
    headlights=[[float(center[0]/w),float(center[1]/h)] for area,center in candidates[:2]]
    metadata={'raw':path.name,'raw_dimensions':list(image.size),'raw_sha256':sha(path),'alpha_range':[int(alpha.min()),int(alpha.max())],'crop_xyxy':box,'path':target.name,'sha256':sha(target),'dimensions':[w,h],'headlights_normalized':headlights,'headlamp_rule':'Two largest warm bright source fixtures in front-left lower half; inspect annotation before use.'}
    (folder/'passing-sedan.json').write_text(json.dumps(metadata,indent=2)+'\n')
    review=Image.fromarray(crop);draw=ImageDraw.Draw(review)
    for hx,hy in headlights:
        x,y=hx*w,hy*h;draw.ellipse((x-14,y-14,x+14,y+14),outline='red',width=3)
    review.save(folder/'sedan-headlamp-review.png')
    assets=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'dimensions':list(Image.open(p).size)} for p in folder.glob('*.png')]
    (folder/'asset-manifest.json').write_text(json.dumps({'mode':'Built-in imagegen with exact requests preserved in *-generation.json','assets':assets,'clean_tree_background_usage':'Retained as a rejected experiment. Final foliage uses bounded original-source warping; no generated sky is consumed. The original cutout introduced an internal blue chord; see source-audit/correction-validation.json.'},indent=2)+'\n')
    print(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
