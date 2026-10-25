from PIL import Image,ImageDraw
from pathlib import Path
H=Path(__file__).parent
im=Image.open(H/'source.png')
for name,r,step,scale in [('bridge',(800,370,1450,435),25,2),('keys',(0,575,225,660),10,4),('buttons',(0,250,45,580),10,3)]:
 a=im.crop(r);d=ImageDraw.Draw(a)
 for x in range((r[0]//step+1)*step,r[2],step):d.line((x-r[0],0,x-r[0],a.height),fill=(30,180,180));d.text((x-r[0],0),str(x),fill='white')
 for y in range((r[1]//step+1)*step,r[3],step):d.line((0,y-r[1],a.width,y-r[1]),fill=(30,180,180));d.text((0,y-r[1]),str(y),fill='white')
 a.resize((a.width*scale,a.height*scale)).save(H/f'{name}-grid.png')
