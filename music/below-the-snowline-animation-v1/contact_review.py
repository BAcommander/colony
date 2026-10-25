from PIL import Image
from pathlib import Path
p=Path(__file__).parent
out=Image.new('RGB',(1000,640))
for i,t in enumerate(['0.000','2.000','4.000','8.000']):
 im=Image.open(p/f'sample-{t}.png')
 out.paste(im.crop((230,480,355,640)).resize((250,320)),((i%2)*250,(i//2)*320))
 out.paste(im.crop((50,260,180,395)).resize((250,260)),(500+(i%2)*250,(i//2)*320))
out.save(p/'interior-temporal-review.png')
