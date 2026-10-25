from pathlib import Path
import sys,subprocess,json,hashlib
sys.path.insert(0,str(Path(__file__).parent))
from render import Scene,H,digest,save
s=Scene();video=H/'Below-the-Snowline-v2-preview-20s.mp4';checks=[]
vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
for i in [0,1,119,120,239,240,359,360,479,480,598,599]:
 expected=subprocess.check_output(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'],input=s.frame(i/30).tobytes())
 actual=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf',f'select=eq(n\\,{i})','-frames:v','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1'])
 assert actual==expected,('Direct render mismatch',i)
 checks.append({'frame':i,'exact_native_to_decoded_yuv':True})
save('direct-validation.json',{'fingerprint':s.fingerprint(),'checks':checks,'visual_review':'Source/mask/temporal/decoded stills only; no continuous playback claim'})
print('12 direct native-to-decoded YUV checks passed',flush=True)

