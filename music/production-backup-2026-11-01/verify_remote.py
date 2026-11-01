"""Verify fresh remote branch and fetch selected LFS payloads into an empty store."""
from pathlib import Path
import subprocess,json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=R).decode().strip()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(16*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 m=json.loads((H/'backup-manifest.json').read_text());branch=m['branch'];commit=git('rev-parse','HEAD')
 remote=git('ls-remote','--heads','origin',branch).split()[0];assert remote==commit
 cache=H/'cache/remote-lfs';assert not cache.exists(),'Fresh verification store required'
 media=[f for f in m['files'] if f['storage']=='lfs'];include=','.join(f['path'] for f in media)
 cmd=['git','-c','lfs.storage='+cache.as_posix(),'lfs','fetch','--include='+include,'--exclude=','origin',branch]
 print('Fetching',len(media),'selected media paths into a fresh verification store...',flush=True)
 subprocess.run(cmd,cwd=R,check=True)
 checked=[]
 for f in media:
  oid=f['sha256'];p=cache/'objects'/oid[:2]/oid[2:4]/oid
  assert p.stat().st_size==f['bytes'] and digest(p)==oid,('Remote LFS payload mismatch',f['path'])
  checked.append({'path':f['path'],'sha256':oid,'bytes':f['bytes'],'fresh_remote_payload_verified':True})
 remote=git('ls-remote','--heads','origin',branch).split()[0];assert remote==commit
 receipt={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'remote_head':remote,'branch':branch,'remote':git('remote','get-url','origin'),'fresh_remote_head_matches':True,'selected_lfs_paths':len(checked),'unique_lfs_objects':len({f['sha256'] for f in checked}),'all_selected_lfs_fresh_downloads_verified':True,'media':checked,'full_clone_restore_performed':False,'full_hour_exports_uploaded':False,'scope_manifest':'backup-manifest.json','unrelated_work_preserved':True}
 (H/'remote-backup-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:receipt[k] for k in ['commit','branch','fresh_remote_head_matches','selected_lfs_paths','unique_lfs_objects','all_selected_lfs_fresh_downloads_verified']}),flush=True)
if __name__=='__main__':main()
