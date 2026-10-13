"""
Colony renderer: one short video looped under a playlist of audio tracks.

The output MP4 is the video repeated for as long as the playlist runs, with
every track played in full, in order, and an equal-power crossfade between
neighbours.

Built on the Speedy SlideShow exporter (app/exporter.py): its ffmpeg
lookup, concat lists, cancellable runners and stderr progress parsing. How
the export works, and why:

1. The video is re-encoded ONCE into a clean loop unit (H.264, yuv420p,
   even dimensions, constant frame rate, no B-frames, no audio). Every
   copy of it is then byte-identical, so the concat demuxer can repeat it
   with stream copy: a 90-minute export encodes 10 seconds of video, not
   90 minutes. No B-frames keeps the timestamps monotonic across each
   loop seam under stream copy.
2. Each track is measured with ebur128 (integrated LUFS, the same
   EBU R128 measure loudnorm uses, and the exact decoded length: a VBR
   MP3's header duration can be off by seconds). A single decode gives
   both. Not loudnorm's analysis pass: it resamples to 192 kHz internally
   and took 13 s per 9.5-minute track against ebur128's 0.5 s, for the
   same reading (-12.46 vs -12.4 LUFS).
3. One final ffmpeg run: an optional per-track linear gain to TARGET_LUFS,
   the acrossfade chain, one peak limiter at the end, AAC audio, and the
   looped video copied in and cut at the playlist's length.

Audio level. By default every track keeps the level it was supplied at:
Colony's output goes to YouTube, which turns loud uploads down to -14 LUFS
and leaves quiet ones alone, so a soundtrack mastered at -17.7 LUFS plays
at -17.7 either way, and gaining it to a target only makes this video
louder than the others in a series that use the same soundtrack (the
first two-hour Basalt export came out 1.7 dB above its soundtrack for
exactly that reason). Loudness matching is an option for playlists of
mixed sources, and then it is a fixed linear gain per track to
TARGET_LUFS, not loudnorm's dynamic mode, which rides the level inside a
track and flattens music.

The optional overlay (a greenscreen clip, e.g. a subscribe banner) keeps
the copy-only video path. Each showing starts on a loop-unit boundary
(the nearest one to the wanted time, so at most half a loop early or
late), which makes every showing the SAME few seconds of video: k
consecutive loop units with the overlay keyed on top, where k units cover
the overlay's length. That chunk is encoded once, with the loop unit's
exact encoder settings so the concat demuxer can splice it in by stream
copy, and the concat list simply names the chunk wherever a showing is
due. The default is one showing, centred on the middle of the video.

Colour. The chunk is built in YUV end to end and both encodes carry the
same explicit colour tags. The first version keyed the overlay in RGBA
and let ffmpeg's overlay filter pick its working format, which pushed the
whole background through RGB and back with a different matrix and
dropped the bt709 tags from the chunk: the background visibly shifted
warmer for the duration of every showing, graphic or no graphic. The
graphic alone is keyed in RGB (colorkey needs it) and converted to
yuva420p with the loop's own matrix; the background never leaves
yuv420p. TestRender.test_overlay_chunk_keeps_colour guards this.
"""

import json
import logging
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from colony.sfx import SfxSettings, mix_graph, prepare_loop
from colony import intro as opening
from colony.intro import IntroSettings
from app import exporter
from app.exporter import (
    ExportCancelled, get_ffmpeg_path, get_video_duration, write_concat_list,
)
from app.utils import atomic_write_json

logger = logging.getLogger(__name__)

# Loudness tracks are matched to when matching is on: YouTube's reference.
# The main app's LOUDNORM_FILTER targets -16 for PC/TV playback; a -16
# upload sits 2 dB under everything YouTube normalises around it
TARGET_LUFS = -14.0
# A near-silent track (a long fade, a spoken intro recorded quietly) must
# not be boosted into a wall of noise; beyond this it stays quieter
MAX_GAIN_DB = 20.0
# At or below this the measurement is silence, not a level (ebur128's
# absolute gate is -70 LUFS: a silent track reads exactly -70.0)
SILENCE_LUFS = -70.0
# The limiter ceiling: -1.5 dBFS, LOUDNORM_FILTER's TP. Linear gain can
# push a quiet-but-peaky track past full scale, and two tracks overlapping
# in a crossfade can sum above either one. A track already under the
# ceiling passes through it untouched
LIMIT_DBFS = -1.5
LIMIT_LINEAR = round(10 ** (LIMIT_DBFS / 20), 4)
SAMPLE_RATE = 48000
AUDIO_BITRATE = '192k'
DEFAULT_CROSSFADE_S = 5.0
MAX_CROSSFADE_S = 30.0
# The loop unit is encoded once, so it can afford the slow preset; its
# bitrate is the whole export's video bitrate (a 72-minute 1080p export of
# a busy test pattern: CRF 18 medium 3.6 GB/hour, CRF 20 slow 3.1)
LOOP_CRF = 20
LOOP_PRESET = 'slow'

# Overlay: keyed on pure green (a flat #00FF00 background; similarity 0.3
# and blend 0.1 took the anti-aliased edges of the 1080x200 sponsor banner
# cleanly with no green fringe, so no despill, which would also tint any
# genuinely green part of the overlay). The overlay is treated as authored
# for 1080p: on a 4K export it and its bottom margin are scaled x2, and it
# is shrunk if it would be wider than OVERLAY_MAX_WIDTH of the frame.
OVERLAY_KEY_COLOR = '0x00FF00'
OVERLAY_KEY_SIMILARITY = 0.3
OVERLAY_KEY_BLEND = 0.1
OVERLAY_REFERENCE_HEIGHT = 1080
OVERLAY_MAX_WIDTH = 0.9
DEFAULT_OVERLAY_EVERY_S = 15 * 60
DEFAULT_OVERLAY_BOTTOM_PX = 100
OVERLAY_OFF, OVERLAY_ONCE, OVERLAY_EVERY = 'off', 'once', 'every'
OVERLAY_MODES = (OVERLAY_OFF, OVERLAY_ONCE, OVERLAY_EVERY)

# The finished file may be up to this much longer than the playlist: the
# copied video stops at the first packet past the cut, the audio exactly
DURATION_TOLERANCE_S = 1.0

# ebur128's closing summary: "Integrated loudness:" then "I: -12.4 LUFS"
_EBUR128_I_RE = re.compile(r'Integrated loudness:\s*I:\s*(-?[0-9.]+|-?inf)\s*LUFS')
# "Stream #0:0[0x1](und): Video: h264 (High) (avc1 / 0x31637661),
#  yuv420p(tv, bt709, progressive), 3840x2160 [SAR 1:1 DAR 16:9], 30 fps"
_VIDEO_LINE_RE = re.compile(
    r'Stream #\d+:\d+.*?: Video: (?P<codec>[^,]+), (?P<pix>[a-z0-9]+)'
    r'(?:\((?P<pixinfo>[^)]*)\))?, (?P<w>\d{2,5})x(?P<h>\d{2,5})')
_FPS_RE = re.compile(r', (\d+(?:\.\d+)?) fps')
_TBR_RE = re.compile(r', (\d+(?:\.\d+)?) tbr')
# "Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp"
_AUDIO_LINE_RE = re.compile(
    r'Stream #\d+:\d+.*?: Audio: (?P<codec>[^,]+), (?P<rate>\d+) Hz, (?P<layout>[^,\n]+)')
_DURATION_RE = re.compile(r'Duration: (\d+):(\d{2}):(\d{2}(?:\.\d+)?)')

# Colour tags as ffmpeg prints them (the -colorspace names) -> what the
# scale filter's out_color_matrix calls the same matrix
_SCALE_MATRIX = {
    'bt709': 'bt709', 'smpte170m': 'smpte170m', 'bt470bg': 'bt470',
    'bt2020nc': 'bt2020', 'bt2020c': 'bt2020', 'smpte240m': 'smpte240m', 'fcc': 'fcc',
}
# The primaries + transfer that go with a matrix when the source tags
# only the matrix (ffmpeg prints "bt709" alone when all three agree, and
# "bt470bg/unknown/unknown" when the others are missing)
_PARTNER_TAGS = {
    'bt709': ('bt709', 'bt709'), 'smpte170m': ('smpte170m', 'smpte170m'),
    'bt470bg': ('bt470bg', 'smpte170m'), 'smpte240m': ('smpte240m', 'smpte240m'),
    'bt2020nc': ('bt2020', 'bt2020-10'), 'bt2020c': ('bt2020', 'bt2020-10'),
    'fcc': ('bt470m', 'bt709'),
}

ProgressFn = Callable[[float, Optional[float]], None]     # (fraction 0..1, ETA seconds or None)
StatusFn = Callable[[str], None]


# ── Track arithmetic ──

@dataclass
class TrackInfo:
    path: str
    duration: float                 # seconds, from the full decode
    loudness: Optional[float]       # integrated LUFS; None when silent/unmeasurable

    @property
    def gain_db(self) -> float:
        """The gain loudness matching WOULD apply (0 when it is off)."""
        return track_gain_db(self.loudness)


def track_gain_db(loudness: Optional[float]) -> float:
    """The linear gain that brings a track to TARGET_LUFS, capped at
    +MAX_GAIN_DB; 0 for silence or a failed measurement."""
    if loudness is None or not math.isfinite(loudness) or loudness <= SILENCE_LUFS:
        return 0.0
    return min(MAX_GAIN_DB, TARGET_LUFS - loudness)


def clamp_crossfade(crossfade: float, durations: List[float]) -> float:
    """The crossfade actually used: 0 for a single track, never negative,
    at most MAX_CROSSFADE_S, and at most half the shortest track (acrossfade
    needs both sides longer than the fade, and a track shorter than two
    fades would be crossfaded into from both ends at once)."""
    if len(durations) < 2 or crossfade <= 0:
        return 0.0
    return max(0.0, min(float(crossfade), MAX_CROSSFADE_S, min(durations) / 2.0))


def total_duration(durations: List[float], crossfade: float) -> float:
    """Length of the finished playlist: every track in full, each
    crossfade overlapping two of them."""
    if not durations:
        return 0.0
    return sum(durations) - clamp_crossfade(crossfade, durations) * (len(durations) - 1)


def loop_repeats(total: float, loop_duration: float) -> int:
    """Copies of the loop unit to list: enough to cover the playlist, plus
    one so the output cut never lands past the end of the video."""
    return max(1, math.ceil(total / loop_duration)) + 1


def build_audio_graph(gains_db: List[float], crossfade: float, first_input: int = 1) -> str:
    """The -filter_complex audio graph, ending in [aout].

    Each track (ffmpeg input first_input + i) is resampled to 48 kHz
    stereo float, gained, then chained through acrossfade (qsin: equal
    power, so the overlap doesn't dip in loudness) or concat when the
    crossfade is 0. The chain ends in one limiter; level=0 stops alimiter
    from its default auto-levelling, latency=1 compensates its lookahead
    delay so audio stays on the video's clock."""
    if not gains_db:
        raise ValueError('No audio tracks')
    parts = []
    labels = []
    for i, gain in enumerate(gains_db):
        label = f'a{i}'
        parts.append(f'[{first_input + i}:a:0]aresample={SAMPLE_RATE},'
                     f'aformat=sample_fmts=fltp:channel_layouts=stereo,'
                     f'volume={gain:.2f}dB[{label}]')
        labels.append(label)

    if len(labels) == 1:
        last = labels[0]
    elif crossfade > 0:
        last = labels[0]
        for i, label in enumerate(labels[1:], start=1):
            out = f'x{i}'
            parts.append(f'[{last}][{label}]acrossfade=d={crossfade:.3f}:c1=qsin:c2=qsin[{out}]')
            last = out
    else:
        parts.append(''.join(f'[{l}]' for l in labels) + f'concat=n={len(labels)}:v=0:a=1[cat]')
        last = 'cat'

    parts.append(f'[{last}]alimiter=limit={LIMIT_LINEAR}:level=0:latency=1[aout]')
    return ';'.join(parts)


def parse_ebur128_report(stderr: str) -> Optional[float]:
    """Integrated loudness (LUFS) from ebur128's closing summary, None
    when absent or not a finite level."""
    hits = _EBUR128_I_RE.findall(stderr or '')
    if not hits:
        return None
    value = float(hits[-1])
    return value if math.isfinite(value) else None


def parse_decoded_seconds(stderr: str) -> Optional[float]:
    """The final "time=" in ffmpeg's stats: how much audio was decoded."""
    hits = exporter._FFMPEG_TIME_RE.findall(stderr or '')
    if not hits:
        return None
    h, m, s = hits[-1]
    secs = int(h) * 3600 + int(m) * 60 + float(s)
    return secs if secs > 0 else None


def measure_track(ffmpeg: str, path: str) -> TrackInfo:
    """Decode one track once: integrated loudness and exact length."""
    header = get_video_duration(path)
    timeout = int(300 + 2 * header) if header else 3600
    r = exporter._run_ffmpeg(
        [ffmpeg, '-hide_banner', '-nostdin', '-i', path, '-vn', '-sn', '-dn',
         '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'],
        timeout=timeout)
    duration = parse_decoded_seconds(r.stderr) or header
    if not duration:
        raise RuntimeError(f'Could not read the length of {os.path.basename(path)}')
    return TrackInfo(path, duration, parse_ebur128_report(r.stderr))


# ── Probing ──

@dataclass
class VideoInfo:
    path: str
    width: int
    height: int
    fps: Optional[float]
    duration: Optional[float]
    pix_fmt: str = ''
    color_space: Optional[str] = None
    color_primaries: Optional[str] = None
    color_trc: Optional[str] = None
    color_range: Optional[str] = None
    audio: Optional[str] = None         # "aac, 48000 Hz, stereo" or None

    @property
    def size(self) -> Tuple[int, int]:
        return self.width, self.height

    def describe(self) -> str:
        fps = f'{self.fps:g} fps' if self.fps else 'unknown fps'
        return f'{self.width}x{self.height}, {fps}'


def parse_stream_info(stderr: str) -> dict:
    """What `ffmpeg -i` says about a file's first video and audio streams
    (a dict of VideoInfo fields minus path); ValueError with no video."""
    text = stderr or ''
    m = _VIDEO_LINE_RE.search(text)
    if not m:
        raise ValueError('no video stream')
    end = text.find('\n', m.start())
    line = text[m.start():end if end != -1 else len(text)]
    info = {
        'width': int(m.group('w')), 'height': int(m.group('h')), 'pix_fmt': m.group('pix'),
        'fps': None, 'duration': None, 'color_space': None, 'color_primaries': None,
        'color_trc': None, 'color_range': None, 'audio': None,
    }
    for tok in (m.group('pixinfo') or '').split(','):
        tok = tok.strip()
        if tok in ('tv', 'pc'):
            info['color_range'] = tok
        elif '/' in tok or tok in _SCALE_MATRIX:
            parts = (tok.split('/') + [None, None, None])[:3]
            space, primaries, trc = [None if p in (None, 'unknown') else p for p in parts]
            if '/' not in tok:
                primaries = trc = space
            info.update(color_space=space, color_primaries=primaries, color_trc=trc)
    fps = _FPS_RE.search(line) or _TBR_RE.search(line)
    if fps:
        info['fps'] = float(fps.group(1))
    a = _AUDIO_LINE_RE.search(text)
    if a:
        info['audio'] = f"{a.group('codec').split(' ')[0]}, {a.group('rate')} Hz, {a.group('layout').strip()}"
    d = _DURATION_RE.search(text)
    if d:
        info['duration'] = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))
    return info


def probe_video(ffmpeg: str, path: str) -> VideoInfo:
    """Header probe of a video file (ffmpeg -i: no ffprobe in imageio-ffmpeg)."""
    r = subprocess.run([ffmpeg, '-hide_banner', '-i', path], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=30,
                       creationflags=exporter._subprocess_flags)
    try:
        info = parse_stream_info(r.stderr)
    except ValueError:
        raise RuntimeError(f'No video found in {os.path.basename(path)}')
    if not info['duration']:
        info['duration'] = get_video_duration(path)
    return VideoInfo(path=path, **info)


@dataclass(frozen=True)
class ColorTags:
    """The colour metadata every encode in one export is stamped with.
    The loop unit and the overlay chunk MUST match: the concat demuxer
    splices them by stream copy and a player reads one set of tags."""
    space: str = 'bt709'
    primaries: str = 'bt709'
    trc: str = 'bt709'
    range: str = 'tv'

    @property
    def matrix(self) -> str:
        """The same matrix as the scale filter names it."""
        return _SCALE_MATRIX.get(self.space, 'bt709')

    def encoder_args(self) -> list:
        return ['-colorspace', self.space, '-color_primaries', self.primaries,
                '-color_trc', self.trc, '-color_range', self.range]

    def describe(self) -> str:
        return self.space if self.space == self.primaries == self.trc \
            else f'{self.space}/{self.primaries}/{self.trc}'


def color_tags_for(source: VideoInfo) -> ColorTags:
    """The source's own tags, completed where it only tags the matrix;
    untagged HD is bt709, untagged SD is bt601 (what players assume)."""
    space = source.color_space if source.color_space in _SCALE_MATRIX else None
    if space is None:
        space = 'bt709' if source.height >= 720 else 'smpte170m'
    primaries, trc = _PARTNER_TAGS[space]
    return ColorTags(space, source.color_primaries or primaries, source.color_trc or trc, 'tv')


# ── Encodes ──

def _loop_encode_args(color: ColorTags) -> list:
    """The one encoder setting for everything that goes in the concat
    list. The loop unit and the overlay chunk MUST share it: the demuxer
    splices them by stream copy under the first file's stream headers."""
    return (['-an', '-sn', '-dn', '-fps_mode', 'cfr',
             '-c:v', 'libx264', '-preset', LOOP_PRESET, '-crf', str(LOOP_CRF),
             '-bf', '0', '-pix_fmt', 'yuv420p'] + color.encoder_args()
            + ['-movflags', '+faststart'])


def _encode_timeout(seconds: Optional[float]) -> int:
    """Room for the slow preset on a 4K source: a few fps at worst."""
    return int(900 + 30 * (seconds or 0))


def make_loop_unit(ffmpeg: str, video: str, out_path: str, color: ColorTags,
                   source_duration: Optional[float] = None,
                   on_progress: Optional[Callable[[float], None]] = None) -> float:
    """Re-encode the video into the loop unit (see module docstring).
    Returns its duration."""
    exporter._run_ffmpeg_streaming(
        [ffmpeg, '-y', '-hide_banner', '-nostdin', '-i', video, '-map', '0:v:0',
         '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2:out_range=tv']
        + _loop_encode_args(color) + [out_path],
        timeout=_encode_timeout(source_duration), total_seconds=source_duration,
        on_progress=on_progress)
    duration = get_video_duration(out_path)
    if not duration or duration <= 0:
        raise RuntimeError('Could not read the length of the video')
    return duration


def overlay_placement(frame_w: int, frame_h: int, ov_w: int, ov_h: int,
                      bottom_px: float) -> tuple:
    """(width, height, bottom margin) of the overlay on this frame: scaled
    by frame_h / OVERLAY_REFERENCE_HEIGHT, shrunk to fit OVERLAY_MAX_WIDTH,
    even sizes (yuv420p), never pushed off the top of the frame."""
    scale = min(frame_h / OVERLAY_REFERENCE_HEIGHT, OVERLAY_MAX_WIDTH * frame_w / ov_w)
    w = max(2, int(round(ov_w * scale / 2)) * 2)
    h = max(2, int(round(ov_h * scale / 2)) * 2)
    margin = int(round(max(0.0, bottom_px) * frame_h / OVERLAY_REFERENCE_HEIGHT))
    return w, h, max(0, min(margin, frame_h - h))


def overlay_graph(w: int, h: int, margin: int, color: ColorTags) -> str:
    """The chunk's filter graph. The graphic is keyed in RGB (colorkey
    works there) and converted to yuva420p with the loop's own matrix;
    the overlay filter is pinned to yuv420 so the background never leaves
    YUV. See the module docstring for the shift this replaced."""
    return (f'[1:v:0]scale={w}:{h},format=rgba,'
            f'colorkey={OVERLAY_KEY_COLOR}:{OVERLAY_KEY_SIMILARITY}:{OVERLAY_KEY_BLEND},'
            f'scale=out_color_matrix={color.matrix}:out_range=tv,format=yuva420p[ov];'
            f'[0:v:0][ov]overlay=x=(W-w)/2:y=H-h-{margin}:eof_action=pass:format=yuv420[v]')


def make_overlay_chunk(ffmpeg: str, loop: VideoInfo, loop_duration: float,
                       overlay: VideoInfo, bottom_px: float, color: ColorTags,
                       out_path: str,
                       on_progress: Optional[Callable[[float], None]] = None) -> int:
    """Encode k loop units with the overlay keyed on top, from the loop's
    first frame. Returns k."""
    chunk_units = max(1, math.ceil(overlay.duration / loop_duration - 1e-6))
    w, h, margin = overlay_placement(loop.width, loop.height, overlay.width, overlay.height, bottom_px)
    length = chunk_units * loop_duration
    exporter._run_ffmpeg_streaming(
        [ffmpeg, '-y', '-hide_banner', '-nostdin',
         '-stream_loop', str(chunk_units - 1), '-i', loop.path, '-i', overlay.path,
         '-filter_complex', overlay_graph(w, h, margin, color), '-map', '[v]',
         '-t', f'{length:.6f}'] + _loop_encode_args(color) + [out_path],
        timeout=_encode_timeout(length), total_seconds=length, on_progress=on_progress)
    return chunk_units


# ── Overlay schedule ──

def overlay_schedule(mode: str, total: float, overlay_duration: float,
                     every_s: float = DEFAULT_OVERLAY_EVERY_S) -> List[float]:
    """The seconds at which showings are WANTED (before snapping to the
    loop): one centred on the middle of the video, or every_s, 2*every_s,
    ... (never at the very start), or none."""
    if mode == OVERLAY_ONCE:
        return [max(0.0, (total - overlay_duration) / 2.0)] if total > 0 else []
    if mode == OVERLAY_EVERY:
        if every_s <= 0:
            return []
        return [n * every_s for n in range(1, int(math.ceil(total / every_s)) + 1)
                if n * every_s < total]
    return []


def overlay_starts(total: float, loop_duration: float, overlay_duration: float,
                   chunk_units: int, times: List[float]) -> List[int]:
    """Loop-unit indices where a showing starts: each wanted time snapped
    to the nearest unit boundary. A showing must end before the playlist
    does, and two showings never overlap."""
    if loop_duration <= 0:
        return []
    starts = []
    for t in sorted(times):
        unit = int(round(max(0.0, t) / loop_duration))
        if starts:
            unit = max(unit, starts[-1] + chunk_units)
        if unit * loop_duration + overlay_duration > total:
            break
        starts.append(unit)
    return starts


def plan_overlay(mode: str, total: float, loop_duration: float, overlay_duration: float,
                 every_s: float = DEFAULT_OVERLAY_EVERY_S, intro: bool = False) -> List[float]:
    """The seconds at which showings will actually start: what the
    export summary shows before anything is rendered."""
    if not loop_duration or not overlay_duration or mode == OVERLAY_OFF:
        return []
    chunk_units = max(1, math.ceil(overlay_duration / loop_duration - 1e-6))
    times = overlay_schedule(mode, total, overlay_duration, every_s)
    if intro:
        first = math.ceil(opening.DURATION / loop_duration - 1e-6) * loop_duration
        times = [max(t, first) for t in times]
    return [u * loop_duration for u in overlay_starts(total, loop_duration, overlay_duration,
                                                       chunk_units, times)]


def timeline(total_units: int, starts: List[int], chunk_units: int) -> List[str]:
    """The concat list as 'loop' / 'chunk' entries, covering at least
    total_units loop units (a chunk counts as chunk_units of them)."""
    entries = []
    unit = 0
    pending = sorted(starts)
    while unit < total_units:
        if pending and pending[0] == unit:
            pending.pop(0)
            entries.append('chunk')
            unit += chunk_units
        else:
            entries.append('loop')
            unit += 1
    return entries


# ── Progress ──

class Reporter:
    """Stage-aware progress: each stage owns a slice of the 0..1 bar and
    reports an ETA for itself once it has run long enough to measure."""

    def __init__(self, on_status: Optional[StatusFn] = None,
                 on_progress: Optional[ProgressFn] = None):
        self.on_status, self.on_progress = on_status, on_progress
        self.lo, self.hi, self.t0 = 0.0, 0.0, time.monotonic()

    def stage(self, message: str, lo: float, hi: float):
        logger.info(message)
        self.lo, self.hi, self.t0 = lo, hi, time.monotonic()
        if self.on_status:
            self.on_status(message)
        self.tick(0.0)

    def tick(self, frac: float):
        frac = max(0.0, min(1.0, frac))
        eta = None
        if frac >= 0.03:
            eta = (time.monotonic() - self.t0) * (1.0 - frac) / frac
        if self.on_progress:
            self.on_progress(self.lo + (self.hi - self.lo) * frac, eta)


# ── Prepared video (shared by preview and export) ──

@dataclass
class Prepared:
    """The loop unit and, with an overlay, the chunk: kept between runs so
    a preview's encodes are reused by the export that follows it."""
    dir: str
    video_key: tuple
    source: VideoInfo
    color: ColorTags
    loop_path: str
    loop_duration: float
    loop: VideoInfo
    overlay_key: Optional[tuple] = None
    overlay: Optional[VideoInfo] = None
    chunk_path: Optional[str] = None
    chunk_units: int = 1


_prepared: Optional[Prepared] = None


def _file_key(path: str) -> tuple:
    st = os.stat(path)
    return os.path.normcase(os.path.abspath(path)), st.st_size, st.st_mtime_ns


def clear_prepared() -> None:
    """Drop the cached encodes (the GUI calls this on exit)."""
    global _prepared
    p, _prepared = _prepared, None
    if p:
        shutil.rmtree(p.dir, ignore_errors=True)


def opening_entries(ffmpeg, prep, entries, settings, report):
    """Replace complete opening units once; leave every later unit untouched.

    Keeping complete units retains scene phase at the join. The prepared
    directory owns the cache and is removed on source changes / application exit.
    """
    import hashlib
    settings.validate()
    count, units = 0, 0
    while count < len(entries) and units * prep.loop_duration < opening.DURATION - 1e-6:
        units += prep.chunk_units if entries[count] == prep.chunk_path else 1
        count += 1
    length = units * prep.loop_duration
    key = repr((settings.record(), [_file_key(p) for p in entries[:count]],
                asdict(prep.color), LOOP_CRF, LOOP_PRESET))
    identity = hashlib.sha256(key.encode('utf-8')).hexdigest()[:20]
    target = os.path.join(prep.dir, f'opening-{identity}.mp4')
    if os.path.isfile(target):
        report.stage('Opening ready (reused from preview)', .20, .35)
        report.tick(1)
    else:
        report.stage('Rendering the opening titles...', .20, .35)
        work = tempfile.mkdtemp(prefix='intro_', dir=prep.dir)
        try:
            source = os.path.join(work, 'opening-list.txt')
            write_concat_list(source, entries[:count])
            cards = opening.make_cards(settings, prep.loop.width, prep.loop.height, work)
            cmd = [ffmpeg, '-y', '-hide_banner', '-nostdin', '-f', 'concat', '-safe', '0', '-i', source]
            for path, _, _ in cards:
                cmd += ['-loop', '1', '-framerate', str(prep.loop.fps), '-t', '20', '-i', path]
            cmd += ['-filter_complex', opening.video_graph(cards, prep.loop.width, prep.loop.height,
                     prep.loop.fps, prep.color.matrix), '-map', '[v]', '-t', f'{length:.9f}']
            partial = os.path.join(work, 'opening.mp4')
            exporter._run_ffmpeg_streaming(cmd + _loop_encode_args(prep.color) + [partial],
                timeout=_encode_timeout(length), total_seconds=length, on_progress=report.tick)
            os.replace(partial, target)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    return [target] + entries[count:]


def prepare(ffmpeg: str, video: str, overlay: Optional[str], bottom_px: float,
            report: Optional[Reporter] = None, span: Tuple[float, float] = (0.0, 1.0)) -> Prepared:
    """The loop unit and overlay chunk for these inputs, encoded now or
    reused from the last run when the files and settings are unchanged."""
    global _prepared
    report = report or Reporter()
    lo, hi = span
    mid = lo + (hi - lo) * 0.6
    vkey = _file_key(video)
    okey = (_file_key(overlay), round(float(bottom_px), 2)) if overlay else None

    p = _prepared
    if p and (p.video_key != vkey or not os.path.isfile(p.loop_path)):
        clear_prepared()
        p = None
    if p is not None:
        report.stage('Video loop ready (reused from the last run)', lo, mid)
        report.tick(1.0)
    else:
        source = probe_video(ffmpeg, video)
        color = color_tags_for(source)
        d = tempfile.mkdtemp(prefix='colony_')
        loop_path = os.path.join(d, 'loop.mp4')
        report.stage('Encoding the video loop...', lo, mid)
        try:
            loop_duration = make_loop_unit(ffmpeg, video, loop_path, color, source.duration,
                                           on_progress=report.tick)
            loop = probe_video(ffmpeg, loop_path)
        except BaseException:
            shutil.rmtree(d, ignore_errors=True)
            raise
        p = Prepared(d, vkey, source, color, loop_path, loop_duration, loop)
        _prepared = p

    if okey != p.overlay_key or (okey and not os.path.isfile(p.chunk_path or '')):
        if p.chunk_path and os.path.exists(p.chunk_path):
            os.remove(p.chunk_path)
        p.overlay_key, p.overlay, p.chunk_path, p.chunk_units = None, None, None, 1
        if overlay:
            ov = probe_video(ffmpeg, overlay)
            if not ov.duration:
                raise RuntimeError(f'Could not read the length of {os.path.basename(overlay)}')
            chunk_path = os.path.join(p.dir, 'overlay_chunk.mp4')
            report.stage('Encoding the overlay...', mid, hi)
            p.chunk_units = make_overlay_chunk(ffmpeg, p.loop, p.loop_duration, ov, bottom_px,
                                               p.color, chunk_path, on_progress=report.tick)
            p.overlay_key, p.overlay, p.chunk_path = okey, ov, chunk_path
    report.stage('Overlay ready' if overlay else 'Video ready', hi, hi)
    return p


# ── Output ──

def versioned_path(path: str) -> str:
    """path itself when free, else "name (2).ext", "name (3).ext", ..."""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f'{stem} ({n}){ext}'):
        n += 1
    return f'{stem} ({n}){ext}'


def manifest_path(output: str) -> str:
    return os.path.splitext(output)[0] + '.export.json'


def error_log_path(output: str) -> str:
    return os.path.splitext(output)[0] + '.error.log'


@dataclass
class Check:
    name: str
    ok: Optional[bool]      # None: could not be checked
    detail: str


def verify_output(ffmpeg: str, path: str, expected_duration: float,
                  expected_size: Tuple[int, int], expected_fps: Optional[float],
                  full_decode: bool = False,
                  on_progress: Optional[Callable[[float], None]] = None) -> List[Check]:
    """Technical checks on the finished file. The header checks are
    instant; the full decode reads every packet through the decoders
    (-xerror: any decode error fails it) and takes a while on two hours
    of 4K. None of this says the loop LOOKS right: that is a human check."""
    checks = []
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return [Check('File', False, 'missing or empty')]
    try:
        info = probe_video(ffmpeg, path)
    except Exception as e:  # noqa: BLE001
        return [Check('Video stream', False, str(e))]
    checks.append(Check('Video stream', info.size == tuple(expected_size),
                        f'{info.width}x{info.height} (expected {expected_size[0]}x{expected_size[1]})'))
    if info.fps and expected_fps:
        checks.append(Check('Frame rate', abs(info.fps - expected_fps) < 0.05,
                            f'{info.fps:g} fps (expected {expected_fps:g})'))
    else:
        checks.append(Check('Frame rate', None, 'not readable from the header'))
    checks.append(Check('Audio stream', info.audio is not None, info.audio or 'none'))
    if info.duration:
        drift = info.duration - expected_duration
        checks.append(Check('Duration', -0.05 <= drift <= DURATION_TOLERANCE_S,
                            f'{_clock(info.duration)} (expected {_clock(expected_duration)}, '
                            f'{drift:+.2f} s)'))
    else:
        checks.append(Check('Duration', None, 'not readable from the header'))
    if full_decode:
        try:
            exporter._run_ffmpeg_streaming(
                [ffmpeg, '-hide_banner', '-nostdin', '-v', 'error', '-stats', '-xerror',
                 '-err_detect', 'explode', '-i', path, '-f', 'null', '-'],
                timeout=int(1800 + 3 * expected_duration), total_seconds=expected_duration,
                on_progress=on_progress)
            checks.append(Check('Full decode', True, 'every frame and sample decoded without errors'))
        except ExportCancelled:
            checks.append(Check('Full decode', None, 'cancelled'))
        except Exception as e:  # noqa: BLE001
            checks.append(Check('Full decode', False, str(e)))
    return checks


@dataclass
class RenderResult:
    output: str                     # the file actually written (may be versioned)
    duration: float
    crossfade: float
    tracks: List[TrackInfo]
    gains_db: List[float]           # what was applied (all 0 unless matching)
    overlay_times: List[float]      # seconds where each overlay showing starts
    width: int = 0
    height: int = 0
    fps: Optional[float] = None
    checks: Optional[List[Check]] = None
    manifest: Optional[str] = None

    @property
    def verified(self) -> bool:
        return bool(self.checks) and all(c.ok is not False for c in self.checks)


class _LogCapture:
    """Everything the renderer and the exporter log during one job, kept
    in the job's temp dir and promoted to <output>.error.log on failure."""

    NAMES = ('colony', 'app.exporter')

    def __init__(self, path: str):
        self.handler = logging.FileHandler(path, encoding='utf-8')
        self.handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
        self.levels = {}
        for name in self.NAMES:
            lg = logging.getLogger(name)
            self.levels[name] = lg.level
            lg.setLevel(logging.DEBUG)
            lg.addHandler(self.handler)
        self.path = path

    def close(self):
        for name in self.NAMES:
            lg = logging.getLogger(name)
            lg.removeHandler(self.handler)
            lg.setLevel(self.levels[name])
        self.handler.close()

    def promote(self, dest: str, exc: BaseException):
        try:
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write('\n' + ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            self.handler.flush()
            shutil.copyfile(self.path, dest)
        except OSError:
            pass


def render(video: str, tracks: List[str], output: str,
           crossfade: float = DEFAULT_CROSSFADE_S,
           on_status: Optional[StatusFn] = None,
           on_progress: Optional[ProgressFn] = None,
           overlay: Optional[str] = None,
           overlay_mode: str = OVERLAY_ONCE,
           overlay_every_s: float = DEFAULT_OVERLAY_EVERY_S,
           overlay_bottom_px: float = DEFAULT_OVERLAY_BOTTOM_PX,
           match_loudness: bool = False,
           full_decode: bool = False,
           overwrite: bool = False,
           sfx: Optional[SfxSettings] = None,
           intro: Optional[IntroSettings] = None,
           preview_seconds: Optional[float] = None) -> RenderResult:
    """Render the looped video under the playlist to output (.mp4).

    overlay: a greenscreen clip shown once centred on the middle of the
    video (OVERLAY_ONCE), every overlay_every_s seconds (OVERLAY_EVERY,
    first at overlay_every_s, not at the start), or not at all; bottom
    centre, overlay_bottom_px up from the bottom edge (1080p pixels). Its
    own audio, if any, is not used.
    match_loudness: gain each track to TARGET_LUFS; off keeps the levels.
    full_decode: also decode the whole finished file as a check.
    overwrite: write over an existing output. Off, an existing file is
    kept and the export goes to "name (2).mp4" (the result says where).
    intro: once-only branded opening; None preserves the existing path.
    preview_seconds: shorten delivery for review without changing the
    playlist's SFX fade-out or subscription schedule. None exports it all.

    Cancellable from another thread with exporter.request_export_cancel(),
    which raises ExportCancelled here. The file is written beside output
    under a temporary name and moved into place only when complete, so a
    failed or cancelled export never leaves a half-written MP4 behind. A
    manifest (settings, inputs, checks) is written beside a finished file;
    the job's log goes beside a failed one.
    """
    if sfx:
        sfx.validate()
    if intro:
        intro.validate()
    if preview_seconds is not None and (not math.isfinite(preview_seconds) or preview_seconds <= 0):
        raise ValueError('Preview duration must be positive and finite.')
    if not tracks:
        raise ValueError('Add at least one audio track')
    if overlay_mode not in OVERLAY_MODES:
        raise ValueError(f'Unknown overlay mode {overlay_mode!r}')
    if not overwrite:
        output = versioned_path(output)

    report = Reporter(on_status, on_progress)
    exporter.reset_export_cancel()
    ffmpeg = get_ffmpeg_path()
    tmpdir = tempfile.mkdtemp(prefix='colony_job_')
    log = _LogCapture(os.path.join(tmpdir, 'export.log'))
    partial = output + '.partial'
    started = datetime.now()
    render_hi = 0.60 if full_decode else 0.95
    try:
        logger.info(f'Export: video={video} tracks={tracks} overlay={overlay} '
                    f'mode={overlay_mode} every={overlay_every_s} bottom={overlay_bottom_px} '
                    f'crossfade={crossfade} match={match_loudness} full_decode={full_decode} '
                    f'output={output}')
        # Progress split, by measured time (72 minutes of audio: loop ~2 s,
        # measuring ~6 s, final render ~85 s; the loop takes far longer on
        # a long 4K source, which is why it now streams its own progress)
        prep = prepare(ffmpeg, video, overlay if overlay_mode != OVERLAY_OFF else None,
                       overlay_bottom_px, report, (0.0, 0.15))
        loop_duration = prep.loop_duration

        infos = []
        for i, path in enumerate(tracks):
            report.stage(f'Measuring track {i + 1} of {len(tracks)}: {os.path.basename(path)}',
                         0.15 + 0.05 * i / len(tracks), 0.15 + 0.05 * (i + 1) / len(tracks))
            infos.append(measure_track(ffmpeg, path))
        report.tick(1.0)

        durations = [t.duration for t in infos]
        xfade = clamp_crossfade(crossfade, durations)
        total = total_duration(durations, xfade)
        playlist_total = total
        if intro and total < opening.DURATION:
            raise ValueError('Opening titles need at least 20 seconds of audio.')
        if preview_seconds is not None:
            total = min(total, preview_seconds)
        gains = [t.gain_db if match_loudness else 0.0 for t in infos]

        total_units = loop_repeats(total, loop_duration)
        starts = []
        if prep.chunk_path:
            times = plan_overlay(overlay_mode, playlist_total, loop_duration,
                                 prep.overlay.duration, overlay_every_s, intro=bool(intro))
            starts = [round(t / loop_duration) for t in times if t < total]
        paths = {'loop': prep.loop_path, 'chunk': prep.chunk_path}
        list_file = os.path.join(tmpdir, 'loop_list.txt')
        entries = [paths[e] for e in timeline(total_units, starts, prep.chunk_units)]
        if intro:
            entries = opening_entries(ffmpeg, prep, entries, intro, report)
        write_concat_list(list_file, entries)

        cmd = [ffmpeg, '-y', '-hide_banner', '-nostdin',
               '-f', 'concat', '-safe', '0', '-i', list_file]
        for path in tracks:
            cmd += ['-i', path]
        graph = build_audio_graph(gains, xfade)
        sfx_record = None
        if sfx:
            report.stage('Preparing rain/SFX loop...', 0.20, 0.20)
            sfx_info = measure_track(ffmpeg, sfx.path)
            sfx_loop = os.path.join(tmpdir, 'sfx-loop.wav')
            actual_overlap = prepare_loop(ffmpeg, sfx, sfx_loop, sfx_info.duration)
            cmd += ['-stream_loop', '-1', '-i', sfx_loop]
            graph = mix_graph(graph, sfx, playlist_total, len(tracks) + 1)
            sfx_record = {**asdict(sfx), 'source_duration_s': sfx_info.duration,
                          'source_lufs': sfx_info.loudness, 'actual_loop_crossfade_s': actual_overlap}
        graph = opening.audio_graph(graph, intro)
        cmd += ['-filter_complex', graph,
                '-map', '0:v:0', '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', AUDIO_BITRATE, '-ar', str(SAMPLE_RATE),
                '-t', f'{total:.3f}', '-movflags', '+faststart', '-f', 'mp4', partial]

        report.stage(f'Rendering {_clock(total)} of video...', 0.35 if intro else 0.20, render_hi)
        exporter._run_ffmpeg_streaming(cmd, timeout=int(900 + total), total_seconds=total,
                                       on_progress=report.tick)

        try:
            os.replace(partial, output)
        except PermissionError:
            # the old file is open in a player: keep it, write beside it
            output = versioned_path(output)
            os.replace(partial, output)
            logger.warning(f'Destination was locked; wrote {output} instead')

        report.stage('Checking the finished file...' if not full_decode
                     else 'Decoding the finished file to check it...', render_hi, 1.0)
        checks = verify_output(ffmpeg, output, total, prep.loop.size, prep.loop.fps,
                               full_decode=full_decode, on_progress=report.tick)
        overlay_times = [u * loop_duration for u in starts]
        result = RenderResult(output, total, xfade, infos, gains, overlay_times,
                              prep.loop.width, prep.loop.height, prep.loop.fps, checks)
        result.manifest = _write_manifest(result, prep, started, overlay_mode, overlay_every_s,
                                          overlay_bottom_px, match_loudness, full_decode, total_units,
                                          sfx_record, intro.record() if intro else None, preview_seconds)
        report.tick(1.0)
        bad = [c for c in checks if c.ok is False]
        report.stage(f'Done: {os.path.basename(output)} ({_clock(total)})' if not bad
                     else f'Done with {len(bad)} failed check(s): {os.path.basename(output)}', 1.0, 1.0)
        return result
    except BaseException as exc:
        # ExportCancelled is a BaseException on purpose (see exporter)
        try:
            if os.path.exists(partial):
                os.remove(partial)
        except OSError:
            pass
        if not isinstance(exc, ExportCancelled):
            log.promote(error_log_path(output), exc)
        raise
    finally:
        log.close()
        shutil.rmtree(tmpdir, ignore_errors=True)


def _write_manifest(result: RenderResult, prep: Prepared, started: datetime, overlay_mode: str,
                    overlay_every_s: float, overlay_bottom_px: float, match_loudness: bool,
                    full_decode: bool, total_units: int, sfx_record=None, intro_record=None,
                    preview_seconds=None) -> Optional[str]:
    data = {
        'tool': 'Colony',
        'opening': intro_record,
        'preview_limit_s': preview_seconds,
        'started': started.isoformat(timespec='seconds'),
        'finished': datetime.now().isoformat(timespec='seconds'),
        'output': {
            'path': result.output, 'duration_s': round(result.duration, 3),
            'width': result.width, 'height': result.height, 'fps': result.fps,
            'color': asdict(prep.color),
        },
        'video': {
            'path': prep.source.path, 'width': prep.source.width, 'height': prep.source.height,
            'fps': prep.source.fps, 'duration_s': prep.source.duration,
            'loop_duration_s': round(prep.loop_duration, 3), 'loops': total_units,
            'source_color': {'space': prep.source.color_space, 'primaries': prep.source.color_primaries,
                             'trc': prep.source.color_trc, 'range': prep.source.color_range},
        },
        'overlay': None if not prep.overlay else {
            'path': prep.overlay.path, 'duration_s': prep.overlay.duration, 'mode': overlay_mode,
            'every_s': overlay_every_s if overlay_mode == OVERLAY_EVERY else None,
            'bottom_px_at_1080p': overlay_bottom_px, 'chunk_units': prep.chunk_units,
            'times_s': [round(t, 3) for t in result.overlay_times],
            'times': [_clock(t) for t in result.overlay_times],
        },
        'audio': {
            'tracks': [{'path': t.path, 'duration_s': round(t.duration, 3),
                        'loudness_lufs': t.loudness, 'gain_db': round(g, 2)}
                       for t, g in zip(result.tracks, result.gains_db)],
            'sfx': sfx_record,
            'crossfade_s': result.crossfade,
            'match_loudness': match_loudness,
            'target_lufs': TARGET_LUFS if match_loudness else None,
            'limiter_dbfs': LIMIT_DBFS,
            'codec': f'aac {AUDIO_BITRATE} {SAMPLE_RATE} Hz stereo',
        },
        'verification': {
            'full_decode': full_decode,
            'passed': result.verified,
            'checks': [asdict(c) for c in result.checks or []],
            'note': 'Technical checks only. Whether the loop and the overlay look and '
                    'sound right is a human check.',
        },
    }
    path = manifest_path(result.output)
    try:
        atomic_write_json(path, data)
    except Exception as e:  # noqa: BLE001 - a manifest must never fail an export
        logger.warning(f'Could not write the manifest {path}: {e}')
        return None
    return path


def preview(video: str, overlay: Optional[str], overlay_bottom_px: float, out_path: str,
            on_status: Optional[StatusFn] = None,
            on_progress: Optional[ProgressFn] = None) -> str:
    """A short MP4 with the real export settings: a loop unit, the
    overlay chunk (when there is an overlay) and another loop unit, so it
    shows the loop seam and the overlay's entrance and exit. The encodes
    are kept and reused by the export that follows."""
    report = Reporter(on_status, on_progress)
    exporter.reset_export_cancel()
    ffmpeg = get_ffmpeg_path()
    prep = prepare(ffmpeg, video, overlay, overlay_bottom_px, report, (0.0, 0.85))
    entries = [prep.loop_path, prep.chunk_path, prep.loop_path] if prep.chunk_path \
        else [prep.loop_path, prep.loop_path]
    length = prep.loop_duration * (len(entries) - 1 + prep.chunk_units)
    tmpdir = tempfile.mkdtemp(prefix='colony_job_')
    try:
        list_file = os.path.join(tmpdir, 'preview_list.txt')
        write_concat_list(list_file, entries)
        report.stage('Assembling the preview...', 0.85, 1.0)
        exporter._run_ffmpeg_streaming(
            [ffmpeg, '-y', '-hide_banner', '-nostdin', '-f', 'concat', '-safe', '0',
             '-i', list_file, '-map', '0:v:0', '-c:v', 'copy', '-movflags', '+faststart',
             '-f', 'mp4', out_path],
            timeout=600, total_seconds=length, on_progress=report.tick)
        report.stage(f'Preview ready ({_clock(length)})', 1.0, 1.0)
        return out_path
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _clock(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


__all__ = [
    'ExportCancelled', 'RenderResult', 'TrackInfo', 'VideoInfo', 'ColorTags', 'Check',
    'Reporter', 'Prepared',
    'render', 'preview', 'prepare', 'clear_prepared', 'measure_track', 'probe_video',
    'verify_output', 'versioned_path', 'manifest_path', 'error_log_path',
    'build_audio_graph', 'clamp_crossfade', 'total_duration', 'track_gain_db',
    'overlay_schedule', 'overlay_starts', 'plan_overlay', 'timeline', 'overlay_placement',
    'DEFAULT_CROSSFADE_S', 'MAX_CROSSFADE_S', 'TARGET_LUFS', 'LIMIT_DBFS',
    'OVERLAY_OFF', 'OVERLAY_ONCE', 'OVERLAY_EVERY', 'OVERLAY_MODES',
    'DEFAULT_OVERLAY_EVERY_S', 'DEFAULT_OVERLAY_BOTTOM_PX',
]


def preview_opening(video, tracks, output, crossfade=DEFAULT_CROSSFADE_S, **options):
    """The first 25 seconds through the real exporter; music is optional.

    Without music, a temporary silent track allows a visual-only review.
    It never becomes a production soundtrack or changes the audio playlist.
    """
    if not options.get('intro'):
        raise ValueError('Enable opening titles to preview them.')
    options.update(preview_seconds=25, full_decode=True)
    if tracks:
        return render(video, tracks, output, crossfade, **options)
    with tempfile.TemporaryDirectory(prefix='colony_silent_preview_') as work:
        silent = os.path.join(work, 'visual-preview-silence.wav')
        exporter.reset_export_cancel()
        exporter._run_ffmpeg_streaming(
            [get_ffmpeg_path(), '-y', '-hide_banner', '-nostdin', '-f', 'lavfi',
             '-i', 'anullsrc=r=48000:cl=stereo', '-t', '25', silent], timeout=60)
        # A visual-only preview must not silently introduce a selected SFX track.
        options['sfx'] = None
        result = render(video, [silent], output, crossfade, **options)
        if result.manifest:
            with open(result.manifest, encoding='utf-8') as stream:
                record = json.load(stream)
            record['preview_silent'] = True
            record['audio']['tracks'] = []
            record['audio']['note'] = 'Visual preview with generated silence; no music or SFX auditioned.'
            atomic_write_json(result.manifest, record)
        return result


def preview_audio(tracks, output, crossfade=DEFAULT_CROSSFADE_S, sfx=None,
                  match_loudness=False, on_status=None, on_progress=None, intro=None):
    """Audition actual opening settings through one rain gap and re-entry (max 10 min).

    Continuous mode previews 90 seconds. Long delays stay silent in the preview,
    as in the export; no timing is compressed. Video is not required.
    """
    if not tracks:
        raise ValueError('Add at least one audio track.')
    if sfx:
        sfx.validate()
    if intro:
        intro.validate()
    exporter.reset_export_cancel()
    ffmpeg = get_ffmpeg_path()
    report = Reporter(on_status, on_progress)
    tmpdir = tempfile.mkdtemp(prefix='colony_audio_preview_')
    output = versioned_path(output)
    partial = output + '.partial'
    try:
        report.stage('Measuring audio for preview...', 0, 0.15)
        infos = [measure_track(ffmpeg, p) for p in tracks]
        durations = [i.duration for i in infos]
        xfade = clamp_crossfade(crossfade, durations)
        total = total_duration(durations, xfade)
        wanted = (sfx.start_s + sfx.on_s + sfx.off_s + sfx.fade_in_s + 10
                  if sfx and sfx.mode == 'intermittent' else 90)
        length = min(total, max(90, min(600, wanted)))
        gains = [i.gain_db if match_loudness else 0 for i in infos]
        cmd = [ffmpeg, '-y', '-hide_banner', '-nostdin']
        for path in tracks:
            cmd += ['-i', path]
        graph = build_audio_graph(gains, xfade, first_input=0)
        if sfx:
            info = measure_track(ffmpeg, sfx.path)
            loop = os.path.join(tmpdir, 'sfx.wav')
            prepare_loop(ffmpeg, sfx, loop, info.duration)
            cmd += ['-stream_loop', '-1', '-i', loop]
            graph = mix_graph(graph, sfx, total, len(tracks))
        graph = opening.audio_graph(graph, intro)
        cmd += ['-filter_complex', graph, '-map', '[aout]', '-t', str(length),
                '-c:a', 'libmp3lame', '-b:a', AUDIO_BITRATE, '-f', 'mp3', partial]
        report.stage(f'Previewing first {_clock(length)} (actual rain timing)...', 0.15, 1)
        exporter._run_ffmpeg_streaming(cmd, timeout=int(300+length), total_seconds=length,
                                       on_progress=report.tick)
        os.replace(partial, output)
        return output
    finally:
        if os.path.exists(partial):
            os.remove(partial)
        shutil.rmtree(tmpdir, ignore_errors=True)
