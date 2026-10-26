"""
Video exporter module.
Renders a slideshow (photos + videos) into a single video file using ffmpeg.
Supports crossfade transitions, configurable resolution/fps/format.
"""

import os
import re
import sys
import json
import shutil
import logging
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable

from app import trims

# Suppress CMD windows on Windows when running ffmpeg
_subprocess_flags = 0
if sys.platform == 'win32':
    _subprocess_flags = subprocess.CREATE_NO_WINDOW

# Render spawns (the real encodes in _run_ffmpeg, not the header probes)
# additionally run below normal priority: libx264 saturates every logical
# core, and at normal priority that starves the UI/OS and "hangs" the PC.
# Below-normal still uses all idle cores, so export speed is unaffected
# when the machine isn't doing anything else.
_render_flags = _subprocess_flags
if sys.platform == 'win32':
    _render_flags |= subprocess.BELOW_NORMAL_PRIORITY_CLASS

logger = logging.getLogger(__name__)


# ── Export cancellation ────────────────────────────────────────
#
# The UI's Cancel button used to only flip frontend state; ffmpeg kept
# rendering and the "cancelled" file appeared in Exports. These hooks give
# the backend a real cancel: _run_ffmpeg checks the event between segments
# and the active ffmpeg process is killed mid-render.

class ExportCancelled(BaseException):
    """Raised when the user cancels an in-progress export.

    Deliberately derives from BaseException (like KeyboardInterrupt) so the
    many pre-existing broad `except Exception` handlers inside the export
    pipeline (music prep/mix fallbacks, per-segment tolerance) cannot swallow
    a cancellation and let the export complete "successfully". Only the
    explicit `except ExportCancelled` handlers at the API boundary catch it.
    """


class FfmpegTimeout(RuntimeError):
    """Raised when an ffmpeg step exceeds its timeout. Distinct from plain
    render failures so callers that tolerate per-clip failures can still
    surface timeouts as hard errors."""


_cancel_event = threading.Event()
_active_proc_lock = threading.Lock()
_active_proc: Optional[subprocess.Popen] = None


def request_export_cancel() -> None:
    """Signal the in-progress export to stop and kill the active ffmpeg.

    The kill happens under the same lock that _run_ffmpeg spawns/registers
    under, so a cancel can't slip between Popen() and registration."""
    _cancel_event.set()
    with _active_proc_lock:
        proc = _active_proc
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass


def reset_export_cancel() -> None:
    """Clear the cancel flag before starting a new export."""
    _cancel_event.clear()

# Resolution presets
RESOLUTIONS = {
    '720': (1280, 720),
    '1080': (1920, 1080),
    '2160': (3840, 2160),
    '4k': (3840, 2160),
}

# Quality presets → CRF values (lower = better quality, bigger file)
QUALITY_CRF = {
    'low': 28,
    'medium': 23,
    'high': 18,
    'max': 15,
}

# ── Hardware encoders ──────────────────────────────────────────
#
# The bundled ffmpeg (gyan.dev essentials) carries NVIDIA NVENC, Intel
# Quick Sync, AMD AMF and Windows MediaFoundation encoders. Measured
# 2026-09-05 on a real 1080p30 clip (RTX 3090 / i9-12900K): at the same
# file size the picture is the same as libx264 (SSIM 0.9646 vs 0.9648);
# H.264 encodes 1.5x faster on a 16-core desktop and 4.4x on a 4-thread
# CPU, H.265 3.7x faster everywhere, and the GPU path is unaffected by
# the below-normal process priority that slows x264 on a busy PC.
#
# Rate control has to be translated per encoder because only x264/x265
# understand crf:
#   nvenc  -rc vbr -cq (crf + 7): calibrated against x264/x265 at crf
#          18/23/28 on video and on a Ken Burns photo segment; cq 25
#          gives crf-18-sized files, cq 30 ~ crf 23, cq 35 ~ crf 28.
#   qsv    -global_quality crf (ICQ mode, crf-like scale per Intel).
#   amf    constant QP at crf (QP is the same 0-51 scale).
#   mf     -rate_control quality: quality 60 ~ crf 18 measured, 2 points
#          per crf step assumed either side.
# Quick Sync and AMF could not be measured here (no Intel/AMD GPU), so
# every encoder is PROBED before use with exactly the arguments it will
# get, and a segment whose hardware encode fails is re-run in software
# (run_encode). Playback is unaffected: this is export only.
HW_ENCODER_CANDIDATES = {
    'libx264': ('h264_nvenc', 'h264_qsv', 'h264_amf', 'h264_mf'),
    'libx265': ('hevc_nvenc', 'hevc_qsv', 'hevc_amf', 'hevc_mf'),
}
NVENC_CQ_OFFSET = 7
ENCODER_LABELS = {
    'nvenc': 'NVIDIA graphics card',
    'qsv': 'Intel Quick Sync',
    'amf': 'AMD graphics card',
    'mf': 'Windows Media Foundation',
    'libx264': 'software (x264)',
    'libx265': 'software (x265)',
}


def encoder_label(encoder: str) -> str:
    for key, label in ENCODER_LABELS.items():
        if encoder == key or encoder.endswith('_' + key):
            return label
    return encoder


def encoder_args(encoder: str, crf: int) -> list:
    """The `-c:v ... -pix_fmt` block for one encoder at the quality the
    user asked for (expressed as x264 crf). Ends with the hvc1 tag for
    HEVC so Apple players and browsers recognise the stream."""
    is_hevc = encoder in ('libx265',) or encoder.startswith('hevc_')
    if encoder in ('libx264', 'libx265'):
        args = ['-c:v', encoder, '-preset', 'fast', '-crf', str(crf), '-pix_fmt', 'yuv420p']
    elif encoder.endswith('_nvenc'):
        cq = max(1, min(51, int(crf) + NVENC_CQ_OFFSET))
        args = ['-c:v', encoder, '-preset', 'p4', '-rc', 'vbr', '-cq', str(cq),
                '-b:v', '0', '-pix_fmt', 'yuv420p']
    elif encoder.endswith('_qsv'):
        args = ['-c:v', encoder, '-preset', 'medium', '-global_quality', str(int(crf)),
                '-pix_fmt', 'nv12']
    elif encoder.endswith('_amf'):
        qp = max(0, min(51, int(crf)))
        args = ['-c:v', encoder, '-quality', 'balanced', '-rc', 'cqp',
                '-qp_i', str(qp), '-qp_p', str(qp), '-pix_fmt', 'yuv420p']
    elif encoder.endswith('_mf'):
        q = max(20, min(90, 60 - (int(crf) - 18) * 2))
        args = ['-c:v', encoder, '-rate_control', 'quality', '-quality', str(q),
                '-pix_fmt', 'yuv420p']
    else:
        args = ['-c:v', encoder, '-pix_fmt', 'yuv420p']
    if is_hevc:
        args += ['-tag:v', 'hvc1']
    return args


_encoder_probe_cache: Dict[tuple, bool] = {}
_encoder_probe_lock = threading.Lock()


def probe_encoder(ffmpeg: str, encoder: str) -> bool:
    """Can this ffmpeg actually encode with `encoder` on this machine?
    Encodes a third of a second of lavfi colour with the exact arguments
    the export would use. Cached per process: a GPU does not come and go
    between exports."""
    key = (ffmpeg, encoder)
    with _encoder_probe_lock:
        if key in _encoder_probe_cache:
            return _encoder_probe_cache[key]
    ok = False
    try:
        cmd = ([ffmpeg, '-y', '-hide_banner', '-f', 'lavfi', '-i', 'color=c=gray:s=320x180:r=30',
                '-t', '0.3'] + encoder_args(encoder, 23) + ['-f', 'null', '-'])
        r = subprocess.run(cmd, capture_output=True, timeout=30, creationflags=_subprocess_flags)
        ok = r.returncode == 0
    except Exception:
        ok = False
    with _encoder_probe_lock:
        _encoder_probe_cache[key] = ok
    return ok


def pick_encoder(ffmpeg: str, video_codec: str, hw_encode: bool = True) -> str:
    """The encoder to use for `video_codec` ('libx264' / 'libx265'): the
    first hardware candidate that passes its probe, else the software one."""
    if hw_encode:
        for candidate in HW_ENCODER_CANDIDATES.get(video_codec, ()):
            if probe_encoder(ffmpeg, candidate):
                return candidate
    return video_codec


class EncoderChoice:
    """The encoder an export is using, with the software encoder it falls
    back to. One instance per export; run_encode demotes it the first
    time a hardware encode fails, so the rest of the segments go straight
    to software instead of failing one by one."""

    def __init__(self, ffmpeg: str, video_codec: str, crf: int, hw_encode: bool = True):
        self.software = video_codec
        self.crf = int(crf)
        self.encoder = pick_encoder(ffmpeg, video_codec, hw_encode)
        self.fell_back = False

    @classmethod
    def software_only(cls, video_codec: str, crf: int) -> 'EncoderChoice':
        choice = cls.__new__(cls)
        choice.software = video_codec
        choice.crf = int(crf)
        choice.encoder = video_codec
        choice.fell_back = False
        return choice

    @property
    def is_hw(self) -> bool:
        return self.encoder != self.software

    def args(self) -> list:
        return encoder_args(self.encoder, self.crf)

    def software_args(self) -> list:
        return encoder_args(self.software, self.crf)

    def demote(self, reason: str = '') -> None:
        if self.is_hw:
            logger.warning(f"Hardware encoder {self.encoder} failed ({reason[:200]}); "
                           f"falling back to {self.software} for the rest of this export")
            self.encoder = self.software
            self.fell_back = True

    def describe(self) -> str:
        label = encoder_label(self.encoder)
        return label + (' after a hardware fallback' if self.fell_back else '')


def swap_codec_args(cmd: list, old_args: list, new_args: list) -> list:
    """Return `cmd` with the contiguous `old_args` block replaced by
    `new_args` (for re-running a command built with hardware arguments
    through the software encoder). Unchanged if the block is not found."""
    n = len(old_args)
    if n == 0:
        return list(cmd)
    for i in range(len(cmd) - n + 1):
        if cmd[i:i + n] == old_args:
            return list(cmd[:i]) + list(new_args) + list(cmd[i + n:])
    return list(cmd)


def run_encode(build_cmd, enc: 'EncoderChoice', runner=None) -> None:
    """Run an encode built by `build_cmd(codec_args)`; if the hardware
    encoder fails, demote the choice and run the same command with the
    software arguments. Cancellation and timeouts propagate untouched."""
    run = runner or _run_ffmpeg
    try:
        run(build_cmd(enc.args()))
    except (ExportCancelled, FfmpegTimeout, FileNotFoundError):
        raise
    except Exception as e:
        if not enc.is_hw:
            raise
        enc.demote(str(e))
        run(build_cmd(enc.args()))

# Aspect ratio presets → (width_ratio, height_ratio)
ASPECT_RATIOS = {
    '16:9': (16, 9),
    '9:16': (9, 16),
    '1:1': (1, 1),
    '4:3': (4, 3),
}

# Map UI transition names to ffmpeg xfade transition names.
# Curated set - every entry must also have a CSS playback equivalent in
# app.js (TRANSITIONS registry) so the in-app slideshow preview matches
# the export. Names never come from user input directly; only values
# from this dict (or MIX_SEQUENCE) reach the ffmpeg filter graph.
XFADE_TRANSITIONS = {
    'crossfade': 'fade',
    'fade-black': 'fadeblack',
    'fade-white': 'fadewhite',
    'memory-lane': 'fadegrays',
    'slide-left': 'slideleft',
    'cover': 'coverleft',
    'sweep': 'wipeleft',
    'soft-sweep': 'smoothleft',
    'circle': 'circleopen',
    'clock': 'radial',
    'zoom': 'zoomin',
    'dreamy': 'hblur',
}

# 'Mix' rotates through this tasteful subset, one per boundary, in a fixed
# rotation - deterministic, so re-exporting an album gives identical output.
# app.js mirrors this sequence for playback (same order, keyed by slide index).
MIX_SEQUENCE = ['fade', 'slideleft', 'circleopen', 'wipeleft']

# EBU R128 single-pass loudness normalization. Applied per-clip at segment
# encode (so a quiet phone clip and a loud GoPro land at the same level
# BEFORE they're concatenated - normalizing the combined track instead
# would pump across the silent photo segments) and to the music track
# before the user's volume slider scales it.
LOUDNORM_FILTER = 'loudnorm=I=-16:TP=-1.5:LRA=11'

# loudnorm's analysis window needs a few seconds of audio. Given less it
# emits NO audio stream at all (silently — ffmpeg still exits 0), and a
# segment with no audio then breaks any filtergraph that maps [n:a], e.g.
# the chain export's acrossfade. Skip loudnorm below this and keep the
# original audio: unnormalised is always better than missing.
LOUDNORM_MIN_SECONDS = 3.0

# Deinterlacer for camcorder footage (e.g. 1080i AVCHD .mts). deint=interlaced
# only touches frames the decoder flags as interlaced, so progressive sources
# pass through untouched (keeps output deterministic). send_frame keeps one
# frame per frame, matching the CFR segment pipeline.
DEINT_FILTER = 'bwdif=mode=send_frame:parity=auto:deint=interlaced'

# ── Clip audio clean-up ─────────────────────────────────────
#
# Camcorder and phone clips carry hiss and wind. Our automatic answer to
# Movavi's noise-removal sliders: each clip's noise floor is measured
# (astats over its first AUDIO_CLEANUP_ANALYSIS_S seconds after the trim
# in-point) and only a clip whose floor is above AUDIO_CLEANUP_FLOOR_DB -
# audible hiss - gets a high-pass (wind and handling rumble) plus an FFT
# denoiser tuned to that floor, ahead of loudnorm. Clean recordings pass
# through untouched, so a quiet room stays a quiet room and the output is
# deterministic for a given source. Export only, like loudnorm.
#
# The floor is measured ABOVE 6 kHz. Measured full-band, a steady tone or
# continuous music reads as "noise" and every music video would be
# denoised; above 6 kHz, speech and music have gaps while hiss is constant.
# The high-pass is applied four times (48 dB/octave): a 0 dBFS 1 kHz tone
# leaked through one 12 dB/octave pass at -53 dB and through two at -67,
# both read as hiss; with four it reads -87, and a 0 dBFS 2 kHz tone -82.
# Loud content at 3-4 kHz still leaks (too close to the band edge for any
# order to help); that is the continuous-music limitation in TODO.md.
#
# How the floor is read: the band is cut into 50 ms windows, each window's
# RMS level is taken, and the floor is a low percentile of those levels
# (the first and last windows are dropped: the last is a short partial
# window and the first can carry decoder start-up). Hiss is steady at this
# window size (under 0.5 dB of spread), so the reading is stable, while a
# real pause in speech or music still pulls the percentile down. Windows of
# digital silence (exact zeros: a mute, a dropout, silent padding) are left
# out: they say nothing about the recording's noise, and counting them let
# a short mute in a hissy clip pass as a quiet room.
#
# 1.0.9 used astats' Noise_floor instead: the minimum local peak over a
# window of a few samples. On steady hiss that minimum is a random extreme:
# about 1 hissy 6 s clip in 20 read 10-30 dB low and about 1 in 200 past
# the gate, so the clean-up was skipped at random. It also returned -inf (no reading)
# for any clip with a moment of digital silence.
#
# Calibration, measured 2026-09-24 with this reading. White hiss sits about
# 10 dB lower here than on 1.0.9's Noise_floor scale, so the old -60 dB gate
# becomes -70 dB. The hissy test clip reads -44.2 (was -33), a hiss ten
# times fainter -64.1 (was -53, alongside 1.0.9's AVCHD camcorder .mts at
# -52), the clean test clips -104 / -115 (were -72). Across ~30 real clips
# (phone .movs, screen captures, game trailers) the verdicts match 1.0.9's
# typical readings exactly; that pass used two band passes, and going to
# four moved hiss readings by under 1 dB.
AUDIO_CLEANUP_FLOOR_DB = -70.0
AUDIO_CLEANUP_BAND_HZ = 6000
AUDIO_CLEANUP_BAND_PASSES = 4            # 12 dB/octave each
AUDIO_CLEANUP_ANALYSIS_S = 30
AUDIO_CLEANUP_REDUCTION_DB = 10
AUDIO_CLEANUP_WINDOW_SAMPLES = 2400      # 50 ms at the 48 kHz analysis rate
AUDIO_CLEANUP_PERCENTILE = 2             # tolerates short dropouts and glitches
# Where afftdn starts, relative to the measured floor. afftdn tracks the
# real profile (tn=1), so this only sets its starting point: 4 dB above
# 1.0.9's floor, which is 14 dB above this reading's floor for the same hiss.
AUDIO_CLEANUP_NF_OFFSET_DB = 14.0
# Window levels under this are digital silence. astats reports exact zeros
# as -inf and denormal near-zeros around -890 dB; no recording's noise sits
# below 24-bit audio's -144 dB.
_DIGITAL_SILENCE_DB = -200.0


def _percentile(values: List[float], pct: float) -> float:
    """Nearest-rank low percentile of a non-empty list."""
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * pct / 100.0))]


def measure_noise_floor(ffmpeg: str, path: str, start: float = 0.0,
                        seconds: float = AUDIO_CLEANUP_ANALYSIS_S) -> Optional[float]:
    """The clip's high-band (above AUDIO_CLEANUP_BAND_HZ) noise floor in
    dBFS: the AUDIO_CLEANUP_PERCENTILE-th percentile of its 50 ms window
    RMS levels, digital silence left out. None when it cannot be
    measured (no audio, all digital silence, unreadable, odd build)."""
    cmd = [ffmpeg, '-hide_banner', '-nostats', '-v', 'error']
    if start and start > 0:
        cmd += ['-ss', f'{start:.3f}']
    band = ','.join([f'highpass=f={AUDIO_CLEANUP_BAND_HZ}'] * AUDIO_CLEANUP_BAND_PASSES)
    cmd += ['-t', f'{seconds:.3f}', '-i', path, '-vn',
            '-af', f'aresample=48000,{band},'
                   f'asetnsamples=n={AUDIO_CLEANUP_WINDOW_SAMPLES}:p=0,'
                   'astats=metadata=1:reset=1:measure_perchannel=none:measure_overall=RMS_level,'
                   'ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-',
            '-f', 'null', '-']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=120, creationflags=_subprocess_flags)
    except Exception:
        return None
    windows = []
    for raw in re.findall(r'lavfi\.astats\.Overall\.RMS_level=(\S+)', r.stdout or ''):
        try:
            windows.append(float(raw))
        except ValueError:
            windows.append(float('nan'))
    if len(windows) > 2:
        windows = windows[1:-1]          # decoder start-up; short final window
    # nan / +inf would be a broken build; digital silence is left out
    levels = [v for v in windows if v == v and _DIGITAL_SILENCE_DB <= v < float('inf')]
    if not levels:
        return None
    return _percentile(levels, AUDIO_CLEANUP_PERCENTILE)


def audio_cleanup_filter(noise_floor_db: float) -> str:
    """The ffmpeg audio chain that cleans a hissy clip: wind/rumble
    high-pass, then afftdn starting from the measured (high-band) floor."""
    nf = max(-80.0, min(-20.0, float(noise_floor_db) + AUDIO_CLEANUP_NF_OFFSET_DB))
    return (f'highpass=f=70,'
            f'afftdn=nr={AUDIO_CLEANUP_REDUCTION_DB}:nf={nf:.1f}:tn=1')


def clip_audio_filters(ffmpeg: str, path: str, start: float, eff_dur: Optional[float]) -> list:
    """The -af chain for one clip's audio: optional clean-up, then loudnorm
    when the clip is long enough for it. Returns [] when nothing applies."""
    parts = []
    # Measure only what gets exported: past a trim out-point, a quiet
    # stretch would pull the low percentile down and skip the clean-up
    seconds = AUDIO_CLEANUP_ANALYSIS_S
    if eff_dur:
        seconds = min(seconds, eff_dur)
    floor = measure_noise_floor(ffmpeg, path, start, seconds)
    if floor is not None and floor > AUDIO_CLEANUP_FLOOR_DB:
        parts.append(audio_cleanup_filter(floor))
        logger.info(f"Audio clean-up on {os.path.basename(path)}: noise floor {floor:.1f} dB")
    if eff_dur is None or eff_dur >= LOUDNORM_MIN_SECONDS:
        parts.append(LOUDNORM_FILTER)
    return ['-af', ','.join(parts)] if parts else []

def _timestamp_label(full_path: str) -> str:
    """Human date & time for the corner stamp, e.g. "13 Jul 2026  09:57".

    Same source chain as the rest of the app: filename time > EXIF/video
    metadata (scanner.get_time_sort), then date-only, then file modified
    time. Returns '' when nothing at all is known."""
    from datetime import datetime
    from app.scanner import get_time_sort, get_date_taken

    p = Path(full_path)
    stamp = None
    try:
        stamp = get_time_sort(p)
    except Exception:
        stamp = None
    if stamp:
        try:
            dt = datetime.strptime(stamp, '%Y-%m-%d %H:%M:%S')
            return f"{dt.day} {dt.strftime('%b %Y')}  {dt.strftime('%H:%M')}"
        except ValueError:
            pass
    try:
        date = get_date_taken(p)
    except Exception:
        date = None
    if date:
        try:
            dt = datetime.strptime(date[:10], '%Y-%m-%d')
            return f"{dt.day} {dt.strftime('%b %Y')}"
        except ValueError:
            pass
    try:
        dt = datetime.fromtimestamp(os.path.getmtime(full_path))
        return f"{dt.day} {dt.strftime('%b %Y')}  {dt.strftime('%H:%M')}"
    except OSError:
        return ''


def _build_timestamp_filter(text: str, width: int, height: int) -> str:
    """Small camcorder-style date stamp, bottom-left corner, no box."""
    font_size = max(14, int(height * 0.024))
    font_file = _resolve_font_file(DEFAULT_FONT_NAME)
    fontfile_expr = f":fontfile='{_escape_drawtext_path(font_file)}'" if font_file else ''
    return (
        f"drawtext=text='{_escape_drawtext_text(text)}'"
        f"{fontfile_expr}"
        f":fontsize={font_size}"
        f":fontcolor=white@0.9"
        f":x={int(width * 0.015)}"
        f":y=h-th-{int(height * 0.025)}"
        f":shadowcolor=black@0.6:shadowx=0:shadowy=1"
    )


# Music ducking during video clips — export side of the playback fade
# (app.js _setSlideshowMusicDucked): music ramps to silence over this many
# seconds when a video starts and ramps back up when it ends.
MUSIC_DUCK_FADE_S = 0.8


def build_duck_volume_expr(intervals: List[tuple], fade: float = MUSIC_DUCK_FADE_S) -> str:
    """ffmpeg volume expression that dips the music to silence across each
    (start, end) interval with linear `fade`-second ramps, staying at 1.0
    elsewhere. Intervals must be sorted, non-overlapping, and separated by
    more than the ramp time — the caller merges near-adjacent ones."""
    expr = '1'
    for a, b in reversed(intervals):
        expr = (
            f'if(lt(t,{a:.3f}),1,'
            f'if(lt(t,{a + fade:.3f}),1-(t-{a:.3f})/{fade},'
            f'if(lt(t,{b:.3f}),0,'
            f'if(lt(t,{b + fade:.3f}),(t-{b:.3f})/{fade},{expr}))))'
        )
    return expr

# Ken Burns zoom depth: photos drift from 1.0x to 1.08x (or back) over
# their slide duration. app.js kb-0..kb-3 keyframes mirror these four
# variants (same order, keyed by slide index) so playback matches export.
KENBURNS_ZOOM = 0.08


def _kenburns_filter(index: int, width: int, height: int,
                     fps: int, duration: float) -> str:
    """Build a zoompan filter for the photo at `index`.

    Runs AFTER the scale+pad filter (so pan math sees the final frame) and
    BEFORE drawtext (so title text doesn't zoom). The 2x lanczos upscale
    feeding zoompan suppresses its well-known integer-rounding jitter.
    Direction rotates through 4 variants by slide index, matching the
    kb-0..kb-3 CSS animations in app.js.
    """
    n = max(2, int(round(fps * duration)))
    d = n - 1  # zoom expression denominator: on ranges 0..n-1
    z_in = f'1+{KENBURNS_ZOOM}*on/{d}'
    z_out = f'{1 + KENBURNS_ZOOM}-{KENBURNS_ZOOM}*on/{d}'
    centre_x = 'iw/2-(iw/zoom)/2'
    centre_y = 'ih/2-(ih/zoom)/2'
    variants = [
        (z_in, centre_x, centre_y),                    # 0: zoom in, centred
        (z_out, centre_x, centre_y),                   # 1: zoom out, centred
        (z_in, f'(iw-iw/zoom)*on/{d}', centre_y),      # 2: zoom in, pan L->R
        (z_in, centre_x, f'(ih-ih/zoom)*on/{d}'),      # 3: zoom in, pan T->B
    ]
    z, x, y = variants[index % 4]
    return (f'scale={width * 2}:{height * 2}:flags=lanczos,'
            f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={width}x{height}:fps={fps}")


# Blurred fill behind photos and videos. A portrait photo or clip in a
# 16:9 frame used to be pillarboxed on black; now the bars are a
# cover-cropped, blurred and darkened copy of the same frame. CSS mirror:
# .slide-fill in styles.css (an <img> behind photos, a muted <video> kept
# in step behind clips) - blur/brightness/saturation were matched by eye
# at 1080p, so change both sides together.
PHOTO_FILL_BRIGHTNESS = -0.26
PHOTO_FILL_SATURATION = 0.9


def _photo_fill_filter(width: int, height: int) -> str:
    """The scale+pad stage for photo and video segments, with the padding
    drawn from a blurred copy of the frame instead of black.

    One input and one output, so it still goes through -vf like the plain
    scale filter did; the split/overlay happen inside the chain. Ends with
    setsar=1 for the same reason as the plain filter (see scale_filter in
    export_slideshow: without it xfade silently breaks). Ken Burns and
    drawtext chain onto the overlay output exactly as they did onto pad.
    The blur radius scales with the frame so 720p and 4K look alike.
    """
    radius = max(4, int(round(height / 90)))
    chroma = max(2, radius // 2)
    blur = (f'boxblur=luma_radius={radius}:luma_power=2'
            f':chroma_radius={chroma}:chroma_power=1')
    tone = f'eq=brightness={PHOTO_FILL_BRIGHTNESS}:saturation={PHOTO_FILL_SATURATION}'
    return (
        f'split=2[fill][pic];'
        f'[fill]scale={width}:{height}:force_original_aspect_ratio=increase,'
        f'crop={width}:{height},{blur},{tone}[bg];'
        f'[pic]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];'
        f'[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1'
    )

# Curated font catalog for title / end cards.
# Each entry maps a UI-facing name to Windows font file names for
# regular / bold / italic / bold-italic variants. Files are resolved
# against the Windows Fonts directory at render time.
FONT_CATALOG = {
    'Arial':           {'r': 'arial.ttf',    'b': 'arialbd.ttf', 'i': 'ariali.ttf',   'bi': 'arialbi.ttf'},
    'Calibri':         {'r': 'calibri.ttf',  'b': 'calibrib.ttf','i': 'calibrii.ttf', 'bi': 'calibriz.ttf'},
    'Georgia':         {'r': 'georgia.ttf',  'b': 'georgiab.ttf','i': 'georgiai.ttf', 'bi': 'georgiaz.ttf'},
    'Verdana':         {'r': 'verdana.ttf',  'b': 'verdanab.ttf','i': 'verdanai.ttf', 'bi': 'verdanaz.ttf'},
    'Tahoma':          {'r': 'tahoma.ttf',   'b': 'tahomabd.ttf','i': 'tahoma.ttf',   'bi': 'tahomabd.ttf'},
    'Trebuchet MS':    {'r': 'trebuc.ttf',   'b': 'trebucbd.ttf','i': 'trebucit.ttf', 'bi': 'trebucbi.ttf'},
    'Times New Roman': {'r': 'times.ttf',    'b': 'timesbd.ttf', 'i': 'timesi.ttf',   'bi': 'timesbi.ttf'},
    'Courier New':     {'r': 'cour.ttf',     'b': 'courbd.ttf',  'i': 'couri.ttf',    'bi': 'courbi.ttf'},
    'Impact':          {'r': 'impact.ttf',   'b': 'impact.ttf',  'i': 'impact.ttf',   'bi': 'impact.ttf'},
    'Comic Sans MS':   {'r': 'comic.ttf',    'b': 'comicbd.ttf', 'i': 'comici.ttf',   'bi': 'comicz.ttf'},
}

# Default font used when the caller doesn't specify one. Arial is present
# on essentially every Windows install, so it's the safest fallback.
DEFAULT_FONT_NAME = 'Arial'


def _windows_fonts_dir() -> str:
    """Return the Windows fonts directory, falling back to a sensible default."""
    win_dir = os.environ.get('WINDIR') or os.environ.get('SystemRoot') or r'C:\Windows'
    return os.path.join(win_dir, 'Fonts')


def _resolve_font_file(font_name: Optional[str], bold: bool = False, italic: bool = False) -> Optional[str]:
    """
    Resolve a font name + bold/italic flags to an absolute path to a .ttf file
    inside the Windows Fonts directory. Returns None if no matching file exists,
    in which case callers should let ffmpeg fall back to its default font.
    """
    if not font_name:
        font_name = DEFAULT_FONT_NAME
    entry = FONT_CATALOG.get(font_name) or FONT_CATALOG.get(DEFAULT_FONT_NAME) or {}
    if bold and italic:
        variant = entry.get('bi') or entry.get('b') or entry.get('r')
    elif bold:
        variant = entry.get('b') or entry.get('r')
    elif italic:
        variant = entry.get('i') or entry.get('r')
    else:
        variant = entry.get('r')
    if not variant:
        return None
    fonts_dir = _windows_fonts_dir()
    path = os.path.join(fonts_dir, variant)
    if os.path.isfile(path):
        return path
    # Fall back to the regular variant if the requested bold/italic file
    # doesn't exist on this system (e.g. Impact has no italic).
    regular = entry.get('r')
    if regular:
        alt = os.path.join(fonts_dir, regular)
        if os.path.isfile(alt):
            return alt
    return None


def _escape_drawtext_text(text: str) -> str:
    """Escape user-supplied text for ffmpeg's ``drawtext`` filter.

    The filter graph parser and the drawtext filter itself have several
    special characters that must be escaped for a literal title to render
    correctly.  The escaping layers (applied in this order):

      1. ``\\`` - backslash is the escape character. Must be doubled
         **before** any later replacements that introduce new backslashes.
      2. ``'``  - single quote delimits values; escaped by closing the
         current quoted section, emitting an escaped quote, and
         reopening: ``'\\''``
      3. ``:``  - separates ``key=value`` pairs in a filter option list;
         escaped as ``\\:``
      4. ``;``  - separates filter chains; escaped as ``\\;``
      5. ``%``  - triggers ``drawtext`` printf-style time expansions
         (e.g. ``%{pts}``) ; escaped as ``%%`` for a literal percent.

    Without this, a title like ``John's Holiday: 50% Fun; Done!`` would
    produce a cryptic ffmpeg filter-graph parse error instead of
    rendering the title.
    """
    s = text
    s = s.replace('\\', '\\\\')     # must be first!
    s = s.replace("'", "'\\''")
    s = s.replace(':', '\\:')
    s = s.replace(';', '\\;')
    s = s.replace('%', '%%')
    return s


def _escape_drawtext_path(path: str) -> str:
    """
    ffmpeg's drawtext filter needs backslashes and colons escaped in the
    fontfile argument (Windows paths contain both).
    """
    return path.replace('\\', '/').replace(':', '\\:')


def _font_kwargs_from_settings(settings: Optional[Dict]) -> Dict:
    """
    Pull font-related keys off a title card / end card settings dict
    and return them as kwargs suitable for passing to _build_drawtext_filter.

    Recognised keys on `settings`:
      fontName, fontSize, fontColor, fontBold, fontItalic
    Missing / empty values fall through to the filter's defaults.
    """
    if not settings:
        return {}
    out = {}
    name = settings.get('fontName')
    if name:
        out['font_name'] = str(name)
    size = settings.get('fontSize')
    try:
        if size is not None and int(size) > 0:
            out['font_size_override'] = int(size)
    except (TypeError, ValueError):
        pass
    color = settings.get('fontColor')
    if color:
        out['font_color'] = str(color)
    if settings.get('fontBold'):
        out['bold'] = True
    if settings.get('fontItalic'):
        out['italic'] = True
    return out


def _normalize_color(color: Optional[str], default: str = 'white') -> str:
    """
    Validate and normalize a CSS-style color for ffmpeg drawtext.
    Accepts '#rrggbb', '#rgb', or a named color. Returns a safe string.
    """
    if not color:
        return default
    c = color.strip()
    if re.match(r'^#[0-9a-fA-F]{3}$', c):
        # Expand #rgb to #rrggbb for ffmpeg
        return '#' + ''.join(ch * 2 for ch in c[1:])
    if re.match(r'^#[0-9a-fA-F]{6}$', c):
        return c
    if re.match(r'^[a-zA-Z]+$', c):
        return c
    return default


def get_ffmpeg_path() -> str:
    """
    Get path to ffmpeg binary.
    Tries in order: imageio-ffmpeg bundle → system PATH → raises clear error.
    """
    # 1. Try imageio-ffmpeg (bundled binary)
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.isfile(path):
            logger.debug(f"Using imageio-ffmpeg: {path}")
            return path
    except ImportError:
        logger.debug("imageio-ffmpeg not installed, trying system ffmpeg")
    except Exception as e:
        logger.warning(f"imageio-ffmpeg error: {e}")

    # 2. Try system ffmpeg on PATH
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        logger.debug(f"Using system ffmpeg: {system_ffmpeg}")
        return system_ffmpeg

    # 3. Nothing found — raise a helpful error
    raise FileNotFoundError(
        "Video export requires ffmpeg, which could not be found.\n\n"
        "If you installed from the Microsoft Store, please reinstall the app "
        "or contact support:\nhttps://www.bacommander.com/speedy-slideshow-25-support\n\n"
        "For developers: pip install imageio-ffmpeg  OR  install ffmpeg from https://ffmpeg.org"
    )


def get_ffprobe_path() -> str:
    """Get path to ffprobe binary."""
    try:
        ffmpeg = get_ffmpeg_path()
    except FileNotFoundError:
        return 'ffprobe'  # Will fail gracefully in get_video_duration
    ffprobe = ffmpeg.replace('ffmpeg', 'ffprobe')
    if os.path.isfile(ffprobe):
        return ffprobe
    return shutil.which('ffprobe') or 'ffprobe'


def get_video_duration(filepath: str) -> Optional[float]:
    """Get duration of a video file in seconds.

    Tries ffprobe first, then falls back to parsing ffmpeg stderr.
    Returns ``None`` if both methods fail. Callers must decide whether
    a missing duration is fatal (e.g. music mixing - bail out) or
    survivable (e.g. logging - just print "?").

    History: this used to return a hard-coded 5.0s on total failure.
    That hid real ffprobe failures behind a broken-but-plausible value
    that propagated into music timing calculations and could produce a
    5-second music track for a 60-minute video.
    """
    # Method 1: ffprobe (most accurate)
    try:
        ffprobe = get_ffprobe_path()
        result = subprocess.run(
            [ffprobe, '-v', 'quiet', '-print_format', 'json',
             '-show_format', filepath],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=30,
            creationflags=_subprocess_flags
        )
        data = json.loads(result.stdout)
        dur = float(data['format']['duration'])
        if dur > 0:
            return dur
    except Exception:
        pass

    # Method 2: parse duration from ffmpeg stderr (works without ffprobe).
    # Bare `ffmpeg -i` prints the container's Duration line and exits
    # immediately ("At least one output file must be specified") - the old
    # `-f null -` form decoded the ENTIRE file, which stalled exports for
    # minutes per long clip and could hit the timeout, silently degrading
    # callers to their fallback durations.
    try:
        ffmpeg = get_ffmpeg_path()
        result = subprocess.run(
            [ffmpeg, '-hide_banner', '-i', filepath],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=15,
            creationflags=_subprocess_flags
        )
        # Parse "Duration: HH:MM:SS.ms" from stderr
        import re
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+)\.(\d+)', result.stderr)
        if m:
            h, mins, s, frac = m.groups()
            dur = int(h) * 3600 + int(mins) * 60 + int(s) + float(f'0.{frac}')
            if dur > 0:
                logger.debug(f"Duration from ffmpeg stderr for {filepath}: {dur:.2f}s")
                return dur
    except Exception as e:
        logger.warning(f"Could not get duration for {filepath}: {e}")

    logger.warning(f"Duration detection failed for {filepath} - caller must handle None")
    return None


def get_video_info(filepath: str) -> Dict:
    """Header-only probe for duration + interlacing in ONE ffmpeg spawn.

    Returns {'duration': float|None, 'interlaced': bool}. Parses bare
    `ffmpeg -i` stderr (no ffprobe — imageio-ffmpeg doesn't ship one):
    interlaced sources show a field flag in the video stream line, e.g.
    ``yuv420p(top first)`` for 1080i AVCHD. This matches what DEINT_FILTER
    keys on (frame flags), so the badge and the export fix agree.
    """
    info: Dict = {'duration': None, 'interlaced': False}
    try:
        ffmpeg = get_ffmpeg_path()
        result = subprocess.run(
            [ffmpeg, '-hide_banner', '-i', filepath],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=15,
            creationflags=_subprocess_flags
        )
        import re
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+)\.(\d+)', result.stderr)
        if m:
            h, mins, s, frac = m.groups()
            dur = int(h) * 3600 + int(mins) * 60 + int(s) + float(f'0.{frac}')
            if dur > 0:
                info['duration'] = dur
        for line in result.stderr.splitlines():
            if 'Stream' in line and 'Video' in line:
                if re.search(r'\((?:top|bottom)(?: coded)? first', line):
                    info['interlaced'] = True
                break
    except Exception as e:
        logger.warning(f"Video info probe failed for {filepath}: {e}")
    return info


def export_slideshow(
    media_list: List[Dict],
    photos_root: str,
    output_path: str,
    resolution: str = '1080',
    fps: int = 30,
    format: str = 'mp4',
    photo_duration: float = 5.0,
    transition: str = 'crossfade',
    transition_duration: float = 1.0,
    progress_callback: Optional[Callable] = None,
    show_title: bool = True,
    show_day_title: bool = True,
    title_position: str = 'top',
    title_text: str = '',
    music_paths: Optional[List[str]] = None,
    music_volume: float = 0.5,
    video_volume: float = 1.0,
    music_fade_out: bool = True,
    music_fade_duration: float = 3.0,
    track_crossfade: float = 2.0,
    quality: str = 'high',
    codec: str = 'h264',
    aspect: str = '16:9',
    audio_bitrate: int = 192,
    title_cards: Optional[Dict] = None,
    end_card: Optional[Dict] = None,
    ken_burns: bool = True,
    music_duck_for_videos: bool = True,
    show_timestamp: bool = False,
    photo_fill: bool = True,
    hw_encode: bool = True,
) -> Dict:
    """
    Export a slideshow as a video file.

    Args:
        media_list: List of dicts with 'path' (relative), 'type' ('photo'/'video'), 'name'
        photos_root: Root directory for resolving relative paths
        output_path: Full path for the output video file
        resolution: '1080', '2160', or '4k'
        fps: Frames per second (30 or 60)
        format: 'mp4' or 'avi'
        photo_duration: How long each photo is shown (seconds)
        transition: 'crossfade' or 'cut'
        transition_duration: Duration of crossfade (seconds), ignored for 'cut'
        progress_callback: fn(percent, message) called during export

    Returns:
        Dict with 'ok', 'output_path', 'duration', or 'error'
    """
    base_width, base_height = RESOLUTIONS.get(resolution, (1920, 1080))

    # Apply aspect ratio to resolution
    ar = ASPECT_RATIOS.get(aspect, (16, 9))
    if ar == (16, 9):
        width, height = base_width, base_height
    elif ar == (9, 16):
        # Portrait: swap dimensions (e.g. 1080x1920)
        width, height = base_height, base_width
    elif ar == (1, 1):
        # Square: use the shorter dimension
        side = min(base_width, base_height)
        width, height = side, side
    elif ar == (4, 3):
        # 4:3: keep height, adjust width
        width = int(base_height * 4 / 3)
        # Ensure even dimensions
        width = width if width % 2 == 0 else width + 1
        height = base_height
    else:
        width, height = base_width, base_height

    # Resolve codec and CRF
    crf = QUALITY_CRF.get(quality, 18)
    video_codec = 'libx265' if codec == 'h265' else 'libx264'
    audio_br = f'{audio_bitrate}k'

    if not media_list:
        return {'error': 'No media to export'}

    logger.info(f"Starting export: {len(media_list)} items, {width}x{height}, {fps}fps, "
                f"{format}, codec={video_codec}, crf={crf}, aspect={aspect}, audio={audio_br}")

    # Warnings accumulated during export (music-mix failures, dropped
    # tracks, etc.). The render itself still succeeds - these surface to
    # the UI so the user knows not everything they asked for happened.
    warnings: List[str] = []

    reset_export_cancel()
    tmpdir = None
    try:
        # Inside the try so a missing ffmpeg returns the friendly
        # {'error': ...} dict instead of raising out of the API contract
        ffmpeg = get_ffmpeg_path()
        tmpdir = tempfile.mkdtemp(prefix='sss_export_')

        # Hardware encoder if one passes its probe (and the user left the
        # switch on); every encode below goes through run_encode so a
        # failing GPU encode falls back to software instead of failing.
        enc = EncoderChoice(ffmpeg, video_codec, crf, hw_encode)
        logger.info(f"Video encoder: {enc.encoder} ({enc.describe()})")

        if progress_callback:
            progress_callback(5, 'Preparing media segments...')

        # Phase 1: Convert each media item into a video segment
        segments = []
        segment_durations = []  # Track each segment's duration for total calculation
        segment_is_video = []   # Parallel: True for video clips (drives music ducking)

        # Pre-scan: weight each item by predicted encode cost so the
        # progress % (and the UI's ETA extrapolated from it) tracks
        # wall-clock work. Videos re-encode at roughly real time while
        # photos render in a second or two — the old per-item count made
        # photo-heavy starts look deceptively fast, so the ETA ballooned
        # as soon as the videos began.
        if progress_callback:
            progress_callback(4, 'Scanning media durations...')
        item_weights = []
        for it in media_list:
            if it.get('type') == 'titleCard':
                item_weights.append(2.0)
                continue
            full = os.path.join(photos_root, it.get('path', '').replace('/', os.sep))
            if it.get('type') == 'video':
                # Weight by the TRIMMED length: a 20-minute source cut to
                # 8s costs 8s of encoding, and weighting it as 20 minutes
                # pins the progress bar near zero for the whole render.
                t_start, t_end = trims.range_for(it.get('trim'))
                dur = trims.effective_duration(get_video_duration(full), t_start, t_end)
                if dur is None:  # not `or 10.0` — that swallows a real 0.0
                    dur = 10.0
                item_weights.append(4.0 + dur * 1.5)  # ~realtime encode + startup
            else:
                item_weights.append(1.0 + float(photo_duration) * 0.25)
        total_weight = sum(item_weights) or 1.0
        weight_done = 0.0
        total = len(media_list)
        last_day = None  # Track day changes for day title overlays

        # Base scale+pad filter. setsar=1 is critical — without it, some sources
        # (notably lavfi color and some JPEGs) come out with SAR 0:1, which makes
        # xfade silently produce a broken video stream where only the first
        # segment's frames render. Forcing SAR=1 keeps every segment uniform.
        scale_filter = f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1'

        # Media-only view + per-group index, used to auto-pick title card
        # backgrounds and build subtitles (app.js mirrors this in
        # _decorateTitleCards for playback)
        media_only = [it for it in media_list if it.get('type') != 'titleCard']
        groups_by_key: Dict[str, list] = {}
        for it in media_only:
            gk = it.get('tc_group_key', '')
            if gk:
                groups_by_key.setdefault(gk, []).append(it)

        def _group_bg_path(items, tag):
            """Full path of the auto background for a title card: the
            group's first photo, else a frame pulled from its first video.
            Returns None when nothing usable exists (gradient fallback)."""
            for it in items:
                if it.get('type') != 'video':
                    p = os.path.join(photos_root, it['path'].replace('/', os.sep))
                    if os.path.isfile(p):
                        return p
            for it in items:
                if it.get('type') == 'video':
                    p = os.path.join(photos_root, it['path'].replace('/', os.sep))
                    if os.path.isfile(p):
                        return _extract_video_frame(
                            ffmpeg, p, os.path.join(tmpdir, f'tcbg_{tag}.jpg'),
                            start=trims.range_for(it.get('trim'))[0])
            return None

        for i, item in enumerate(media_list):
            # Inline title card (used by custom slideshows with First/Last cards).
            # These items have no file on disk — generate a full-frame segment.
            if item.get('type') == 'titleCard':
                tc_text = item.get('title', '') or ''
                tc_pos = item.get('textPosition', 'middle') or 'middle'
                if tc_pos == 'middle':
                    tc_pos = 'center'
                tc_dark_box = bool(item.get('darkBox', False))
                tc_image = item.get('imagePath', '') or ''
                tc_duration = float(item.get('duration', 3) or 3)
                tc_font_kwargs = _font_kwargs_from_settings(item)

                tc_seg_path = os.path.join(tmpdir, f'titlecard_{i:04d}.mp4')

                if progress_callback:
                    pct = 5 + int((weight_done / total_weight) * 60)
                    progress_callback(pct, f'Generating title card {i+1}/{total}...')

                # Auto background + subtitle: a trailing (last) card gets
                # the show's final item as backdrop and no subtitle; any
                # other card gets the location/count subtitle. The blurred
                # auto backdrop only applies to text-only cards — a
                # user-chosen image is kept as-is (but still subtitled).
                tc_bg = None
                tc_subtitle = ''
                if media_only:
                    trailing = all(m.get('type') == 'titleCard'
                                   for m in media_list[i + 1:])
                    if not trailing:
                        tc_subtitle = build_titlecard_subtitle(media_only, tc_text)
                    if not tc_image:
                        tc_bg = _group_bg_path(
                            media_only[::-1] if trailing else media_only, f'{i:04d}')

                ok = _render_title_card_segment(
                    ffmpeg, tc_seg_path,
                    width=width, height=height, fps=fps, duration=tc_duration,
                    video_codec=video_codec, crf=crf, audio_br=audio_br, encoder=enc,
                    text=tc_text, subtitle=tc_subtitle, position=tc_pos,
                    dark_box=tc_dark_box, font_kwargs=tc_font_kwargs,
                    image_path=tc_image or None, bg_photo_path=tc_bg,
                )
                if ok:
                    segments.append(tc_seg_path)
                    segment_durations.append(tc_duration)
                    segment_is_video.append(False)
                    logger.debug(
                        f"Title card segment {i}: {tc_duration:.2f}s "
                        f"text='{tc_text[:30]}' image={bool(tc_image)} bg={bool(tc_bg)}"
                    )
                else:
                    logger.error(f"Inline title card segment missing after ffmpeg run: {tc_seg_path}")
                # Reset day tracking so next item triggers day title correctly
                last_day = None
                weight_done += item_weights[i]
                continue

            rel_path = item['path'].replace('/', os.sep)
            full_path = os.path.join(photos_root, rel_path)

            if not os.path.isfile(full_path):
                logger.warning(f"File not found, skipping: {full_path}")
                weight_done += item_weights[i]
                continue

            segment_path = os.path.join(tmpdir, f'seg_{i:04d}.mp4')
            pct = 5 + int((weight_done / total_weight) * 60)

            # Determine if this segment needs a title overlay or title card
            overlay_text = None
            overlay_font_kwargs = {}
            current_day = item.get('day', '')
            tc_group_key = item.get('tc_group_key', '')

            # Look up per-group title card settings
            tc_settings = (title_cards or {}).get(tc_group_key, {}) if tc_group_key else {}
            tc_enabled = tc_settings.get('enabled', True)
            tc_custom_text = tc_settings.get('text', '')
            tc_image_path = tc_settings.get('imagePath', '')
            tc_duration = tc_settings.get('duration', 3)
            tc_text_position = tc_settings.get('textPosition', 'center')
            tc_dark_box = tc_settings.get('darkBox', False)
            tc_font_kwargs = _font_kwargs_from_settings(tc_settings)

            if i == 0 and show_title and title_text:
                # First slide: show the main title
                overlay_text = title_text
            elif show_day_title and current_day and current_day != last_day and tc_enabled:
                # First item of a new day — check for title card image or custom text
                day_label = tc_custom_text or _format_day_label(current_day)

                # Map UI position name to drawtext position
                tc_pos = 'center' if tc_text_position == 'middle' else tc_text_position

                if tc_image_path and os.path.isfile(tc_image_path):
                    # Full-frame title card from the custom image (not
                    # blurred), still with the auto location/count subtitle
                    tc_seg_path = os.path.join(tmpdir, f'tc_{i:04d}.mp4')
                    group_items = groups_by_key.get(tc_group_key, [])
                    tc_subtitle = build_titlecard_subtitle(group_items, day_label) if group_items else ''
                    if _render_title_card_segment(
                        ffmpeg, tc_seg_path,
                        width=width, height=height, fps=fps, duration=tc_duration,
                        video_codec=video_codec, crf=crf, audio_br=audio_br, encoder=enc,
                        text=day_label, subtitle=tc_subtitle, position=tc_pos,
                        dark_box=tc_dark_box, font_kwargs=tc_font_kwargs,
                        image_path=tc_image_path,
                    ):
                        segments.append(tc_seg_path)
                        segment_durations.append(tc_duration)
                        segment_is_video.append(False)
                elif tc_custom_text or 'duration' in tc_settings:
                    # Standalone card only on explicit user intent
                    # (custom text or an explicitly-set duration). The old
                    # `tc_duration != photo_duration` compared two DEFAULTS
                    # (3 vs 5.0), so every day boundary got a standalone
                    # card and the overlay branch below was unreachable.
                    # Background: the group's own first photo, blurred;
                    # subtitle: location + counts from the group's items.
                    tc_seg_path = os.path.join(tmpdir, f'tc_{i:04d}.mp4')
                    group_items = groups_by_key.get(tc_group_key, [])
                    tc_bg = _group_bg_path(group_items, f'{i:04d}') if group_items else None
                    tc_subtitle = build_titlecard_subtitle(group_items, day_label) if group_items else ''
                    if _render_title_card_segment(
                        ffmpeg, tc_seg_path,
                        width=width, height=height, fps=fps, duration=tc_duration,
                        video_codec=video_codec, crf=crf, audio_br=audio_br, encoder=enc,
                        text=day_label, subtitle=tc_subtitle, position=tc_pos,
                        dark_box=tc_dark_box, font_kwargs=tc_font_kwargs,
                        bg_photo_path=tc_bg,
                    ):
                        segments.append(tc_seg_path)
                        segment_durations.append(tc_duration)
                        segment_is_video.append(False)
                    overlay_text = None  # Already handled as standalone segment
                else:
                    # Standard text overlay on the first photo of the day
                    overlay_text = day_label
                    overlay_font_kwargs = tc_font_kwargs
            elif current_day != last_day and not tc_enabled:
                pass  # Title card disabled for this group

            last_day = current_day

            # Build the video filter with optional title overlay.
            # drawtext is kept separate so Ken Burns can slot between the
            # scale and the text (title text must not zoom with the photo).
            drawtext_part = ''
            if overlay_text:
                drawtext_part = ',' + _build_drawtext_filter(
                    overlay_text, width, height, title_position, fps,
                    **overlay_font_kwargs
                )
            # Optional camcorder-style date & time in the corner
            if show_timestamp:
                ts_label = _timestamp_label(full_path)
                if ts_label:
                    drawtext_part += ',' + _build_timestamp_filter(ts_label, width, height)
            vf = scale_filter + drawtext_part

            if item['type'] == 'photo':
                # Convert photo to a video segment of photo_duration seconds
                # Include a silent audio track so all segments are uniform for concat
                if progress_callback:
                    progress_callback(pct, f'Processing photo {i+1}/{total}: {item["name"]}')

                # Photos letterbox over a blurred copy of themselves rather
                # than black (playback mirror: .slide-fill), unless the
                # user turned the fill off. Videos get the same below.
                photo_base = _photo_fill_filter(width, height) if photo_fill else scale_filter
                vf = photo_base + drawtext_part
                if ken_burns:
                    vf = (photo_base + ','
                          + _kenburns_filter(i, width, height, fps, photo_duration)
                          + drawtext_part)

                def photo_cmd(codec_args, vf=vf, full_path=full_path, segment_path=segment_path):
                    return [
                        ffmpeg, '-y',
                        '-framerate', str(fps),
                        '-loop', '1',
                        '-i', full_path,
                        '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                        '-t', str(photo_duration),
                        '-vf', vf,
                    ] + codec_args + [
                        '-r', str(fps),
                        '-c:a', 'aac',
                        '-b:a', audio_br,
                        '-ar', '48000',
                        '-ac', '2',
                        '-shortest',
                        segment_path
                    ]
                run_encode(photo_cmd, enc)

            else:
                # Re-encode video segment to match target resolution/fps
                # Always ensure an audio track exists for uniform concat
                if progress_callback:
                    progress_callback(pct, f'Processing video {i+1}/{total}: {item["name"]}')

                has_audio = _has_audio_stream(ffmpeg, full_path)

                # Deinterlace before scaling — no-op for progressive sources.
                # Same blurred fill as photos behind a portrait clip
                # (playback mirror: the muted .slide-fill video).
                video_base = _photo_fill_filter(width, height) if photo_fill else scale_filter
                vf = DEINT_FILTER + ',' + video_base + drawtext_part

                # Scale the ffmpeg timeout with the source duration — the
                # flat 300s default killed re-encodes of long clips (a
                # 10-min 4K video takes well over 5 minutes) with
                # misleading "reduce the number of media items" advice.
                # Header-only probe: cheap. ~6x realtime headroom, capped
                # at 1 hour, never below the old default.
                orig_dur = get_video_duration(full_path)

                # The clip's in/out points, stamped on the item by
                # api.export_video. Everything below keys off eff_dur (how
                # long the segment will actually be), never orig_dur —
                # see the loudnorm guard.
                t_start, t_end = trims.range_for(item.get('trim'), orig_dur)
                eff_dur = trims.effective_duration(orig_dur, t_start, t_end)
                trim_args = []
                if t_start > 0:
                    # Input-side seek: ffmpeg jumps to the nearest keyframe
                    # and decodes forward, so it stays frame-accurate when
                    # transcoding without decoding-and-discarding the whole
                    # head. Output-side -ss would do the latter, and since
                    # the timeout below is now derived from the TRIMMED
                    # length, a long clip cut short would reliably time out.
                    trim_args = ['-ss', f'{t_start:.3f}']
                dur_args = []
                if t_end is not None:
                    dur_args = ['-t', f'{max(0.0, t_end - t_start):.3f}']

                encode_timeout = 300
                if eff_dur:
                    encode_timeout = min(3600, max(300, int(eff_dur * 6) + 120))

                # Same guard as the chain export's normalize pass: on a
                # clip under LOUDNORM_MIN_SECONDS loudnorm silently emits
                # NO audio stream, and a segment without one breaks the
                # uniform-concat contract for the whole slideshow.
                # Keyed on the TRIMMED length, not the source's: a 60s
                # clip cut to 2s is still a sub-3s segment, and
                # loudnorm would emit no audio stream for it, which
                # breaks the concat for the entire export.
                # Plus the automatic hiss/wind clean-up when the clip's
                # measured noise floor calls for it (clip_audio_filters).
                af_args = clip_audio_filters(ffmpeg, full_path, t_start, eff_dur) if has_audio else []

                def video_cmd(v_codec_args, vf=vf, full_path=full_path, segment_path=segment_path,
                              trim_args=trim_args, dur_args=dur_args, af_args=af_args,
                              has_audio=has_audio):
                    if has_audio:
                        return [
                            ffmpeg, '-y',
                        ] + trim_args + [
                            '-i', full_path,
                            '-vf', vf,
                        ] + af_args + v_codec_args + dur_args + [
                            '-r', str(fps),
                            '-vsync', 'cfr',
                            '-c:a', 'aac', '-b:a', audio_br,
                            '-ar', '48000', '-ac', '2',
                            '-avoid_negative_ts', 'make_zero',
                            segment_path
                        ]
                    # No audio — add silent track
                    # -ss is a PER-INPUT option and must sit immediately
                    # before the video's -i. Appended to a shared prefix it
                    # would seek the anullsrc generator instead, silently
                    # leaving the video untrimmed with no error anywhere.
                    return [
                        ffmpeg, '-y',
                    ] + trim_args + [
                        '-i', full_path,
                        '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                        '-vf', vf,
                        '-map', '0:v:0', '-map', '1:a:0',
                    ] + v_codec_args + dur_args + [
                        '-r', str(fps),
                        '-vsync', 'cfr',
                        '-c:a', 'aac', '-b:a', audio_br,
                        '-ar', '48000', '-ac', '2',
                        '-shortest',
                        '-avoid_negative_ts', 'make_zero',
                        segment_path
                    ]
                run_encode(video_cmd, enc,
                           runner=lambda c, t=encode_timeout: _run_ffmpeg(c, timeout=t))

            # Size check, not just existence: _run_ffmpeg only raises on a
            # non-zero exit, and an -ss past the end of a clip exits 0 with
            # a header-only file. Appending that stub would surface later as
            # an unrelated concat failure with no hint of the real cause.
            if os.path.isfile(segment_path) and os.path.getsize(segment_path) > 0:
                segments.append(segment_path)
                segment_is_video.append(item['type'] != 'photo')
                # Track duration: photos use photo_duration, videos use re-encoded segment duration
                if item['type'] == 'photo':
                    segment_durations.append(photo_duration)
                else:
                    # Probe the re-encoded segment (not original) for accurate duration.
                    # The re-encode may change duration due to fps/codec differences.
                    # If probing fails we fall back to photo_duration so the
                    # render finishes; we surface a warning so the user knows
                    # one of their videos has unknown timing.
                    seg_dur = get_video_duration(segment_path)
                    # orig_dur already probed above for the encode timeout
                    if seg_dur is None:
                        warnings.append(
                            f"Couldn't measure duration of video segment '{item['name']}' - "
                            f"using {photo_duration:.1f}s as a fallback. Final timing may be off."
                        )
                        seg_dur = photo_duration
                    seg_str = f"{seg_dur:.2f}s"
                    orig_str = f"{orig_dur:.2f}s" if orig_dur is not None else "?"
                    trim_str = f", {trims.describe(item.get('trim'))}" if item.get('trim') else ""
                    logger.info(f"Video segment '{item['name']}': original={orig_str}, "
                                f"re-encoded={seg_str}{trim_str}")
                    segment_durations.append(seg_dur)
            else:
                # A dropped segment was silent before; say so, because the
                # likeliest cause is a trim that no longer fits the clip.
                warnings.append(
                    f"'{item['name']}' produced no usable video and was skipped."
                )
                logger.warning(f"Empty segment for '{item['name']}' - skipped")

            weight_done += item_weights[i]

        if not segments:
            return {'error': 'No segments were created'}

        # Generate end card segment if enabled
        if end_card:
            ec_text = end_card.get('text', 'Thanks for watching')
            ec_pos = end_card.get('position', 'middle')
            if ec_pos == 'middle':
                ec_pos = 'center'
            ec_dark_box = end_card.get('darkBox', False)
            ec_image = end_card.get('imagePath', '')
            ec_duration = end_card.get('duration', 4)
            ec_font_kwargs = _font_kwargs_from_settings(end_card)

            ec_seg_path = os.path.join(tmpdir, 'endcard.mp4')

            if progress_callback:
                progress_callback(68, 'Generating end card...')
            # Text-only end cards get the show's last item as a blurred
            # backdrop (matches playback); custom images pass through as-is.
            ec_bg = None
            if not (ec_image and os.path.isfile(ec_image)) and media_only:
                ec_bg = _group_bg_path(media_only[::-1], 'endcard')
            if _render_title_card_segment(
                ffmpeg, ec_seg_path,
                width=width, height=height, fps=fps, duration=ec_duration,
                video_codec=video_codec, crf=crf, audio_br=audio_br, encoder=enc,
                text=ec_text, position=ec_pos,
                dark_box=ec_dark_box, font_kwargs=ec_font_kwargs,
                image_path=ec_image or None, bg_photo_path=ec_bg,
            ):
                segments.append(ec_seg_path)
                segment_durations.append(ec_duration)
                segment_is_video.append(False)
            else:
                logger.warning(f"End card segment missing after ffmpeg run: {ec_seg_path}")

        if progress_callback:
            progress_callback(70, 'Joining segments...')

        # Phase 2: Concatenate segments
        logger.info(
            f"Concat phase: {len(segments)} segments, "
            f"known durations (s) = {[round(d, 2) for d in segment_durations]}, "
            f"transition = {transition}"
        )
        xfade_name = 'mix' if transition == 'mix' else XFADE_TRANSITIONS.get(transition)
        if xfade_name and len(segments) > 1:
            # Use xfade filter for transitions.
            # Pass segment_durations explicitly so _xfade_pass does NOT re-probe with ffprobe
            # (which may fall back to a constant 5.0 if ffprobe is unavailable, breaking offsets).
            final_path = _concat_with_crossfade(
                ffmpeg, segments, tmpdir, output_path,
                width, height, fps, format, transition_duration,
                progress_callback, xfade_name,
                video_codec=video_codec, crf=crf, audio_br=audio_br, encoder=enc,
                segment_durations=segment_durations,
            )
        else:
            # Simple concat (cut transition or single segment)
            final_path = _concat_simple(
                ffmpeg, segments, tmpdir, output_path,
                format, progress_callback
            )

        # Phase 3: Mix in background music if provided
        valid_music = [p for p in (music_paths or []) if p and os.path.isfile(p)]

        # Warn about any music the user selected that we couldn't find
        # (e.g. they unplugged an external drive between picking and
        # exporting, or synced the path came from a OneDrive placeholder).
        requested = [p for p in (music_paths or []) if p]
        missing = [p for p in requested if p not in valid_music]
        if missing:
            names = ', '.join(os.path.basename(p) for p in missing[:3])
            more = '' if len(missing) <= 3 else f' (+{len(missing) - 3} more)'
            warnings.append(
                f"{len(missing)} of {len(requested)} music file(s) couldn't "
                f"be read and were skipped: {names}{more}"
            )

        if valid_music and os.path.isfile(final_path):
            if progress_callback:
                progress_callback(92, 'Mixing background music...')

            # Calculate the expected video duration from known inputs
            # instead of relying on ffprobe (which can return wrong values)
            total_segment_dur = sum(segment_durations)
            if xfade_name and len(segments) > 1:
                # xfade shortens the video by transition_duration per transition
                calculated_dur = total_segment_dur - ((len(segments) - 1) * transition_duration)
            else:
                calculated_dur = total_segment_dur

            logger.info(f"Music mix: calculated video duration = {calculated_dur:.1f}s "
                        f"({len(segments)} segments, {total_segment_dur:.1f}s total)")

            # Duck the music while video clips play (mirrors the playback
            # fade). Segment start times come from the same clamped xfade
            # timeline the video concat used, so the dips line up exactly.
            duck_intervals = None
            if music_duck_for_videos and any(segment_is_video):
                duck_intervals = _build_duck_intervals(
                    segment_durations, segment_is_video,
                    transition_duration if (xfade_name and len(segments) > 1) else None)

            final_path = _mix_background_music(
                ffmpeg, final_path, valid_music, tmpdir,
                output_path, format,
                music_volume=music_volume,
                video_volume=video_volume,
                fade_out=music_fade_out,
                fade_duration=music_fade_duration,
                video_duration=calculated_dur,
                audio_br=audio_br,
                track_crossfade=track_crossfade,
                duck_intervals=duck_intervals,
                warnings_out=warnings,
            )

        if progress_callback:
            progress_callback(95, 'Finalizing...')

        # Get output duration and file size. get_video_duration returns
        # None on probe failure; report 0 to the UI in that case (the
        # file exists, we just couldn't measure it - rare for our own
        # freshly-rendered output).
        duration = (get_video_duration(final_path) or 0) if os.path.isfile(final_path) else 0
        file_size = 0
        try:
            file_size = os.path.getsize(final_path) if os.path.isfile(final_path) else 0
        except Exception:
            pass

        # Cleanup temp dir
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

        if progress_callback:
            progress_callback(100, 'Export complete!')

        logger.info(f"Export complete: {final_path} ({duration:.1f}s, {file_size / 1048576:.1f} MB)")

        return {
            'ok': True,
            'output_path': final_path,
            'duration': duration,
            'file_size': file_size,
            'filename': os.path.basename(final_path),
            # Which encoder did the work (shown on the export summary)
            'encoder': enc.describe(),
            'encoder_id': enc.encoder,
            # Non-fatal warnings accumulated during the render (e.g. music
            # tracks that couldn't be mixed). Empty list on a clean run.
            'warnings': warnings,
        }

    except ExportCancelled:
        logger.info("Export cancelled by user")
        try:
            if tmpdir:
                shutil.rmtree(tmpdir)
        except Exception:
            pass
        # Remove the partial output so a "cancelled" file doesn't show
        # up in Exports
        try:
            if os.path.isfile(output_path):
                os.remove(output_path)
        except Exception:
            pass
        return {'cancelled': True, 'error': 'Export cancelled'}
    except FileNotFoundError as e:
        logger.error(f"Export failed - ffmpeg not found: {e}")
        try:
            if tmpdir:
                shutil.rmtree(tmpdir)
        except Exception:
            pass
        return {'error': f"ffmpeg not found. Install it with: pip install imageio-ffmpeg"}
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        try:
            if tmpdir:
                shutil.rmtree(tmpdir)
        except Exception:
            pass
        return {'error': str(e)}


def _format_day_label(iso_date: str) -> str:
    """Format an ISO date string (YYYY-MM-DD) into a readable label like 'Sun, Jul 6, 2025'."""
    try:
        from datetime import datetime
        d = datetime.strptime(iso_date, '%Y-%m-%d')
        # %-d works on Linux/macOS, %#d on Windows — fall back to stripping leading zero
        try:
            return d.strftime('%a, %b %-d, %Y')
        except ValueError:
            return d.strftime('%a, %b %d, %Y').replace(' 0', ' ')
    except Exception:
        return iso_date


def _build_drawtext_filter(
    text: str, width: int, height: int,
    position: str = 'top', fps: int = 30,
    dark_box: bool = False,
    font_name: Optional[str] = None,
    font_size_override: Optional[int] = None,
    font_color: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
) -> str:
    """
    Build an ffmpeg drawtext filter string for title overlays.
    Text fades in over 0.5s and fades out after 3s, displayed for ~4s total.

    Optional font params control the appearance:
      font_name: curated font family name (see FONT_CATALOG)
      font_size_override: pixel size, overrides the automatic size
      font_color: ffmpeg color string (e.g. 'white', '#ff0000')
      bold/italic: select the bold/italic variant of the chosen font
    """
    safe_text = _escape_drawtext_text(text)

    # Font size proportional to resolution (unless overridden)
    auto_font_size = max(24, int(height * 0.04))

    # Position: top, bottom, or center, centered horizontally
    if position == 'center':
        y_pos = '(h-th)/2'
        auto_font_size = max(32, int(height * 0.06))  # Larger for title cards
    elif position == 'bottom':
        y_pos = f'h-th-{int(height * 0.08)}'
    else:
        y_pos = str(int(height * 0.06))

    if font_size_override and int(font_size_override) > 0:
        font_size = int(font_size_override)
    else:
        font_size = auto_font_size

    # Fade in from 0-0.5s, hold until 3s, fade out 3-4s.
    # The box can't fade (boxcolor doesn't take expressions), so the whole
    # drawtext is disabled at t=4 — otherwise the dark box stayed on
    # screen after the text had faded out.
    alpha_expr = (
        "if(lt(t\\,0.5)\\,t/0.5\\,"
        "if(lt(t\\,3)\\,1\\,"
        "if(lt(t\\,4)\\,(4-t)/1\\,0)))"
    )
    enable_expr = "lt(t\\,4)"

    # Background box: darker and larger when dark_box is enabled
    if dark_box:
        box_color = 'black@0.7'
        box_border = int(font_size * 0.8)
    else:
        box_color = 'black@0.5'
        box_border = int(font_size * 0.4)

    fg_color = _normalize_color(font_color, 'white')

    font_file = _resolve_font_file(font_name, bold=bold, italic=italic)
    fontfile_expr = ''
    if font_file:
        fontfile_expr = f":fontfile='{_escape_drawtext_path(font_file)}'"

    return (
        f"drawtext=text='{safe_text}'"
        f"{fontfile_expr}"
        f":fontsize={font_size}"
        f":fontcolor={fg_color}"
        f":x=(w-tw)/2"
        f":y={y_pos}"
        f":alpha='{alpha_expr}'"
        f":enable='{enable_expr}'"
        f":box=1"
        f":boxcolor={box_color}"
        f":boxborderw={box_border}"
    )


# ── Title card rendering ─────────────────────────────────────────────
# Matched implementation with playback: styles.css (.title-card-bg,
# .title-card-text, .title-card-subtitle keyframes) mirrors these
# timings and treatments. Change one side and the live slideshow stops
# matching the export.
TITLECARD_TEXT_FADE_S = 0.8    # title fade-in / rise duration
TITLECARD_TEXT_RISE = 24       # px the title rises during entrance
TITLECARD_SUB_DELAY_S = 0.3    # subtitle entrance starts this late
TITLECARD_BG_GRADIENT = ('0x1a1a2e', '0x0f3460')  # fallback, mirrors CSS

# Location segment of filenames produced by the renamer:
# "2025-07-13 - Blackpool - 09-57-42.jpg" -> "Blackpool"
_LOC_FROM_NAME_RE = re.compile(r'^\d{4}-\d{2}-\d{2} - (.+?) - \d{2}-\d{2}-\d{2}')


def build_titlecard_subtitle(items: list, title: str = '') -> str:
    """Build the auto subtitle for a title card: "Location · N photos · M videos".

    `items` are export media dicts ({'path', 'type', ...}). The location is
    the most common one found in the renamed filenames (deterministic
    tie-break: alphabetical), omitted when absent or already part of the
    title. Mirrored in app.js (_buildTitleCardSubtitle).
    """
    photos = sum(1 for it in items if it.get('type') != 'video')
    videos = sum(1 for it in items if it.get('type') == 'video')
    locs = {}
    for it in items:
        name = os.path.basename(it.get('path', '') or '')
        m = _LOC_FROM_NAME_RE.match(name)
        if m:
            loc = m.group(1).strip()
            if loc:
                locs[loc] = locs.get(loc, 0) + 1
    parts = []
    if locs:
        best = max(sorted(locs), key=lambda k: locs[k])
        if best.lower() not in (title or '').lower():
            parts.append(best)
    if photos:
        parts.append(f"{photos} photo{'s' if photos != 1 else ''}")
    if videos:
        parts.append(f"{videos} video{'s' if videos != 1 else ''}")
    return ' · '.join(parts)


_FFMPEG_MAJOR_CACHE: Dict[str, int] = {}


def _ffmpeg_supports_per_side_box() -> bool:
    """Per-side drawtext boxborderw (top|right|bottom|left) needs
    ffmpeg >= 6. The bundled imageio-ffmpeg is 7.x, but running from source
    can fall back to an older system ffmpeg where the pipe syntax fails the
    drawtext parse and with it the whole export."""
    ffmpeg = get_ffmpeg_path()
    if ffmpeg not in _FFMPEG_MAJOR_CACHE:
        major = 0
        try:
            out = subprocess.run(
                [ffmpeg, '-version'], capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=15,
                creationflags=_subprocess_flags,
            ).stdout or ''
            m = re.search(r'ffmpeg version\s+n?(\d+)', out)
            if m:
                major = int(m.group(1))
        except Exception:
            pass
        _FFMPEG_MAJOR_CACHE[ffmpeg] = major
    return _FFMPEG_MAJOR_CACHE[ffmpeg] >= 6


def _build_titlecard_text_filter(
    text: str, width: int, height: int,
    position: str = 'center',
    subtitle: str = '',
    dark_box: bool = False,
    font_name: Optional[str] = None,
    font_size_override: Optional[int] = None,
    font_color: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
) -> str:
    """drawtext chain for title cards: title (+ optional subtitle).

    Unlike _build_drawtext_filter (photo overlays), the text fades in and
    HOLDS for the whole card — no fade-out, so long cards don't lose their
    text (the old path went blank after 4s on a 5s card). The title rises
    slightly as it fades in; the subtitle follows a beat later. The dark
    box is only drawn when the user asked for it — matching playback,
    which never drew a box by default.
    """
    fade = TITLECARD_TEXT_FADE_S
    rise = TITLECARD_TEXT_RISE
    sub_delay = TITLECARD_SUB_DELAY_S

    if font_size_override and int(font_size_override) > 0:
        title_size = int(font_size_override)
    elif position == 'center':
        title_size = max(32, int(height * 0.06))
    else:
        title_size = max(24, int(height * 0.04))
    sub_size = max(16, int(height * 0.028))

    # y positions for the title / subtitle pair per text position
    if position == 'center':
        # Title sits slightly above centre when a subtitle follows it
        title_y = f'(h-th)/2-{int(height * 0.03)}' if subtitle else '(h-th)/2'
        sub_y = f'(h-th)/2+{int(height * 0.055)}'
    elif position == 'bottom':
        title_y = f'h-th-{int(height * 0.08)}'
        sub_y = f'h-th-{int(height * 0.045)}'
    else:  # top
        title_y = str(int(height * 0.06))
        sub_y = str(int(height * 0.06 + title_size * 1.35))

    # Rise: text drifts up `rise` px while fading in, then holds still
    rise_expr = f'+{rise}*(1-min(t/{fade}\\,1))'
    title_alpha = f"if(lt(t\\,{fade})\\,t/{fade}\\,1)"
    sub_alpha = (
        f"0.9*if(lt(t\\,{sub_delay})\\,0\\,"
        f"if(lt(t\\,{sub_delay + fade})\\,(t-{sub_delay})/{fade}\\,1))"
    )

    if dark_box:
        pad = int(title_size * 0.8)
        if subtitle and _ffmpeg_supports_per_side_box():
            # One box around BOTH lines: extend the title's box downward
            # past the subtitle with per-side borders (top|right|bottom|left,
            # ffmpeg >= 6). The subtitle is then drawn shadow-only on top of
            # the extended box - giving it its own translucent box instead
            # would double-darken wherever the two boxes cross, and a box
            # around the title alone sliced straight through the subtitle.
            # Text heights are estimated (drawtext's th isn't known here);
            # the padding absorbs the estimate error.
            th_t = int(title_size * 1.2)
            th_s = int(sub_size * 1.2)
            if position == 'center':
                title_y_px = (height - th_t) / 2 - height * 0.03
                sub_y_px = (height - th_s) / 2 + height * 0.055
            elif position == 'bottom':
                title_y_px = height - th_t - height * 0.08
                sub_y_px = height - th_s - height * 0.045
            else:
                title_y_px = height * 0.06
                sub_y_px = height * 0.06 + title_size * 1.35
            bottom = int(sub_y_px + th_s + sub_size * 0.9 - (title_y_px + th_t))
            bottom = max(pad, bottom)
            # The box hugs the TITLE's width, so a subtitle wider than the
            # title would poke out the sides. Estimated glyph widths decide
            # how much wider the side borders must be - biased so the only
            # failure mode is a slightly roomy box, never a sliced subtitle.
            title_w_low = len(text) * title_size * 0.42
            sub_w_high = len(subtitle) * sub_size * 0.65
            side = max(pad, int((sub_w_high - title_w_low) / 2 + pad))
            box_args = f":box=1:boxcolor=black@0.7:boxborderw={pad}|{side}|{bottom}|{side}"
        else:
            box_args = f":box=1:boxcolor=black@0.7:boxborderw={pad}"
    else:
        box_args = ":shadowcolor=black@0.6:shadowx=0:shadowy=2"

    fg_color = _normalize_color(font_color, 'white')
    font_file = _resolve_font_file(font_name, bold=bold, italic=italic)
    fontfile_expr = f":fontfile='{_escape_drawtext_path(font_file)}'" if font_file else ''

    chain = (
        f"drawtext=text='{_escape_drawtext_text(text)}'"
        f"{fontfile_expr}"
        f":fontsize={title_size}"
        f":fontcolor={fg_color}"
        f":x=(w-tw)/2"
        f":y={title_y}{rise_expr}"
        f":alpha='{title_alpha}'"
        f"{box_args}"
    )
    if subtitle:
        sub_font = _resolve_font_file(font_name, bold=False, italic=italic)
        sub_fontfile = f":fontfile='{_escape_drawtext_path(sub_font)}'" if sub_font else ''
        chain += (
            f",drawtext=text='{_escape_drawtext_text(subtitle)}'"
            f"{sub_fontfile}"
            f":fontsize={sub_size}"
            f":fontcolor={fg_color}"
            f":x=(w-tw)/2"
            f":y={sub_y}{rise_expr}"
            f":alpha='{sub_alpha}'"
            f":shadowcolor=black@0.6:shadowx=0:shadowy=2"
        )
    return chain


def _titlecard_bg_filter(width: int, height: int, fps: int, duration: float) -> str:
    """Filter chain for a title card's auto photo background.

    Cover-crop (fill the frame, no letterboxing — the blur hides any
    composition loss), heavy blur + darken so the text stays readable,
    then the standard Ken Burns drift (variant 0: slow zoom in, centred —
    fixed variant keeps output deterministic). CSS mirror: .title-card-bg.
    """
    cover = (f'scale={width}:{height}:force_original_aspect_ratio=increase,'
             f'crop={width}:{height},setsar=1')
    soften = 'boxblur=luma_radius=6:luma_power=2:chroma_radius=3:chroma_power=1,eq=brightness=-0.18:saturation=0.9'
    return cover + ',' + soften + ',' + _kenburns_filter(0, width, height, fps, duration)


def _extract_video_frame(ffmpeg: str, video_path: str, out_jpg: str,
                         start: float = 0.0) -> Optional[str]:
    """Grab one frame from a video for use as a title card background.
    Returns the jpg path, or None if extraction failed (caller falls back
    to the gradient background).

    `start` is the clip's trim in-point, so a trimmed clip backs its day's
    title card with a frame the viewer will actually see rather than one
    from the discarded head."""
    try:
        _run_ffmpeg([ffmpeg, '-y', '-ss', f'{max(0.0, start) + 0.5:.3f}', '-i', video_path,
                     '-vf', DEINT_FILTER,
                     '-frames:v', '1', '-q:v', '3', out_jpg], timeout=60)
    except ExportCancelled:
        raise
    except Exception as e:
        logger.warning(f"Title card frame extraction failed for {video_path}: {e}")
        return None
    return out_jpg if os.path.isfile(out_jpg) else None


def _render_title_card_segment(
    ffmpeg: str, out_path: str, *,
    width: int, height: int, fps: int, duration: float,
    video_codec: str, crf: int, audio_br: str,
    text: str = '', subtitle: str = '', position: str = 'center',
    dark_box: bool = False, font_kwargs: Optional[Dict] = None,
    image_path: Optional[str] = None,
    bg_photo_path: Optional[str] = None,
    encoder: Optional['EncoderChoice'] = None,
) -> bool:
    """Render one title/end card segment. Single implementation for all
    card types (custom slideshow first/last, day-boundary, end card).

    Background priority:
      1. `image_path`  — user-chosen image, letterboxed, NOT blurred
      2. `bg_photo_path` — auto-picked photo/frame: blurred + darkened + Ken Burns
      3. dark gradient (matches the playback CSS gradient)
    `encoder` is the export's EncoderChoice (hardware with software
    fallback); without one the card encodes in software.
    Returns True if the segment file exists afterwards.
    """
    enc = encoder or EncoderChoice.software_only(video_codec, crf)

    def tail_for(codec_args):
        return codec_args + [
            '-r', str(fps),
            '-c:a', 'aac', '-b:a', audio_br,
            '-ar', '48000', '-ac', '2',
            '-shortest', out_path,
        ]
    tail = tail_for(enc.args())

    def run(cmd):
        # cmd was built with the current encoder's tail; rebuild the tail
        # for whichever encoder run_encode ends up using
        head = cmd[:len(cmd) - len(tail)]
        run_encode(lambda codec_args: head + tail_for(codec_args), enc)
    text_part = ''
    if text or subtitle:
        text_part = ',' + _build_titlecard_text_filter(
            text or ' ', width, height, position=position,
            subtitle=subtitle, dark_box=dark_box, **(font_kwargs or {})
        )

    audio_in = ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    if image_path and os.path.isfile(image_path):
        # setsar=1 is critical for every branch — without it, xfade/concat
        # chains silently break (see the "only first slide shown" bug).
        # User images drift too (same Ken Burns variant as the auto bg),
        # just without the blur.
        vf = (f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
              f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,'
              + _kenburns_filter(0, width, height, fps, duration))
        cmd = [ffmpeg, '-y', '-loop', '1', '-i', image_path] + audio_in + [
            '-t', str(duration), '-vf', vf + text_part] + tail
        run(cmd)
    elif bg_photo_path and os.path.isfile(bg_photo_path):
        vf = _titlecard_bg_filter(width, height, fps, duration)
        cmd = [ffmpeg, '-y', '-loop', '1', '-i', bg_photo_path] + audio_in + [
            '-t', str(duration), '-vf', vf + text_part] + tail
        run(cmd)
    else:
        c0, c1 = TITLECARD_BG_GRADIENT
        vf = f'scale={width}:{height},setsar=1'
        grad_cmd = [ffmpeg, '-y', '-f', 'lavfi', '-i',
                    f'gradients=s={width}x{height}:c0={c0}:c1={c1}'
                    f':x0=0:y0=0:x1={width}:y1={height}:speed=0.00001:r={fps}',
                    ] + audio_in + ['-t', str(duration), '-vf', vf + text_part] + tail
        try:
            run(grad_cmd)
        except ExportCancelled:
            raise
        except Exception:
            # Older ffmpeg without the gradients source — flat colour fallback
            logger.warning("gradients lavfi source unavailable, using flat colour title card")
            flat_cmd = [ffmpeg, '-y', '-f', 'lavfi', '-i',
                        f'color=c={c0}:s={width}x{height}:r={fps}',
                        ] + audio_in + ['-t', str(duration), '-vf', vf + text_part] + tail
            run(flat_cmd)
    return os.path.isfile(out_path)


def _run_ffmpeg(cmd: list, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run an ffmpeg command, raising on failure with detailed errors.
    Returns the CompletedProcess, for callers that read ffmpeg's report
    (a filter's summary on stderr, e.g. loudnorm's measurement).

    Honors the export cancel flag: raises ExportCancelled if a cancel was
    requested before the command starts, and kills + raises if the active
    process is cancelled mid-run (via request_export_cancel).
    """
    global _active_proc
    logger.debug(f"Running: {' '.join(cmd[:6])}...")
    # Spawn AND register under the lock, with a cancel check inside it —
    # otherwise a cancel landing between Popen() and registration would
    # kill nothing and the segment would render to completion.
    with _active_proc_lock:
        if _cancel_event.is_set():
            raise ExportCancelled('Export cancelled')
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', errors='replace',
                creationflags=_render_flags
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                f"ffmpeg could not be found. "
                "Please reinstall the app or contact support at "
                "https://www.bacommander.com/speedy-slideshow-25-support"
            )
        _active_proc = proc
    try:
        try:
            _stdout, stderr_text = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            raise FfmpegTimeout(
                f"ffmpeg timed out after {timeout}s. "
                "Try reducing the number of media items or resolution."
            )
    finally:
        with _active_proc_lock:
            _active_proc = None

    if _cancel_event.is_set():
        raise ExportCancelled('Export cancelled')

    result = subprocess.CompletedProcess(cmd, proc.returncode, stdout=_stdout, stderr=stderr_text)
    if result.returncode != 0:
        # Extract the most useful part of stderr
        stderr = result.stderr.strip()
        # Look for the last meaningful error line
        lines = stderr.split('\n')
        error_lines = [l for l in lines if l.strip() and not l.strip().startswith('frame=')]
        short_err = error_lines[-1] if error_lines else stderr[-300:]
        logger.error(f"ffmpeg error (exit {result.returncode}): {stderr[-800:]}")
        raise RuntimeError(f"ffmpeg error: {short_err}")
    return result


# The encoder position in ffmpeg's periodic stats lines ("time=00:01:23.45")
_FFMPEG_TIME_RE = re.compile(r'time=(\d+):(\d{2}):(\d{2}(?:\.\d+)?)')


def _run_ffmpeg_streaming(cmd: list, timeout: int = 300,
                          total_seconds: Optional[float] = None,
                          on_progress: Optional[Callable] = None):
    """Like _run_ffmpeg, but reads stderr as it arrives and reports the
    encoder's position via on_progress(fraction 0..1).

    Exists because _run_ffmpeg blocks in communicate(): a single long encode
    (a multi-GB clip in a chain export) gives no sign of life for minutes,
    so the UI's progress bar froze mid-number. Same cancel + timeout + error
    semantics as _run_ffmpeg; a watchdog timer replaces communicate(timeout)
    since a streaming read has no built-in deadline.
    """
    global _active_proc
    logger.debug(f"Running (streaming): {' '.join(cmd[:6])}...")
    with _active_proc_lock:
        if _cancel_event.is_set():
            raise ExportCancelled('Export cancelled')
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', errors='replace',
                creationflags=_render_flags
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                f"ffmpeg could not be found. "
                "Please reinstall the app or contact support at "
                "https://www.bacommander.com/speedy-slideshow-25-support"
            )
        _active_proc = proc

    timed_out = threading.Event()

    def _kill_on_timeout():
        timed_out.set()
        try:
            proc.kill()
        except Exception:
            pass

    watchdog = threading.Timer(timeout, _kill_on_timeout)
    watchdog.daemon = True
    watchdog.start()

    tail = []  # last stderr lines, for error reporting
    try:
        # text=True enables universal newlines, so ffmpeg's \r-terminated
        # stats lines arrive as ordinary lines here
        for line in proc.stderr:
            tail.append(line)
            if len(tail) > 80:
                del tail[:40]
            if on_progress and total_seconds and total_seconds > 0:
                m = _FFMPEG_TIME_RE.search(line)
                if m:
                    secs = (int(m.group(1)) * 3600 + int(m.group(2)) * 60
                            + float(m.group(3)))
                    try:
                        on_progress(min(1.0, secs / total_seconds))
                    except Exception:
                        pass
        proc.wait()
    finally:
        watchdog.cancel()
        with _active_proc_lock:
            _active_proc = None

    if timed_out.is_set():
        raise FfmpegTimeout(
            f"ffmpeg timed out after {timeout}s. "
            "Try reducing the number of media items or resolution."
        )
    if _cancel_event.is_set():
        raise ExportCancelled('Export cancelled')
    if proc.returncode != 0:
        stderr = ''.join(tail).strip()
        lines = stderr.split('\n')
        error_lines = [l for l in lines if l.strip() and not l.strip().startswith('frame=')]
        short_err = error_lines[-1] if error_lines else stderr[-300:]
        logger.error(f"ffmpeg error (exit {proc.returncode}): {stderr[-800:]}")
        raise RuntimeError(f"ffmpeg error: {short_err}")


def _has_audio_stream(ffmpeg: str, filepath: str) -> bool:
    """Check if a media file contains an audio stream.

    Prefers ffprobe, but the bundled imageio-ffmpeg ships without it -
    in that case parse ffmpeg's own stream listing instead of assuming
    True, which made silent videos skip the silent-track branch and
    later abort the export ("Stream specifier ':a' matches no streams").
    """
    ffprobe = ffmpeg.replace('ffmpeg', 'ffprobe')
    if not os.path.isfile(ffprobe):
        ffprobe = get_ffprobe_path()
    if not os.path.isfile(ffprobe):
        ffprobe = shutil.which(ffprobe)

    if ffprobe:
        try:
            result = subprocess.run(
                [ffprobe, '-v', 'quiet', '-select_streams', 'a',
                 '-show_entries', 'stream=codec_type', '-of', 'csv=p=0',
                 filepath],
                capture_output=True, text=True, encoding='utf-8',
                errors='replace', timeout=10,
                creationflags=_subprocess_flags
            )
            return 'audio' in result.stdout
        except Exception:
            pass  # Fall through to the ffmpeg-based check

    # `ffmpeg -i file` exits non-zero (no output requested) but prints
    # "Stream #0:N ... Audio: ..." to stderr for each audio stream.
    try:
        result = subprocess.run(
            [ffmpeg, '-hide_banner', '-i', filepath],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=15,
            creationflags=_subprocess_flags
        )
        if 'Stream #' not in result.stderr:
            # ffmpeg couldn't read any stream info (odd container the
            # export pass may still handle) - keep the conservative
            # assumption rather than silently stripping real audio
            return True
        return 'Audio:' in result.stderr
    except Exception:
        return True  # Assume audio exists if we can't check


def write_concat_list(list_file: str, paths) -> None:
    """Write an ffmpeg concat-demuxer list file.

    ffmpeg reads the list as UTF-8, and a single quote inside a quoted
    path must be escaped as '\\'' - paths routinely include the user's
    temp dir, so an apostrophe or non-ASCII Windows username otherwise
    breaks the concat parse. Backslashes are normalised to '/' (accepted
    by the demuxer on Windows and avoids escape ambiguity).
    """
    with open(list_file, 'w', encoding='utf-8') as f:
        for p in paths:
            escaped = str(p).replace('\\', '/').replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")


def _concat_simple(
    ffmpeg: str, segments: list, tmpdir: str,
    output_path: str, format: str,
    progress_callback=None
) -> str:
    """Concatenate segments using the concat demuxer (no transitions)."""
    list_file = os.path.join(tmpdir, 'segments.txt')
    write_concat_list(list_file, segments)

    if progress_callback:
        progress_callback(80, 'Concatenating segments...')

    if format == 'avi':
        cmd = [
            ffmpeg, '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c:v', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-c:a', 'pcm_s16le',
            output_path
        ]
    else:
        cmd = [
            ffmpeg, '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            output_path
        ]

    _run_ffmpeg(cmd, timeout=600)
    return output_path


def _concat_with_crossfade(
    ffmpeg: str, segments: list, tmpdir: str,
    output_path: str, width: int, height: int,
    fps: int, format: str, xfade_dur: float,
    progress_callback=None, xfade_transition: str = 'fade',
    video_codec: str = 'libx264', crf: int = 18, audio_br: str = '192k',
    segment_durations: Optional[List[float]] = None,
    encoder: Optional['EncoderChoice'] = None,
) -> str:
    """
    Concatenate segments with xfade transitions using xfade filter.
    For large numbers of segments, we chain in batches to avoid
    overly complex filter graphs.

    segment_durations is the caller's known-good list of durations for each
    segment. If omitted, _xfade_pass will probe each file with ffprobe (which
    is unreliable when ffprobe is not on the system).
    """
    if len(segments) <= 1:
        shutil.copy2(segments[0], output_path)
        return output_path

    # For manageable numbers (<=20), do it in one pass
    # For larger counts, batch them
    if len(segments) <= 20:
        return _xfade_pass(ffmpeg, segments, tmpdir, output_path,
                           format, xfade_dur, progress_callback, 75,
                           xfade_transition, video_codec, crf, audio_br,
                           segment_durations=segment_durations, encoder=encoder)
    else:
        # Batch into groups of 15, crossfade each batch, then crossfade the results
        batch_size = 15
        batch_outputs = []
        batch_out_durations = []
        for batch_start in range(0, len(segments), batch_size):
            batch = segments[batch_start:batch_start + batch_size]
            batch_durs = (segment_durations[batch_start:batch_start + batch_size]
                          if segment_durations else None)
            batch_out = os.path.join(tmpdir, f'batch_{batch_start:04d}.mp4')
            pct = 70 + int((batch_start / len(segments)) * 20)
            if progress_callback:
                progress_callback(pct, f'Processing batch {len(batch_outputs)+1}...')
            _xfade_pass(ffmpeg, batch, tmpdir, batch_out, 'mp4', xfade_dur,
                        None, 0, xfade_transition, video_codec, crf, audio_br,
                        segment_durations=batch_durs, encoder=encoder)
            if os.path.isfile(batch_out):
                batch_outputs.append(batch_out)
                # Batch length must use the same clamped per-boundary xfade
                # math as _xfade_pass, or short clips throw off the join pass
                if batch_durs:
                    _, _, batch_total = _xfade_timeline(batch_durs, xfade_dur)
                    batch_out_durations.append(batch_total)

        if len(batch_outputs) == 1:
            shutil.copy2(batch_outputs[0], output_path)
            return output_path

        if progress_callback:
            progress_callback(92, 'Joining batches...')

        return _xfade_pass(ffmpeg, batch_outputs, tmpdir, output_path,
                           format, xfade_dur, None, 0, xfade_transition,
                           video_codec, crf, audio_br,
                           segment_durations=(batch_out_durations or None),
                           encoder=encoder)


def _build_duck_intervals(segment_durations: List[float],
                          segment_is_video: List[bool],
                          transition_duration: Optional[float] = None):
    """(start, end) spans where background music should dip for a clip.

    Mirrors the playback fade. Segment start times come from the same
    clamped xfade timeline the video concat used, so the dips line up
    exactly; pass `transition_duration=None` for a cut concat, where
    segments simply abut.

    Returns None when nothing is worth ducking.
    """
    if transition_duration is not None and len(segment_durations) > 1:
        offsets, _eff, _tot = _xfade_timeline(segment_durations, transition_duration)
    else:
        offsets = []
        acc = 0.0
        for d in segment_durations:
            offsets.append(acc)
            acc += d

    merged = []
    for i, isv in enumerate(segment_is_video):
        if not isv:
            continue
        a, b = offsets[i], offsets[i] + segment_durations[i]
        if b - a < MUSIC_DUCK_FADE_S * 2:
            continue  # blink-length clip: a dip reads as a glitch
        if merged and a - merged[-1][1] < MUSIC_DUCK_FADE_S * 2:
            merged[-1] = (merged[-1][0], b)  # back-to-back videos: one dip
        else:
            merged.append((a, b))
    return merged or None


def _xfade_timeline(durations: List[float], xfade_dur: float):
    """Compute xfade offsets with per-boundary clamping.

    Returns (offsets, eff_xfades, total_duration) where offsets[i] is the
    start time of segment i in the final output, eff_xfades[i-1] is the
    clamped transition duration at the boundary into segment i, and
    total_duration is the length of the crossfaded output.

    The effective xfade at each boundary is clamped so it never exceeds the
    previous segment's duration; the clamped value is what accumulates into
    later offsets (using the nominal xfade_dur would drift every subsequent
    transition and the audio track).
    """
    offsets = [0.0]
    eff_xfades = []
    for i in range(1, len(durations)):
        prev_dur = durations[i - 1]
        eff = min(xfade_dur, max(0.1, prev_dur - 0.1))
        eff_xfades.append(eff)
        offsets.append(max(offsets[i - 1], offsets[i - 1] + prev_dur - eff))
    total = offsets[-1] + durations[-1] if durations else 0.0
    return offsets, eff_xfades, total


def _xfade_pass(
    ffmpeg: str, segments: list, tmpdir: str,
    output_path: str, format: str, xfade_dur: float,
    progress_callback=None, base_pct: int = 0,
    xfade_transition: str = 'fade',
    video_codec: str = 'libx264', crf: int = 18, audio_br: str = '192k',
    segment_durations: Optional[List[float]] = None,
    encoder: Optional['EncoderChoice'] = None,
) -> str:
    """Apply xfade between a list of segments.

    If segment_durations is provided the caller's known-good durations are
    used verbatim. Otherwise we fall back to probing with ffprobe, which is
    unreliable when ffprobe is not installed alongside ffmpeg (e.g. when
    using the imageio-ffmpeg bundle).
    """
    if len(segments) == 1:
        shutil.copy2(segments[0], output_path)
        return output_path

    # Build the xfade filter chain
    inputs = []
    for seg in segments:
        inputs.extend(['-i', seg])

    # Prefer caller-supplied durations over ffprobe. When ffprobe isn't
    # available (e.g. an imageio-ffmpeg-only install) get_video_duration
    # returns None; we use a conservative per-segment fallback (5s) so
    # the math at least has finite numbers, but the xfade offsets will
    # be wrong. The render still completes - the user just gets a video
    # with mistimed transitions rather than a hard failure.
    if segment_durations and len(segment_durations) == len(segments):
        durations = [float(d) for d in segment_durations]
    else:
        durations = []
        for seg in segments:
            d = get_video_duration(seg)
            durations.append(d if d is not None else 5.0)
    logger.info(
        f"xfade pass: {len(segments)} segments, durations (s) = "
        f"{[round(d, 2) for d in durations]}, xfade_dur = {xfade_dur}"
    )

    # Compute per-boundary xfade durations and cumulative offsets. Each
    # boundary's effective xfade is clamped to the previous segment's
    # duration, and the clamped value (NOT the nominal xfade_dur) is
    # accumulated into every later offset — otherwise one short clip
    # desyncs every subsequent transition and the audio track.
    offsets, eff_xfades, _total = _xfade_timeline(durations, xfade_dur)
    for i in range(1, len(segments)):
        if durations[i - 1] <= xfade_dur:
            logger.warning(
                f"Segment {i-1} duration ({durations[i-1]:.2f}s) is <= xfade "
                f"duration ({xfade_dur:.2f}s); clamping xfade for this boundary."
            )

    # Build xfade filter chain. 'mix' rotates through MIX_SEQUENCE per
    # boundary; anything else is a literal xfade name from XFADE_TRANSITIONS.
    filter_parts = []
    prev_label = '[0:v]'

    for i in range(1, len(segments)):
        next_label = f'[{i}:v]'
        out_label = f'[v{i}]' if i < len(segments) - 1 else '[vout]'

        if xfade_transition == 'mix':
            style = MIX_SEQUENCE[(i - 1) % len(MIX_SEQUENCE)]
        else:
            style = xfade_transition

        filter_parts.append(
            f'{prev_label}{next_label}xfade=transition={style}:duration={eff_xfades[i-1]:.3f}:offset={offsets[i]:.3f}{out_label}'
        )
        prev_label = out_label

    filter_complex = ';'.join(filter_parts)

    # Handle audio: position each segment's audio at the exact time offset
    # that matches the video xfade timing, then mix them together.
    # Simple concat causes audio drift because video xfade shortens the
    # output by xfade_dur per transition, but concat keeps full audio length.
    # Using adelay+amix ensures perfect audio/video sync.
    audio_filter = ''
    if len(segments) > 1:
        audio_parts = []
        for i in range(len(segments)):
            # Each segment starts at the same clamped offset the video uses
            delay_ms = max(0, int(offsets[i] * 1000))

            if delay_ms > 0:
                audio_parts.append(
                    f'[{i}:a]adelay={delay_ms}|{delay_ms},apad=whole_dur=0[ad{i}]'
                )
            else:
                audio_parts.append(f'[{i}:a]acopy[ad{i}]')

        mix_inputs = ''.join(f'[ad{i}]' for i in range(len(segments)))
        audio_parts.append(
            f'{mix_inputs}amix=inputs={len(segments)}:duration=longest:normalize=0[aout]'
        )
        audio_filter = ';' + ';'.join(audio_parts)

    full_filter = filter_complex + audio_filter

    enc = encoder or EncoderChoice.software_only(video_codec, crf)

    def xfade_cmd(codec_args):
        if format == 'avi':
            output_args = ['-c:v', 'rawvideo', '-pix_fmt', 'bgr24',
                           '-c:a', 'pcm_s16le']
        else:
            output_args = codec_args + ['-c:a', 'aac', '-b:a', audio_br]
        cmd = [ffmpeg, '-y'] + inputs
        if audio_filter:
            cmd += ['-filter_complex', full_filter, '-map', '[vout]', '-map', '[aout]']
        else:
            cmd += ['-filter_complex', full_filter, '-map', '[vout]']
        return cmd + output_args + [output_path]

    run_encode(xfade_cmd, enc, runner=lambda c: _run_ffmpeg(c, timeout=1200))
    return output_path


def _get_video_stream_duration(ffmpeg: str, filepath: str) -> float:
    """Get duration of the video stream specifically (not audio or container)."""
    try:
        ffprobe = ffmpeg.replace('ffmpeg', 'ffprobe')
        if not os.path.isfile(ffprobe):
            ffprobe = get_ffprobe_path()
        result = subprocess.run(
            [ffprobe, '-v', 'quiet', '-select_streams', 'v:0',
             '-show_entries', 'stream=duration',
             '-of', 'json', filepath],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=30,
            creationflags=_subprocess_flags
        )
        data = json.loads(result.stdout)
        streams = data.get('streams', [])
        if streams and 'duration' in streams[0]:
            return float(streams[0]['duration'])
    except Exception as e:
        logger.warning(f"Could not get video stream duration for {filepath}: {e}")
    return 0.0


def _build_music_track(
    ffmpeg: str,
    music_paths: List[str],
    tmpdir: str,
    video_dur: float,
    track_crossfade: float = 2.0,
    music_volume: float = 0.5,
    audio_br: str = '192k',
    warnings_out: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Build a single continuous music track from a playlist of audio files.
    Tracks crossfade into each other. If the playlist is shorter than the
    video, it loops back to the first track and repeats.
    Returns path to the combined music file, or None on failure.

    If ``warnings_out`` is a list, user-visible warnings (e.g. "a batch
    of tracks failed to crossfade") are appended to it. The export still
    succeeds - the user just gets fewer tracks than they asked for -
    but now the UI can tell them why.
    """
    if not music_paths:
        return None

    def _warn(msg: str) -> None:
        """Append a warning for the user AND log it at warning level."""
        logger.warning(msg)
        if warnings_out is not None:
            warnings_out.append(msg)

    xfade_dur = max(0, min(5.0, track_crossfade))

    # Get durations of all tracks. None means we couldn't probe; surface
    # that as a warning and fall back to a 60s estimate so the loop math
    # has finite numbers. Better than the old behaviour which silently
    # used 5s for every unprobeable track.
    track_durations = []
    unprobeable = []
    for p in music_paths:
        d = get_video_duration(p)
        if d is None or d <= 0:
            unprobeable.append(os.path.basename(p))
            d = 60.0  # fallback
        track_durations.append(d)
    if unprobeable:
        names = ', '.join(unprobeable[:3])
        more = '' if len(unprobeable) <= 3 else f' (+{len(unprobeable) - 3} more)'
        _warn(
            f"Couldn't measure duration of {len(unprobeable)} music track(s) - "
            f"used 60s as a fallback for each: {names}{more}. "
            f"Music timing in the output may be inaccurate."
        )

    # Calculate how long one full pass through the playlist is (accounting for crossfades)
    def playlist_duration(n_tracks):
        """Duration of n_tracks from the playlist with crossfades."""
        if n_tracks <= 0:
            return 0
        total = sum(track_durations[i % len(music_paths)] for i in range(n_tracks))
        if n_tracks > 1 and xfade_dur > 0:
            total -= xfade_dur * (n_tracks - 1)
        return total

    # Figure out how many tracks we need to cover the video duration
    # Build the ordered list, looping the playlist as needed
    ordered_paths = []
    ordered_durations = []
    accumulated = 0
    idx = 0
    while accumulated < video_dur + 10:  # +10s buffer
        track_path = music_paths[idx % len(music_paths)]
        track_dur = track_durations[idx % len(music_paths)]
        ordered_paths.append(track_path)
        ordered_durations.append(track_dur)
        accumulated += track_dur
        if idx > 0 and xfade_dur > 0:
            accumulated -= xfade_dur
        idx += 1
        # Safety limit: 200 tracks max
        if idx >= 200:
            break

    logger.info(f"Music playlist: {len(ordered_paths)} tracks needed for {video_dur:.1f}s video "
                f"(from {len(music_paths)} unique tracks, crossfade={xfade_dur}s)")

    # If only one track instance, just return it directly (caller handles looping/trim)
    if len(ordered_paths) == 1:
        return ordered_paths[0]

    # If no crossfade, use simple concat
    if xfade_dur <= 0:
        list_file = os.path.join(tmpdir, 'music_concat.txt')
        write_concat_list(list_file, ordered_paths)
        # AAC audio needs an MP4-family container - the mp3 muxer rejects
        # AAC streams outright, which used to fail every playlist merge
        combined = os.path.join(tmpdir, 'music_combined.m4a')
        cmd = [
            ffmpeg, '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c:a', 'aac', '-b:a', audio_br,
            combined
        ]
        try:
            _run_ffmpeg(cmd, timeout=300)
            if os.path.isfile(combined):
                return combined
            _warn(
                f"Music concat produced no output (expected {combined}). "
                f"Used only the first track of {len(music_paths)} in the playlist."
            )
            return ordered_paths[0]
        except Exception as e:
            _warn(
                f"Music concat failed for playlist of {len(music_paths)} tracks - "
                f"only the first track was used. ffmpeg said: {str(e)[:160]}"
            )
            return ordered_paths[0]

    # With crossfade: use acrossfade filter chain
    # Process in batches of ~10 to avoid overly complex filter graphs
    batch_size = 10

    def _crossfade_batch(paths, durations, batch_label=''):
        """Crossfade a batch of audio files together."""
        if len(paths) == 1:
            return paths[0]

        inputs = []
        for p in paths:
            inputs.extend(['-i', p])

        # Build acrossfade filter chain
        filter_parts = []
        prev_label = '[0:a]'

        for i in range(1, len(paths)):
            next_label = f'[{i}:a]'
            out_label = f'[a{i}]' if i < len(paths) - 1 else '[aout]'
            # acrossfade crossfades between two audio streams
            cf_dur = min(xfade_dur, durations[i - 1] * 0.4, durations[i] * 0.4)
            filter_parts.append(
                f'{prev_label}{next_label}acrossfade=d={cf_dur:.2f}:c1=tri:c2=tri{out_label}'
            )
            prev_label = out_label

        filter_complex = ';'.join(filter_parts)
        # .m4a container: these batches are AAC-encoded (see mp3-muxer note above)
        out_path = os.path.join(tmpdir, f'music_batch{batch_label}.m4a')

        cmd = [ffmpeg, '-y'] + inputs + [
            '-filter_complex', filter_complex,
            '-map', '[aout]',
            '-c:a', 'aac', '-b:a', audio_br,
            out_path
        ]
        _run_ffmpeg(cmd, timeout=300)
        return out_path

    # Process in batches
    try:
        remaining_paths = ordered_paths[:]
        remaining_durs = ordered_durations[:]
        batch_idx = 0

        while len(remaining_paths) > 1:
            batch_outputs = []
            batch_out_durs = []

            for start in range(0, len(remaining_paths), batch_size):
                batch_p = remaining_paths[start:start + batch_size]
                batch_d = remaining_durs[start:start + batch_size]

                if len(batch_p) == 1:
                    batch_outputs.append(batch_p[0])
                    batch_out_durs.append(batch_d[0])
                else:
                    try:
                        out = _crossfade_batch(batch_p, batch_d, f'_{batch_idx}')
                    except Exception as e:
                        # _run_ffmpeg raises RuntimeError with the ffmpeg
                        # stderr tail. Surface it so the user can see why
                        # their playlist was trimmed.
                        out = ''
                        _warn(
                            f"Music crossfade failed for a batch of "
                            f"{len(batch_p)} tracks - they were replaced "
                            f"by their first track. ffmpeg said: {str(e)[:160]}"
                        )
                    batch_idx += 1
                    if out and os.path.isfile(out):
                        # Calculate output duration
                        out_dur = sum(batch_d) - xfade_dur * (len(batch_d) - 1)
                        batch_outputs.append(out)
                        batch_out_durs.append(out_dur)
                    else:
                        # Fallback: just use first track. If we didn't
                        # already warn above, warn now for the silent
                        # "file never appeared" case.
                        if out:
                            _warn(
                                f"Music crossfade produced no output for a "
                                f"batch of {len(batch_p)} tracks - they "
                                f"were replaced by their first track."
                            )
                        batch_outputs.append(batch_p[0])
                        batch_out_durs.append(batch_d[0])

            remaining_paths = batch_outputs
            remaining_durs = batch_out_durs

        if remaining_paths and os.path.isfile(remaining_paths[0]):
            return remaining_paths[0]
    except Exception as e:
        _warn(
            f"Music crossfade assembly failed - used only the first "
            f"track of {len(music_paths)}. Error: {str(e)[:160]}"
        )

    return ordered_paths[0]  # Fallback: just use first track


def _mix_background_music(
    ffmpeg: str,
    video_path: str,
    music_paths: List[str],
    tmpdir: str,
    output_path: str,
    format: str = 'mp4',
    music_volume: float = 0.5,
    video_volume: float = 1.0,
    fade_out: bool = True,
    fade_duration: float = 3.0,
    video_duration: float = 0.0,
    audio_br: str = '192k',
    track_crossfade: float = 2.0,
    duck_intervals: Optional[List[tuple]] = None,
    warnings_out: Optional[List[str]] = None,
) -> str:
    """
    Mix a multi-track music playlist into the exported video.
    Tracks crossfade into each other and the playlist loops if the video
    is longer than all tracks combined.
    Optionally fades out the music in the last N seconds (configurable).
    Returns the path to the final output file.

    If ``warnings_out`` is a list, user-visible warnings about dropped /
    failed tracks are appended to it. The export still succeeds - only
    the music content degrades - but the UI can now tell the user that
    not all of their tracks made it into the output.
    """

    def _warn(msg: str) -> None:
        logger.warning(msg)
        if warnings_out is not None:
            warnings_out.append(msg)

    video_dur = video_duration if video_duration > 0 else 0
    if video_dur <= 0:
        # get_video_duration returns Optional[float]; coerce None to 0
        # so the next guard fires correctly. Previously the function
        # returned a bogus 5.0s on failure which bypassed this guard
        # and produced a 5-second music track for a 60-minute video.
        video_dur = get_video_duration(video_path) or 0
    if video_dur <= 0:
        _warn("Could not determine video duration, so the exported video "
              "has no background music. (ffprobe failed.)")
        return video_path
    logger.info(f"Music mix: using video_dur={video_dur:.1f}s, {len(music_paths)} track(s)")

    fade_dur = max(1.0, min(5.0, fade_duration))  # clamp 1-5s
    fade_start = max(0, video_dur - fade_dur)

    # Build the combined music track from the playlist.
    # Any warnings from the builder are appended to the same list so
    # they surface alongside mix-phase warnings in the final UI card.
    combined_music = _build_music_track(
        ffmpeg, music_paths, tmpdir, video_dur,
        track_crossfade=track_crossfade,
        music_volume=music_volume,
        audio_br=audio_br,
        warnings_out=warnings_out,
    )

    if not combined_music or not os.path.isfile(combined_music):
        _warn("Could not build a combined music track; the exported video "
              "has no background music.")
        return video_path

    # If the combined track is still shorter than the video (e.g. single track),
    # use -stream_loop to repeat it. If we can't probe the music duration
    # we skip looping - playing the music once is better than looping it
    # an arbitrary number of times based on a wrong duration estimate.
    music_dur = get_video_duration(combined_music)
    loop_count = 0
    if music_dur is not None and music_dur > 0 and music_dur < video_dur:
        loop_count = int(video_dur / music_dur) + 1

    # Video audio: trim to video stream duration and adjust volume
    va_filter = f'[0:a]atrim=0:{video_dur:.3f},asetpts=PTS-STARTPTS,volume={video_volume:.2f}[va]'

    # Music audio: trim to video length, normalize loudness (so tracks from
    # different albums behave the same under the volume slider), adjust
    # volume, optional fade
    ma_filter = (f'[1:a]atrim=0:{video_dur:.3f},asetpts=PTS-STARTPTS,'
                 f'{LOUDNORM_FILTER},volume={music_volume:.2f}')
    if duck_intervals:
        # Dip to silence while video clips play, mirroring live playback
        duck_expr = build_duck_volume_expr(duck_intervals)
        ma_filter += f",volume=volume='{duck_expr}':eval=frame"
    if fade_out and video_dur > fade_dur:
        ma_filter += f',afade=t=out:st={fade_start:.3f}:d={fade_dur:.1f}'
    ma_filter += '[ma]'

    filter_complex = f'{va_filter};{ma_filter};[va][ma]amix=inputs=2:duration=first:dropout_transition=0[aout]'

    mixed_path = os.path.join(tmpdir, f'mixed_output.{format}')

    if format == 'avi':
        output_args = ['-c:v', 'copy', '-c:a', 'pcm_s16le']
    else:
        output_args = ['-c:v', 'copy', '-c:a', 'aac', '-b:a', audio_br]

    cmd = [
        ffmpeg, '-y',
        '-i', video_path,
        '-stream_loop', str(loop_count), '-i', combined_music,
        '-filter_complex', filter_complex,
        '-map', '0:v',
        '-map', '[aout]',
    ] + output_args + [mixed_path]

    try:
        _run_ffmpeg(cmd, timeout=600)
        if os.path.isfile(mixed_path):
            shutil.copy2(mixed_path, output_path)
            return output_path
        _warn("Music mixing produced no output; the exported video has no "
              "background music.")
    except Exception as e:
        _warn(f"Music mixing failed - the exported video has no background "
              f"music. ffmpeg said: {str(e)[:160]}")

    return video_path
