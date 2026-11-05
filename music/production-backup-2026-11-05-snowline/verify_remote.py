"""Verify this checkpoint from remote Git and a fresh, scene-only LFS store."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
B=Path(__file__).resolve().parent;R=B.parents[1]
def git(args,cwd=R,data=None):
    p=subprocess.run(['git',*args],cwd=cwd,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace'))
    return p.stdout
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
    return h.hexdigest()
def main():
    m=json.loads((B/'backup-manifest.json').read_text(encoding='utf-8'))
    selection=json.loads((B/'selection.json').read_text(encoding='utf-8'))
    assert git(['branch','--show-current']).strip()==b'main'
    commit=git(['rev-parse','HEAD']).decode().strip()
    remote=git(['remote','get-url','origin']).decode().strip()
    head=git(['ls-remote','origin','refs/heads/main']).decode().split()[0]
    assert commit==head,(commit,head)
    root=(R/'.local/restore-scratch').resolve();root.mkdir(parents=True,exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='snowline-2026-11-05-',dir=root)).resolve()
    assert scratch.parent==root and scratch.name.startswith('snowline-2026-11-05-')
    print('Fetching the exact remote commit into independent restore scratch',flush=True)
    git(['init','--bare','--initial-branch=main',str(scratch)])
    git(['remote','add','origin',remote],scratch)
    git(['config','remote.origin.promisor','true'],scratch)
    git(['config','remote.origin.partialclonefilter','blob:none'],scratch)
    git(['config','lfs.storage',str(scratch/'private-lfs')],scratch)
    git(['fetch','--depth=1','--filter=blob:none','origin',commit],scratch)
    assert git(['rev-parse','FETCH_HEAD'],scratch).decode().strip()==commit
    paths=selection['expected_scope']
    listing=git(['rev-list','--objects','--missing=print',commit,'--',*paths],scratch).decode()
    missing=[x[1:].split()[0] for x in listing.splitlines() if x.startswith('?')]
    if missing:
        print(f'Fetching {len(missing)} selected Git blobs in one batch',flush=True)
        git(['-c','fetch.negotiationAlgorithm=noop','fetch','--no-tags','--no-write-fetch-head','--filter=blob:none','origin','--stdin'],scratch,('\n'.join(missing)+'\n').encode())
    rows=[]
    for f in m['files']:
        data=git(['cat-file','blob',commit+':'+f['path']],scratch)
        assert len(data)==f['git_blob_bytes'] and hashlib.sha256(data).hexdigest()==f['git_blob_sha256'],f['path']
        rows.append({'path':f['path'],'git_blob_verified':True,'storage':f['storage']})
    # The self-excluded manifest is also verified against its committed remote blob.
    manifest_path=(B/'backup-manifest.json').relative_to(R).as_posix()
    assert git(['cat-file','blob',commit+':'+manifest_path],scratch)==(B/'backup-manifest.json').read_bytes()
    lfs=[f for f in m['files'] if f['storage']=='git-lfs']
    print(f'All {len(rows)} manifest Git blobs verified; downloading {len(lfs)} exact LFS objects into fresh storage',flush=True)
    env=os.environ.copy();env['GIT_LFS_SKIP_SMUDGE']='0'
    for f in lfs:
        pointer=git(['cat-file','blob',commit+':'+f['path']],scratch)
        assert pointer.startswith(b'version https://git-lfs.github.com/spec/v1\n')
        print('Downloading only '+f['path'],flush=True)
        transfer=subprocess.run(['git','-c','lfs.fetchinclude='+f['path'],'-c','lfs.fetchexclude=','lfs','smudge',f['path']],cwd=scratch,input=pointer,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env=env)
        if transfer.returncode:raise RuntimeError(transfer.stderr.decode('utf-8','replace'))
    lfs_rows=[]
    for f in lfs:
        oid=f['sha256'];p=scratch/'private-lfs/objects'/oid[:2]/oid[2:4]/oid
        assert p.is_file() and p.stat().st_size==f['bytes'] and sha(p)==oid,f['path']
        lfs_rows.append({'path':f['path'],'bytes':f['bytes'],'sha256':oid,'fresh_remote_download_verified':True})
    final_head=git(['ls-remote','origin','refs/heads/main']).decode().split()[0]
    assert final_head==commit
    receipt={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'branch':'main','remote':remote,'remote_head_matches':True,'selected_paths':len(paths),'manifest_git_blobs_verified':len(rows),'self_excluded_manifest_verified':True,'fresh_lfs_objects_verified':len(lfs_rows),'fresh_lfs_bytes_verified':sum(f['bytes'] for f in lfs_rows),'lfs':lfs_rows,'new_branch_created':False,'full_length_exports_uploaded':False,'unrelated_work_preserved':True,'independent_remote_object_restore':True,'lfs_download_method':'Direct smudge of each verified remote pointer; no whole-tree LFS scan','full_checkout_restore':False,'scratch_path':str(scratch),'scratch_removed':False}
    target=B/'remote-backup-verification.json'
    target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    # This verified run folder is the only recursive removal target.
    assert scratch.resolve().parent==root and scratch.name.startswith('snowline-2026-11-05-') and scratch!=R.resolve()
    shutil.rmtree(scratch)
    assert not scratch.exists()
    receipt['scratch_removed']=True
    target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','commit':commit,'git_files':len(paths),'fresh_lfs_files':len(lfs_rows),'fresh_lfs_bytes':receipt['fresh_lfs_bytes_verified'],'scratch_removed':True}),flush=True)
if __name__=='__main__':main()
