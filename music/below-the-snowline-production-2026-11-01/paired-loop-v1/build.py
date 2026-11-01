"""Fixed-gain circular A/B crossfade; preserves pitch and playback rate."""
from pathlib import Path
import hashlib, json, math, shutil, subprocess
import numpy as np

HERE=Path(__file__).resolve().parent
HOME=HERE.parent
CACHE=HOME/'cache'
RATE=48000
FF=shutil.which('ffmpeg')
NAMES=['Shelter_on_the_Ice_Plain_2026-11-01T232735.mp4','Outpost_on_the_Ice_2026-11-01T232735.mp4']

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def save(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def decode(p):
    result=subprocess.run([FF,'-v','error','-i',str(p),'-map','0:a:0','-ac','2','-ar',str(RATE),'-f','f32le','pipe:1'],capture_output=True,check=True)
    assert not result.stderr,result.stderr
    x=np.frombuffer(result.stdout,'<f4').reshape(-1,2)
    assert np.isfinite(x).all()
    return x

def measure(p,label):
    r=subprocess.run([FF,'-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-23:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,check=True)
    log=r.stderr.decode(errors='replace')
    (CACHE/(label+'-levels.log')).write_text(log,encoding='utf-8')
    d=json.loads(log[log.rfind('{'):log.rfind('}')+1])
    return {key:float(d['input_'+field]) for key,field in [('integrated_lufs','i'),('loudness_range_lu','lra'),('true_peak_dbtp','tp')]}

def write(name,x):
    out=HERE/name
    raw=CACHE/(name+'.f32')
    x.astype('<f4').tofile(raw)
    codec=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24'] if out.suffix=='.flac' else ['-c:a','libmp3lame','-b:a','192k']
    subprocess.run([FF,'-v','error','-n','-f','f32le','-ar',str(RATE),'-ac','2','-i',str(raw),*codec,str(out)],check=True)
    y=decode(out)
    assert x.shape==y.shape and np.max(np.abs(y))<1
    energy=error=0.;maxerr=0.
    for i in range(0,len(x),RATE*10):
        expected=x[i:i+RATE*10].astype(float)
        delta=expected-y[i:i+RATE*10]
        energy+=float(np.sum(expected**2));error+=float(np.sum(delta**2))
        maxerr=max(maxerr,float(np.abs(delta).max()))
    snr=10*math.log10(energy/max(error,1e-30))
    assert maxerr<2.4e-7 if out.suffix=='.flac' else snr>20
    record={'path':str(out),'sha256':sha(out),'duration_seconds':len(y)/RATE,'decoded_frames_per_channel':len(y),'finite_unclipped':True,'sample_peak_dbfs':20*math.log10(float(np.abs(y).max())),'all_samples_recipe_snr_db':snr,'max_absolute_recipe_error':maxerr}
    print('Verified',name,round(snr,2),'dB SNR',flush=True)
    return record,y

def seam(x,index):
    left=(index-1)%len(x);right=index%len(x)
    step=float(np.sqrt(np.mean((x[right].astype(float)-x[left])**2)))
    ids=np.arange(index-RATE,index+RATE)%len(x)
    differences=np.sqrt(np.mean(np.diff(x[ids].astype(float),axis=0)**2,axis=1))
    typical=float(np.quantile(differences,.999))
    assert step<=typical*1.5+1e-7
    return {'sample_index':index,'rms_sample_step':step,'nearby_step_p99_9':typical,'passed':True}

def main():
    arrays=[];records=[];analyses={}
    for name,label in zip(NAMES,['shelter','outpost']):
        src=HOME/'sources'/name;original=Path('C:/Users/jazzs/Downloads')/name
        if original.exists():
            assert sha(src)==sha(original)
        x=decode(src);assert len(x)==300*RATE
        for kind in ['full','body']:
            report=json.loads((HERE/'analysis'/(label+'-'+kind+'.json')).read_text())
            analyses[label+'-'+kind]={**{k:v for k,v in report.items() if k!='measurements'},'measurements':{k:v for k,v in report['measurements'].items() if k!='timeline'}}
        body_lufs=analyses[label+'-body']['measurements']['integrated_lufs']
        gain=round(-23-body_lufs,2)
        arrays.append((x[4*RATE:294*RATE]*10**(gain/20)).astype(np.float32))
        records.append({'title':label,'original_path':str(original),'copy_path':str(src),'source_sha256':sha(src),'source_seconds':300,'selected_source_range_seconds':[4,294],'gain_db':gain,'gain_basis':'Fixed gain toward -23 LUFS over source 30–270s; no dynamic normalization'})
    a,b=arrays;fade=20*RATE
    phase=np.arange(fade,dtype=np.float64)/fade*np.pi/2
    cosine=np.cos(phase).astype(np.float32)[:,None]
    sine=np.sin(phase).astype(np.float32)[:,None]
    x=np.concatenate([a[fade:],b[fade:]])
    x[250*RATE:270*RATE]=a[-fade:]*cosine+b[:fade]*sine
    x[-fade:]=b[-fade:]*cosine+a[:fade]*sine
    assert len(x)==540*RATE and np.isfinite(x).all() and np.abs(x).max()<1
    checks=[seam(x,k*RATE) for k in [0,250,270,520]]
    outputs=[]
    record,lossless=write('Below-the-Snowline-paired-loop-9min-v1.flac',x);outputs.append(record)
    lossless_checks=[seam(lossless,k*RATE) for k in [0,250,270,520]]
    del lossless
    record,compressed=write('Below-the-Snowline-paired-loop-9min-v1.mp3',x);outputs.append(record)
    del compressed
    excerpt=x[230*RATE:290*RATE]
    record,_=write('Shelter-to-Outpost-transition-60s.mp3',excerpt);outputs.append(record)
    boundary=np.concatenate([x[-40*RATE:],x[:20*RATE]])
    record,_=write('Outpost-to-Shelter-loop-boundary-60s.mp3',boundary);outputs.append(record)
    # Test an actual decoded two-cycle concatenation across the file boundary.
    master=HERE/'Below-the-Snowline-paired-loop-9min-v1.flac'
    tail=decode(master)[-40*RATE:];head=decode(master)[:20*RATE]
    decoded_boundary=np.concatenate([tail,head])
    boundary_error=float(np.max(np.abs(decoded_boundary-boundary)))
    assert boundary_error<2.4e-7
    levels=measure(master,'paired-loop')
    assert levels['true_peak_dbtp']<-2
    save('source-analysis.json',analyses)
    save('mix-recipe.json',{'date':'2026-11-01','user_request':'Analyse and pair both five-minute tracks into a potentially loopable ten-minute file','duration_preference':'Natural transitions, roughly 9–10 minutes (recommended)','status':'Unapproved listening candidate','sources':records,'duration_seconds':540,'sample_rate':RATE,'channels':2,'start_phase':'Shelter source24s: starts inside the active music to make a circular loop','timeline':[{'range_seconds':[0,250],'content':'Shelter source24–274s'},{'range_seconds':[250,270],'content':'Shelter274–294s into Outpost4–24s'},{'range_seconds':[270,520],'content':'Outpost24–274s'},{'range_seconds':[520,540],'content':'Outpost274–294s into Shelter4–24s; continues at file start'}],'crossfade':'20s equal-power cosine/sine at both joins','duration_arithmetic':'600s minus 20s total source-edge trims minus two20s overlaps =540s','processing':'Fixed gains, edge trims and crossfades only; no EQ, compression, pitch changes, time stretch, SFX or added opening/closing fade','trim_reason':'Remove first4s near-silence and last6s deep terminal fade; incoming quiet heads are covered by preceding tails. Musical suitability remains a listening decision.','assistant_listening':False,'user_join_approval':False,'preview_timing':'Both60s excerpts crossfade at0:20–0:40; boundary excerpt crosses actual file end/start at0:40','playback_note':'FLAC is the gapless assembly master. A player may insert pauses between repeated files; use gapless playback or concatenate decoded audio. MP3 is a listening copy.'})
    save('delivery-validation.json',{'status':'passed','outputs':outputs,'master_levels':levels,'raw_join_checks':checks,'decoded_flac_join_checks':lossless_checks,'decoded_master_tail_head_vs_expected_max_error':boundary_error,'all_original_hashes_unchanged':all(sha(r['copy_path'])==r['source_sha256'] and (not Path(r['original_path']).exists() or sha(r['original_path'])==r['source_sha256']) for r in records),'full_source_and_output_audio_decode':True,'assistant_listening':False,'musical_approval':'Pending user review; sample continuity does not establish harmonic compatibility'})
    print(json.dumps({'duration_seconds':540,'gains_db':[r['gain_db'] for r in records],'levels':levels,'joins_passed':True}),flush=True)

if __name__=='__main__':main()
