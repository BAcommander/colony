from pathlib import Path
import subprocess,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 manifest=json.loads((H/'backup-manifest.json').read_text())
 selected=set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''}
 expected={x['path'] for x in manifest['files']}
 assert expected<=selected
 assert all(p in expected or p.startswith('music/empty-junction-backup-2026-11-01/') for p in selected)
 p=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 results=[]
 for item in manifest['files']:
  path=item['path'];raw=(R/path).read_bytes();item.update(bytes=len(raw),sha256=digest(raw))
  p.stdin.write((':'+path+'\n').encode());p.stdin.flush();header=p.stdout.readline().split();assert header[1]==b'blob'
  blob=p.stdout.read(int(header[2]));assert p.stdout.read(1)==b'\n'
  if item['storage']=='lfs':
   assert f'oid sha256:{digest(raw)}\n'.encode() in blob and f'size {len(raw)}\n'.encode() in blob
   oid=digest(raw);obj=R/'.git/lfs/objects'/oid[:2]/oid[2:4]/oid
   assert obj.exists() and digest(obj.read_bytes())==oid
  elif blob!=raw:
   assert path in ['.gitignore','.gitattributes','PRODUCTION_PIPELINE.md'],path
   assert blob==raw.replace(b'\r\n',b'\n'),path
   item['git_stored_sha256']=digest(blob);item['line_endings']='Git text normalization; fingerprinted source packages remain exact'
  results.append({'path':path,'index_blob_oid':header[0].decode(),'stored_sha256':digest(blob),'working_sha256':digest(raw),'storage':item['storage']})
 p.stdin.close();assert p.wait()==0
 manifest['bytes']=sum(x['bytes'] for x in manifest['files'])
 (H/'backup-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (H/'staged-content-verification.json').write_text(json.dumps({'all_manifest_assets_match_index':True,'verified_assets':len(results),'lfs_local_objects_checked':sum(x['storage']=='lfs' for x in results),'files':results},indent=2)+'\n')
 print('Verified',len(results),'manifest assets against staged blobs and LFS objects; scope contains no unrelated work.')
if __name__=='__main__':main()
