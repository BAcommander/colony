"""Acquire published Colony comparison passages and apply the same local analyser."""
import concurrent.futures
import datetime as dt
import hashlib
import html
import json
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import yt_dlp

from analyze_ambient_audio import write_json, hash_file

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/reference-analysis/comparison-2026-10-30'
CHANNEL = 'UCT5K7bJk5yJGUO_uu_17BdQ'
TRACKS = [('ringfall', 'Ringfall', '4wYgfUVlvnA'), ('basalt', 'Basalt', 'QTJGwrVvv8s'),
          ('rainline', 'Rainline', 'rZERVj1aqGE'), ('shoreless', 'Shoreless', 'UiVU-M1-ZW0'),
          ('spirewatch', 'Spirewatch', 'wDnRb8yvoWg')]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def acquire_and_analyse(track):
    slug, name, video_id = track
    out = OUT / slug
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'published-passage.m4a'
    metadata = out / 'source-metadata.json'
    if not source.exists():
        options = {'quiet': True, 'no_warnings': True, 'noplaylist': True,
                   'format': 'bestaudio[ext=m4a]/bestaudio/best', 'socket_timeout': 20,
                   'retries': 1, 'js_runtimes': {'node': {}}}
        with yt_dlp.YoutubeDL(options) as y:
            info = y.extract_info('https://www.youtube.com/watch?v=' + video_id, download=False)
        if info.get('channel_id') != CHANNEL or info.get('is_live'):
            raise RuntimeError(f'{name}: unexpected channel/live state')
        meta = {k: info.get(k) for k in ['id', 'title', 'channel', 'channel_id', 'duration', 'webpage_url', 'format_id', 'acodec', 'asr', 'abr']}
        meta.update(scope='Published YouTube mix, 02:00–32:00; includes any baked SFX. Not an isolated music master.',
                    excerpt_start_seconds=120, excerpt_requested_seconds=1800,
                    acquired_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        write_json(metadata, meta)
        print(f'{name}: downloading published audio, then selecting 30-minute passage', flush=True)
        download = out / ('download-full.' + info['ext'])
        if not download.exists():
            options.update(outtmpl=str(out / 'download-full.%(ext)s'), noprogress=True)
            with yt_dlp.YoutubeDL(options) as y:
                y.download(['https://www.youtube.com/watch?v=' + video_id])
        codec = ['-c:a', 'copy'] if info.get('ext') in ['m4a', 'mp4'] else ['-c:a', 'aac', '-b:a', '192k']
        temporary = out / 'capture-in-progress.m4a'
        with (out / 'capture-log.txt').open('wb') as log:
            r = subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'warning', '-ss', '120', '-i', str(download),
                                '-t', '1800', '-vn', *codec, '-n', str(temporary)], stdout=subprocess.DEVNULL, stderr=log, timeout=240)
        if r.returncode:
            raise RuntimeError(f'{name}: capture failed; see {out / "capture-log.txt"}')
        temporary.rename(source)
    analysis = out / 'analysis'
    if not (analysis / 'analysis.json').exists():
        print(f'{name}: measuring passage', flush=True)
        with (out / 'analysis-log.txt').open('wb') as log:
            r = subprocess.run([sys.executable, str(ROOT / 'scripts/analyze_ambient_audio.py'), str(source),
                                '--metadata', str(metadata), '--out', str(analysis)], stdout=log, stderr=subprocess.STDOUT)
        if r.returncode:
            raise RuntimeError(f'{name}: analysis failed; see {out / "analysis-log.txt"}')
    print(f'{name}: complete', flush=True)
    return slug, name, analysis / 'analysis.json'


def summarize(path, slug, name):
    r = json.loads(path.read_text(encoding='utf-8'))
    m = r['measurements']
    if not 1799 <= m['decoded_duration_seconds'] <= 1801:
        raise ValueError(f'{name}: incomplete passage ({m["decoded_duration_seconds"]} seconds)')
    levels = np.array([x['rms_dbfs'] for x in m['timeline'] if x['duration_seconds'] >= .99])
    b = list(m['band_energy_percent'].values())
    return {'id': slug, 'name': name, 'analysis_file': str(path), 'source': r['source'],
            'seconds': m['decoded_duration_seconds'], 'lufs': m['integrated_lufs'],
            'lra': m['loudness_range_lu'], 'true_peak': m['true_peak_dbtp'],
            'bands_percent': b, 'below_250_percent': sum(b[:2]), 'above_1k_percent': sum(b[3:]),
            'stereo_correlation': m['stereo_correlation'], 'side_percent': m['side_energy_percent'],
            'rms_spread_db': m['rms_p95_minus_p5_db'],
            'median_absolute_1s_level_change_db': float(np.median(np.abs(np.diff(levels)))),
            'p95_absolute_1s_level_change_db': float(np.percentile(np.abs(np.diff(levels)), 95)),
            'recurrence': m['recurrence_candidates']}


def build_comparison(results):
    ref_path = ROOT / 'exports/reference-analysis/winter-watch-30min-v2/analysis.json'
    rows = [summarize(ref_path, 'reference', 'WINTER WATCH')]
    rows += [summarize(path, slug, name) for slug, name, path in sorted(results)]
    write_json(OUT / 'comparison.json', {'scope': 'One 30-minute live DVR reference and five 30-minute published Colony passages, same analyser/method. SFX are not separated.', 'tracks': rows})
    header = '<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ambient Colony · Listening comparison</title><style>body{background:#101919;color:#eeeadd;font:15px/1.6 system-ui;margin:0}main{max-width:1350px;margin:auto;padding:32px}h1{font:40px Georgia}h2{font-weight:500}p{color:#afc1ba}a{color:#dfba80}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{text-align:left;padding:12px;border-bottom:1px solid #354343}th{color:#afc1ba;font-size:12px}.scroll{overflow:auto}.ref{background:#243331}canvas{width:100%;height:260px}audio{width:100%}section{border-top:1px solid #354343;padding-top:22px;margin-top:26px}.note{font-size:13px}button{padding:8px;background:#233331;color:#eeeadd;border:1px solid #6e8078;cursor:pointer;margin:5px}</style><main><p>AMBIENT COLONY / LISTENING LAB / 30 OCTOBER 2026</p><h1>What differs from our all-day reference?</h1><p>Measured differences, not a preference score. Thirty-minute public passages; Colony intros excluded. Rainline/Shoreless include their published SFX. The reference is a moving live DVR excerpt.</p><div class="scroll"><table><tr><th>Track</th><th>LUFS</th><th>LRA (LU)</th><th>Below 250 Hz</th><th>Above 1 kHz</th><th>Stereo correlation</th><th>RMS spread (dB)</th><th>Median 1s change (dB)</th></tr>'
    for row in rows:
        relative = Path(row['analysis_file']).parent.relative_to(ROOT).as_posix() + '/report.html'
        url = Path(row['analysis_file']).parent / 'report.html'
        import os
        relative = Path(os.path.relpath(url, OUT)).as_posix()
        header += f'<tr class="{"ref" if row["id"] == "reference" else ""}"><td><a href="{html.escape(relative)}">{html.escape(row["name"])}</a></td>'
        header += ''.join(f'<td>{row[key]:.1f}{suffix}</td>' for key, suffix in [('lufs',''),('lra',''),('below_250_percent','%'),('above_1k_percent','%'),('stereo_correlation',''),('rms_spread_db',''),('median_absolute_1s_level_change_db','')]) + '</tr>'
    header += '</table></div><section><h2>How to interpret this</h2><p>LUFS differences can be corrected with gain and are not evidence of better composition. Frequency balance and stereo are distinct from harmony, phrasing and perceived comfort. Tonal variation is not a proven loop. Use the level-matched listening experiments below before choosing a new production recipe.</p></section><section id="experiments"><h2>Level-matched listening experiments</h2><p>Audio comparisons and experimental treatments are saved alongside this report when available. None autoplay. Names and treatment details can bias preference: use the blind trial sheet before revealing treatment labels.</p></section></main></html>'
    (OUT / 'comparison.html').write_text(header, encoding='utf-8')
    print(json.dumps([{k: v for k, v in r.items() if k in ['name', 'lufs', 'lra', 'below_250_percent', 'above_1k_percent', 'stereo_correlation', 'rms_spread_db', 'median_absolute_1s_level_change_db']} for r in rows], indent=2), flush=True)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(acquire_and_analyse, TRACKS):
            results.append(result)
    build_comparison(results)
