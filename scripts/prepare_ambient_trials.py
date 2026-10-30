"""Create unlabelled, gain-matched reference/Colony listening trials."""
import html
import json
import random
import subprocess
from pathlib import Path

import imageio_ffmpeg

from analyze_ambient_audio import loudness, hash_file, write_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/reference-analysis/comparison-2026-10-30'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def build():
    comparison = json.loads((OUT / 'comparison.json').read_text(encoding='utf-8'))
    trials = [(r['id'], r['name'], r['source']['path'], None) for r in comparison['tracks']]
    ringfall = next(r for r in comparison['tracks'] if r['id'] == 'ringfall')
    # Target implied by measured below-80-Hz odds. Shelf shape is an experimental approximation.
    b = ringfall['bands_percent'][0] / 100
    target = comparison['tracks'][0]['bands_percent'][0] / 100
    import math
    gain = 10 * math.log10((target / (1 - target)) / (b / (1 - b)))
    trials.append(('ringfall_eq', 'Ringfall · diagnostic sub-bass shelf', ringfall['source']['path'], f'bass=g={gain:.4f}:f=80:t=q:w=0.707'))
    random.Random(301026).shuffle(trials)
    assets = OUT / 'listening-trials'
    assets.mkdir(exist_ok=True)
    key, cards = [], []
    for index, (slug, name, source, treatment) in enumerate(trials):
        code = chr(65 + index)
        folder = assets / code
        folder.mkdir(exist_ok=True)
        raw, final = folder / 'prepared.flac', folder / 'listen.flac'
        record = folder / 'validation.json'
        if not final.exists():
            cmd = [FFMPEG, '-v', 'error', '-ss', '60', '-i', source, '-t', '180', '-vn']
            if treatment:
                cmd += ['-af', treatment]
            subprocess.run([*cmd, '-c:a', 'flac', '-sample_fmt', 's16', '-n', str(raw)], check=True)
            before = loudness(raw, FFMPEG, folder)
            adjustment = -23 - before['integrated_lufs']
            if before['true_peak_dbtp'] + adjustment > -1:
                raise ValueError('This clip needs a lower common target; no limiter applied')
            subprocess.run([FFMPEG, '-v', 'error', '-i', str(raw), '-af', f'volume={adjustment:.6f}dB',
                            '-c:a', 'flac', '-sample_fmt', 's16', '-n', str(final)], check=True)
            measured = loudness(final, FFMPEG, folder)
            if abs(measured['integrated_lufs'] + 23) > .15 or measured['true_peak_dbtp'] > -1:
                raise ValueError(f'{code}: level-match validation failed')
            write_json(record, {'trial': code, 'source_sha256': hash_file(Path(source)),
                                'clip_start_seconds_in_passage': 60, 'clip_duration_seconds': 180,
                                'treatment': treatment, 'gain_db': adjustment,
                                'target_lufs': -23, 'measured': measured, 'output_sha256': hash_file(final)})
        key.append({'trial': code, 'id': slug, 'name': name, 'source': source, 'treatment': treatment})
        cards.append(f'<section><h2>Trial {code}</h2><audio controls preload="none" src="{code}/listen.flac"></audio><div class="scores"><label>Comfort (1–5)<input data-code="{code}" data-field="comfort" type="number" min="1" max="5"></label><label>Would leave playing (1–5)<input data-code="{code}" data-field="keep_playing" type="number" min="1" max="5"></label><label>Attention pulled away (1–5)<input data-code="{code}" data-field="distraction" type="number" min="1" max="5"></label></div><textarea data-code="{code}" data-field="notes" placeholder="Any tiring/bass-heavy/empty/insistent moment? Note its time."></textarea></section>')
        print('Prepared and verified trial', code, flush=True)
    write_json(assets / 'answer-key.json', key)
    page = '''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ambient Colony · Listening trials</title><style>body{background:#111b1b;color:#eee8dc;font:16px/1.6 system-ui;margin:0}main{max-width:1000px;margin:auto;padding:30px}h1{font:40px Georgia}p,label{color:#b3c2bb}section{border-top:1px solid #40524b;padding-top:15px;margin-top:24px}audio{width:100%}.scores{display:flex;gap:22px;flex-wrap:wrap}input{width:60px;margin:10px}input,textarea,button{background:#22332e;color:#eee8dc;border:1px solid #698172;padding:9px}textarea{width:100%;min-height:80px}button{cursor:pointer;margin:15px 10px 15px 0}a{color:#dcb987}</style><main><p>AMBIENT COLONY / UNLABELLED LISTENING</p><h1>What would you leave playing?</h1><p>Seven three-minute excerpts, each measured at −23 LUFS using constant gain. One is the external reference; five are our published tracks; one is a diagnostic EQ treatment of the same Ringfall passage. No new music was generated. Keep your device volume and listening setup fixed. Do a short pass in shuffled order, then repeat another day/order before choosing. This is a practical personal test, not a formal blinded clinical study.</p><p>Record ratings before opening the answer key. A 3-minute preference is a screening result: the winner still needs at least 30–60 minutes while doing your usual work, followed by a longer repeat test.</p>'''
    page += ''.join(cards)
    page += '''<button id="save">Download ratings</button><p><a href="answer-key.json">Reveal trial identities after rating</a> · <a href="../comparison.html">Measurement comparison</a></p></main><script>const fields=[...document.querySelectorAll('[data-code]')];function collect(){const out={test:'ambient-colony-2026-10-30',rated_at:new Date().toISOString(),ratings:{}};for(const f of fields){(out.ratings[f.dataset.code]??={})[f.dataset.field]=f.value}return out}try{const old=JSON.parse(localStorage.getItem('colony-audio-trials')||'null');if(old)for(const f of fields)f.value=old.ratings[f.dataset.code]?.[f.dataset.field]||''}catch{}for(const f of fields)f.onchange=()=>{try{localStorage.setItem('colony-audio-trials',JSON.stringify(collect()))}catch{}};document.querySelector('#save').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(collect(),null,2)],{type:'application/json'}));a.href=u;a.download='ambient-listening-ratings.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};document.querySelectorAll('audio').forEach(a=>a.onplay=()=>document.querySelectorAll('audio').forEach(b=>{if(a!==b)b.pause()}));</script></html>'''
    (assets / 'trials.html').write_text(page, encoding='utf-8')
    comparison_file = OUT / 'comparison.html'
    page = comparison_file.read_text(encoding='utf-8').replace('<section id="experiments">', '<section id="experiments"><p><a href="listening-trials/trials.html">Open unlabelled, level-matched listening trials →</a></p>')
    comparison_file.write_text(page, encoding='utf-8')


if __name__ == '__main__':
    build()
