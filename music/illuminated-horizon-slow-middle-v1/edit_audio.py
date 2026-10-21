"""Local, pitch-preserving tempo edit; no generation or external services."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'C:\Users\jazzs\Downloads\Illuminated_Horizon_2026-10-21T141941.mp4')
SR = 48000
MIN_TEMPO = 0.65

def run(args, log=None):
    p = subprocess.run([str(v) for v in args], cwd=ROOT, capture_output=True)
    if log:
        (ROOT / log).write_bytes(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace')[-6000:])
    return p.stdout

def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path]))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def tempo(t):
    if t < 90 or t >= 390:
        return 1.0
    if t < 180:
        return 1 - (1-MIN_TEMPO)*(1-math.cos(math.pi*(t-90)/90))/2
    if t <= 300:
        return MIN_TEMPO
    return MIN_TEMPO + (1-MIN_TEMPO)*(1-math.cos(math.pi*(t-300)/90))/2

def mapped_time(t):
    grid = np.linspace(0, t, max(2, int(t*100)+1))
    return float(np.trapezoid([1/tempo(float(s)) for s in grid], grid))

def decode(path, name):
    target = ROOT / name
    run(['ffmpeg','-hide_banner','-v','error','-n','-i',path,'-map','0:a:0','-ar',SR,
         '-ac',2,'-f','f32le',target])
    return np.memmap(target, dtype='<f4', mode='r').reshape(-1,2)

def measure(x):
    peak = 0.0
    power = 0.0
    finite = True
    for start in range(0,len(x),SR*20):
        block = np.asarray(x[start:start+SR*20])
        finite = finite and bool(np.isfinite(block).all())
        peak = max(peak,float(np.max(np.abs(block))))
        power += float(np.square(block.astype(np.float64)).sum())
    return {'frames':len(x),'seconds':len(x)/SR,'finite':finite,
            'peak':peak,'peak_dbfs':20*math.log10(max(peak,1e-12)),
            'rms_dbfs':10*math.log10(max(power/(len(x)*2),1e-24)),
            'samples_at_or_above_full_scale':int(np.count_nonzero(np.abs(x)>=1))}

def main():
    original = ROOT / 'source-original.mp4'
    if not original.exists():
        shutil.copy2(SOURCE,original)
    assert sha(original) == sha(SOURCE)
    meta = probe(original)
    (ROOT/'source-probe.json').write_text(json.dumps(meta,indent=2))
    length = float(next(s['duration'] for s in meta['streams'] if s['codec_type']=='audio'))
    commands = []
    for t in np.arange(90,390.001,.1):
        commands.append(f'{t:.3f} rubberband tempo {tempo(float(t)):.9f};')
    (ROOT/'tempo-commands.txt').write_text('\n'.join(commands))
    print('Rendering gradual 1.0 -> 0.65 -> 1.0 tempo, pitch fixed at 1.0.',flush=True)
    filt = ('asendcmd=f=tempo-commands.txt,'
            'rubberband=tempo=1:pitch=1:transients=mixed:detector=compound:'
            'phase=laminar:window=long:smoothing=on:pitchq=quality:channels=together')
    master = ROOT/'Illuminated-Horizon-Slow-Middle-v1.wav'
    run(['ffmpeg','-hide_banner','-loglevel','info','-n','-i',original,'-map','0:a:0',
         '-vn','-af',filt,'-c:a','pcm_f32le','-ar',SR,master], 'render.log')
    print('Analysing full decoded source and edit.',flush=True)
    src = decode(original,'source-decoded.f32')
    edited = decode(master,'edit-decoded.f32')
    source_stats, edit_stats = measure(src), measure(edited)
    assert edit_stats['finite'] and abs(edit_stats['seconds']-mapped_time(length)) < 2
    # One fixed headroom adjustment only, if needed; no compressor or loudness pumping.
    gain = min(1.0,10**(-2/20)/max(edit_stats['peak'],1e-12))
    out = ROOT/'Illuminated-Horizon-Slow-Middle-v1.mp3'
    run(['ffmpeg','-hide_banner','-v','error','-n','-i',master,'-af',f'volume={gain:.12f}',
         '-c:a','libmp3lame','-b:a','320k','-id3v2_version','3',
         '-metadata','title=Illuminated Horizon - Slower Middle v1',out])
    final = decode(out,'delivery-decoded.f32')
    delivery_stats = measure(final)
    assert delivery_stats['finite'] and delivery_stats['samples_at_or_above_full_scale']==0
    assert abs(delivery_stats['seconds']-edit_stats['seconds']) < .05
    run(['ffmpeg','-hide_banner','-v','error','-n','-ss','80','-i',out,'-t','170',
         '-af','afade=t=in:d=0.03,afade=t=out:st=167:d=3',
         '-c:a','libmp3lame','-b:a','320k',ROOT/'Slowing-Transition-Review-v1.mp3'])
    rise = max(0,mapped_time(300)-12)
    run(['ffmpeg','-hide_banner','-v','error','-n','-ss',str(rise),'-i',out,'-t','140',
         '-af','afade=t=in:d=0.03,afade=t=out:st=137:d=3',
         '-c:a','libmp3lame','-b:a','320k',ROOT/'Return-Transition-Review-v1.mp3'])
    # Compare 30-second local pulse envelopes. The edited middle should follow the
    # original envelope stretched to 1/0.65 duration, allowing filter delay.
    def envelope(x):
        size = 480
        a = np.asarray(x[:len(x)//size*size]).reshape(-1,size,2)
        return np.sqrt(np.mean(a*a,axis=(1,2))).astype(np.float64)
    comparisons = []
    for t in (195,240,265):
        a = envelope(src[int(t*SR):int((t+25)*SR)])
        ot = mapped_time(t)
        b = envelope(edited[int((ot-1)*SR):int((ot+25/MIN_TEMPO+1)*SR)])
        expected = np.interp(np.arange(int(len(a)/MIN_TEMPO))*MIN_TEMPO,np.arange(len(a)),a)
        best = (-2,None)
        for offset in range(0,201):
            z = b[offset:offset+len(expected)]
            if len(z)!=len(expected): continue
            corr = float(np.corrcoef(expected,z)[0,1])
            if corr>best[0]: best=(corr,offset/100-1)
        comparisons.append({'source_start_s':t,'mapped_output_start_s':ot,
                            'stretched_envelope_correlation':best[0],
                            'best_offset_s':best[1]})
    record = {'status':'local candidate; user listening review pending',
              'source':str(SOURCE),'source_sha256':sha(original),
              'source_audio':source_stats,'unscaled_edit':edit_stats,'delivery':delivery_stats,
              'method':'continuous FFmpeg Rubber Band tempo automation; pitch=1; linked stereo; 0.1 s cosine-ramp commands',
              'minimum_tempo_ratio':MIN_TEMPO,'fixed_delivery_gain_db':20*math.log10(gain),
              'expected_duration_s':mapped_time(length),
              'source_to_output_landmarks_s':{str(t):mapped_time(t) for t in (0,90,180,300,390,length)},
              'middle_envelope_checks':comparisons,
              'limits':['Existing repeating figures remain; no stems or beatless rearrangement.',
                        'Assistant measured signals; no continuous listening verdict.',
                        'Source ending retained; no new full-track fade or cadence.',
                        'No generation service, model installation, credits, commit or push.'],
              'outputs':{p.name:sha(p) for p in (master,out,ROOT/'Slowing-Transition-Review-v1.mp3',ROOT/'Return-Transition-Review-v1.mp3')}}
    (ROOT/'delivery-v1.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2),flush=True)

if __name__=='__main__':
    main()
