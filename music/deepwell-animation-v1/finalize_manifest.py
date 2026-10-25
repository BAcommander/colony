"""Record a local delivery manifest after all technical checks and status updates."""
from render_deepwell import *
import shutil
assert (H/'project-status-update.json').exists()
preview=json.loads((H/'preview-validation.json').read_text());direct=json.loads((H/'direct-render-validation.json').read_text())
assert direct['all_selected_yuv_bytes_exact']
runtime_paths=[Path(sys.executable),Path(shutil.which('ffmpeg')),Path(shutil.which('ffprobe'))]
for module in [cv2,np]:
 folder=Path(module.__file__).parent
 runtime_paths.extend(folder.rglob('*.pyd'))
runtime={str(p):{'sha256':digest(p),'bytes':p.stat().st_size} for p in runtime_paths}
write_json('runtime-binary-fingerprint.json',runtime)
files={}
for p in sorted(H.rglob('*')):
 if p.is_file() and p.name!='package-manifest.json':files[p.relative_to(H).as_posix()]={'bytes':p.stat().st_size,'sha256':digest(p)}
write_json('package-manifest.json',{'scene':'Deepwell Station','date':'2026-10-25','status':'First planet and motion candidate; user review pending','current_source':'artwork-planet-v1.png','current_preview':'Deepwell-v1-preview-20s.mp4','repeat_review':'Deepwell-v1-three-loops-60s.mp4','silent':True,'runtime_binary_fingerprint':'runtime-binary-fingerprint.json','fingerprint':preview['fingerprint'],'files':files,'remote_backup':False,'assistant_review':'Source/masks/native temporal stills, water-scale study, isolated decoded crops and selected decoded full-composition pictures. Continuous playback not claimed.','scope':'No soundtrack, opening, 4K, long assembly, model install, commit or push. Original art and thumbnail preserved.'})
print('Local delivery manifest complete:',len(files),'files; source/preview/repeats and binary runtime recorded.')
