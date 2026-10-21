"""Short original-source text-directed neural separation, inference only.

Uses upstream AudioSep ResUNet30 unchanged. Loads only the trained RoBERTa
text-query branch of CLAP, omitting the unused audio-query/training machinery.
No waveform is uploaded, stretched, spectrally re-created or convolved.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,math,argparse

ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parent/'.local'/'audiosep-separation'
for name,value in {'HF_HOME':CACHE/'hf-cache','TORCH_HOME':CACHE/'torch-cache',
                   'NUMBA_CACHE_DIR':CACHE/'numba-cache'}.items():
    os.environ[name]=str(value)
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
sys.dont_write_bytecode=True
sys.path[:0]=[str(CACHE/'packages'),r'C:\AI\ComfyUI\venv\Lib\site-packages',str(CACHE/'AudioSep')]
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

SR=32000
SOURCE=ROOT.parent/'illuminated-horizon-slow-middle-v1'/'source-original.mp4'
CKPT=CACHE/'weights'/'audiosep_base_4M_steps.ckpt'

def run(args,log=None):
    result=subprocess.run([str(v) for v in args],capture_output=True,cwd=ROOT)
    if log: (ROOT/log).write_bytes(result.stdout+result.stderr)
    if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace')[-5000:])
    return result.stdout

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''): h.update(block)
    return h.hexdigest()

def load_models():
    print('Loading public AudioSep checkpoint with weights_only=True.',flush=True)
    checkpoint=torch.load(CKPT,map_location='cpu',weights_only=True,mmap=True)
    state=checkpoint.get('state_dict',checkpoint)
    (ROOT/'checkpoint-key-summary.json').write_text(json.dumps({
        'top_level_keys':list(checkpoint)[:30], 'state_dict_key_count':len(state),
        'first_state_dict_keys':list(state)[:35],
        'query_keys':[k for k in state if 'text_branch' in k][:12]},indent=2))
    if '--inspect' in sys.argv:
        print((ROOT/'checkpoint-key-summary.json').read_text(),flush=True)
        return None
    from models.resunet import ResUNet30
    from transformers import RobertaModel,RobertaConfig,RobertaTokenizer
    tokenizer=RobertaTokenizer.from_pretrained(str(CACHE/'roberta-tokenizer'),local_files_only=True)
    text=RobertaModel(RobertaConfig.from_pretrained(str(CACHE/'roberta-tokenizer'),local_files_only=True))
    proj=nn.Sequential(nn.Linear(768,512),nn.ReLU(),nn.Linear(512,512))
    separator=ResUNet30(input_channels=1,output_channels=1,condition_size=512)
    def load_exact(module,prefix,allow_position_ids=False):
        values={k[len(prefix):]:v for k,v in state.items() if k.startswith(prefix)}
        if allow_position_ids:
            values={k:v for k,v in values.items() if not k.endswith(('position_ids','token_type_ids'))}
        assert values, f'No weights with prefix {prefix}'
        info=module.load_state_dict(values,strict=True)
        print('Strictly loaded',prefix,len(values),'tensors',info,flush=True)
    load_exact(separator,'ss_model.')
    load_exact(text,'query_encoder.model.text_branch.',True)
    load_exact(proj,'query_encoder.model.text_projection.')
    del checkpoint,state
    separator=separator.eval().cuda()
    text=text.eval().cuda()
    proj=proj.eval().cuda()
    return separator,text,proj,tokenizer

def embedding(description,text,proj,tokenizer):
    tokens=tokenizer([description],padding='max_length',truncation=True,max_length=512,return_tensors='pt')
    with torch.inference_mode():
        values=text(input_ids=tokens['input_ids'].cuda(),attention_mask=tokens['attention_mask'].cuda())
        return F.normalize(proj(values.pooler_output),dim=-1)

def separate_stereo(audio,condition,separator,label):
    # Original upstream model accepts mono batches. Stereo L/R are processed
    # together with the same query and identical chunk boundaries. This is an
    # adaptation, not a claim that this checkpoint was trained in stereo.
    size,hop=10*SR,5*SR
    padded=np.pad(audio,((5*SR,5*SR),(0,0)),mode='reflect')
    result=np.zeros_like(padded)
    weight=np.zeros(len(padded),dtype=np.float32)
    window=np.hanning(size).astype(np.float32)
    starts=list(range(0,len(padded)-size+1,hop))
    if starts[-1]!=len(padded)-size: starts.append(len(padded)-size)
    for count,pos in enumerate(starts,1):
        chunk=np.array(padded[pos:pos+size].T[:,None,:],copy=True)
        with torch.inference_mode():
            values=separator({'mixture':torch.from_numpy(chunk).cuda(),
                              'condition':condition.expand(2,-1)})['waveform']
        out=values[:,0,:].float().cpu().numpy().T
        assert out.shape==(size,2) and np.isfinite(out).all()
        result[pos:pos+size]+=out*window[:,None]
        weight[pos:pos+size]+=window
        if count%3==0 or count==len(starts):
            print(label,'chunk',count,'/',len(starts),'GPU peak GiB',round(torch.cuda.max_memory_allocated()/1024**3,2),flush=True)
    result/=np.maximum(weight[:,None],1e-8)
    return result[5*SR:5*SR+len(audio)]

def stats(audio):
    return {'frames':len(audio),'seconds':len(audio)/SR,
            'finite':bool(np.isfinite(audio).all()),
            'peak_dbfs':20*math.log10(max(float(np.max(np.abs(audio))),1e-12)),
            'rms_dbfs':10*math.log10(max(float(np.mean(audio.astype(np.float64)**2)),1e-24)),
            'full_scale_samples':int(np.count_nonzero(np.abs(audio)>=1))}

def write_clip(name,audio,gain):
    raw=ROOT/(name+'.f32')
    scaled=np.asarray(audio*gain,dtype=np.float32)
    # Identical 20-ms edge fades for all audition excerpts, not musical edits.
    fade=np.linspace(0,1,int(.02*SR),dtype=np.float32)
    scaled[:len(fade)]*=fade[:,None]
    scaled[-len(fade):]*=fade[::-1,None]
    scaled.tofile(raw)
    wav=ROOT/(name+'.wav')
    mp3=ROOT/(name+'.mp3')
    run(['ffmpeg','-hide_banner','-v','error','-n','-f','f32le','-ar',SR,'-ac',2,'-i',raw,'-c:a','pcm_s24le',wav])
    run(['ffmpeg','-hide_banner','-v','error','-n','-i',wav,'-c:a','libmp3lame','-b:a','256k',mp3])
    decoded=run(['ffmpeg','-hide_banner','-v','error','-i',mp3,'-f','f32le','pipe:1'])
    decoded=np.frombuffer(decoded,dtype='<f4').reshape(-1,2)
    check=stats(decoded)
    assert check['frames']==len(audio) and check['finite'] and check['full_scale_samples']==0
    raw.unlink()
    return {'wav_sha256':sha(wav),'mp3_sha256':sha(mp3),'decoded_mp3':check}

def main():
    started=time.time()
    print('Runtime',sys.version.split()[0], 'torch',torch.__version__,'GPU',torch.cuda.get_device_name(),flush=True)
    torch.set_num_threads(8)
    torch.manual_seed(20261021)
    models=load_models()
    if models is None: return
    separator,text,proj,tokenizer=models
    if '--control' in sys.argv:
        raw=run(['ffmpeg','-hide_banner','-v','error','-ss','215','-i',SOURCE,'-t','10',
                 '-ar',SR,'-ac',2,'-f','f32le','pipe:1'])
        x=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
        controls={}
        for prompt in ['a repeating synthesizer arpeggio','a dog barking','a person speaking',
                       'slow sustained synthesizer chords']:
            condition=embedding(prompt,text,proj,tokenizer)
            with torch.inference_mode():
                target=separator({'mixture':torch.from_numpy(x.T[:,None,:].copy()).cuda(),
                                  'condition':condition.expand(2,-1)})['waveform'][:,0,:].cpu().numpy().T
            middle=slice(2*SR,8*SR)
            rms_ratio=float(np.sqrt(np.mean(target[middle]**2)/np.mean(x[middle]**2)))
            controls[prompt]={'central_6s_target_to_source_rms_ratio':rms_ratio,
                              'target_source_correlation':float(np.corrcoef(target[middle].ravel(),x[middle].ravel())[0,1]),
                              'embedding_first_6':condition[0,:6].cpu().tolist()}
        (ROOT/'query-control-checks.json').write_text(json.dumps(controls,indent=2))
        print(json.dumps(controls,indent=2),flush=True)
        return
    # Extra source context is excluded from the 45-second listening deliverables.
    raw=run(['ffmpeg','-hide_banner','-v','error','-ss','190','-i',SOURCE,'-t','65',
             '-map','0:a:0','-ar',SR,'-ac',2,'-f','f32le','pipe:1'])
    original=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
    excerpt=original[10*SR:55*SR]
    prompts=[('arpeggio','a repeating synthesizer arpeggio'),
             ('pulse','a pulsing electronic synthesizer'),
             ('sequence','a synthesizer playing a repetitive melody')]
    targets={}
    for label,prompt in prompts:
        print('Query:',prompt,flush=True)
        condition=embedding(prompt,text,proj,tokenizer)
        estimate=separate_stereo(original,condition,separator,label)[10*SR:55*SR]
        estimate.tofile(ROOT/(label+'-target-raw.f32'))
        targets[label]=estimate
    # One shared fixed gain for every comparison: don't independently normalize
    # the remainder and disguise the amount of music removed by the model.
    peak=max(float(np.max(np.abs(excerpt))),*(float(np.max(np.abs(y))) for y in targets.values()),
             *(float(np.max(np.abs(excerpt-y))) for y in targets.values()))
    gain=min(1.,10**(-3/20)/peak)
    outputs={'01-original-3m20-to-4m05':write_clip('01-original-3m20-to-4m05',excerpt,gain)}
    metrics={}
    for index,(label,prompt) in enumerate(prompts,2):
        target=targets[label]
        remainder=excerpt-target
        reduced=excerpt-.75*target
        reconstruction=float(np.max(np.abs(target+remainder-excerpt)))
        assert reconstruction<1e-6
        metrics[label]={'prompt':prompt,'target_before_common_gain':stats(target),
                        'remainder_before_common_gain':stats(remainder),
                        'target_plus_remainder_max_error':reconstruction}
        for suffix,values in [('extracted',target),('removed',remainder),('reduced',reduced)]:
            name=f'{index:02d}-{label}-{suffix}'
            outputs[name]=write_clip(name,values,gain)
    record={'status':'short neural separation experiment; user listening verdict pending',
            'source':str(SOURCE),'source_sha256':sha(SOURCE),
            'source_excerpt_s':[200,245],'inference_context_s':[190,255],
            'sample_rate':SR,'channels':2,'stereo_method':'same mono model applied to L/R as a batch',
            'source_repo':'https://github.com/Audio-AGI/AudioSep',
            'source_commit':run(['git','-C',CACHE/'AudioSep','rev-parse','HEAD']).decode().strip(),
            'checkpoint_sha256':sha(CKPT),'checkpoint':str(CKPT),
            'inference_adaptation':'strict checkpoint weights; unchanged ResUNet30; trained CLAP RoBERTa+projection text branch only; unused audio-query and Lightning training wrappers omitted',
            'chunk_seconds':10,'chunk_hop_seconds':5,'chunk_join':'Hann overlap-add with context',
            'fixed_common_gain_db':20*math.log10(gain),
            'reduced_mix':'original minus 0.75 * estimated target (equivalent to retaining target at 25%)',
            'time_stretch':False,'reverb_or_spectral_resynthesis':False,'audio_uploaded':False,
            'model_metrics':metrics,'outputs':outputs,'elapsed_s':time.time()-started,
            'peak_gpu_memory_gib':torch.cuda.max_memory_allocated()/1024**3,
            'limits':['AudioSep is a 32-kHz mono-trained model; stereo handling here is an inference adaptation.',
                      'Prompted target is an estimate and may include wanted pads, bass or melody.',
                      'A lower residual level is evidence of removed signal, not proof of good separation.',
                      'Assistant performed technical checks, not listening; user must judge the clips.',
                      'No full-track edit, UI, paid service, commit or push.']}
    (ROOT/'delivery-test-v1.json').write_text(json.dumps(record,indent=2))
    print(json.dumps({'status':record['status'],'elapsed_s':record['elapsed_s'],
                      'common_gain_db':record['fixed_common_gain_db'],
                      'metrics':metrics,'outputs':list(outputs)},indent=2),flush=True)

if __name__=='__main__': main()
