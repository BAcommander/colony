"""Once-only Ambient Colony opening, rendered as native transparent graphics.

The scene stays in YUV. Only the small title cards are converted from RGB;
the normal loop is stream-copied after the opening segment by render.py.
"""
from dataclasses import dataclass, asdict
import hashlib
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

VERSION = 3
DURATION = 22.0
TAGLINE = 'Stay a while and listen'
IVORY = '#F3EBDD'
AMBER = '#E7A83E'
FONTS = Path(__file__).resolve().parent / 'assets' / 'fonts'
# (start fade-in, end fade-in, start fade-out, end fade-out).
# The final invitation deliberately overlaps the location title and holds
# fully visible for five seconds after that title has cleared.
WINDOWS = {'brand': (2, 3.2, 8, 9), 'presents': (4.8, 5.8, 8, 9),
           'title': (10, 11, 14, 15), 'tagline': (12, 13, 20, 21.5)}
DIM_OPACITY = .88


@dataclass(frozen=True)
class IntroSettings:
    title: str
    fade_audio: bool = True

    def validate(self):
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError('Enter the public video title for the opening.')
        if len(self.title) > 160 or any(ord(c) < 32 and c != '\n' for c in self.title):
            raise ValueError('Opening title must be at most 160 characters, without control characters.')
        if len(self.title.strip().splitlines()) > 2:
            raise ValueError('Use one or two lines for the opening title.')

    def record(self):
        self.validate()
        return {**asdict(self), 'version': VERSION, 'duration_s': DURATION,
                'channel': 'AMBIENT COLONY', 'tagline': TAGLINE,
                'brand_s': WINDOWS['brand'], 'presents_s': WINDOWS['presents'],
                'title_s': WINDOWS['title'], 'tagline_s': WINDOWS['tagline'],
                'presents': 'PRESENTS', 'presents_center_y_fraction': .525, 'tagline_center_y_fraction': .89,
                'channel_font_height_fraction': .077, 'title_font_height_fraction': .165,
                'underline_width_height_fraction': .22,
                'black_overlay_opacity': DIM_OPACITY, 'scene_reveal_s': [10, 20],
                'audio_fade_s': [5, 20] if self.fade_audio else None,
                'font_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(FONTS.glob('*.ttf'))},
                'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def _font(size, bold=True):
    return ImageFont.truetype(str(FONTS / ('BarlowCondensed-SemiBold.ttf' if bold
                                         else 'BarlowCondensed-Regular.ttf')), max(1, round(size)))


def _tracked(draw, text, font, spacing, xy=None):
    width = sum(draw.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)
    if xy is not None:
        x, y = xy
        for c in text:
            draw.text((x, y), c, font=font, fill=IVORY, anchor='lm')
            x += draw.textlength(c, font=font) + spacing
    return width


def _title_lines(draw, title, font, max_width):
    title = title.strip().upper()
    if '\n' in title:
        return [s.strip() for s in title.splitlines()]
    if draw.textlength(title, font=font) <= max_width:
        return [title]
    words = title.split()
    if len(words) < 2:
        return [title]
    pairs = [(' '.join(words[:i]), ' '.join(words[i:])) for i in range(1, len(words))]
    return list(min(pairs, key=lambda pair: max(draw.textlength(s, font=font) for s in pair)))


def make_cards(settings, width, height, directory):
    """Four cropped, antialiased cards at output resolution (including 4K)."""
    settings.validate()
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    # Supersampling also keeps thin orbital strokes clean in small previews.
    scale = 2 if width < 2560 else 1
    w, h = width * scale, height * scale
    cards = []
    for kind in WINDOWS:
        im = Image.new('RGBA', (w, h))
        d = ImageDraw.Draw(im)
        if kind == 'brand':
            font = _font(h * .077)
            spacing = h * .010
            tw = _tracked(d, 'AMBIENT COLONY', font, spacing)
            radius, gap = h * .043, h * .038
            total = radius * 2 + gap * 2 + tw
            x, y = (w - total) / 2, h * .455
            cx = x + radius
            d.ellipse((x, y-radius, x+2*radius, y+radius), outline=IVORY, width=max(1, round(h*.002)))
            dotx, doty = cx+radius/math.sqrt(2), y-radius/math.sqrt(2)
            dot = h * .006
            d.ellipse((dotx-dot, doty-dot, dotx+dot, doty+dot), fill=IVORY)
            rule_x = x+radius*2+gap
            d.line((rule_x, y-radius*.85, rule_x, y+radius*.85), fill=AMBER, width=max(1, round(h*.002)))
            _tracked(d, 'AMBIENT COLONY', font, spacing, (rule_x+gap, y))
        elif kind == 'presents':
            font, spacing = _font(h*.030, bold=False), h*.010
            tw = _tracked(d, 'PRESENTS', font, spacing)
            _tracked(d, 'PRESENTS', font, spacing, ((w-tw)/2, h*.525))
        elif kind == 'title':
            size = h * .165
            font = _font(size)
            lines = _title_lines(d, settings.title, font, w*.80)
            while max(d.textlength(line, font=font) for line in lines) > w*.80 and size > h*.035:
                size -= max(1, h*.002)
                font = _font(size)
            if max(d.textlength(line, font=font) for line in lines) > w*.84:
                raise ValueError('Title is too wide. Use a shorter title or a line break.')
            line_h = size * 1.05
            for i, line in enumerate(lines):
                d.text((w/2, h/2+(i-(len(lines)-1)/2)*line_h), line, font=font, fill=IVORY, anchor='mm')
            ry = h/2+len(lines)*line_h/2+h*.021
            d.line((w/2-h*.110, ry, w/2+h*.110, ry), fill=AMBER, width=max(1, round(h*.005)))
        else:
            d.text((w/2, h*.89), TAGLINE, font=_font(h*.044, bold=False), fill=IVORY, anchor='mm')
        # Even padding avoids clipping glyph antialiasing / chroma conversion.
        box = im.getbbox()
        left = max(0, (box[0]//scale-4)//2*2)
        top = max(0, (box[1]//scale-4)//2*2)
        right = min(width, math.ceil((box[2]/scale+4)/2)*2)
        bottom = min(height, math.ceil((box[3]/scale+4)/2)*2)
        if scale != 1:
            im = im.resize((width, height), Image.Resampling.LANCZOS)
        path = directory / (kind + '.png')
        im.crop((left, top, right, bottom)).save(path)
        cards.append((str(path), left, top))
    return cards


def video_graph(cards, width, height, fps, matrix):
    # Explicit alpha fading, explicit YUV format: no whole-scene RGB round-trip.
    graphs = [f'color=c=black@{DIM_OPACITY}:s={width}x{height}:r={fps}:d=20,format=yuva420p,'
              'fade=t=out:st=10:d=10:alpha=1[dim]',
              '[0:v:0][dim]overlay=eof_action=pass:repeatlast=0:format=yuv420[bg]']
    previous = 'bg'
    for i, ((_, x, y), (start, hold, end, clear)) in enumerate(zip(cards, WINDOWS.values()), 1):
        graphs.append(f'[{i}:v:0]format=rgba,fade=t=in:st={start}:d={hold-start}:alpha=1,'
                      f'fade=t=out:st={end}:d={clear-end}:alpha=1,'
                      f'scale=out_color_matrix={matrix}:out_range=tv,format=yuva420p[card{i}]')
        label = 'v' if i == len(cards) else f'bg{i}'
        graphs.append(f'[{previous}][card{i}]overlay=x={x}:y={y}:eof_action=pass:'
                      f'repeatlast=0:format=yuv420[{label}]')
        previous = label
    return ';'.join(graphs)


def audio_graph(graph, settings):
    """One sample-based fade after the final music/SFX mix; events are not moved."""
    if not settings or not settings.fade_audio:
        return graph
    return graph.replace('[aout]', '[intro_mix]') + ';[intro_mix]afade=t=in:st=5:d=15:curve=hsin[aout]'
