"""Restore untouched source ends and remove Rubber Band's flush artifact."""
from pathlib import Path
import json
import math
import shutil
import numpy as np
from edit_audio import ROOT, SR, run, sha, decode, measure, mapped_time

src = np.memmap(ROOT/'source-decoded.f32',dtype='<f4',mode='r').reshape(-1,2)
y = np.memmap(ROOT/'edit-decoded.f32',dtype='<f4',mode='r').reshape(-1,2)
coarse_shift = len(y)-len(src)
alignments = []
for t in (420,450,480):
    pos = t*SR
    a = np.asarray(src[pos:pos+24000:4,0])
    b = np.asarray(y[pos+coarse_shift-12000:pos+coarse_shift+36000:4,0])
    corr = np.correlate(b,a,'valid')
    offset = int(corr.argmax())*4-12000
    best = (-2,None)
    for delta in range(offset-4,offset+5):
        z = y[pos+coarse_shift+delta:pos+coarse_shift+delta+24000:4,0]
        c = float(np.corrcoef(a,z)[0,1])
        if c > best[0]: best=(c,delta)
    alignments.append({'source_s':t,'correlation':best[0],
                       'offset_samples':coarse_shift+best[1]})
assert min(a['correlation'] for a in alignments) > .95, alignments
shift = int(np.median([a['offset_samples'] for a in alignments]))
n = len(src)+shift
out = np.array(y[:n],dtype=np.float32)
# Source is already at its original pace here. Correlated, linear crossfades
# avoid the level boost of equal-power mixing nearly identical waveforms.
out[:80*SR] = src[:80*SR]
w = (.5-.5*np.cos(np.linspace(0,np.pi,5*SR))).astype(np.float32)[:,None]
out[80*SR:85*SR] = src[80*SR:85*SR]*(1-w)+out[80*SR:85*SR]*w
start,end = 400*SR+shift,410*SR+shift
w = (.5-.5*np.cos(np.linspace(0,np.pi,10*SR))).astype(np.float32)[:,None]
out[start:end] = out[start:end]*(1-w)+src[400*SR:410*SR]*w
out[end:] = src[410*SR:]
peak = float(np.max(np.abs(out)))
gain = min(1.,10**(-2/20)/peak)
out *= gain
pcm = ROOT/'final-master.f32'
out.tofile(pcm)
history = ROOT/'history'/'internal-unrepaired'
history.mkdir(parents=True,exist_ok=False)
names = ['Illuminated-Horizon-Slow-Middle-v1.wav','Illuminated-Horizon-Slow-Middle-v1.mp3',
         'Slowing-Transition-Review-v1.mp3','Return-Transition-Review-v1.mp3','delivery-v1.json']
for name in names:
    shutil.move(str(ROOT/name),str(history/name))
master = ROOT/names[0]
run(['ffmpeg','-hide_banner','-v','error','-n','-f','f32le','-ar',SR,'-ac',2,'-i',pcm,
     '-c:a','pcm_s24le',master])
delivery = ROOT/names[1]
run(['ffmpeg','-hide_banner','-v','error','-n','-i',master,'-c:a','libmp3lame','-b:a','320k',
     '-metadata','title=Illuminated Horizon - Slower Middle v1',delivery])
final = decode(delivery,'final-delivery-decoded.f32')
stats = measure(final)
assert stats['finite'] and stats['samples_at_or_above_full_scale']==0
assert abs(stats['seconds']-n/SR)<.001
for name,ss,duration in [('Slowing-Transition-Review-v1.mp3',80,170),
                          ('Return-Transition-Review-v1.mp3',mapped_time(300)-12,140)]:
    run(['ffmpeg','-hide_banner','-v','error','-n','-ss',str(ss),'-i',master,'-t',duration,
         '-af',f'afade=t=in:d=0.03,afade=t=out:st={duration-3}:d=3',
         '-c:a','libmp3lame','-b:a','320k',ROOT/name])
record = json.loads((history/'delivery-v1.json').read_text())
record['delivery'] = stats
record['master'] = measure(out)
record['fixed_delivery_gain_db'] = 20*math.log10(gain)
record['unrepaired_render_diagnostics'] = record.pop('unscaled_edit')
record['repair'] = {'reason':'Rubber Band EOF flush produced a large endpoint spike.',
                    'original_opening_restored_through_s':80,
                    'opening_linear_cosine_blend_s':[80,85],
                    'source_tail_linear_cosine_blend_s':[400,410],
                    'tail_alignment_checks':alignments,
                    'tail_shift_samples':shift,
                    'no_new_full_track_fades':True,
                    'first_80s_identical_to_source_before_fixed_gain':bool(np.array_equal(out[:80*SR],src[:80*SR]*gain)),
                    'last_100s_identical_to_source_before_fixed_gain':bool(np.array_equal(out[-100*SR:],src[-100*SR:]*gain))}
record['outputs']={name:sha(ROOT/name) for name in names[:-1]}
(ROOT/'delivery-v1.json').write_text(json.dumps(record,indent=2))
print(json.dumps({'delivery':stats,'fixed_gain_db':record['fixed_delivery_gain_db'],
                  'repair':record['repair'],'outputs':record['outputs']},indent=2),flush=True)
