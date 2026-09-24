"""Extract a labelled contact sheet and metadata; does not substitute for playback review."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

p = argparse.ArgumentParser()
p.add_argument('video', type=Path)
args = p.parse_args()
cap = cv2.VideoCapture(str(args.video))
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
indices = np.linspace(0, n-1, 6).astype(int).tolist()
canvas = Image.new('RGB', (1280, 1140))
draw = ImageDraw.Draw(canvas)
for j, index in enumerate(indices):
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError(f'Unreadable frame {index}')
    preview = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    preview.thumbnail((640, 352))
    x, y = (j % 2)*640, (j//2)*380
    canvas.paste(preview, (x, y))
    draw.text((x+8, y+355), f'Frame {index}/{n} - {index/fps:.2f}s', fill='white')
out = args.video.with_suffix('.contact.jpg')
canvas.save(out)
metadata = {'frames': n, 'fps': fps, 'duration_seconds': n/fps,
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'bytes': args.video.stat().st_size, 'inspected_frames': indices}
args.video.with_suffix('.inspection.json').write_text(json.dumps(metadata, indent=2), encoding='utf8')
print(json.dumps(metadata))
print(out)
