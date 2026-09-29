"""Restore the exact requested Saltline 4K LFS master in a fresh remote clone."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,os,stat
from render_saltline import HERE,ROOT,digest

def git(*args,cwd=ROOT):
    return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.PIPE)

def main():
    delivery=json.loads((HERE/'v7-delivery-validation.json').read_text())
    url=git('remote','get-url','origin').decode().strip()
    expected=git('rev-parse','HEAD').decode().strip()
    temp_base=Path(tempfile.gettempdir()).resolve()
    temp=Path(tempfile.mkdtemp(prefix='saltline-v7-remote-')).resolve()
    assert temp.is_relative_to(temp_base) and temp.name.startswith('saltline-v7-remote-')
    try:
        repo=temp/'repo.git';storage=temp/'fresh-lfs'
        subprocess.run(['git','clone','--bare','--depth','1','--filter=blob:none','--single-branch','--branch','main',url,str(repo)],check=True)
        head=git('rev-parse','HEAD',cwd=repo).decode().strip();assert head==expected,(head,expected)
        master=delivery['master'];sha=master['sha256']
        pointer=git('show','HEAD:'+master['path'],cwd=repo).decode()
        assert 'oid sha256:'+sha in pointer and 'size '+str(master['bytes']) in pointer
        git('config','lfs.storage',str(storage),cwd=repo)
        assert not storage.exists(), 'Fresh download must not reuse the local LFS cache'
        print('Fetching only the requested 4K LFS master into fresh storage',flush=True)
        subprocess.run(['git','lfs','fetch','origin','main','--include='+master['path'],'--exclude='],cwd=repo,check=True)
        restored=storage/'objects'/sha[:2]/sha[2:4]/sha
        assert restored.is_file() and restored.stat().st_size==master['bytes']
        assert digest(restored)==sha
        approval=json.loads(git('show','HEAD:music/saltline-animation-v1/approved-v5-preview.json',cwd=repo))
        prefix='music/saltline-animation-v1/'
        files={master['path']:sha}
        code={prefix+k:v for k,v in delivery['fingerprint']['code_sha256'].items()}
        code[prefix+'scene-plan-v7.json']=delivery['fingerprint']['config_sha256']
        code['final/05-saltline-receiver/artwork-v2-animation.png']=delivery['fingerprint']['source_sha256']
        code[approval['preview_path']]=approval['preview_sha256']
        code[prefix+'scene-plan-v5.json']=approval['config_sha256']
        code[prefix+'scene-plan-v6.json']=digest(HERE/'scene-plan-v6.json')
        code.update({v['snapshot_path']:v['sha256'] for v in approval['exact_dependency_snapshots'].values()})
        for path,wanted in code.items():
            data=git('show','HEAD:'+path,cwd=repo)
            assert hashlib.sha256(data).hexdigest()==wanted,path
            files[path]=wanted
        record={'date':'2026-09-30','remote_url':url,'remote_commit':head,'independent_fresh_bare_clone':True,
                'master_path':master['path'],'master_sha256':sha,'master_bytes':master['bytes'],
                'fresh_isolated_lfs_download':True,'restored_size_and_sha256_match':True,
                'verified_objects':files,'authorization':'User: commit and push, 2026-09-30',
                'approval_scope':'Backup authorization; v7 visual review remains pending',
                'restore':'git lfs pull --include='+master['path']+' --exclude=""; verify SHA-256 against this record',
                'local_only':'720p preview and repeated join review remain ignored reproducible outputs'}
        (HERE/'remote-backup-v7.json').write_text(json.dumps(record,indent=2)+'\n')
        delivery['media_backup']={'master':'Exact-path Git LFS uploaded and independently restored/hash-verified',
                                  'evidence':'remote-backup-v7.json','verified_remote_commit':head,
                                  'review_previews':'Local ignored files, not backed up'}
        for key in ('master','preview'):
            delivery[key]['repeated_decoded_payloads_identical']=None
            delivery[key]['repeat_identity_note']='Single cycle; three-cycle decoded payload identity was checked on the repeated 720p review file.'
        (HERE/'v7-delivery-validation.json').write_text(json.dumps(delivery,indent=2)+'\n')
        p=ROOT/'final/05-saltline-receiver/manifest.json';data=json.loads(p.read_text(encoding='utf-8'))
        data['video']['backup']='Exact-path Git LFS uploaded; fresh isolated remote download size/SHA-256 verified'
        data['video']['backup_evidence']='../../music/saltline-animation-v1/remote-backup-v7.json'
        p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        p=ROOT/'AGENTS.md';text=p.read_text(encoding='utf-8')
        text=text.replace('with independent remote restore/hash verification recorded in remote-backup-v7.json when completed.','uploaded and independently restored/hash-verified from fresh isolated LFS storage; evidence is remote-backup-v7.json.')
        p.write_text(text,encoding='utf-8')
        p=HERE/'LOOP_V7.md';text=p.read_text(encoding='utf-8')
        text=text.replace('for independent remote restore/hash evidence when completed.','for completed independent remote restore/hash evidence.')
        p.write_text(text,encoding='utf-8')
        print('4K LFS restore/hash verified, plus',len(code),'source/config/code/dependency/history blobs',flush=True)
    finally:
        assert temp.is_relative_to(temp_base) and temp.name.startswith('saltline-v7-remote-')
        def remove_readonly(function,path,error):
            assert Path(path).resolve().is_relative_to(temp)
            os.chmod(path,stat.S_IWRITE|stat.S_IREAD);function(path)
        shutil.rmtree(temp,onexc=remove_readonly)

if __name__=='__main__':main()
