"""Download public AudioSep weights and tokenizer assets; no audio upload."""
from pathlib import Path
import hashlib,json,time,urllib.request

ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parent/'.local'/'audiosep-separation'
WEIGHTS=CACHE/'weights'
TOK=CACHE/'roberta-tokenizer'
WEIGHTS.mkdir(parents=True,exist_ok=True)
TOK.mkdir(parents=True,exist_ok=True)

def fetch(url,destination,expected=None):
    if destination.exists():
        print('Already present:',destination.name,flush=True)
        return
    temp=destination.with_suffix(destination.suffix+'.partial')
    request=urllib.request.Request(url,headers={'User-Agent':'Local-AudioSep-Test/1.0'})
    start=time.time(); last=start; count=0; h=hashlib.sha256()
    with urllib.request.urlopen(request,timeout=90) as response,temp.open('wb') as f:
        while True:
            block=response.read(8*1024*1024)
            if not block: break
            f.write(block);h.update(block);count+=len(block)
            if time.time()-last>10:
                print(destination.name,round(count/1024**2),'MiB downloaded',flush=True)
                last=time.time()
    digest=h.hexdigest()
    if expected and digest!=expected:
        raise RuntimeError(f'Hash mismatch for {destination.name}: {digest}')
    temp.rename(destination)
    print(destination.name,count,'bytes SHA256',digest,flush=True)

metadata=json.load(urllib.request.urlopen('https://huggingface.co/api/spaces/Audio-AGI/AudioSep/tree/main/checkpoint'))
item=next(v for v in metadata if v['path'].endswith('audiosep_base_4M_steps.ckpt'))
(ROOT/'model-download-metadata.json').write_text(json.dumps(item,indent=2))
fetch('https://huggingface.co/spaces/Audio-AGI/AudioSep/resolve/main/checkpoint/audiosep_base_4M_steps.ckpt',
      WEIGHTS/'audiosep_base_4M_steps.ckpt',item.get('lfs',{}).get('oid'))
for name in ('config.json','vocab.json','merges.txt','tokenizer.json','tokenizer_config.json'):
    fetch('https://huggingface.co/FacebookAI/roberta-base/resolve/main/'+name,TOK/name)
