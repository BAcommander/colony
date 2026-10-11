from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
H=Path(__file__).parent
config=json.loads((H/'scene-plan-v3.json').read_text());path=H/'spirewatch-v3-preview-60s.mp4'
assert (H/'preview-validation.json').exists(), 'Inspect only after full preview validation'
out=H/'encoded-inspection';out.mkdir(exist_ok=True)
times=[0,4,8,9.6,20,28,32,34.6,40,48,52.6,56,59+29/30]
for t in times:
 target=out/f'frame-{t:06.2f}s.png'
 if target.exists():continue
 subprocess.run([config['ffmpeg'],'-v','error','-n','-ss',str(t),'-i',str(path),'-map','0:v:0','-frames:v','1','-vf','scale=in_color_matrix=bt709:out_range=full','-update','1',str(target)],check=True)
for name,box,selected in [('storm',(480,0,1240,270),[8,9.6,32,34.6,48,52.6]),('tower',(914,12,1046,325),[4,8,28,32,40,48]),('room',(0,403,330,610),[4,8,20,32,40,56])]:
 w,h=box[2]-box[0],box[3]-box[1];sheet=Image.new('RGB',(w*3,(h+22)*2))
 for i,t in enumerate(selected):
  x=(i%3)*w;y=(i//3)*(h+22);im=Image.open(out/f'frame-{t:06.2f}s.png').crop(box)
  sheet.paste(im,(x,y+22));ImageDraw.Draw(sheet).text((x+3,y+3),str(t)+' seconds',fill='white')
 sheet.save(out/f'{name}-temporal.png')
record={'source_video':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'colour_aware':True,'times':times,'sheets':['storm-temporal.png','tower-temporal.png','room-temporal.png'],'inspection_status':'Prepared for assistant sampled-frame inspection','continuous_playback':False,'user_motion_approved':False}
(H/'encoded-inspection.json').write_text(json.dumps(record,indent=2)+'\n')
print('Thirteen encoded frames and three temporal sheets prepared')
