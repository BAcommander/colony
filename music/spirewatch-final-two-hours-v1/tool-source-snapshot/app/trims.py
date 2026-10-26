"""
Non-destructive video trim — in/out points as a recipe.

Unlike photo edits (see ``app/edits.py``), a trim NEVER touches the video
file. Re-encoding a multi-gigabyte clip to shave off its first few
seconds would cost minutes, lose quality, and — if we also kept a
pristine copy the way ``originals/`` does for photos — double the
library's footprint. So the clip on disk stays exactly as the camera
wrote it and we store only the range:

    <library>/.speedyslideshow/video_trims.json

``app/exporter.py`` applies it with ffmpeg ``-ss``/``-t`` when rendering
the segment, and the slideshow player seeks to ``start`` and advances at
``end``. "Revert" is simply deleting the entry, and because the source
was never modified the revert is exact.

The consequence to keep in mind: the trim is real everywhere inside
Speedy SlideShow, but the file opened in Explorer is still the whole
clip.

Times are absolute seconds into the source file. There is deliberately
no ``compose`` primitive here — the photo crop needs one because the
visible file really is cropped, so a fresh box has to be folded back
into original coordinates. A trimmed video is untouched, so the trim bar
always shows the whole clip with its handles parked at the stored
points, and dragging them reports absolute source times.

``end`` of ``None`` means "play to the end of the clip".
"""

import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# Shortest clip we will let a trim produce. This is not cosmetic — three
# separate places downstream break on very short segments:
#
#   < ~1 frame  the segment has no frames at all, so probing its duration
#               fails and exporter.py falls back to photo_duration (5s),
#               putting every later crossfade offset 5s out.
#   < 0.1s      _xfade_timeline's offset stops advancing, so a segment
#               inherits its predecessor's offset and xfade breaks.
#   < 1.6s      the clip is dropped from the music ducking intervals
#               (benign, and self-correcting).
#
# 1.0s clears all three with margin. Enforced here as well as in the UI,
# because this module is the only guard between a hand-edited
# video_trims.json and ffmpeg.
MIN_TRIM_SECONDS = 1.0

# Times are stored to millisecond precision: finer than any frame rate we
# care about, and it keeps the JSON stable so a no-op save doesn't churn
# the file.
TIME_PRECISION = 3


# ── Recipe format ─────────────────────────────────────────────

def empty_record() -> Dict:
    """A recipe that plays the clip whole."""
    return {'start': 0.0, 'end': None}


def _as_time(value: Any) -> Optional[float]:
    """Coerce to a finite, non-negative float, or None."""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float('inf'), float('-inf')):  # NaN / inf
        return None
    return f if f > 0.0 else 0.0


def normalize_record(raw: Any, duration: Optional[float] = None) -> Dict:
    """Coerce anything off disk or from JS into a valid trim recipe.

    Returns ``empty_record()`` — i.e. "no trim" — for anything malformed,
    degenerate, or shorter than ``MIN_TRIM_SECONDS``. Callers treat every
    one of those cases the same way, so there is no error to handle.

    ``duration`` is the source clip's length when known. Passing it lets
    us clamp an out-point that runs past the end of the file and reject a
    range that starts past it; passing None skips those checks (the
    stored recipe is read long before anything probes the video).
    """
    if not isinstance(raw, dict):
        return empty_record()

    start = _as_time(raw.get('start')) or 0.0
    end = _as_time(raw.get('end'))
    dur = _as_time(duration)

    if dur is not None and dur > 0:
        # An out-point past the end of the file is the same as no
        # out-point; a start past the end is not a trim at all.
        if end is not None and end > dur:
            end = None
        if start >= dur:
            return empty_record()

    if end is not None and end <= start:
        return empty_record()

    length = effective_duration(dur, start, end)
    if length is not None and length < MIN_TRIM_SECONDS:
        return empty_record()

    if start <= 0.0 and end is None:
        return empty_record()

    return {
        'start': round(start, TIME_PRECISION),
        'end': None if end is None else round(end, TIME_PRECISION),
    }


def is_empty(record: Any) -> bool:
    """True when the recipe plays the whole clip, i.e. nothing is trimmed."""
    rec = record if isinstance(record, dict) else {}
    start = _as_time(rec.get('start')) or 0.0
    return start <= 0.0 and _as_time(rec.get('end')) is None


# ── Applying a trim ───────────────────────────────────────────

def effective_duration(src_duration: Optional[float],
                       start: float,
                       end: Optional[float]) -> Optional[float]:
    """How long the clip actually plays for, or None if unknowable.

    Returns None ONLY when the source duration could not be probed *and*
    the trim has no explicit out-point. When the probe failed but the
    user set an end, the arithmetic still gives a real number — which
    matters, because the exporter's loudnorm guard has to know whether
    the segment is under three seconds, and guessing wrong there costs
    the segment its audio stream.
    """
    s = _as_time(start) or 0.0
    e = _as_time(end)
    if e is not None:
        return max(0.0, e - s)
    d = _as_time(src_duration)
    if d is not None:
        return max(0.0, d - s)
    return None


def range_for(record: Any,
              src_duration: Optional[float] = None) -> Tuple[float, Optional[float]]:
    """(start, end) to hand to a player or to ffmpeg.

    ``(0.0, None)`` for an untrimmed clip, so callers can use it
    unconditionally without checking for a trim first.
    """
    rec = normalize_record(record, src_duration)
    if is_empty(rec):
        return 0.0, None
    return rec['start'], rec['end']


def describe(record: Any) -> str:
    """Short human-readable summary of a trim, for logs."""
    rec = normalize_record(record)
    if is_empty(rec):
        return 'whole clip'
    end = 'end' if rec['end'] is None else f"{rec['end']:.3f}s"
    return f"trim {rec['start']:.3f}s to {end}"
