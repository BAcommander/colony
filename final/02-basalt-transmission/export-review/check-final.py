from pathlib import Path
import subprocess,json,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent/'final-check';R.mkdir(exist_ok=True)
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'G:\AI\colony\exports\02-basalt-transmission\basalt.mp4'
AUDIO=r'G:\AI\colony\exports\02-basalt-transmission\Basalt-Transmission-2-Hours.mp3'
def run(args):return subprocess.run([FF,'-hide_banner','-nostats',*args],capture_output=True,check=True)
times=[4,124,904,1804,3604,7199]
grid=Image.new('RGB',(1280,1140),'#101820');draw=ImageDraw.Draw(grid)
for j,t in enumerate(times):
 p=run(['-v','error','-ss',str(t),'-i',SRC,'-frames:v','1','-vf','scale=640:360','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
 im=Image.frombytes('RGB',(640,360),p.stdout);im.save(R/f'frame-{t}.png')
 grid.paste(im,((j%2)*640,(j//2)*380+20));draw.text(((j%2)*640+8,(j//2)*380+3),f'{t//3600:02}:{t%3600//60:02}:{t%60:02}',fill='white')
grid.save(R/'export-contact-sheet.jpg')
report={'inspection':'Selected decoded frames, sampled boundary checks, sampled audio alignment, full packet traversal and full audio loudness; not a full video decode or playback review','visual_samples_seconds':times,'boundary_checks':[],'audio_checks':[]}
for t in [20,40,900,1800,3600,7180]:
 p=run(['-v','error','-ss',str(t-1),'-i',SRC,'-t','2','-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
 frames=np.frombuffer(p.stdout,np.uint8).reshape(-1,180,320,3).astype(float)
 diff=abs(np.diff(frames,axis=0)).mean((1,2,3))
 report['boundary_checks'].append({'time':t,'decoded_frames':len(frames),'seam_mae':float(diff[29]),'median_adjacent_mae':float(np.median(diff)),'max_adjacent_mae':float(diff.max())})
def audio(path,t):
 p=run(['-v','error','-ss',str(t),'-i',path,'-t','10','-vn','-ar','8192','-ac','2','-f','f32le','pipe:1']);return np.frombuffer(p.stdout,np.float32).reshape(-1,2).astype(float)
for t in [60,3590,7190]:
 x=audio(SRC,t);y=audio(AUDIO,t);n=min(len(x),len(y));x=x[:n];y=y[:n]
 report['audio_checks'].append({'time':t,'correlation':float(np.corrcoef(x.ravel(),y.ravel())[0,1]),'level_difference_db':float(10*np.log10(np.mean(x*x)/np.mean(y*y)))})
p=run(['-v','warning','-i',SRC,'-map','0','-c','copy','-f','null','-']);(R/'packet-check.txt').write_bytes(p.stderr)
report['full_packet_traversal_exit_code']=p.returncode
(R/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
p=run(['-i',SRC,'-vn','-af','ebur128=peak=true:framelog=verbose','-f','null','-']);(R/'audio-loudness.txt').write_bytes(p.stderr);print(p.stderr.decode(errors='replace')[-750:])
