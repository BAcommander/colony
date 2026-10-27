"""Commit the dedicated index and retain any unrelated shared-index staging."""
from pathlib import Path
import os,sys,subprocess,json,tempfile,shutil
H=Path(__file__).resolve().parent;R=H.parents[1]
state=json.loads((H/'staging-validation.json').read_text())
own=dict(os.environ,GIT_INDEX_FILE=state['dedicated_index'])
def git(*args,env=None,input=None):
    p=subprocess.run(['git','-C',str(R),*args],env=env,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def indexmap(data):
    out={}
    for entry in data.split(b'\0'):
        if entry:
            fields,name=entry.split(b'\t',1);mode,oid,stage=fields.split();assert stage==b'0'
            out[name.decode()]=(mode.decode(),oid.decode())
    return out
assert git('rev-parse','HEAD').decode().strip()==state['base_commit'],'HEAD changed: refresh dedicated staging before committing'
assert git('branch','--show-current').strip()==b'main'
lock=R/'.git/index.lock';assert lock.resolve().parent==(R/'.git').resolve()
fd=os.open(str(lock),os.O_CREAT|os.O_EXCL|os.O_WRONLY)
work=Path(tempfile.mkdtemp(prefix='spirewatch-index-'));reconciled=work/'index'
committed=False
try:
    original=git('ls-files','--stage','-z');current=indexmap(original)
    selected=git('diff','--cached','--name-only','-z',env=own).decode().strip('\0').split('\0')
    desired=indexmap(git('ls-files','--stage','-z',env=own))
    base={}
    for entry in git('ls-tree','-r','-z',state['base_commit']).split(b'\0'):
        if entry:
            fields,name=entry.split(b'\t',1);mode,kind,oid=fields.split()
            base[name.decode()]=(mode.decode(),oid.decode())
    shutil.copyfile(R/'.git/index',reconciled)
    combined=dict(os.environ,GIT_INDEX_FILE=str(reconciled));updates=[]
    for name in selected:
        wanted=desired[name];old=base.get(name);existing=current.get(name)
        if existing==wanted:continue
        if existing==old:
            result=wanted
        elif wanted==old:
            continue
        elif old is not None and existing is not None:
            parts=[]
            for label,entry in [('current',existing),('base',old),('new',wanted)]:
                data=git('cat-file','blob',entry[1]);assert b'\0' not in data,('Concurrent binary edit',name)
                p=work/label;p.write_bytes(data);parts.append(str(p))
            merge=subprocess.run(['git','merge-file','-p',*parts],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            assert merge.returncode==0,('Concurrent shared-file conflict; original staging retained',name)
            oid=git('hash-object','-w','--stdin',input=merge.stdout).decode().strip();result=(wanted[0],oid)
        else:raise RuntimeError('Concurrent selected-path edit: '+name)
        updates.append(f'{result[0]} {result[1]}\t{name}\0'.encode())
    git('update-index','-z','--index-info',env=combined,input=b''.join(updates))
    assert git('ls-files','--stage','-z')==original,'Default index changed unexpectedly'
    assert git('rev-parse','HEAD').decode().strip()==state['base_commit']
    tree=git('write-tree',env=own).decode().strip()
    git('commit','--file',str(H/'commit-message.txt'),env=own)
    committed=True;commit=git('rev-parse','HEAD').decode().strip()
    assert git('rev-parse','HEAD^').decode().strip()==state['base_commit']
    assert git('rev-parse','HEAD^{tree}').decode().strip()==tree
    with os.fdopen(fd,'wb') as stream:stream.write(reconciled.read_bytes())
    fd=None;os.replace(lock,R/'.git/index');lock=None
    print(json.dumps({'commit':commit,'tree':tree,'selected_files':len(selected),'unrelated_staging_preserved':True}),flush=True)
finally:
    if fd is not None:os.close(fd)
    if lock is not None and lock.exists():lock.unlink()
    # Small temporary index/merge files remain outside the repository for recovery.
