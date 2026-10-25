"""Record a local v3 delivery inventory and actual binary/runtime fingerprint."""
from render_deepwell_v3 import *
import shutil
assert (H/'project-status-update.json').exists()
p=json.loads((H/'preview-validation.json').read_text());d=json.loads((H/'direct-render-validation.json').read_text())
assert d['all_selected_yuv_bytes_exact'] and d['all_v2_manifest_files_exact']
paths=[Path(sys.executable),Path(shutil.which('ffmpeg')),Path(shutil.which('ffprobe'))]
for module in [cv2,np]:paths.extend(Path(module.__file__).parent.rglob('*.pyd'))
save('runtime-binary-fingerprint.json',{str(q):{'bytes':q.stat().st_size,'sha256':digest(q)} for q in paths})
files={q.relative_to(H).as_posix():{'bytes':q.stat().st_size,'sha256':digest(q)} for q in sorted(H.rglob('*')) if q.is_file() and q.name!='package-manifest.json'}
save('package-manifest.json',{'scene':'Deepwell Station','version':'v3','date':'2026-10-25','status':'Whole-pane mask/steam/pipeline-indicator candidate; user review pending','current_source':{'path':'v2-snapshot/baseline-snapshot/artwork-planet-v1.png','sha256':p['fingerprint']['files']['v2-snapshot/baseline-snapshot/artwork-planet-v1.png']},'current_preview':'Deepwell-v3-preview-20s.mp4','repeat_review':'Deepwell-v3-three-loops-60s.mp4','fingerprint':p['fingerprint'],'files':files,'runtime_binary_fingerprint':'runtime-binary-fingerprint.json','v2_preservation':{'all_manifest_files_exact':True,'checked_count':d['v2_preserved_file_count']},'remote_backup':False,'scope':'Silent 720p review and repeat; no opening, audio, 4K, long assembly, new image generation, paid service, model install, commit or push.','assistant_inspection':'Source/mask/bright-core/all-dim and native/decoded temporal stills; continuous playback not claimed.'})
print('V3 local delivery manifest complete:',len(files),'files; v2 remains exact.',flush=True)
