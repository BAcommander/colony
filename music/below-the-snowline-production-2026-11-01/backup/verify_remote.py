"""Confirm remote commit and freshly download every selected LFS object."""
from pathlib import Path
import hashlib,json,subprocess,datetime
H=Path(__file__).resolve().parent;R=H.parents[2]
def git(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((H/'backup-manifest.json').read_text());branch=m['branch'];commit=git('rev-parse','HEAD')
assert git('ls-remote','--heads','origin',branch).split()[0]==commit
cache=H/'cache/remote-lfs';assert not cache.exists()
media=[f for f in m['files'] if f['storage']=='lfs']
subprocess.run(['git','-c','lfs.storage='+cache.as_posix(),'lfs','fetch','--include='+','.join(f['path'] for f in media),'--exclude=','origin',branch],cwd=R,check=True)
for f in media:
    oid=f['sha256'];p=cache/'objects'/oid[:2]/oid[2:4]/oid
    assert p.stat().st_size==f['bytes'] and sha(p)==oid
for f in m['files']:
    if f['storage']=='git':
        blob=subprocess.check_output(['git','show',commit+':'+f['path']],cwd=R)
        assert hashlib.sha256(blob).hexdigest()==f['sha256']
assert git('ls-remote','--heads','origin',branch).split()[0]==commit
receipt={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'branch':branch,'remote_head_matches':True,'remote':git('remote','get-url','origin'),'fresh_lfs_objects_verified':len(media),'media_bytes':sum(f['bytes'] for f in media),'all_manifest_git_blobs_verified':True,'official_hoth_audio_uploaded':False,'shared_main_modified':False,'full_restore_performed':False}
(H/'remote-backup-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
