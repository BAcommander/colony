import subprocess,json
import numpy as np
from render_spirewatch import Spirewatch,H,save
s=Spirewatch();indices=[449,450,899,900,1349,1350];ff=s.config['ffmpeg'];path=H/'spirewatch-v6-preview-60s.mp4';w,h=s.config['preview_size'];framebytes=w*h*3//2
selection='+'.join('eq(n\\,%d)'%i for i in indices)
decoded=subprocess.run([ff,'-v','error','-i',str(path),'-vf','select='+selection,'-vsync','0','-pix_fmt','yuv420p','-f','rawvideo','-'],stdout=subprocess.PIPE,check=True).stdout
assert len(decoded)==len(indices)*framebytes
rows=[]
for j,i in enumerate(indices):
 source=s.frame(i/30)
 expected=subprocess.run([ff,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{s.w}x{s.h}','-r','30','-i','pipe:0','-frames:v','1','-vf',f'scale={w}:{h}:flags=lanczos:out_color_matrix=bt709:out_range=tv','-pix_fmt','yuv420p','-f','rawvideo','-'],input=source.tobytes(),stdout=subprocess.PIPE,check=True).stdout
 actual=decoded[j*framebytes:(j+1)*framebytes]
 assert actual==expected,('Chunk boundary picture differs',i)
 rows.append({'frame':i,'scene_time':i/30,'decoded_yuv_matches_native_render_exactly':True})
save('chunk-join-validation.json',{'fingerprint':s.fingerprint(),'checks':rows,'pass':True})
print('All six pictures adjoining the three chunk boundaries match native scene time exactly')


