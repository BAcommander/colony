"""
Colony: loop a short video under a playlist of audio tracks, export MP4.

Run from the repo root:  python -m colony.gui   (or python colony/gui.py)
Build the exe:           colony/build.bat
"""

import os
import queue
import shutil
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

if not getattr(sys, 'frozen', False):
    # python colony/gui.py puts colony/ on sys.path, not the repo root
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import exporter                                    # noqa: E402
from app.media_exts import AUDIO_EXTENSIONS, VIDEO_EXTENSIONS  # noqa: E402
from colony import render                                   # noqa: E402

APP_TITLE = 'Colony'


def _patterns(exts):
    return ' '.join(f'*{e}' for e in sorted(exts))


def _clock(seconds):
    return render._clock(seconds)


class ColonyApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.video = None
        self.video_info = None          # render.VideoInfo
        self.overlay = None
        self.overlay_info = None
        self.sfx_path = None
        self.tracks = []                # [(path, header duration or None)]
        self.events = queue.Queue()
        self.worker = None
        self.job_started = None
        self.last_eta = None
        self.preview_dirs = []

        try:
            self.ffmpeg = exporter.get_ffmpeg_path()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(APP_TITLE, f'ffmpeg is not available:\n\n{e}')
            raise SystemExit(1)

        root.title(APP_TITLE)
        root.minsize(860, 650)
        root.geometry(f'960x{min(900, max(650, root.winfo_screenheight()-120))}')
        root.protocol('WM_DELETE_WINDOW', self._on_close)
        # Keep export/cancel reachable on smaller displays as options grow.
        content = ttk.Frame(root)
        content.pack(fill='both', expand=True)
        canvas = tk.Canvas(content, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        root = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=root, anchor='nw')
        root.bind('<Configure>', lambda _e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(window, width=e.width))
        pad = {'padx': 10, 'pady': 6}

        # ── Video ──
        vf = ttk.LabelFrame(root, text='Video (loops for the whole export; output keeps its size and frame rate)')
        vf.pack(fill='x', **pad)
        self.video_btn = ttk.Button(vf, text='Choose video...', command=self.choose_video)
        self.video_btn.pack(side='left', padx=8, pady=8)
        self.video_label = ttk.Label(vf, text='No video chosen', foreground='#666')
        self.video_label.pack(side='left', padx=4, fill='x', expand=True)

        # Shared thumbnail branding, once at the start of the final export.
        intro_box = ttk.LabelFrame(root, text='Opening titles · Ambient Colony')
        intro_box.pack(fill='x', **pad)
        row = ttk.Frame(intro_box)
        row.pack(fill='x', padx=8, pady=5)
        self.intro_enabled = tk.BooleanVar(value=True)
        self.intro_title = tk.StringVar()
        self.intro_fade = tk.BooleanVar(value=True)
        ttk.Checkbutton(row, text='Include opening', variable=self.intro_enabled,
                        command=self.refresh_total).pack(side='left')
        ttk.Label(row, text='Video title:').pack(side='left', padx=(14, 5))
        ttk.Entry(row, textvariable=self.intro_title).pack(side='left', fill='x', expand=True)
        ttk.Label(intro_box, text='Logo + AMBIENT COLONY / PRESENTS → video title + lower tagline',
                  foreground='#666').pack(anchor='w', padx=8, pady=2)
        ttk.Checkbutton(intro_box, variable=self.intro_fade,
            text='Fade audio from 0:05 to 0:20 (use audio without a baked-in opening fade)'
        ).pack(anchor='w', padx=8, pady=2)
        ttk.Label(intro_box, text='Untick audio fade to keep supplied fades. Scene stays dark until the title, '
                  'then brightens by 0:20.', foreground='#666').pack(anchor='w', padx=8, pady=(0, 5))

        # ── Overlay ──
        ovf = ttk.LabelFrame(root, text='Overlay (optional): greenscreen clip keyed over the video, bottom centre')
        ovf.pack(fill='x', **pad)
        ov_row = ttk.Frame(ovf)
        ov_row.pack(fill='x', padx=8, pady=(8, 2))
        self.overlay_choose_btn = ttk.Button(ov_row, text='Choose overlay...', command=self.choose_overlay)
        self.overlay_choose_btn.pack(side='left')
        self.overlay_clear_btn = ttk.Button(ov_row, text='Remove', command=self.clear_overlay)
        self.overlay_clear_btn.pack(side='left', padx=6)
        self.overlay_label = ttk.Label(ov_row, text='No overlay', foreground='#666')
        self.overlay_label.pack(side='left', padx=4, fill='x', expand=True)

        self.overlay_mode = tk.StringVar(value=render.OVERLAY_ONCE)
        mode_row = ttk.Frame(ovf)
        mode_row.pack(fill='x', padx=8, pady=2)
        ttk.Label(mode_row, text='Show it').pack(side='left')
        ttk.Radiobutton(mode_row, text='once, halfway through', value=render.OVERLAY_ONCE,
                        variable=self.overlay_mode, command=self.refresh_total).pack(side='left', padx=(6, 12))
        ttk.Radiobutton(mode_row, text='every', value=render.OVERLAY_EVERY,
                        variable=self.overlay_mode, command=self.refresh_total).pack(side='left')
        self.overlay_every = tk.DoubleVar(value=render.DEFAULT_OVERLAY_EVERY_S / 60)
        every_spin = ttk.Spinbox(mode_row, from_=1, to=240, increment=1, textvariable=self.overlay_every,
                                 width=5, command=self.refresh_total)
        every_spin.pack(side='left', padx=4)
        every_spin.bind('<KeyRelease>', lambda _e: self.refresh_total())
        ttk.Label(mode_row, text='minutes').pack(side='left')

        pos_row = ttk.Frame(ovf)
        pos_row.pack(fill='x', padx=8, pady=(2, 8))
        self.overlay_bottom = tk.DoubleVar(value=render.DEFAULT_OVERLAY_BOTTOM_PX)
        ttk.Spinbox(pos_row, from_=0, to=1000, increment=10, textvariable=self.overlay_bottom,
                    width=5).pack(side='left')
        ttk.Label(pos_row, text='px up from the bottom (at 1080p; scaled with the video)').pack(side='left', padx=4)
        self.overlay_plan_label = ttk.Label(pos_row, text='', foreground='#666')
        self.overlay_plan_label.pack(side='right')

        # ── Audio playlist ──
        af = ttk.LabelFrame(root, text='Audio tracks (played in order, each in full)')
        af.pack(fill='both', expand=True, **pad)
        list_row = ttk.Frame(af)
        list_row.pack(fill='both', expand=True, padx=8, pady=8)
        self.listbox = tk.Listbox(list_row, activestyle='none', selectmode='browse',
                                  font=('Segoe UI', 10), height=4)
        self.listbox.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(list_row, orient='vertical', command=self.listbox.yview)
        scroll.pack(side='left', fill='y')
        self.listbox.configure(yscrollcommand=scroll.set)

        buttons = ttk.Frame(list_row)
        buttons.pack(side='left', fill='y', padx=(8, 0))
        self.track_buttons = []
        for text, cmd in (('Add audio...', self.add_audio), ('Remove', self.remove_track),
                          ('Move up', lambda: self.move_track(-1)),
                          ('Move down', lambda: self.move_track(1)), ('Clear', self.clear_tracks)):
            b = ttk.Button(buttons, text=text, command=cmd, width=14)
            b.pack(pady=2)
            self.track_buttons.append(b)

        # ── Audio options ──
        of = ttk.LabelFrame(root, text='Audio')
        of.pack(fill='x', **pad)
        xf_row = ttk.Frame(of)
        xf_row.pack(fill='x', padx=8, pady=(8, 2))
        ttk.Label(xf_row, text='Crossfade between tracks (seconds):').pack(side='left')
        self.crossfade = tk.DoubleVar(value=render.DEFAULT_CROSSFADE_S)
        self.crossfade_spin = ttk.Spinbox(xf_row, from_=0, to=render.MAX_CROSSFADE_S, increment=1,
                                          textvariable=self.crossfade, width=5, command=self.refresh_total)
        self.crossfade_spin.pack(side='left', padx=6)
        self.crossfade_spin.bind('<KeyRelease>', lambda _e: self.refresh_total())
        self.crossfade_note = ttk.Label(xf_row, text='', foreground='#666')
        self.crossfade_note.pack(side='left', padx=4)
        self.total_label = ttk.Label(xf_row, text='')
        self.total_label.pack(side='right')

        self.match_loudness = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            of, variable=self.match_loudness, command=self.refresh_total,
            text=f'Match every track to {render.TARGET_LUFS:g} LUFS (for playlists from mixed sources). '
                 f'Off: each track keeps the level it was supplied at.').pack(anchor='w', padx=8, pady=2)
        self.full_decode = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            of, variable=self.full_decode,
            text='Full decode check after export (reads the whole file back; slow on hours of 4K)'
        ).pack(anchor='w', padx=8, pady=(2, 8))

        # Optional rain / environmental sound, independent of the playlist.
        rain = ttk.LabelFrame(root, text='Rain / SFX (optional; mixed under music)')
        rain.pack(fill='x', **pad)
        row = ttk.Frame(rain)
        row.pack(fill='x', padx=8, pady=5)
        self.sfx_choose_btn = ttk.Button(row, text='Choose rain/SFX...', command=self.choose_sfx)
        self.sfx_choose_btn.pack(side='left')
        self.sfx_clear_btn = ttk.Button(row, text='Remove', command=self.clear_sfx)
        self.sfx_clear_btn.pack(side='left', padx=6)
        self.sfx_label = ttk.Label(row, text='No rain/SFX')
        self.sfx_label.pack(side='left')
        self.sfx_mode = tk.StringVar(value='intermittent')
        ttk.Combobox(row, textvariable=self.sfx_mode, values=('continuous', 'intermittent'),
                     state='readonly', width=13).pack(side='right')
        self.sfx_fields = {}
        for specs in ((('gain_db', 'Volume (dB)', -6, -60, 12),
                       ('start_s', 'Start after (s)', 20, 0, 3600),
                       ('on_s', 'Rain incl. fades (s)', 120, 1, 3600),
                       ('off_s', 'Gap (s)', 90, 0, 3600)),
                      (('fade_in_s', 'Fade in (s)', 20, 0, 600),
                       ('fade_out_s', 'Fade out (s)', 30, 0, 600),
                       ('loop_crossfade_s', 'Loop join (s)', 2, 0, 30))):
            row = ttk.Frame(rain)
            row.pack(fill='x', padx=8, pady=3)
            for key, label, default, low, high in specs:
                var = tk.DoubleVar(value=default)
                self.sfx_fields[key] = var
                ttk.Label(row, text=label).pack(side='left')
                ttk.Spinbox(row, textvariable=var, from_=low, to=high, width=6).pack(side='left', padx=(4, 10))
        ttk.Label(rain, text='Continuous ignores Rain/Gap. Loop join smooths the source repeat. '
                  'Preview mix uses actual timing (up to 10 min).', foreground='#666').pack(anchor='w', padx=8, pady=4)

        # ── Export ──
        ef = ttk.Frame(self.root)
        ef.pack(fill='x', **pad)
        self.preview_btn = ttk.Button(ef, text='Preview video...', command=self.preview)
        self.preview_btn.pack(side='left')
        self.audio_preview_btn = ttk.Button(ef, text='Preview mix...', command=self.preview_mix)
        self.audio_preview_btn.pack(side='left', padx=6)
        self.intro_preview_btn = ttk.Button(ef, text='Preview opening...', command=self.preview_opening)
        self.intro_preview_btn.pack(side='left', padx=6)
        self.export_btn = ttk.Button(ef, text='Export MP4...', command=self.export)
        self.export_btn.pack(side='left', padx=6)
        self.cancel_btn = ttk.Button(ef, text='Cancel', command=self.cancel, state='disabled')
        self.cancel_btn.pack(side='left')
        self.progress = ttk.Progressbar(ef, maximum=1000)
        self.progress.pack(side='left', fill='x', expand=True, padx=(6, 0))
        sf = ttk.Frame(self.root)
        sf.pack(fill='x', padx=10, pady=(0, 10))
        self.status = ttk.Label(sf, text='Choose a video and add audio tracks.', anchor='w')
        self.status.pack(side='left', fill='x', expand=True)
        self.time_label = ttk.Label(sf, text='', foreground='#666')
        self.time_label.pack(side='right')

        self.refresh()
        self.root.after(100, self._drain_events)

    # ── Inputs ──

    def _intro_settings(self):
        if not self.intro_enabled.get():
            return None
        settings = render.IntroSettings(self.intro_title.get().strip(), bool(self.intro_fade.get()))
        settings.validate()
        return settings

    def preview_opening(self):
        if not self.video:
            messagebox.showinfo(APP_TITLE, 'Choose a video first. Music is optional for this preview.')
            return
        try:
            intro = self._intro_settings()
            if intro is None:
                raise ValueError('Enable opening titles to preview them.')
            sfx = self._sfx_settings()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        d = tempfile.mkdtemp(prefix='colony_opening_preview_')
        self.preview_dirs.append(d)
        options = dict(intro=intro, sfx=sfx, overlay=self.overlay, overlay_mode=self._mode(),
                       overlay_every_s=self._every_seconds(), overlay_bottom_px=self._bottom_px(),
                       match_loudness=bool(self.match_loudness.get()), preview_seconds=25, full_decode=True)
        self._start(self._run_opening_preview, self.video, [p for p, _ in self.tracks],
                    os.path.join(d, 'Colony opening preview.mp4'), self._crossfade_value(), options)

    def _run_opening_preview(self, video, tracks, out, crossfade, options):
        try:
            result = render.preview_opening(video, tracks, out, crossfade,
                on_status=lambda s: self.events.put(('status', s)),
                on_progress=lambda f, eta: self.events.put(('progress', (f, eta))), **options)
            if not result.verified:
                raise RuntimeError('Opening preview failed technical verification. Check its manifest.')
            self.events.put(('opening_preview_done', (result.output, bool(tracks))))
        except render.ExportCancelled:
            self.events.put(('cancelled', None))
        except Exception as exc:
            self.events.put(('error', (str(exc), render.error_log_path(out))))

    def choose_sfx(self):
        path = filedialog.askopenfilename(title='Choose rain / SFX',
            filetypes=[('Audio', _patterns(AUDIO_EXTENSIONS)), ('All files', '*.*')])
        if path:
            self.sfx_path = path
            self.sfx_label.configure(text=os.path.basename(path))

    def clear_sfx(self):
        self.sfx_path = None
        self.sfx_label.configure(text='No rain/SFX')

    def _sfx_settings(self):
        if not self.sfx_path:
            return None
        try:
            settings = render.SfxSettings(path=self.sfx_path, mode=self.sfx_mode.get(),
                **{k: float(v.get()) for k, v in self.sfx_fields.items()})
            settings.validate()
            return settings
        except (tk.TclError, ValueError) as exc:
            raise ValueError(f'Check rain/SFX settings: {exc}') from exc

    def preview_mix(self):
        if not self.tracks:
            messagebox.showinfo(APP_TITLE, 'Add music to the audio playlist first.')
            return
        try:
            settings = self._sfx_settings()
            intro = render.IntroSettings(self.intro_title.get().strip() or 'Audio preview',
                       bool(self.intro_fade.get())) if self.intro_enabled.get() else None
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        d = tempfile.mkdtemp(prefix='colony_mix_preview_')
        self.preview_dirs.append(d)
        self._start(self._run_audio_preview, [p for p, _ in self.tracks],
                    os.path.join(d, 'Colony mix preview.mp3'), self._crossfade_value(),
                    settings, bool(self.match_loudness.get()), intro)

    def _run_audio_preview(self, tracks, out, crossfade, sfx, match, intro):
        try:
            path = render.preview_audio(tracks, out, crossfade, sfx, match,
                intro=intro,
                on_status=lambda s: self.events.put(('status', s)),
                on_progress=lambda f, eta: self.events.put(('progress', (f, eta))))
            self.events.put(('audio_preview_done', path))
        except render.ExportCancelled:
            self.events.put(('cancelled', None))
        except Exception as exc:
            self.events.put(('error', (str(exc), None)))

    def choose_video(self):
        path = filedialog.askopenfilename(
            title='Choose the video to loop',
            filetypes=[('Video', _patterns(VIDEO_EXTENSIONS)), ('All files', '*.*')])
        if not path:
            return
        try:
            info = render.probe_video(self.ffmpeg, path)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(APP_TITLE, f'Could not read that video:\n\n{e}')
            return
        self.video, self.video_info = path, info
        self.refresh()

    def choose_overlay(self):
        path = filedialog.askopenfilename(
            title='Choose the greenscreen overlay',
            filetypes=[('Video', _patterns(VIDEO_EXTENSIONS)), ('All files', '*.*')])
        if not path:
            return
        try:
            info = render.probe_video(self.ffmpeg, path)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(APP_TITLE, f'Could not read that overlay:\n\n{e}')
            return
        self.overlay, self.overlay_info = path, info
        self.refresh()

    def clear_overlay(self):
        self.overlay = self.overlay_info = None
        self.refresh()

    def add_audio(self):
        paths = filedialog.askopenfilenames(
            title='Add audio tracks',
            filetypes=[('Audio', _patterns(AUDIO_EXTENSIONS)), ('All files', '*.*')])
        for path in paths:
            self.tracks.append((path, exporter.get_video_duration(path)))
        if paths:
            self.refresh()
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set('end')
            self.listbox.see('end')

    def _selected(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def remove_track(self):
        i = self._selected()
        if i is None:
            return
        del self.tracks[i]
        self.refresh()
        if self.tracks:
            self.listbox.selection_set(min(i, len(self.tracks) - 1))

    def move_track(self, step):
        i = self._selected()
        if i is None or not 0 <= i + step < len(self.tracks):
            return
        self.tracks[i], self.tracks[i + step] = self.tracks[i + step], self.tracks[i]
        self.refresh()
        self.listbox.selection_set(i + step)
        self.listbox.see(i + step)

    def clear_tracks(self):
        if self.tracks and messagebox.askyesno(APP_TITLE, 'Remove all audio tracks?'):
            self.tracks = []
            self.refresh()

    # ── Display ──

    @staticmethod
    def _number(var, default, minimum=0.0):
        try:
            return max(minimum, float(var.get()))
        except (tk.TclError, ValueError):
            return default

    def _crossfade_value(self):
        return self._number(self.crossfade, 0.0)

    def _every_seconds(self):
        return 60 * self._number(self.overlay_every, render.DEFAULT_OVERLAY_EVERY_S / 60, 1.0)

    def _bottom_px(self):
        return self._number(self.overlay_bottom, render.DEFAULT_OVERLAY_BOTTOM_PX)

    def _mode(self):
        return self.overlay_mode.get() if self.overlay else render.OVERLAY_OFF

    def _estimated_total(self):
        """The playlist length from the tracks' header durations, or None
        while any track is unreadable."""
        durations = [d for _p, d in self.tracks if d]
        if not self.tracks or len(durations) < len(self.tracks):
            return None
        return render.total_duration(durations, self._crossfade_value())

    def _planned_overlay_times(self, total):
        if not (self.overlay_info and self.video_info and total):
            return []
        return render.plan_overlay(self._mode(), total, self.video_info.duration,
                                   self.overlay_info.duration, self._every_seconds(), intro=self.intro_enabled.get())

    def refresh(self):
        if self.video_info:
            vi = self.video_info
            length = f', {_clock(vi.duration)} loop' if vi.duration else ''
            self.video_label.configure(text=f'{os.path.basename(self.video)}   {vi.describe()}{length}',
                                       foreground='')
        if self.overlay_info:
            length = f'  ({_clock(self.overlay_info.duration)})' if self.overlay_info.duration else ''
            self.overlay_label.configure(text=os.path.basename(self.overlay) + length, foreground='')
        else:
            self.overlay_label.configure(text='No overlay', foreground='#666')
        self.listbox.delete(0, 'end')
        for n, (path, dur) in enumerate(self.tracks, start=1):
            length = _clock(dur) if dur else '?'
            self.listbox.insert('end', f'{n:>2}.  {os.path.basename(path)}   [{length}]')
        self.refresh_total()

    def refresh_total(self):
        one = len(self.tracks) < 2
        self.crossfade_spin.configure(state='disabled' if one else 'normal')
        self.crossfade_note.configure(
            text='(only between separate audio files; nothing is added to a single track)' if one else '')
        total = self._estimated_total()
        if not self.tracks:
            self.total_label.configure(text='')
        elif total is None:
            self.total_label.configure(text=f'{len(self.tracks)} tracks')
        else:
            n = f'{len(self.tracks)} track' + ('s' if len(self.tracks) != 1 else '')
            self.total_label.configure(text=f'{n}, about {_clock(total)}')
        times = self._planned_overlay_times(total)
        if not self.overlay:
            self.overlay_plan_label.configure(text='')
        elif total is None:
            self.overlay_plan_label.configure(text='')
        elif not times:
            self.overlay_plan_label.configure(text='Would not be shown: the video is too short for it')
        else:
            shown = ', '.join(_clock(t) for t in times[:6]) + (', ...' if len(times) > 6 else '')
            self.overlay_plan_label.configure(text=f'Planned: {len(times)}x at {shown}')

    # ── Preview / export ──

    def _busy(self, busy):
        state = 'disabled' if busy else 'normal'
        for b in self.track_buttons + [self.video_btn, self.overlay_choose_btn, self.overlay_clear_btn,
                                       self.preview_btn, self.export_btn, self.audio_preview_btn,
                                       self.sfx_choose_btn, self.sfx_clear_btn, self.intro_preview_btn]:
            b.configure(state=state)
        self.cancel_btn.configure(state='normal' if busy else 'disabled')
        self.job_started = time.monotonic() if busy else None
        self.last_eta = None
        if not busy:
            self.time_label.configure(text='')

    def _start(self, target, *args):
        self._busy(True)
        self.progress['value'] = 0
        self.worker = threading.Thread(target=target, args=args, daemon=True)
        self.worker.start()

    def preview(self):
        if not self.video:
            messagebox.showinfo(APP_TITLE, 'Choose a video first.')
            return
        d = tempfile.mkdtemp(prefix='colony_preview_')
        self.preview_dirs.append(d)
        out = os.path.join(d, 'Colony preview.mp4')
        self._start(self._run_preview, self.video, self.overlay, self._bottom_px(), out)

    def _run_preview(self, video, overlay, bottom_px, out):
        try:
            path = render.preview(video, overlay, bottom_px, out,
                                  on_status=lambda s: self.events.put(('status', s)),
                                  on_progress=lambda f, eta: self.events.put(('progress', (f, eta))))
            self.events.put(('preview_done', path))
        except render.ExportCancelled:
            self.events.put(('cancelled', None))
        except Exception as e:  # noqa: BLE001 - shown to the user
            self.events.put(('error', (str(e) or e.__class__.__name__, None)))

    def _summary(self, out, overwrite, total):
        vi = self.video_info
        lines = [f'Output: {out}' + ('   (replaces the existing file)' if overwrite else ''), '']
        loop = f', {_clock(vi.duration)} loop' if vi.duration else ''
        lines.append(f'Video: {os.path.basename(self.video)}  {vi.describe()}{loop}')
        lines.append(f'Output size and frame rate: {vi.describe()} (same as the video, no scaling)')
        intro = self._intro_settings()
        if intro:
            lines.append(f'Opening: {intro.title} · logo, PRESENTS, title and lower tagline; once, clearing by 0:22')
            lines.append('Opening audio: silence until 0:05; gradual rise to supplied level at 0:20'
                         if intro.fade_audio else 'Opening audio: supplied fades retained')
        n = len(self.tracks)
        if n == 1:
            lines.append(f'Length: {_clock(total)}, the length of the audio track')
        else:
            xf = render.clamp_crossfade(self._crossfade_value(), [d for _p, d in self.tracks])
            lines.append(f'Length: {_clock(total)}: {n} tracks in full'
                         + (f', {xf:g} s crossfades between them' if xf else ', no crossfades'))
        if self.match_loudness.get():
            lines.append(f'Audio level: every track matched to {render.TARGET_LUFS:g} LUFS')
        else:
            lines.append('Audio level: kept as supplied')
        lines.append(f'Peak limiter at {render.LIMIT_DBFS:g} dBFS (touches nothing already under it); '
                     f'AAC {render.AUDIO_BITRATE} stereo')
        sfx = self._sfx_settings()
        if sfx:
            lines.append(f'Rain/SFX: {os.path.basename(sfx.path)}, {sfx.gain_db:+g} dB, {sfx.mode}; starts at {sfx.start_s:g} s')
            lines.append(f'Rain {sfx.on_s:g} s / gap {sfx.off_s:g} s (intermittent only); fades {sfx.fade_in_s:g}/{sfx.fade_out_s:g} s; loop join {sfx.loop_crossfade_s:g} s')
        times = self._planned_overlay_times(total)
        if not self.overlay:
            lines.append('Overlay: none')
        elif not times:
            lines.append('Overlay: NOT shown, the video is too short for it')
        else:
            when = ', '.join(_clock(t) for t in times[:8]) + (', ...' if len(times) > 8 else '')
            if self._mode() == render.OVERLAY_ONCE:
                how = f'once, at {when}'
            else:
                how = f'every {self._every_seconds() / 60:g} min: {len(times)}x at {when}'
            lines.append(f'Overlay: {os.path.basename(self.overlay)} {how}'
                         f' (snapped to the loop), {self._bottom_px():g} px up')
        lines.append('Checks after export: streams, size, frame rate, duration'
                     + (', then a full decode of the file' if self.full_decode.get() else ''))
        lines.append('')
        lines.append('Start the export?')
        return '\n'.join(lines)

    def export(self):
        if not self.video:
            messagebox.showinfo(APP_TITLE, 'Choose a video first.')
            return
        if not self.tracks:
            messagebox.showinfo(APP_TITLE, 'Add at least one audio track.')
            return
        total = self._estimated_total()
        if total is None:
            messagebox.showerror(APP_TITLE, 'One of the tracks could not be read. Remove it and try again.')
            return
        try:
            sfx = self._sfx_settings()
            intro = self._intro_settings()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        default = os.path.splitext(os.path.basename(self.video))[0] + ' - looped.mp4'
        default = os.path.basename(render.versioned_path(os.path.join(os.path.dirname(self.video), default)))
        out = filedialog.asksaveasfilename(
            title='Export MP4', defaultextension='.mp4', initialfile=default,
            initialdir=os.path.dirname(self.video), filetypes=[('MP4 video', '*.mp4')])
        if not out:
            return
        if os.path.normcase(os.path.abspath(out)) in {
                os.path.normcase(os.path.abspath(p))
                for p in [self.video, self.overlay, self.sfx_path] + [t[0] for t in self.tracks] if p}:
            messagebox.showerror(APP_TITLE, 'Choose a different file name: that one is an input.')
            return
        overwrite = os.path.exists(out)        # the save dialog already asked
        if not messagebox.askokcancel(APP_TITLE, self._summary(out, overwrite, total)):
            return
        options = {
            'intro': intro,
            'sfx': sfx,
            'overlay': self.overlay,
            'overlay_mode': self._mode(),
            'overlay_every_s': self._every_seconds(),
            'overlay_bottom_px': self._bottom_px(),
            'match_loudness': bool(self.match_loudness.get()),
            'full_decode': bool(self.full_decode.get()),
            'overwrite': overwrite,
        }
        self._start(self._run_export, self.video, [p for p, _d in self.tracks], out,
                    self._crossfade_value(), options)

    def _run_export(self, video, tracks, out, crossfade, options):
        try:
            result = render.render(
                video, tracks, out, crossfade,
                on_status=lambda s: self.events.put(('status', s)),
                on_progress=lambda f, eta: self.events.put(('progress', (f, eta))),
                **options)
            self.events.put(('done', result))
        except render.ExportCancelled:
            self.events.put(('cancelled', None))
        except Exception as e:  # noqa: BLE001 - shown to the user
            log = render.error_log_path(out)
            self.events.put(('error', (str(e) or e.__class__.__name__,
                                       log if os.path.isfile(log) else None)))

    def cancel(self):
        self.status.configure(text='Cancelling...')
        exporter.request_export_cancel()

    def _update_time(self):
        if self.job_started is None:
            return
        text = f'Elapsed {_clock(time.monotonic() - self.job_started)}'
        if self.last_eta is not None:
            text += f' - about {_clock(self.last_eta)} left in this step'
        self.time_label.configure(text=text)

    def _drain_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'status':
                    self.status.configure(text=value)
                    self.last_eta = None
                elif kind == 'progress':
                    frac, eta = value
                    self.progress['value'] = frac * 1000
                    self.last_eta = eta
                elif kind == 'audio_preview_done':
                    self._busy(False)
                    self.status.configure(text='Mix preview opened. Check rain level, fades, quiet gap and re-entry; long delays may exceed the preview.')
                    os.startfile(value)
                elif kind == 'opening_preview_done':
                    self._busy(False)
                    path, has_music = value
                    self.status.configure(text='Opening preview opened. Review logo, title, tagline and scene reveal.'
                        + (' Check the audio entrance too.' if has_music else ' Silent preview; no music selected.'))
                    os.startfile(path)
                elif kind == 'preview_done':
                    self._busy(False)
                    self.status.configure(text='Preview opened in your video player. Check the loop seam '
                                               'and the overlay; the export will reuse these encodes.')
                    os.startfile(value)
                elif kind == 'done':
                    self._busy(False)
                    self.status.configure(text=f'Exported {value.output}')
                    self._show_done(value)
                elif kind == 'cancelled':
                    self._busy(False)
                    self.progress['value'] = 0
                    self.status.configure(text='Cancelled.')
                elif kind == 'error':
                    self._busy(False)
                    message, log = value
                    self.status.configure(text='Export failed.')
                    extra = f'\n\nThe log is beside the output:\n{log}' if log else ''
                    messagebox.showerror(APP_TITLE, f'Export failed:\n\n{message}{extra}')
        except queue.Empty:
            pass
        self._update_time()
        self.root.after(100, self._drain_events)

    def _show_done(self, result):
        win = tk.Toplevel(self.root)
        win.title('Export finished')
        win.transient(self.root)
        win.resizable(False, False)
        body = ttk.Frame(win, padding=14)
        body.pack(fill='both', expand=True)

        lines = [f'{os.path.basename(result.output)}   {_clock(result.duration)}, '
                 f'{result.width}x{result.height}' + (f', {result.fps:g} fps' if result.fps else '')]
        if result.overlay_times:
            at = ', '.join(_clock(t) for t in result.overlay_times[:8])
            at += ', ...' if len(result.overlay_times) > 8 else ''
            lines.append(f'Overlay shown {len(result.overlay_times)}x, at {at}')
        elif self.overlay:
            lines.append('The overlay was not shown: the video is too short for it.')
        ttk.Label(body, text='\n'.join(lines), justify='left').pack(anchor='w')

        marks = {True: 'OK', False: 'FAILED', None: '?'}
        rows = [f'  {marks[c.ok]:6} {c.name}: {c.detail}' for c in result.checks or []]
        failed = [c for c in result.checks or [] if c.ok is False]
        head = 'Technical checks passed.' if not failed else f'{len(failed)} technical check(s) FAILED.'
        ttk.Label(body, text=head, font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        ttk.Label(body, text='\n'.join(rows), justify='left', font=('Consolas', 9)).pack(anchor='w')
        ttk.Label(body, justify='left', foreground='#666', wraplength=560,
                  text='These confirm the file is well formed. Whether the loop seam and the overlay '
                       'look and sound natural is your check: watch a seam and the overlay before '
                       'publishing.' + (f'\nManifest: {result.manifest}' if result.manifest else '')
                  ).pack(anchor='w', pady=(8, 10))

        btns = ttk.Frame(body)
        btns.pack(fill='x')
        ttk.Button(btns, text='Open video', command=lambda: os.startfile(result.output)).pack(side='left')
        ttk.Button(btns, text='Open folder',
                   command=lambda: os.startfile(os.path.dirname(result.output))).pack(side='left', padx=6)
        ttk.Button(btns, text='Close', command=win.destroy).pack(side='right')
        win.grab_set()

    def _on_close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno(APP_TITLE, 'An export is running. Cancel it and quit?'):
                return
            exporter.request_export_cancel()
            self.worker.join(timeout=5)
        render.clear_prepared()
        for d in self.preview_dirs:
            shutil.rmtree(d, ignore_errors=True)   # a preview still open in a player stays
        self.root.destroy()


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)   # crisp text on scaled displays
    except Exception:
        pass
    root = tk.Tk()
    ColonyApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
