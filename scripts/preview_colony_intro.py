"""Render a silent branding review through the actual Colony assembly engine."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-root', type=Path, default=Path('C:/dev/SpeedySlideShow'))
    parser.add_argument('--video', type=Path, default=root/'music/rainline-animation-v5/rainline-relay-v5-preview-20s.mp4')
    parser.add_argument('--title', default='Rainline Relay')
    parser.add_argument('--output', type=Path, default=root/'creative/brand/intro-v3')
    args = parser.parse_args()
    sys.path.insert(0, str(args.tool_root))
    from colony import render as R
    from colony.intro import IntroSettings, make_cards, VERSION
    from PIL import Image, ImageDraw
    args.output.mkdir(parents=True, exist_ok=True)
    settings = IntroSettings(args.title)
    result = R.preview_opening(str(args.video), [], str(args.output/f'colony-intro-v{VERSION}-silent-preview.mp4'),
                              intro=settings, on_status=print)
    if not result.verified:
        raise RuntimeError('Preview verification failed')
    samples = []
    for t, label in [(1, 'Near-black opening'), (6, 'Larger logo / channel / PRESENTS'),
                     (13, 'Larger title + lower invitation'), (16, 'Title gone; invitation stays'),
                     (19, 'Invitation still held'), (23, 'Clear scene')]:
        path = args.output/f'frame-{t:02d}s.png'
        subprocess.run([R.get_ffmpeg_path(), '-y', '-v', 'error', '-ss', str(t), '-i', result.output,
                        '-frames:v', '1', str(path)], check=True)
        samples.append((path, label, t))
    sheet = Image.new('RGB', (1280, 3*400), '#121820')
    d = ImageDraw.Draw(sheet)
    for i, (path, label, t) in enumerate(samples):
        x, y = (i%2)*640, (i//2)*400
        im = Image.open(path).convert('RGB').resize((640, 360), Image.Resampling.LANCZOS)
        sheet.paste(im, (x, y))
        d.text((x+12, y+371), f'{t:02d}s â€” {label}', fill='#F3EBDD')
    sheet.save(args.output/'timing-contact-sheet.jpg', quality=93)
    make_cards(settings, 3840, 2160, args.output/'native-4k-graphics')
    record = {'date': '2026-10-13', 'purpose': 'Reusable opening treatment, not a new release or soundtrack',
              'source_video': str(args.video), 'source_sha256': hashlib.sha256(args.video.read_bytes()).hexdigest(),
              'tool_root': str(args.tool_root), 'settings': settings.record(),
              'preview': str(Path(result.output).resolve()), 'manifest': str(Path(result.manifest).resolve()),
              'silent': True, 'user_visual_approval': 'pending',
              'inspection': 'Decoded temporal stills and technical checks; no continuous playback or listening claim.'}
    (args.output/'delivery.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    R.clear_prepared()
    print(json.dumps({'preview': result.output, 'verified': result.verified}))


if __name__ == '__main__':
    main()
