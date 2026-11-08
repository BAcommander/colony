"""
Small shared utilities used across the app.

Currently contains:
  - atomic_write_json: safe write-to-temp-then-rename for JSON files
  - read_app_version: single-source-of-truth version reader from VERSION.txt
  - safe_rglob: recursive file walk that skips symlinks / Windows junctions
  - ProgressThrottle: rate-limiter for evaluate_js progress callbacks
"""

import json as _json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterator, Union

logger = logging.getLogger(__name__)


_VERSION_CACHE = None


def read_app_version() -> str:
    """Read the app version from VERSION.txt at the project / frozen app root.

    Cached after first read. Falls back to the hardcoded current version
    below if the file is missing or unreadable so the app never crashes
    due to a packaging oversight (keep that fallback in sync on release).
    """
    global _VERSION_CACHE
    if _VERSION_CACHE is not None:
        return _VERSION_CACHE

    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, '..', 'VERSION.txt'),          # source checkout
        os.path.join(here, 'VERSION.txt'),                # alongside app/
        os.path.join(os.getcwd(), 'VERSION.txt'),         # cwd fallback
    ]
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidates.insert(0, os.path.join(meipass, 'VERSION.txt'))

    for path in candidates:
        try:
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as f:
                    version = f.read().strip()
                if version:
                    _VERSION_CACHE = version
                    return version
        except Exception:
            continue

    _VERSION_CACHE = '1.0.9'
    return _VERSION_CACHE


def atomic_write_json(path: str, data: Any, indent: int = 2) -> bool:
    """Atomically write JSON to ``path``.

    Writes to ``<path>.tmp`` first, flushes + fsyncs, and then uses
    ``os.replace`` to swap it into place. ``os.replace`` is atomic on
    both Windows and POSIX, so a power-loss / crash mid-write can only
    ever leave the previous valid file or the new valid file on disk,
    never a truncated or partially-written one.

    Returns True on success, False on any failure (and attempts to
    clean up the temp file).

    The temp name includes pid + thread id: with a SHARED temp path, two
    concurrent writers (a second app instance, or two pywebview API
    threads) truncate/overwrite each other's temp file mid-write and
    os.replace publishes the mangled bytes — this corrupted a user's
    custom_slideshows.json (valid JSON + a stray trailing byte).
    """
    import threading
    tmp_path = f'{path}.{os.getpid()}.{threading.get_ident()}.tmp'
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            _json.dump(data, f, indent=indent)
            f.flush()
            try:
                os.fsync(f.fileno())
            except (OSError, AttributeError):
                # fsync not available on all filesystems / platforms
                pass
        os.replace(tmp_path, path)
        return True
    except Exception:
        # Best-effort cleanup of the temp file on failure
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False


def load_json_lenient(path: str) -> Any:
    """Load a JSON file, salvaging the leading valid document if trailing
    garbage follows it (the footprint of the old shared-temp-file write
    race — see atomic_write_json).

    Returns the parsed value, or None if the file is missing or no valid
    document could be recovered. Callers whose write path is
    read-modify-write MUST treat None/salvage carefully: returning an
    empty default on a corrupt-but-recoverable file, then writing that
    default back, silently wipes the user's data.
    """
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
    except OSError:
        return None
    try:
        return _json.loads(raw)
    except ValueError:
        pass
    try:
        doc, end = _json.JSONDecoder().raw_decode(raw.lstrip())
        logger.warning(
            f"Salvaged leading JSON document from {path} "
            f"({len(raw) - end} trailing chars ignored)")
        return doc
    except ValueError:
        logger.error(f"Unrecoverable JSON in {path}")
        return None


# Directory entries we never descend into during a recursive scan.
# Skipping our own config directory keeps face-data JSONs out of album scans
# and skipping recycle-bin / system-dir names (which Windows creates inside
# a Pictures folder in some OneDrive setups) avoids walking gigabytes of
# irrelevant content.
_SKIP_DIRNAMES = frozenset({
    '.speedyslideshow',
    '$RECYCLE.BIN',
    'System Volume Information',
    '.git',
    '.svn',
    '__pycache__',
})


def cv2_imwrite_unicode(path: str, img: Any, params: Any = None) -> bool:
    """Unicode-safe, atomic OpenCV image write.

    cv2.imwrite silently fails on non-ASCII paths on Windows (e.g. a photo
    library under C:\\Users\\Renée\\...); imencode + numpy tofile sidesteps
    the codepage issue. The write goes to a UNIQUE temp name and is renamed
    into place with os.replace so concurrent writers can't collide on a
    shared .tmp and readers never see a half-written file.

    Returns True on success. Raises OSError on I/O failure (the temp file
    is cleaned up first); returns False only if encoding itself failed.
    """
    import cv2
    ext = os.path.splitext(path)[1].lower() or '.jpg'
    ok, buf = cv2.imencode(ext, img, params if params is not None else [])
    if not ok:
        return False
    tmp = f"{path}.{os.getpid()}_{os.urandom(4).hex()}.tmp"
    try:
        buf.tofile(tmp)
        os.replace(tmp, path)
    except OSError:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        raise
    return True


def safe_rglob(root: Union[str, Path]) -> Iterator[Path]:
    """Yield every regular file under ``root`` without following symlinks
    or Windows directory junctions / reparse points.

    This is a drop-in-ish replacement for ``Path(root).rglob('*')`` that
    is safe against cycles. ``Path.rglob`` follows symlinks by default on
    Python 3.10-3.12; a user-created junction loop
    (``Pictures\\Archive -> D:\\PhotoArchive`` and
    ``D:\\PhotoArchive\\Current -> C:\\Users\\john\\Pictures``) would
    otherwise make the scan walk forever and hang the app.

    We also skip obvious non-photo directories like our own
    ``.speedyslideshow`` config dir and OS-managed folders like
    ``$RECYCLE.BIN`` so they don't pollute album counts.

    When a symlinked subdirectory is encountered we log a debug-level
    message naming the path, so users who have set up a legitimate
    shortcut can diagnose why those photos don't appear.
    """
    root_str = os.fspath(root)

    # os.walk with followlinks=False is the only robust way to skip both
    # POSIX symlinks and Windows directory junctions on every Python we
    # ship on. pathlib didn't grow an equivalent until 3.13.
    for dirpath, dirnames, filenames in os.walk(root_str, followlinks=False):
        # Filter in-place so os.walk doesn't descend into skipped dirs.
        pruned = []
        kept = []
        for d in dirnames:
            if d in _SKIP_DIRNAMES:
                pruned.append(d)
                continue
            # Also catch directory symlinks that made it past followlinks=False
            # on some filesystems (edge case, but cheap to double-check).
            full = os.path.join(dirpath, d)
            try:
                if os.path.islink(full):
                    pruned.append(d)
                    logger.debug("safe_rglob: skipping symlinked directory %s", full)
                    continue
            except OSError:
                # Filesystem can't answer islink - conservatively skip.
                pruned.append(d)
                continue
            kept.append(d)
        dirnames[:] = kept

        for name in filenames:
            yield Path(dirpath) / name


class ProgressThrottle:
    """Rate-limit progress callbacks so high-frequency tickers don't
    overwhelm the pywebview JS bridge with redundant ``evaluate_js`` calls.

    A single call to ``evaluate_js`` costs roughly 1-3ms of round-trip
    through the webview; firing one per photo on a 50k-photo library
    spends minutes doing nothing but telling the UI numbers that almost
    never change what the user sees (the percent bar can't move by less
    than one pixel).

    ``should_emit(pct, is_final=False)`` returns True when ANY of:

      - this is the very first call (no previous emit)
      - ``is_final`` is True (always emit the terminal update so the
        UI lands on the real final value, not a throttled-away 99%)
      - percentage has changed by at least ``min_delta_pct`` since the
        last emit (absolute delta - also allows downward ticks, rare
        but possible when totals are revised mid-run)
      - at least ``min_interval_s`` has elapsed since the last emit

    Typical usage::

        throttle = ProgressThrottle()

        def on_progress(current, total, filename):
            pct = round((current / total) * 100) if total > 0 else 0
            is_final = (total > 0 and current >= total)
            if not throttle.should_emit(pct, is_final=is_final):
                return
            window.evaluate_js(f"updateProgress({pct})")

    Not thread-safe on its own; callers that emit from multiple threads
    should wrap access in their own lock, but in practice each throttle
    instance lives inside a single worker's closure.
    """

    __slots__ = ('_min_delta', '_min_interval', '_last_pct', '_last_ts')

    def __init__(self, min_delta_pct: float = 1.0, min_interval_s: float = 0.25):
        self._min_delta = float(min_delta_pct)
        self._min_interval = float(min_interval_s)
        self._last_pct: float = -1.0     # <0 sentinel = never emitted
        self._last_ts: float = 0.0

    def should_emit(self, pct: float, is_final: bool = False) -> bool:
        now = time.monotonic()
        pct_f = float(pct)

        # Final ticks always go through so the UI never sticks at 99%
        if is_final:
            self._last_pct = pct_f
            self._last_ts = now
            return True

        # First call for this throttle - always emit so the UI shows
        # something rather than starting at a stale previous value.
        if self._last_pct < 0:
            self._last_pct = pct_f
            self._last_ts = now
            return True

        if abs(pct_f - self._last_pct) >= self._min_delta:
            self._last_pct = pct_f
            self._last_ts = now
            return True

        if (now - self._last_ts) >= self._min_interval:
            self._last_pct = pct_f
            self._last_ts = now
            return True

        return False

    def reset(self) -> None:
        """Forget the last emission so the next call always emits.

        Useful when reusing a throttle instance across multiple phases
        (e.g. scan then execute) so each phase starts with a guaranteed
        first tick.
        """
        self._last_pct = -1.0
        self._last_ts = 0.0
