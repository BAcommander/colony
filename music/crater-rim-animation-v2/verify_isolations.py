"""Bind retained eight-second layer auditions to the final renderer's native pictures."""
import json
import subprocess

import cv2

from render_scene import HERE, FFMPEG, Scene, sha
from validate_delivery import framehash


scene = Scene()
reports = []
for name in ['clouds', 'haze', 'shadows', 'survey']:
    path = HERE/f'Crater-Rim-Survey-v2-{name}-8s.mp4'
    framehash(path, 240)
    indices = [0, 150, 239]
    rgb = b''.join(cv2.resize(scene.frame(5+i/30, name), (1280, 720), interpolation=cv2.INTER_AREA).tobytes() for i in indices)
    expected = subprocess.check_output([FFMPEG, '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-s', '1280x720',
                                        '-i', 'pipe:0', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                                        '-pix_fmt', 'yuv420p', '-f', 'rawvideo', '-'], input=rgb)
    decoded = subprocess.check_output([FFMPEG, '-v', 'error', '-i', str(path), '-vf', 'select=eq(n\\,0)+eq(n\\,150)+eq(n\\,239)',
                                       '-fps_mode', 'passthrough', '-frames:v', '3', '-pix_fmt', 'yuv420p', '-f', 'rawvideo', '-'])
    assert decoded == expected, name
    reports.append({'layer': name, 'path': path.name, 'sha256': sha(path), 'bytes': path.stat().st_size,
                    'decoded_frames': 240, 'sequential_timestamps': True, 'audio': False, 'start_scene_time': 5,
                    'direct_picture_control_indices': indices, 'all_native_to_encoded_yuv_controls_exact': True})
report = {'frozen_inputs': scene.fingerprint(), 'verification_script_sha256': sha(__file__), 'clips': reports}
(HERE/'isolation-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print('All four isolated clips match the final native renderer controls', flush=True)
