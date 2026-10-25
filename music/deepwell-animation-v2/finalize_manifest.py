"""Freeze local delivery inventory and actual runtime binaries after verification."""
from render_deepwell_v2 import *
import shutil
assert (H/'project-status-update.json').exists()
d=json.loads((H/'direct-render-validation.json').read_text());p=json.loads((H/'preview-validation.json').read_text())
assert d['v1_all_manifest_files_byte_identical'] and d['direct_native_yuv_controls']['preview']['all_yuv_bytes_exact']
runtime_paths=[Path(sys.executable),Path(shutil.which('ffmpeg')),Path(shutil.which('ffprobe'))]
for module in [cv2,np]:runtime_paths.extend(Path(module.__file__).parent.rglob('*.pyd'))
write_json('runtime-binary-fingerprint.json',{str(q):{'bytes':q.stat().st_size,'sha256':digest(q)} for q in runtime_paths})
inventory={}
for q in sorted(H.rglob('*')):
 if q.is_file() and q.name!='package-manifest.json':inventory[q.relative_to(H).as_posix()]={'bytes':q.stat().st_size,'sha256':digest(q)}
source_info={'path':'baseline-snapshot/artwork-planet-v1.png','sha256':p['fingerprint']['files']['baseline-snapshot/artwork-planet-v1.png']}
write_json('package-manifest.json',{'scene':'Deepwell Station','version':'v2','date':'2026-10-25','status':'Full refinement candidate; v1 decent first pass, v2 user verdict pending','user_feedback':'user-feedback.json','current_source':source_info,'current_preview':'Deepwell-v2-preview-20s.mp4','repeat_review':'Deepwell-v2-three-loops-60s.mp4','fingerprint':p['fingerprint'],'files':inventory,'v1_preservation':{'manifest':'../deepwell-animation-v1/package-manifest.json','all_manifest_files_exact':True,'checked_count':d['v1_preserved_file_count']},'runtime_binary_fingerprint':'runtime-binary-fingerprint.json','assistant_inspection':'Native source/masks, normal-size temporal/decoded stills, isolated exterior/details comparisons. Continuous playback not claimed.','remote_backup':False,'scope':'Silent 720p review and repeat; no audio, opening, 4K, long assembly, new generation, model install, commit or push. 300% is ambition, not a measurement.'})
print('Local v2 delivery manifest complete:',len(inventory),'files; v1 remains exact.',flush=True)
