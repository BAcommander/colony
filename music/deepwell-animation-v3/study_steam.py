"""Internal full-size readability comparison for restrained vapor strength."""
from render_deepwell_v3 import *
s=DeepwellV3()
for plume in s.steam:plume.c['opacity']*=2.2
for t in [0,2,4,8]:Image.fromarray(s.frame(t)).save(H/f'steam-strength-study-{t:02d}.png')
out=Image.new('RGB',(900,660));draw=ImageDraw.Draw(out)
for i,name in enumerate(['sample-4.000s.png','steam-strength-study-04.png']):
 im=Image.open(H/name);out.paste(im.crop((214,640,290,760)).resize((228,360)),(i*450,0));out.paste(im.crop((1120,178,1330,249)).resize((450,152)),(i*450,420));draw.text((i*450+8,375),name,fill='white')
out.save(H/'steam-strength-comparison.png');print('Vapor strength study ready',flush=True)
