from pathlib import Path
import shutil

root = Path('C:/dev/SpeedySlideShow')
stage = Path(__file__).parent
shutil.copy2(stage/'sfx.py', root/'colony/sfx.py')
p = root/'colony/render.py'
s = p.read_text(encoding='utf-8')
def replace(a,b):
    global s
    assert a in s, a
    s = s.replace(a,b,1)
replace('from app import exporter', 'from colony.sfx import SfxSettings, mix_graph, prepare_loop\nfrom app import exporter')
replace('overwrite: bool = False) -> RenderResult:', 'overwrite: bool = False,\n           sfx: Optional[SfxSettings] = None) -> RenderResult:')
replace("    if not tracks:\n        raise ValueError('Add at least one audio track')", "    if sfx:\n        sfx.validate()\n    if not tracks:\n        raise ValueError('Add at least one audio track')")
replace("        cmd += ['-filter_complex', build_audio_graph(gains, xfade),", "        graph = build_audio_graph(gains, xfade)\n        sfx_record = None\n        if sfx:\n            report.stage('Preparing rain/SFX loop...', 0.20, 0.20)\n            sfx_info = measure_track(ffmpeg, sfx.path)\n            sfx_loop = os.path.join(tmpdir, 'sfx-loop.wav')\n            actual_overlap = prepare_loop(ffmpeg, sfx, sfx_loop, sfx_info.duration)\n            cmd += ['-stream_loop', '-1', '-i', sfx_loop]\n            graph = mix_graph(graph, sfx, total, len(tracks) + 1)\n            sfx_record = {**asdict(sfx), 'source_duration_s': sfx_info.duration,\n                          'source_lufs': sfx_info.loudness, 'actual_loop_crossfade_s': actual_overlap}\n        cmd += ['-filter_complex', graph,")
replace('overlay_bottom_px, match_loudness, full_decode, total_units)', 'overlay_bottom_px, match_loudness, full_decode, total_units, sfx_record)')
replace('full_decode: bool, total_units: int) -> Optional[str]:', 'full_decode: bool, total_units: int, sfx_record=None) -> Optional[str]:')
replace("            'crossfade_s': result.crossfade,", "            'sfx': sfx_record,\n            'crossfade_s': result.crossfade,")
s += '''

def preview_audio(tracks, output, crossfade=DEFAULT_CROSSFADE_S, sfx=None,
                  match_loudness=False, on_status=None, on_progress=None):
    """Audition actual opening settings through one rain gap and re-entry (max 10 min).

    Continuous mode previews 90 seconds. Long delays stay silent in the preview,
    as in the export; no timing is compressed. Video is not required.
    """
    if not tracks:
        raise ValueError('Add at least one audio track.')
    if sfx:
        sfx.validate()
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
'''
p.write_text(s, encoding='utf-8')

p = root/'colony/gui.py'
s = p.read_text(encoding='utf-8')
replace('        self.tracks = []', '        self.sfx_path = None\n        self.tracks = []')
replace("root.minsize(720, 720)", "root.minsize(860, 780)")
replace("font=('Segoe UI', 10))", "font=('Segoe UI', 10), height=4)")
replace('        # ── Export ──', '''        # Optional rain / environmental sound, independent of the playlist.
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

        # ── Export ──''')
replace("self.preview_btn = ttk.Button(ef, text='Preview...'", "self.preview_btn = ttk.Button(ef, text='Preview video...'")
replace("        self.export_btn = ttk.Button", "        self.audio_preview_btn = ttk.Button(ef, text='Preview mix...', command=self.preview_mix)\n        self.audio_preview_btn.pack(side='left', padx=6)\n        self.export_btn = ttk.Button")
replace('    def choose_video(self):', '''    def choose_sfx(self):
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
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        d = tempfile.mkdtemp(prefix='colony_mix_preview_')
        self.preview_dirs.append(d)
        self._start(self._run_audio_preview, [p for p, _ in self.tracks],
                    os.path.join(d, 'Colony mix preview.mp3'), self._crossfade_value(),
                    settings, bool(self.match_loudness.get()))

    def _run_audio_preview(self, tracks, out, crossfade, sfx, match):
        try:
            path = render.preview_audio(tracks, out, crossfade, sfx, match,
                on_status=lambda s: self.events.put(('status', s)),
                on_progress=lambda f, eta: self.events.put(('progress', (f, eta))))
            self.events.put(('audio_preview_done', path))
        except render.ExportCancelled:
            self.events.put(('cancelled', None))
        except Exception as exc:
            self.events.put(('error', (str(exc), None)))

    def choose_video(self):''')
replace('self.preview_btn, self.export_btn]:', 'self.preview_btn, self.export_btn, self.audio_preview_btn,\n                                       self.sfx_choose_btn, self.sfx_clear_btn]:')
replace("        times = self._planned_overlay_times(total)\n        if not self.overlay:\n            lines.append", "        sfx = self._sfx_settings()\n        if sfx:\n            lines.append(f'Rain/SFX: {os.path.basename(sfx.path)}, {sfx.gain_db:+g} dB, {sfx.mode}; starts at {sfx.start_s:g} s')\n            lines.append(f'Rain {sfx.on_s:g} s / gap {sfx.off_s:g} s (intermittent only); fades {sfx.fade_in_s:g}/{sfx.fade_out_s:g} s; loop join {sfx.loop_crossfade_s:g} s')\n        times = self._planned_overlay_times(total)\n        if not self.overlay:\n            lines.append")
replace("        default = os.path.splitext(os.path.basename(self.video))[0]", "        try:\n            sfx = self._sfx_settings()\n        except ValueError as exc:\n            messagebox.showerror(APP_TITLE, str(exc))\n            return\n        default = os.path.splitext(os.path.basename(self.video))[0]")
replace('[self.video, self.overlay] + [t[0]', '[self.video, self.overlay, self.sfx_path] + [t[0]')
replace("        options = {\n", "        options = {\n            'sfx': sfx,\n")
replace("                elif kind == 'preview_done':", "                elif kind == 'audio_preview_done':\n                    self._busy(False)\n                    self.status.configure(text='Mix preview opened. Check rain level, fades, quiet gap and re-entry; long delays may exceed the preview.')\n                    os.startfile(value)\n                elif kind == 'preview_done':")
p.write_text(s, encoding='utf-8')
print('Updated Colony renderer, GUI and SFX module')
