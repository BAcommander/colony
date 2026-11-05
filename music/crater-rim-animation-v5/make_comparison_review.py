"""Same scene time and full picture size: ten seconds of V4, then ten seconds of V5."""
import json
import subprocess

from render_scene import HERE, ROOT, FFMPEG, sha

old = ROOT/'music/crater-rim-animation-v4/Crater-Rim-Survey-v4-60s-loop.mp4'
new = HERE/'Crater-Rim-Survey-v5-60s-loop.mp4'
target = HERE/'Crater-Rim-Survey-v4-vs-v5-normal-size-20s.mp4'
if target.exists():
    raise FileExistsError(target)
graph = '[0:v]trim=start=17:end=27,setpts=PTS-STARTPTS[a];[1:v]trim=start=17:end=27,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
subprocess.run([FFMPEG, '-v', 'error', '-n', '-i', str(old), '-i', str(new), '-filter_complex', graph,
                '-map', '[v]', '-an', '-c:v', 'libx264', '-qp', '0', '-preset', 'veryfast', '-threads', '4',
                '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                '-color_range', 'tv', '-movflags', '+faststart', str(target)], check=True)

def framehash(path, count):
    result = subprocess.check_output([FFMPEG, '-v', 'error', '-i', str(path), '-map', '0:v', '-f', 'framehash', '-'], text=True)
    assert '#dimensions 0: 1280x720' in result and '#tb 0: 1/30' in result
    rows = [line.split(',') for line in result.splitlines() if line and not line.startswith('#')]
    assert [int(row[2]) for row in rows] == list(range(count))
    return [row[-1].strip() for row in rows]

actual = framehash(target, 600)
assert actual == framehash(old, 1800)[510:810]+framehash(new, 1800)[510:810]
report = {'path': target.name, 'sha256': sha(target), 'bytes': target.stat().st_size,
          'dimensions': [1280, 720], 'duration_seconds': 20, 'decoded_frames': 600,
          'all_pictures_equal_to_source_segments': True, 'sequential_timestamps': True, 'audio': False,
          'first_10_seconds': {'version': 4, 'source_scene_time': [17, 27], 'source_sha256': sha(old)},
          'second_10_seconds': {'version': 5, 'source_scene_time': [17, 27], 'source_sha256': sha(new)},
          'no_zoom_or_effect_amplification_in_comparison': True, 'script_sha256': sha(__file__)}
(HERE/'comparison-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print('Normal-size V4/V5 comparison verified against all 600 source pictures', flush=True)
