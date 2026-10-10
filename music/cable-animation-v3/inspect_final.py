from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
R=Path('G:/AI/colony');H=Path(__file__).resolve().parent
source=R/'exports/06-last-cable-station/Last-Cable-Station-2-Hours-4K-v1.mp4'
canvas=Image.new('RGB',(1280,3*746),(20,20,20));draw=ImageDraw.Draw(canvas)
for i,t in enumerate([8,3608,7196]):
    p=H/f'combined-frame-{t}s.jpg'
    subprocess.run(['C:/Program Files/ShareX/ffmpeg.exe','-v','error','-n','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=1280:720','-q:v','2',str(p)],check=True)
    canvas.paste(Image.open(p),(0,i*746));draw.text((10,i*746+724),f'Final combined MP4 - {t} seconds',fill='white')
canvas.save(H/'combined-contact-sheet.jpg',quality=94)
print('Saved opening, middle and ending decoded stills')
