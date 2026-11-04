from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
R=Path(__file__).resolve().parent
original=Image.open(R.parent/'apartment-original.png').convert('RGB')
edited=Image.open(R/'car-removal-edit.png').convert('RGB')
if edited.size!=original.size:edited=edited.resize(original.size,Image.Resampling.LANCZOS)
boxes=[(704,430,764,455),(1293,386,1338,407),(1336,383,1383,404),(1458,391,1510,417)]
m=Image.new('L',original.size);d=ImageDraw.Draw(m)
for x0,y0,x1,y1 in boxes:d.rounded_rectangle((x0,y0,x1,y1),radius=4,fill=255)
m=m.filter(ImageFilter.GaussianBlur(1.4))
clean=Image.composite(edited,original,m)
refined=clean.copy()
detail=Image.open(R/'car3-detail-repaired.png').convert('RGB').resize((145,79),Image.Resampling.LANCZOS)
refined.paste(detail,(1282,355))
refine_mask=Image.new('L',original.size)
ImageDraw.Draw(refine_mask).rounded_rectangle(boxes[2],radius=4,fill=255)
refine_mask=refine_mask.filter(ImageFilter.GaussianBlur(1.4))
clean=Image.composite(refined,clean,refine_mask)
clean.save(R/'clean-apartment.png')
sheet=Image.new('RGB',(800,560),(13,18,25));draw=ImageDraw.Draw(sheet)
for i,box in enumerate(boxes):
    x0,y0,x1,y1=box;crop=(x0-15,y0-12,x1+15,y1+12)
    for j,im in enumerate([original,clean]):
        thumb=im.crop(crop);thumb.thumbnail((360,102),Image.Resampling.LANCZOS)
        thumb=thumb.resize((thumb.width*2,thumb.height*2),Image.Resampling.NEAREST) if thumb.width<175 else thumb
        sheet.paste(thumb,(20+j*400,i*140+26))
        draw.text((20+j*400,i*140+8),f'Car {i+1}: '+('original' if j==0 else 'removed'),fill='white')
sheet.save(R/'car-removal-check.jpg',quality=96)
o=np.asarray(original).astype(np.int16);c=np.asarray(clean).astype(np.int16)
unmasked=np.asarray(m)==0
report={'source_dimensions':original.size,'patches':boxes,'maximum_difference_outside_edit_mask':int(np.abs(o-c)[unmasked].max())}
(R/'art-repair-report.json').write_text(json.dumps(report,indent=2))
print(report)
