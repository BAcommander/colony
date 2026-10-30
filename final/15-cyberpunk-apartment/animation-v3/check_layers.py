import render as r
import numpy as np,json
from PIL import Image,ImageDraw
minimums=[]
for route in r.routes:
    smallest=1e9
    for t in np.linspace(0,1,601):
        ds=sorted(r.vehicle_distance(route,v,t) for v in route[5])
        gap=min(np.diff(ds+[ds[0]+route[2]]))
        smallest=min(smallest,float(gap))
    minimums.append(smallest)
assert min(minimums)>12,'Vehicles approach too closely'
frames=[r.frame(i) for i in (0,130,300)]
sheet=Image.new('RGB',(1000,450),'#10151d')
for i,f in enumerate(frames):
    im=Image.fromarray(f)
    im.save(r.R/f'layer-check-{i}.jpg',quality=97)
    crop=im.crop((int(560*r.SX),int(630*r.SY),int(660*r.SX),int(758*r.SY))).resize((300,384),Image.Resampling.LANCZOS)
    sheet.paste(crop,(i*330,30))
    ImageDraw.Draw(sheet).text((i*330,10),f'Time {[0,130/60,5][i]:.2f}s',fill='white')
sheet.save(r.R/'steam-check.jpg',quality=96)
report={'minimum_road_headways_in_1080p_pixels':minimums,'unmoving_sofa_max_pixel_difference':int(np.abs(frames[0][820:990,:430].astype(np.int16)-frames[2][820:990,:430].astype(np.int16)).max())}
(r.R/'layer-check.json').write_text(json.dumps(report,indent=2))
print(report)
