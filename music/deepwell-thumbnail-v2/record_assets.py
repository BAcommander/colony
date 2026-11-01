from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=R/'music/deepwell-animation-v4/v3-snapshot/v2-snapshot/baseline-snapshot/artwork-planet-v1.png'
assert sha(src)==sha(H/'deepwell-scene-master.png')=='8c04e8fbf7af063d00cd05fb587c713f2e0a380b8274410016d072cdf9a25b9b'
files={}
for name in ['deepwell-scene-master.png','deepwell-title-master.png','Deepwell-title-v2.jpg','Deepwell-scene-only-v2.jpg','phone-comparison.png','prompt.txt']:
 p=H/name;entry={'sha256':sha(p),'bytes':p.stat().st_size}
 if p.suffix.lower() in ['.png','.jpg']:
  with Image.open(p) as im:im.load();entry.update(dimensions=list(im.size),mode=im.mode)
 if p.suffix=='.jpg':assert entry['dimensions']==[1280,720] and entry['bytes']<2_000_000
 files[name]=entry
a=np.array(Image.open(H/'deepwell-scene-master.png').convert('RGB')).astype(float)
b=np.array(Image.open(H/'deepwell-title-master.png').convert('RGB')).astype(float)
assert a.shape==b.shape
mask=np.ones(a.shape[:2],bool);mask[:205,:535]=False;diff=abs(a-b)[mask]
record={'date':'2026-11-01','method':'Built-in image_gen lettering edit; ffmpeg Lanczos format-sized JPEGs; exact original clean source retained for scene-only candidate.','prompt':'prompt.txt','references':[{'role':'edit target','path':str(src),'sha256':sha(src)},{'role':'typography reference only','path':'music/empty-junction-visual-revision-v1/thumbnail-revised-junction-v1.jpg','sha256':sha(R/'music/empty-junction-visual-revision-v1/thumbnail-revised-junction-v1.jpg')}],'original_generated_file':'C:/Users/jazzs/.codex/generated_images/01a192a2-705f-7391-80a2-74e52ec3e7ea/exec-f41ea52d-d940-4a25-8566-b8fe9e0fd143.png','files':files,'outside_generous_text_region':{'excluded_roi_xyxy':[0,0,535,205],'mean_absolute_channel_difference_0_255':float(diff.mean()),'fraction_pixels_any_channel_difference_gt5':float((diff.max(axis=1)>5).mean()),'interpretation':'Generative scene changes occur outside lettering. Not a controlled text-only comparison.'},'inspection':'Full generated still and320x180 comparison inspected: title spelled correctly, single-line text, planet and landscape retained, header/subtitle/number removed. Some fine texture and contrast drift.','assistant_preference':'one-word candidate for a readable scene-first upload; no performance claim','user_selection':'pending','canonical_thumbnail_preserved':True,'video_audio_unchanged':True}
(H/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':files,'outside_text':record['outside_generous_text_region']},indent=2))
