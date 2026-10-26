"""Fetch the pushed checkpoint and download its new LFS media into isolated storage."""
from pathlib import Path
import os,subprocess,json,hashlib,sys
from datetime import datetime,timezone
H=Path(__file__).resolve().parent;R=H.parents[1]
commit=sys.argv[1];assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
def git(*args,stream=False):
    if stream:
        p=subprocess.Popen(['git','-C',str(R),*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in p.stdout:print(line.rstrip(),flush=True)
        assert p.wait()==0,'Git/LFS operation failed'
        return b''
    p=subprocess.run(['git','-C',str(R),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def blob(path):
    h=hashlib.sha1(f'blob {path.stat().st_size}\0'.encode())
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
manifest=json.loads((H/'backup-manifest.json').read_text());staging=json.loads((H/'staging-validation.json').read_text())
advertised=git('ls-remote','origin','refs/heads/main').decode().strip()
ref='refs/spirewatch-verification/2026-10-26'
git('fetch','--no-tags','origin',f'+{commit}:{ref}',stream=True)
assert git('rev-parse',ref).decode().strip()==commit
git('fetch','--no-tags','origin','main',stream=True)
git('merge-base','--is-ancestor',commit,'origin/main')
entries={}
for item in git('ls-tree','-r','-z',ref).split(b'\0'):
    if item:
        fields,name=item.split(b'\t',1);entries[name.decode()]=fields.split()[2].decode()
count=0;pointer_count=0
for name,record in manifest['selected_files'].items():
    p=R/name;assert sha(p)==record['sha256'] and p.stat().st_size==record['bytes'],name
    if blob(p)!=entries[name]:
        pointer=git('show',ref+':'+name).decode()
        assert f"oid sha256:{record['sha256']}\n" in pointer and f"size {record['bytes']}\n" in pointer,name
        pointer_count+=1
    count+=1
for p in H.rglob('*'):
    if p.is_file() and p.name!='remote-backup-verification.json':
        name=p.relative_to(R).as_posix();assert entries.get(name)==blob(p),name;count+=1
for name in manifest['shared_documents']:
    assert entries[name]==blob(H/'staged-shared-files'/name),name
store=R/'exports/spirewatch/remote-lfs-verification-2026-10-26'
assert not store.exists(),'Use a fresh isolated LFS verification directory'
new=[x for x in staging['lfs_records'] if x['new_lfs_asset']]
assert len(new)==2
print(f"Downloading {sum(x['bytes'] for x in new)/1024**2:.1f} MiB of selected LFS objects into fresh isolated storage...",flush=True)
git('-c','lfs.storage='+str(store),'lfs','fetch','--include='+','.join(x['path'] for x in new),'--exclude=','origin',commit,stream=True)
fetched=[]
for entry in new:
    oid=entry['sha256'];p=store/'objects'/oid[:2]/oid[2:4]/oid
    assert p.exists() and p.stat().st_size==entry['bytes'] and sha(p)==oid,entry['path']
    fetched.append({'path':entry['path'],'sha256':oid,'bytes':entry['bytes'],'fresh_remote_download_matches':True})
receipt={'verified_utc':datetime.now(timezone.utc).isoformat(),'origin':git('remote','get-url','origin').decode().strip(),'checkpoint_commit':commit,'advertised_main':advertised,'fetched_checkpoint_ref':ref,'checkpoint_reachable_from_remote_main':True,'checked_source_and_backup_files':count,'all_selected_git_blobs_or_lfs_pointers_match':True,'existing_selected_lfs_pointers_checked':pointer_count,'new_lfs_remote_downloads':fetched,'isolated_lfs_storage':str(store),'shared_notes':'Fetched checkpoint matches exact Deepwell/Snowline-preserving scoped staged snapshots','long_final_exports_remote_backed_up':False,'long_exports':manifest['long_exports_not_backed_up'],'scope':'Remote ref fetched into existing Git object store; selected new LFS media independently downloaded into empty storage and hashed. No separate full-repository clone or remote backup of the long exports is claimed.'}
(H/'remote-backup-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','commit':commit,'checked_files':count,'independently_downloaded_lfs_files':len(fetched),'long_exports':'remain local'}),flush=True)
