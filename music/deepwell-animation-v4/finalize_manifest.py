"""Freeze local v4 files and actual runtime binaries after complete checks."""
from render_deepwell_v4 import *
import shutil
assert (H/'project-status-update.json').exists()
p=json.loads((H/'preview-validation.json').read_text());d=json.loads((H/'direct-render-validation.json').read_text())
assert d['all_selected_yuv_bytes_exact'] and d['all_v3_manifest_files_exact']
paths=[Path(sys.executable),Path(shutil.which('ffmpeg')),Path(shutil.which('ffprobe'))]
for module in [cv2,np]:paths.extend(Path(module.__file__).parent.rglob('*.pyd'))
save('runtime-binary-fingerprint.json',{str(q):{'bytes':q.stat().st_size,'sha256':digest(q)} for q in paths})
files={q.relative_to(H).as_posix():{'bytes':q.stat().st_size,'sha256':digest(q)} for q in sorted(H.rglob('*')) if q.is_file() and q.name!='package-manifest.json'}
source='v3-snapshot/v2-snapshot/baseline-snapshot/artwork-planet-v1.png'
save('package-manifest.json',{'scene':'Deepwell Station','version':'v4','date':'2026-10-25','status':'V3 vapor/cyan visibility failed user review; v4 rolling vapor and purple return sequence are review candidates','current_source':{'path':source,'sha256':p['fingerprint']['files'][source]},'current_preview':'Deepwell-v4-preview-20s.mp4','repeat_review':'Deepwell-v4-three-loops-60s.mp4','pipeline_full_roundtrip_test':'deepwell-v4-pipeline-roundtrip-20s.mp4','fingerprint':p['fingerprint'],'files':files,'v3_preservation':{'all_manifest_files_exact':True,'checked_count':d['v3_preserved_file_count']},'runtime_binary_fingerprint':'runtime-binary-fingerprint.json','remote_backup':False,'scope':'Silent 720p review/repeats; no new artwork, audio, opening, 4K, long assembly, paid service, model install, commit or push.','assistant_inspection':'Unamplified native/actual-conversion 720p and isolated/final decoded temporal stills. Continuous playback not claimed; user verdict pending.'})
print('V4 local delivery manifest complete:',len(files),'files; v3 remains exact.',flush=True)
