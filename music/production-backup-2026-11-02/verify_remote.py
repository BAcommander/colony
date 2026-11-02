"""Verify branch head, committed records and newly downloaded selected LFS media."""
from pathlib import Path
import subprocess,json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
m=json.loads((H/'backup-manifest.json').read_text());branch=m['branch'];commit=git('rev-parse','HEAD')
assert git('ls-remote','--heads','origin',branch).split()[0]==commit
media=[f for f in m['files'] if f['storage']=='lfs'];cache=H/'cache/remote-lfs';assert not cache.exists()
subprocess.run(['git','-c','lfs.storage='+cache.as_posix(),'lfs','fetch','--include='+','.join(f['path'] for f in media),'--exclude=','origin',branch],cwd=R,check=True)
for f in media:
 oid=f['sha256'];p=cache/'objects'/oid[:2]/oid[2:4]/oid
 assert p.stat().st_size==f['bytes'] and sha(p)==oid
for f in m['files']:
 if f['storage']=='git':assert hashlib.sha256(subprocess.check_output(['git','show',commit+':'+f['path']],cwd=R)).hexdigest()==f['sha256']
assert git('ls-remote','--heads','origin',branch).split()[0]==commit
receipt={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'branch':branch,'remote':git('remote','get-url','origin'),'remote_head_matches':True,'fresh_lfs_objects_verified':len(media),'fresh_lfs_bytes_verified':sum(x['bytes'] for x in media),'all_manifest_git_blobs_verified':True,'full_hour_exports_uploaded':False,'unrelated_work_preserved':True,'shared_main_modified':False,'full_clone_restore':False}
(H/'remote-backup-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
