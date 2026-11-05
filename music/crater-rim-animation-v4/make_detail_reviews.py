"""Actual-video enlarged settlement and road details for V4 playback review."""
import json
import subprocess

from render_scene import HERE, FFMPEG, sha

source = HERE/'Crater-Rim-Survey-v4-60s-loop.mp4'
reports = []
for name, start, seconds, crop, size in [
    ('village', 15, 12, '328:166:952:238', [984, 498]),
    ('road', 8, 20, '108:92:1128:410', [648, 552]),
]:
    target = HERE/f'Crater-Rim-Survey-v4-{name}-detail-{seconds}s.mp4'
    if target.exists():
        raise FileExistsError(target)
    subprocess.run([FFMPEG, '-v', 'error', '-n', '-ss', str(start), '-i', str(source), '-t', str(seconds), '-an',
                    '-vf', f'crop={crop},scale={size[0]}:{size[1]}:flags=lanczos', '-c:v', 'libx264', '-qp', '0',
                    '-preset', 'veryfast', '-threads', '4', '-colorspace', 'bt709', '-color_primaries', 'bt709',
                    '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', str(target)], check=True)
    result = subprocess.check_output([FFMPEG, '-v', 'error', '-i', str(target), '-map', '0', '-f', 'framehash', '-'], text=True)
    rows = [line.split(',') for line in result.splitlines() if line and not line.startswith('#')]
    assert f'#dimensions 0: {size[0]}x{size[1]}' in result and '#tb 0: 1/30' in result and 'audio' not in result
    assert [int(row[2]) for row in rows] == list(range(seconds*30))
    reports.append({'path': target.name, 'sha256': sha(target), 'bytes': target.stat().st_size, 'source_start_seconds': start,
                    'duration_seconds': seconds, 'crop_720p_whxy': crop, 'dimensions': size,
                    'decoded_frames': len(rows), 'sequential_timestamps': True, 'audio': False,
                    'note': 'Enlarged crop of the actual delivered minute, no new detail or altered effects.'})
(HERE/'detail-review-validation.json').write_text(json.dumps({'source': source.name, 'source_sha256': sha(source),
                                                             'clips': reports, 'script_sha256': sha(__file__)}, indent=2)+'\n')
print('Settlement and traffic detail reviews fully decoded and verified', flush=True)
