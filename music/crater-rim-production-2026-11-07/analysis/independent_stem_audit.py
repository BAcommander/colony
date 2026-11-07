"""Read-only full-PCM stem audit; the exact check executed on 2026-11-07.

This independently checks arithmetic in the rendered float32 cache. It does not
reconstruct the arrangement from source music or decode delivery FLAC/MP3 files.
It prints results and does not modify source, cache or delivery media.
"""
from pathlib import Path
import numpy as np
import json

p=Path(r'G:/AI/colony/.local/crater-rim-audio-2026-11-07-v1')
files={k:(p/(k+'-hour.f32')).open('rb') for k in ['mix','dry','sfx','wind','room']}
frames=0
try:
    while True:
        raw={k:f.read(48000*10*8) for k,f in files.items()}
        if not raw['mix']:
            break
        assert len(set(map(len,raw.values())))==1
        a={k:np.frombuffer(v,'<f4') for k,v in raw.items()}
        assert np.array_equal(a['mix'],a['dry']+a['sfx'])
        assert np.array_equal(a['sfx'],a['wind']+a['room'])
        frames+=len(a['mix'])//2
    assert frames==172800000
finally:
    for f in files.values():
        f.close()
last={}
for k in files:
    with (p/(k+'-hour.f32')).open('rb') as f:
        f.seek(-8,2)
        last[k]=np.frombuffer(f.read(),'<f4').tolist()
assert all(v==[0.0,0.0] for v in last.values())
print(json.dumps({'full_raw_stem_additivity_exact':True,'sample_frames':frames,
                  'last_pcm_stereo_samples':last}))
