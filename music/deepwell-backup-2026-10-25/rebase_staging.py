"""Refresh dedicated staging on the latest HEAD, keeping concurrent commits."""
from pathlib import Path
import os,subprocess,re,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1]
state=json.loads((H/'staging-validation.json').read_text())
env=dict(os.environ,GIT_INDEX_FILE=state['dedicated_index'])
def git(*args,input=None):
    p=subprocess.run(['git','-C',str(R),*args],env=env,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return p.stdout
def norm(b):return b.decode('utf-8-sig').replace('\r','')
base=git('rev-parse','HEAD').decode().strip()
assert base!=state['base_commit']
shared=json.loads((H/'backup-manifest.json').read_text())['shared_files']
ours={n:git('show',':'+n) for n in shared}
head={n:git('show','HEAD:'+n) for n in shared}
staged=dict(head)
status=re.search(r'^Current Deepwell v4 candidate .*$',norm(ours['AGENTS.md']),re.M).group(0).encode()
for n in ['AGENTS.md','PRODUCTION_PIPELINE.md']:
    assert b'Current Deepwell v4 candidate' not in head[n]
    first=head[n].find(b'\n')+1
    staged[n]=head[n][:first]+b'\n'+status+b'\n'+head[n][first:]
row=re.search(r'^\| 12 \|.*$',norm(ours['PRODUCTION_PIPELINE.md']),re.M).group(0).encode()
staged['PRODUCTION_PIPELINE.md'],count=re.subn(rb'^\| 12 \|[^\r\n]*',row,staged['PRODUCTION_PIPELINE.md'],count=1,flags=re.M);assert count==1
bank=norm(ours['creative/ANIMATION_KNOWLEDGE_BANK.md'])
lesson=re.search(r'^## Deepwell .*?(?=^## |\Z)',bank,re.S|re.M).group(0).strip().encode()
assert b'## Deepwell ' not in head['creative/ANIMATION_KNOWLEDGE_BANK.md']
staged['creative/ANIMATION_KNOWLEDGE_BANK.md']=head['creative/ANIMATION_KNOWLEDGE_BANK.md']+b'\n\n'+lesson+b'\n'
staged['final/12-deepwell-station/README.md']=ours['final/12-deepwell-station/README.md']
for n,marker in [('.gitattributes',b'\n# Deepwell checkpoint:'),('.gitignore',b'\n# User-requested complete Deepwell checkpoint,')]:
    assert marker not in head[n];staged[n]=head[n]+ours[n][ours[n].index(marker):]
git('read-tree','HEAD')
for n,data in staged.items():
    (H/'staged-shared-files'/n).write_bytes(data)
    oid=git('hash-object','-w','--stdin',input=data).decode().strip()
    git('update-index','--add','--cacheinfo',f'100644,{oid},{n}')
manifest=json.loads((H/'backup-manifest.json').read_text());manifest['base_commit']=base
(H/'backup-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
git('add','-f','--',*[f'music/deepwell-animation-v{i}' for i in range(1,5)],H.relative_to(R).as_posix())
for n,record in manifest['package_files'].items():
    data=(R/n).read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256']
    oid=git('rev-parse',':'+n).decode().strip()
    assert oid==hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),n
selected=git('diff','--cached','--name-only').decode().splitlines()
assert all(n in shared or n.startswith('music/deepwell-animation-v') or n.startswith('music/deepwell-backup-2026-10-25/') for n in selected)
assert git('rev-parse','HEAD').decode().strip()==base
state.update(base_commit=base,selected_count=len(selected),paths=selected,concurrent_commit_preserved=True)
(H/'staging-validation.json').write_text(json.dumps(state,indent=2)+'\n')
git('add','-f','--',(H/'staging-validation.json').relative_to(R).as_posix())
print(json.dumps({'base':base,'staged_files':len(selected),'exact_package_files':len(manifest['package_files']),'concurrent_commit_preserved':True}))
