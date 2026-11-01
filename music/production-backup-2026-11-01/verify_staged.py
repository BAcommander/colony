"""Verify selected staged bytes and LFS payloads before the requested backup."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 selection=json.loads((H/'selection.json').read_text());selected=set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''}
 expected=set(selection['selected_paths'])
 assert expected<=selected,expected-selected
 assert all(p in expected or p.startswith('music/production-backup-2026-11-01/') for p in selected)
 assert not any(p.startswith('exports/') or '/cache/' in p or '/verification-cache/' in p for p in selected)
 media=set(selection['lfs_paths']);records=[];images=0
 proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for name in sorted(selected):
  if name.endswith(('backup-manifest.json','staged-content-verification.json')):continue
  p=R/name;raw=p.read_bytes();digest=sha(raw)
  proc.stdin.write((':'+name+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().split();assert header[1]==b'blob'
  blob=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
  row={'path':name,'bytes':len(raw),'sha256':digest,'storage':'lfs' if name in media else 'git','index_blob_oid':header[0].decode(),'git_stored_sha256':sha(blob)}
  if name in media:
   assert f'oid sha256:{digest}\n'.encode() in blob and f'size {len(raw)}\n'.encode() in blob
   obj=R/'.git/lfs/objects'/digest[:2]/digest[2:4]/digest;assert sha(obj.read_bytes())==digest
  elif blob!=raw:
   assert not any(name.startswith(s+'/') for s in selection['scopes']),('Fingerprinted package normalization',name)
   assert blob==raw.replace(b'\r\n',b'\n'),('Unexpected staging mutation',name)
   row['normalization']='Standard Git CRLF-to-LF outside frozen packages'
  if p.suffix.lower() in ['.png','.jpg','.jpeg']:
   with Image.open(p) as im:im.load();row['dimensions']=list(im.size)
   images+=1
  if name not in media:assert len(blob)<100_000_000,('Oversized non-LFS object',name)
  records.append(row)
 proc.stdin.close();assert proc.wait()==0
 result={'date':'2026-11-01','requested':selection['request'],'base_commit':selection['base_commit'],'branch':selection['branch'],'files':records,'file_count':len(records),'lfs_files':len(media),'lfs_unique_objects':len({x['sha256'] for x in records if x['storage']=='lfs'}),'bytes':sum(x['bytes'] for x in records),'images_fully_decoded':images,'all_selected_staged_bytes_verified':True,'all_lfs_local_payloads_verified':True,'exclusions':selection['exclusions'],'self_exclusion':'This manifest is staged after verification; it does not recursively hash itself.','remote_verified':False}
 (H/'backup-manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:result[k] for k in ['file_count','lfs_files','lfs_unique_objects','bytes','images_fully_decoded','all_selected_staged_bytes_verified']}))
if __name__=='__main__':main()
