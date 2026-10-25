"""Commit dedicated Deepwell index and preserve the pre-existing shared staging."""
from pathlib import Path
import subprocess,os,json,tempfile,shutil,re
H=Path(__file__).resolve().parent;R=H.parents[1]
state=json.loads((H/'staging-validation.json').read_text())
own=dict(os.environ,GIT_INDEX_FILE=state['dedicated_index'])
def git(*args,env=None,input=None):
    p=subprocess.run(['git','-C',str(R),*args],env=env,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
assert git('rev-parse','HEAD').decode().strip()==state['base_commit'],'HEAD changed: rebase scoped staging first'
assert git('branch','--show-current').strip()==b'main'
lock=R/'.git'/'index.lock'
assert lock.resolve().parent==(R/'.git').resolve()
fd=os.open(str(lock),os.O_CREAT|os.O_EXCL|os.O_WRONLY)
reconciled=Path(tempfile.gettempdir())/'colony-deepwell-reconciled-2026-10-25.index'
assert not reconciled.exists()
committed=False
try:
    original=git('ls-files','--stage','-z')
    shutil.copyfile(R/'.git'/'index',reconciled)
    preserved=dict(os.environ,GIT_INDEX_FILE=str(reconciled))
    shared=['AGENTS.md','PRODUCTION_PIPELINE.md','creative/ANIMATION_KNOWLEDGE_BANK.md','final/12-deepwell-station/README.md','.gitattributes','.gitignore']
    def norm(b):return b.decode('utf-8-sig').replace('\r','')
    staged={n:git('show',':'+n) for n in shared}
    ours={n:git('show',':'+n,env=own) for n in shared}
    current=norm(ours['AGENTS.md'])
    status=re.search(r'^Current Deepwell v4 candidate .*$',current,re.M).group(0).encode()
    for n in ['AGENTS.md','PRODUCTION_PIPELINE.md']:
        assert b'Current Deepwell v4 candidate' not in staged[n]
        first=staged[n].find(b'\n')+1
        staged[n]=staged[n][:first]+b'\n'+status+b'\n'+staged[n][first:]
    row=re.search(r'^\| 12 \|.*$',norm(ours['PRODUCTION_PIPELINE.md']),re.M).group(0).encode()
    staged['PRODUCTION_PIPELINE.md'],count=re.subn(rb'^\| 12 \|[^\r\n]*',row,staged['PRODUCTION_PIPELINE.md'],count=1,flags=re.M)
    assert count==1
    bank=norm(ours['creative/ANIMATION_KNOWLEDGE_BANK.md'])
    lesson=re.search(r'^## Deepwell .*?(?=^## |\Z)',bank,re.S|re.M).group(0).strip().encode()
    assert b'## Deepwell ' not in staged['creative/ANIMATION_KNOWLEDGE_BANK.md']
    staged['creative/ANIMATION_KNOWLEDGE_BANK.md']+=b'\n\n'+lesson+b'\n'
    staged['final/12-deepwell-station/README.md']=ours['final/12-deepwell-station/README.md']
    for n,marker in [('.gitattributes',b'\n# Deepwell checkpoint:'),('.gitignore',b'\n# User-requested complete Deepwell checkpoint,')]:
        assert marker not in staged[n]
        staged[n]+=ours[n][ours[n].index(marker):]
    for n,data in staged.items():
        oid=git('hash-object','-w','--stdin',input=data).decode().strip()
        git('update-index','--add','--cacheinfo',f'100644,{oid},{n}',env=preserved)
    # All newly introduced package paths also enter the shared index at their exact blobs.
    own_entries=git('ls-files','--stage','-z',env=own)
    for entry in own_entries.split(b'\0'):
        if not entry:continue
        info,name=entry.split(b'\t',1)
        if name.startswith(b'music/deepwell-animation-v') or name.startswith(b'music/deepwell-backup-2026-10-25/'):
            mode,oid,stage=info.split();assert stage==b'0'
            git('update-index','--add','--cacheinfo',f'{mode.decode()},{oid.decode()},{name.decode()}',env=preserved)
    assert git('ls-files','--stage','-z')==original,'Shared index changed unexpectedly'
    assert git('rev-parse','HEAD').decode().strip()==state['base_commit']
    body=H/'commit-message.txt'
    git('commit','--file',str(body),env=own)
    committed=True
    commit=git('rev-parse','HEAD').decode().strip()
    # The original index is locked by this process; publish the reconciled bytes atomically.
    with os.fdopen(fd,'wb') as f: f.write(reconciled.read_bytes())
    fd=None
    os.replace(lock,R/'.git'/'index')
    lock=None
    print(json.dumps({'commit':commit,'preserved_preexisting_staging':True,'dedicated_index':state['dedicated_index']}))
finally:
    if fd is not None:os.close(fd)
    if lock is not None and lock.exists():lock.unlink()
    if reconciled.exists() and not committed:reconciled.unlink()
