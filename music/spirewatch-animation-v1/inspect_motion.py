from pathlib import Path
import sys,json
import numpy as np,cv2
from PIL import Image,ImageDraw
from render_spirewatch import Spirewatch,H,save
s=Spirewatch()
# Native pixel inspections for small apertures, alongside complete-frame reviews.
sheet=Image.new('RGB',(1000,480),(18,22,27));d=ImageDraw.Draw(sheet)
dark=Image.fromarray(s.frame(0,'windows',True));base=Image.fromarray(s.base)
for i,rec in enumerate(s.window_records):
 x,y,w,h=rec['aperture'];box=(x-8,y-8,x+w+8,y+h+8);col=i%5;row=i//5
 for j,im in enumerate([base,dark]):sheet.paste(im.crop(box).resize((88,156),Image.Resampling.NEAREST),(col*200+j*96,row*240+35))
 d.text((col*200+4,row*240+6),f'{i}: {x},{y}  original / dim',fill='white')
sheet.save(H/'window-mask-comparison.png')
frames=[s.frame(t) for t in [0,4,8,20,32.1,40,52,59+29/30]]
for name,box in [('falls',(250,195,313,367)),('screen',(138,557,319,698)),('lamp',(19,526,494,802))]:
 images=[Image.fromarray(f).crop(box) for f in frames[:6]];w,h=images[0].size
 canvas=Image.new('RGB',(3*w,2*h))
 for i,im in enumerate(images):canvas.paste(im,(i%3*w,i//3*h))
 canvas.save(H/f'{name}-temporal.png')
# Track the principal flow using source-normalized waterfall variation.
x0,y0,x1,y1=265,227,290,337
source=s.base[y0:y1,x0:x1].astype(np.float32).mean(2)
a=s.frame(0,'falls')[y0:y1,x0:x1].astype(np.float32).mean(2)/(source+1)
b=s.frame(.2,'falls')[y0:y1,x0:x1].astype(np.float32).mean(2)/(source+1)
scores=[]
for shift in range(-12,13):
 aa=a[12:-12];bb=b[12+shift:len(b)-12+shift]
 scores.append((float(np.corrcoef(aa.flatten(),bb.flatten())[0,1]),shift))
score,shift=max(scores);assert shift>0 and score>.75,(shift,score)
coverage={}
for name,box in [('upper_left',(600,45,900,250)),('upper_right',(1320,50,1610,235)),('central_clouds',(850,175,1150,275)),('low_mist',(935,374,1090,403))]:
 a,b,z,d=box;vals=[]
 for t in [0,20,40,52]:
  old=s.frame(t,'atmosphere')[b:d,a:z];new=s.frame(t+4,'atmosphere')[b:d,a:z]
  vals.append(float(np.abs(new.astype(float)-old.astype(float)).mean()))
 assert min(vals)>.04,(name,vals)
 coverage[name]={'native_region':box,'four_second_mean_pixel_change_at_0_20_40_52':vals}
save('targeted-validation.json',{'fingerprint':s.fingerprint(),'fall_tracking':{'native_region':[x0,y0,x1,y1],'interval_seconds':.2,'best_vertical_shift_pixels':shift,'correlation':score,'direction':'downward','expected_speed_native_px_per_second':40},'weather_coverage':coverage,'window_mask_sheet':'window-mask-comparison.png','scope':'Quantitative transport/coverage support plus native crops. These do not establish normal-speed playback quality or user acceptance.'})
print(json.dumps({'fall_shift':shift,'correlation':score,'coverage':coverage},indent=2))
