"""Refresh current diagnostics from the aligned pipeline clip, retaining old studies."""
from render_deepwell_v4 import *
import shutil
A=H/'history'/'pipe-mount-alignment-study';D=H/'pipeline-roundtrip-decoded';D.mkdir(exist_ok=True)
for name in ['pipeline-outward-return-temporal-review.png','far-pipe-alignment-review.png']:
 q=H/name
 if q.exists() and not (A/name).exists():shutil.copy2(q,A/name)
for q in H.glob('isolated-pipeline-decoded-*.png'):
 if not (A/q.name).exists():shutil.copy2(q,A/q.name)
for q in D.glob('*.png'):
 (A/'old-pipeline-roundtrip-decoded').mkdir(exist_ok=True)
 if not (A/'old-pipeline-roundtrip-decoded'/q.name).exists():shutil.copy2(q,A/'old-pipeline-roundtrip-decoded'/q.name)
path=H/'deepwell-v4-pipeline-roundtrip-20s.mp4'
for t in [0,5,10,15,19.9]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(path),'-frames:v','1','-vf','scale=in_color_matrix=bt709:out_range=pc,format=rgb24',str(H/f'isolated-pipeline-decoded-{t}.png')],check=True)
for i in [0,120,240,360,480,599]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(i/30),'-i',str(path),'-frames:v','1','-vf','scale=in_color_matrix=bt709:out_range=pc,format=rgb24',str(D/f'decoded-{i:04d}.png')],check=True)
out=Image.new('RGB',(1280,700));draw=ImageDraw.Draw(out)
for j,t in enumerate([0,5,10,15,19.9]):
 im=Image.open(H/f'isolated-pipeline-decoded-{t}.png');out.paste(im.crop((655,193,1072,264)).resize((1280,140)),(0,j*140));draw.text((8,j*140+5),str(t)+' s',fill='yellow')
out.save(H/'pipeline-outward-return-temporal-review.png')
s=DeepwellV4();r=(865,308,960,340);out=Image.new('RGB',(950,640))
for i,frame in enumerate([s.base,s.frame(0,'pipeline')]):out.paste(Image.fromarray(frame).crop(r).resize((950,320),resample=Image.Resampling.NEAREST),(0,i*320))
out.save(H/'far-pipe-alignment-review.png');print('Current aligned indicator diagnostics refreshed; original studies retained.',flush=True)
