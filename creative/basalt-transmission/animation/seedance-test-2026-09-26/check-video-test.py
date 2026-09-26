from pathlib import Path
import subprocess,numpy as np,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent/'video-test';R.mkdir(exist_ok=True)
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
src=r'C:\Users\jazzs\Downloads\ElevenLabs_video_seedance-2-5_Locked-off trip_2026-09-26T16_47_41.mp4'
old=r'G:\AI\colony\final\02-basalt-transmission\video-4k.mp4'
def frames(path):
 r=subprocess.run([FF,'-v','error','-i',path,'-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True)
 return np.frombuffer(r.stdout,np.uint8).reshape(-1,180,320,3)
report={}
for name,path,fps in [('generated',src,24),('approved',old,30)]:
 f=frames(path);a=f.astype(np.float32);delta=abs(np.diff(a,axis=0)).mean((1,2,3));seam=float(abs(a[-1]-a[0]).mean())
 report[name]={'frames':len(f),'fps':fps,'duration':len(f)/fps,'adjacent_mae_median':float(np.median(delta)),'adjacent_mae_p95':float(np.percentile(delta,95)),'seam_mae':seam,'first_last_exact':bool(np.array_equal(f[0],f[-1])),'max_departure_from_first_mae':float(abs(a-a[0]).mean((1,2,3)).max())}
 if name=='generated':
  grid=Image.new('RGB',(1280,780),'#111111');draw=ImageDraw.Draw(grid)
  for j,idx in enumerate([0,24,48,72,96,len(f)-1]):
   raw=subprocess.run([FF,'-v','error','-i',src,'-vf',f'select=eq(n\\,{idx})','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
   im=Image.frombytes('RGB',(1280,720),raw);im.save(R/f'frame-{idx:03}.png')
   grid.paste(im.resize((640,360)),((j%2)*640,(j//2)*260+25)) if False else None
   grid.paste(im.resize((426,240)),((j%3)*426,(j//3)*390+25))
   draw.text(((j%3)*426+10,(j//3)*390+6),f'{idx/fps:.3f}s / frame {idx}',fill='white')
  grid.save(R/'contact-sheet.jpg')
(R/'comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
subprocess.run([FF,'-y','-v','error','-stream_loop','3','-i',src,'-map','0:v:0','-an','-c:v','copy',str(R/'Basalt-generated-four-repeats.mp4')],check=True)
