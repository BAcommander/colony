"""Stage only the user-requested Deepwell checkpoint, leaving unrelated edits alone."""
from pathlib import Path
import subprocess, hashlib, json, re, os, tempfile

H=Path(__file__).resolve().parent
R=H.parents[1]
assert R==Path('G:/AI/colony')
index_path=Path(tempfile.gettempdir())/'colony-deepwell-2026-10-25.index'
assert not index_path.exists(),'Existing dedicated index: inspect before retry'
env=dict(os.environ,GIT_INDEX_FILE=str(index_path))
def git(*args,input=None):
    return subprocess.run(['git','-C',str(R),*args],env=env,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(b): return b.decode('utf-8-sig').replace('\r','')
def save(name,obj): (H/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

assert git('branch','--show-current').strip()==b'main'
base=git('rev-parse','HEAD').decode().strip()
git('read-tree','HEAD')
packages=[R/'music'/f'deepwell-animation-v{i}' for i in range(1,5)]
files=sorted(p for folder in packages for p in folder.rglob('*') if p.is_file())
assert all(p.suffix.lower() in {'.py','.json','.md','.txt','.png','.mp4'} for p in files)
assert all(p.stat().st_size<50*1024**2 for p in files)
checks=json.loads((packages[-1]/'direct-render-validation.json').read_text())
assert checks['all_selected_yuv_bytes_exact'] and checks['all_v3_manifest_files_exact']

shared=['AGENTS.md','PRODUCTION_PIPELINE.md','creative/ANIMATION_KNOWLEDGE_BANK.md','final/12-deepwell-station/README.md','.gitattributes','.gitignore']
head={name:git('show','HEAD:'+name) for name in shared}
working={name:(R/name).read_bytes() for name in shared}
authorization=' User requested commit and push on 2026-10-25: all Deepwell v1-v4 packages, including review/history media, source/configuration, validation and lessons, are selected. See music/deepwell-backup-2026-10-25/backup-manifest.json and the subsequent local remote-backup-verification.json for actual remote evidence. Backup is a checkpoint, not artistic approval.'
status=re.search(r'^Current Deepwell v4 candidate .*$',norm(working['AGENTS.md']),re.M).group(0)+authorization
for name in ['AGENTS.md','PRODUCTION_PIPELINE.md']:
    raw=working[name]
    raw,n=re.subn(rb'^Current Deepwell v4 candidate [^\r\n]*',status.encode(),raw,count=1,flags=re.M)
    assert n==1
    (R/name).write_bytes(raw)

attrs='\n# Deepwell checkpoint: preserve all source, media and hash-bound records exactly.\nmusic/deepwell-animation-v[1-4]/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\nmusic/deepwell-backup-2026-10-25/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n'
ignore='\n# User-requested complete Deepwell checkpoint, 2026-10-25.\n!music/deepwell-animation-v[1-4]/**/*.mp4\n/music/deepwell-backup-2026-10-25/remote-backup-verification.json\n'
for name,extra in [('.gitattributes',attrs),('.gitignore',ignore)]:
    assert 'Deepwell checkpoint' not in norm(working[name]) and 'complete Deepwell checkpoint' not in norm(working[name])
    (R/name).write_bytes(working[name]+extra.encode())

staged={}
for name in ['AGENTS.md','PRODUCTION_PIPELINE.md']:
    first=head[name].find(b'\n')+1
    staged[name]=head[name][:first]+b'\n'+status.encode()+b'\n'+head[name][first:]
row=re.search(r'^\| 12 \|.*$',norm(working['PRODUCTION_PIPELINE.md']),re.M).group(0).encode()
staged['PRODUCTION_PIPELINE.md'],n=re.subn(rb'^\| 12 \|[^\r\n]*',row,staged['PRODUCTION_PIPELINE.md'],count=1,flags=re.M)
assert n==1
bank=norm(working['creative/ANIMATION_KNOWLEDGE_BANK.md'])
lesson=re.search(r'^## Deepwell .*?(?=^## |\Z)',bank,re.S|re.M).group(0).strip()
assert '## Deepwell ' not in norm(head['creative/ANIMATION_KNOWLEDGE_BANK.md'])
staged['creative/ANIMATION_KNOWLEDGE_BANK.md']=head['creative/ANIMATION_KNOWLEDGE_BANK.md']+b'\n\n'+lesson.encode()+b'\n'
staged['final/12-deepwell-station/README.md']=working['final/12-deepwell-station/README.md']
staged['.gitattributes']=head['.gitattributes']+attrs.encode()
staged['.gitignore']=head['.gitignore']+ignore.encode()

manifest={'date':'2026-10-25','base_commit':base,'authorization':'User: commit and push','scope':'Complete authored Deepwell v1-v4 animation packages, review/history media, frozen dependencies and scoped project lessons. No unrelated scene edits staged.','ordinary_git_media':True,'largest_file_bytes':max(p.stat().st_size for p in files),'package_files':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files},'shared_files':list(staged),'artistic_status':'V4 review pending; previous visibility feedback preserved; backup is not acceptance','remote_verification':'remote-backup-verification.json is generated locally only after push and independent fetch'}
save('backup-manifest.json',manifest)
(H/'README.md').write_text('# Deepwell checkpoint — 2026-10-25\n\nUser requested commit and push. This backup selects the complete Deepwell v1–v4 packages, including original/planet artwork, frozen renderer dependencies, configuration, masks, diagnostics, exact feedback, current and historical short videos, and validation evidence. The six shared project files are staged from HEAD with only Deepwell additions; unrelated working edits remain unstaged. Files are below 50 MiB and use ordinary Git with exact-byte attributes.\n\nThe delivery manifests remain frozen historical records. Their statements about local-only status describe the delivery time. See backup-manifest.json for selected bytes and the later local remote-backup-verification.json for fetched remote evidence. No 4K, music or new assembly is implied. User v4 artistic verdict remains pending.\n',encoding='utf-8')
preview=H/'staged-shared-files'
for name,data in staged.items():
    p=preview/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    oid=git('hash-object','-w','--stdin',input=data).strip().decode()
    git('update-index','--add','--cacheinfo',f'100644,{oid},{name}')
git('add','-f','--',*[p.relative_to(R).as_posix() for p in packages],H.relative_to(R).as_posix())
entries={}
for line in git('ls-files','--stage','-z').split(b'\0'):
    if line:
        info,name=line.split(b'\t',1);entries[name.decode()]=info.split()[1].decode()
for p in files:
    data=p.read_bytes();expected=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
    assert entries[p.relative_to(R).as_posix()]==expected,p
for name,data in staged.items():
    assert git('show',':'+name)==data,name
selected=git('diff','--cached','--name-only').decode().splitlines()
assert all(n in shared or n.startswith('music/deepwell-animation-v') or n.startswith('music/deepwell-backup-2026-10-25/') for n in selected)
save('staging-validation.json',{'base_commit':base,'dedicated_index':str(index_path),'selected_count':len(selected),'package_file_count':len(files),'package_bytes':sum(p.stat().st_size for p in files),'all_package_blobs_exact':True,'scoped_shared_blobs_exact':True,'paths':selected})
git('add','-f','--',(H/'staging-validation.json').relative_to(R).as_posix())
print(json.dumps({'staged_files':len(selected)+1,'package_files':len(files),'package_MiB':round(sum(p.stat().st_size for p in files)/1024**2,2),'all_package_blobs_exact':True,'shared_note_scope':'Deepwell only','base':base}))
