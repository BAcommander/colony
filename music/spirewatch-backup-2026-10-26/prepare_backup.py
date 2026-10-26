"""Prepare a precise Spirewatch Git/LFS checkpoint in a dedicated index."""
from pathlib import Path
import sys,os,subprocess,json,re,hashlib,shutil,tempfile
H=Path(__file__).resolve().parent;R=H.parents[1];assert R==Path('G:/AI/colony')
INDEX=Path(tempfile.gettempdir())/'colony-spirewatch-2026-10-26.index'
refresh='--refresh' in sys.argv
assert refresh or not INDEX.exists(),'Dedicated index already exists; inspect before refreshing'
ENV=dict(os.environ,GIT_INDEX_FILE=str(INDEX))
def git(*args,input=None,env=ENV):
    p=subprocess.run(['git','-C',str(R),*args],input=input,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def blob_sha1(path):
    h=hashlib.sha1(f'blob {path.stat().st_size}\0'.encode())
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def norm(data):return data.decode('utf-8-sig').replace('\r','')
def save(name,obj):(H/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def line(data,pattern):
    m=re.search(pattern,norm(data),re.M);assert m,pattern
    return m.group(0).encode()
def section(data,heading):
    m=re.search(r'^## '+re.escape(heading)+r'.*?(?=^## |\Z)',norm(data),re.S|re.M);assert m,heading
    return m.group(0).strip().encode()
def replace_line(data,pattern,replacement):
    out,n=re.subn(pattern,lambda m:replacement,data,count=1,flags=re.M);assert n==1,pattern
    return out

base=git('rev-parse','HEAD').decode().strip();assert git('branch','--show-current').strip()==b'main'
shared=['AGENTS.md','PRODUCTION_PIPELINE.md','creative/MUSIC_WORKFLOW.md','creative/ANIMATION_KNOWLEDGE_BANK.md','final/local-export-inventory.json','.gitattributes','.gitignore']
head={n:git('show','HEAD:'+n) for n in shared}
receipt=[]
note=' Backup requested 2026-10-26: all authored Spirewatch source/art/configuration, original music generations, prompts, accepted joins, production recipes and lessons selected; exact 4K minute and intro review use Git LFS. Long exports and regenerable render/repeat caches remain local under project media policy. See music/spirewatch-backup-2026-10-26/backup-manifest.json and subsequent local remote-backup-verification.json for actual scope/evidence. Delivery-time local-only statements are historical; no full-length artistic approval is inferred.'
for name in ['AGENTS.md','PRODUCTION_PIPELINE.md','creative/MUSIC_WORKFLOW.md']:
    path=R/name;old=path.read_bytes();new=old
    for pattern in [rb'^Current Spirewatch final production [^\r\n]*',rb'^Current Illuminated Horizon / Stillness soundtrack [^\r\n]*']:
        match=re.search(pattern,new,re.M)
        if match and b'Backup requested 2026-10-26:' not in match.group():
            new=new[:match.start()]+match.group()+note.encode()+new[match.end():]
    if name=='creative/MUSIC_WORKFLOW.md' and b'## Spirewatch checkpoint lessons' not in new:
        new+=b'\n\n## Spirewatch checkpoint lessons - 2026-10-26\n\n'+('The separate Stillness composition and accepted two-direction joins became the workable arrangement; failed stretching, spectral drone, separation and short-reference workarounds remain failed experiments. Preserve fixed source gains, eight-second overlaps, the unfaded soundtrack opening for the once-only intro and the existing closing fade. Source-reference guidance is not literal extension or selective groove removal. Exact decisions, limitations, durable settings and final production evidence are retained in ../music/spirewatch-backup-2026-10-26/LESSONS.md. Full two-hour user playback/upload checks remain pending.\n').encode()
    if new!=old:
        assert path.read_bytes()==old;path.write_bytes(new)
        receipt.append({'path':name,'before':hashlib.sha256(old).hexdigest(),'after':hashlib.sha256(new).hexdigest(),'scope':'Only current Spirewatch/music backup request, plus scoped Music Workflow lesson'})
path=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';old=path.read_bytes()
if b'## Spirewatch production checkpoint - 2026-10-26' not in old:
    text='\n\n## Spirewatch production checkpoint - 2026-10-26\n\nCarry forward the bright frozen source before masks, complete emitter/aperture coverage, separate illumination/transport silhouette margins, foundation protection, peak-frame inspection and retained-layer controls. For final assembly, preserve the exact native-to-4K master, use the hash-verified current intro release, complete sparse colour tags with the tool helper, keep the intro outside the repeating loop, and validate decoded pictures, copied packets, every timestamp and the full audio envelope. Long MP4 finalization can continue after media-time progress reaches the end. Consolidated artistic and technical lessons, exact settings and evidence limits: ../music/spirewatch-backup-2026-10-26/LESSONS.md. These are production learnings, not new claims of full playback approval.\n'
    path.write_bytes(old+text.encode());receipt.append({'path':str(path.relative_to(R)),'scope':'Appended only scoped Spirewatch checkpoint lesson'})
if receipt:save('memory-update.json',receipt)

# Preserve the additional user-generated reference candidates, not only their hashes.
generated=H/'generated-sources';generated.mkdir(exist_ok=True)
originals=[('Open_Skyline_2026-10-25T225849.mp4',None),('Nightfall_Across_Glass_2026-10-25T225849.mp4',None),('TODO_-_Vast_Unfamiliar_World_2026-10-10T192538 (1).mp4','ff13a9de84cc31c08e306304bbbe19473252b98efa1607c8bd1394af3525ca20')]
preserved=[]
for filename,expected in originals:
    source=Path('C:/Users/jazzs/Downloads')/filename;target=generated/filename
    digest=sha(source)
    if expected:assert digest==expected
    if not target.exists():shutil.copy2(source,target)
    assert sha(target)==digest
    preserved.append({'source':str(source),'copy':target.relative_to(H).as_posix(),'sha256':digest,'bytes':target.stat().st_size})
save('additional-source-preservation.json',preserved)
save('feedback-and-approval.json',{'date':'2026-10-26','backup_request':"ok commit and push all the Spirewatch work and save everything we've learnt to memory, how are you feeling about this?",'feedback':[{'stage':'reference-guided tests','user':'both of them still see to have the underlying beat right?','setting':'User later confirms minimum Influence; exact numeric setting not independently recorded'},{'stage':'slow excerpt workaround','user':"ok that doesn't really work either",'result':'User proposes a separate companion track'},{'stage':'Stillness 30s','user':'this has potential'},{'stage':'long Stillness joins','user':"yeah those transitions sound good, can we make an 2-hour long version alternating between illuminated horizon and illuminated stillness?"},{'stage':'final video','user':'ok can we use our tool to make the final 2 hour 4k Spirewatch video with this music and our intro?'}],'limits':'Short joins accepted; final assembly requested. No full two-hour listening or detailed new motion verdict inferred. New source generations were supplied by user; no assistant paid generation.'})

direction=R/'music/digital-city-concepts-v1/current-direction.json';state=json.loads(direction.read_text())
final=json.loads((R/'music/spirewatch-final-two-hours-v1/delivery-validation.json').read_text());assert final['status']=='passed'
state.update(date='2026-10-26',status='Final two-hour 4K Spirewatch with current intro and alternating Horizon/Stillness delivered and technically verified; full combined review/upload checks pending',music_direction='Illuminated Horizon plus standalone Illuminated Stillness companion',long_audio_selected=True,user_authorized_for_final_assembly=True,final_assembly_record='music/spirewatch-final-two-hours-v1/delivery-validation.json',final_video='exports/spirewatch/Spirewatch-2-Hours-4K-v1.mp4',final_video_sha256=final['sha256'],music_record='music/illuminated-horizon-stillness-two-hours-v1/delivery-validation.json',backup_request='2026-10-26: authored Spirewatch work, original music, exact short masters and lessons; long exports remain local',animation_4k_backup_record='music/spirewatch-backup-2026-10-26/remote-backup-verification.json')
state.pop('animation_4k_backed_up',None)
direction.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')

working={n:(R/n).read_bytes() for n in shared}
staged={}
current_spire=line(working['AGENTS.md'],r'^Current Spirewatch final production .*$')
current_music=line(working['AGENTS.md'],r'^Current Illuminated Horizon / Stillness soundtrack .*$')
old4k=line(working['AGENTS.md'],r'^Historical Spirewatch v8 4K delivery .*$')
new=head['AGENTS.md'];first=new.find(b'\n')+1
new=new[:first]+b'\n'+current_spire+b'\n\n'+old4k+b'\n'+new[first:]
new=replace_line(new,rb'^Current Spirewatch v8 \(2026-10-21\):[^\r\n]*',line(head['AGENTS.md'],r'^Current Spirewatch v8 \(2026-10-21\):.*$').replace(b'Current Spirewatch',b'Historical Spirewatch',1))
old_music=line(head['AGENTS.md'],r'^Current Illuminated Horizon / ambient-middle experiment .*$')
staged['AGENTS.md']=replace_line(new,rb'^Current Illuminated Horizon / ambient-middle experiment [^\r\n]*',current_music+b'\n\n'+old_music.replace(b'Current Illuminated',b'Historical Illuminated',1))
new=head['PRODUCTION_PIPELINE.md'];old_music=line(new,r'^(?:Current )?Illuminated Horizon / ambient-middle experiment .*$')
new=replace_line(new,rb'^(?:Current )?Illuminated Horizon / ambient-middle experiment [^\r\n]*',current_music+b'\n\n'+b'Historical '+old_music)
old_spire=line(new,r'^2026-10-21: \[V8 finishing pass\].*$')
staged['PRODUCTION_PIPELINE.md']=replace_line(new,rb'^2026-10-21: \[V8 finishing pass\][^\r\n]*',current_spire+b'\n\n'+old4k+b'\n\nHistorical finishing checkpoint: '+old_spire)
new=head['creative/MUSIC_WORKFLOW.md'];old_music=line(new,r'^(?:Current )?Illuminated Horizon / ambient-middle experiment .*$')
new=replace_line(new,rb'^(?:Current )?Illuminated Horizon / ambient-middle experiment [^\r\n]*',current_music+b'\n\nHistorical '+old_music)
new+=b'\n\n'+section(working['creative/MUSIC_WORKFLOW.md'],'Separate companion-track arrangement')+b'\n\n'+section(working['creative/MUSIC_WORKFLOW.md'],'Spirewatch checkpoint lessons')+b'\n'
staged['creative/MUSIC_WORKFLOW.md']=new
staged['creative/ANIMATION_KNOWLEDGE_BANK.md']=head['creative/ANIMATION_KNOWLEDGE_BANK.md']+b'\n\n'+section(working['creative/ANIMATION_KNOWLEDGE_BANK.md'],'Spirewatch final assembly and preserved intro')+b'\n\n'+section(working['creative/ANIMATION_KNOWLEDGE_BANK.md'],'Spirewatch production checkpoint')+b'\n'
inventory=json.loads(head['final/local-export-inventory.json']);actual=json.loads(working['final/local-export-inventory.json'])
for entry in actual['files']:
    if entry['path'].startswith('exports/spirewatch/'):
        existing=[x for x in inventory['files'] if x['path']==entry['path']]
        if existing:assert existing[0]==entry
        else:inventory['files'].append(entry)
inventory['date']='2026-10-26'
inventory_text=(json.dumps(inventory,indent=2)+'\n').encode()
inventory_eol=re.search(rb'\r*\n',head['final/local-export-inventory.json']).group(0)
staged['final/local-export-inventory.json']=inventory_text.replace(b'\n',inventory_eol)

master='music/spirewatch-animation-v8/delivery-4k-v1/Spirewatch-v8-60s-4K-loop.mp4'
opening='music/spirewatch-final-two-hours-v1/Spirewatch-opening-review-25s-4K.mp4'
lfs_paths=[master,opening]
attrs='\n# Exact Spirewatch final-delivery and music checkpoint bytes.\nmusic/illuminated-stillness-*/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\nmusic/spirewatch-final-two-hours-v1/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\nmusic/spirewatch-backup-2026-10-26/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n'+''.join(f'{name} filter=lfs diff=lfs merge=lfs -text\n' for name in lfs_paths)
tracked=set(git('ls-files','-z',env=None).decode().split('\0'))
roots=[p for p in (R/'music').iterdir() if p.is_dir() and (re.fullmatch(r'spirewatch-animation-v[1-8]',p.name) or p.name in ['spirewatch-artwork-rebuild-v1','digital-city-concepts-v1'] or p.name.startswith('illuminated-horizon-') or p.name.startswith('illuminated-stillness-') or p.name=='spirewatch-final-two-hours-v1')]
allowed_mp4={master,opening,'music/illuminated-stillness-companion-v1/source-original.mp4','music/illuminated-stillness-long-v1/source-original.mp4'}
exclude_names={'render-parts','parts','verification-cache','__pycache__','.local'}
files=[];excluded=[]
for root in roots:
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(R).as_posix()
        reason=None
        if exclude_names.intersection(p.relative_to(root).parts):reason='Regenerable render/verification cache'
        elif p.name=='remote-backup-verification.json':reason='Local post-push verification evidence'
        elif p.suffix.lower() in ['.f32','.pyc','.pyo','.npy','.npz','.pth','.pt','.ckpt','.safetensors','.bin']:reason='Regenerable PCM/model/library cache'
        elif p.suffix.lower() in ['.mp4','.mov','.webm'] and rel not in tracked and rel not in allowed_mp4:reason='Older/repeated/isolated animation review movie; source/configuration preserved'
        if reason:excluded.append({'path':rel,'bytes':p.stat().st_size,'reason':reason})
        else:files.append(p)
selected_videos=sorted({p.relative_to(R).as_posix() for p in files if p.suffix.lower()=='.mp4' and p.relative_to(R).as_posix() not in tracked}|{p.relative_to(R).as_posix() for p in generated.glob('*.mp4')})
ignore='\n# Requested Spirewatch exact masters and supplied music-source checkpoint.\n'+''.join('!'+name+'\n' for name in selected_videos)+'/music/spirewatch-backup-2026-10-26/remote-backup-verification.json\n'
for name,extra,marker in [('.gitattributes',attrs,b'# Exact Spirewatch final-delivery and music checkpoint bytes.'),('.gitignore',ignore,b'# Requested Spirewatch exact masters and supplied music-source checkpoint.')]:
    original=working[name]
    if marker in original:original=original[:original.index(marker)].rstrip(b'\r\n')+b'\n'
    (R/name).write_bytes(original+extra.encode())
    assert marker not in head[name]
    staged[name]=head[name]+extra.encode()
summary={'date':'2026-10-26','base_commit':base,'authorization':'User requested commit/push all Spirewatch work and save everything learned','scope':'All authored Spirewatch source/art/feedback/configuration, exact current 4K minute/intro review, original music sources, prompts/experiments/accepted joins and production records. Existing earlier commits retain historical scope.','selected_files':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files},'additional_sources':preserved,'lfs_paths':lfs_paths,'shared_documents':shared,'excluded_local':excluded,'long_exports_not_backed_up':[x for x in actual['files'] if x['path'].startswith('exports/spirewatch/')],'memory':'LESSONS.md plus scoped AGENTS.md/MUSIC_WORKFLOW.md/ANIMATION_KNOWLEDGE_BANK.md updates','remote_verification':'Local remote-backup-verification.json after successful push/ref fetch and isolated selected-LFS download. Credentials, models, installed binaries and regenerable intermediates excluded.','artistic_status':'Short music handovers approved; final video requested and technically verified. Full combined user playback/upload checks pending.'}
save('backup-manifest.json',summary)
git('read-tree','HEAD')
preview=H/'staged-shared-files'
index_info=[]
for name,data in staged.items():
    p=preview/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    oid=git('hash-object','-w','--stdin',input=data).decode().strip()
    index_info.append(f'100644 {oid}\t{name}\0'.encode())
git('update-index','-z','--index-info',input=b''.join(index_info))
paths=[p.relative_to(R).as_posix() for p in files]+[p.relative_to(R).as_posix() for p in sorted(H.rglob('*')) if p.is_file() and p.name not in ['remote-backup-verification.json','staging-validation.json']]
for offset in range(0,len(paths),120):git('add','-f','--',*paths[offset:offset+120])
entries={}
for item in git('ls-files','--stage','-z').split(b'\0'):
    if item:
        info,name=item.split(b'\t',1);entries[name.decode()]=info.split()[1].decode()
lfs_records=[]
for p in files:
    rel=p.relative_to(R).as_posix();expected=blob_sha1(p)
    if entries[rel]!=expected:
        pointer=git('show',':'+rel).decode()
        assert pointer.startswith('version https://git-lfs.github.com/spec/v1\n')
        assert f'oid sha256:{sha(p)}\n' in pointer and f'size {p.stat().st_size}\n' in pointer,rel
        lfs_records.append({'path':rel,'sha256':sha(p),'bytes':p.stat().st_size,'new_lfs_asset':rel in lfs_paths})
for name,data in staged.items():assert git('show',':'+name)==data,name
selected=git('diff','--cached','--name-only').decode().splitlines()
allowed_roots=tuple(p.relative_to(R).as_posix()+'/' for p in roots)+(H.relative_to(R).as_posix()+'/',)
assert all(name in shared or name.startswith(allowed_roots) for name in selected)
assert git('rev-parse','HEAD').decode().strip()==base,'HEAD changed; rerun --refresh to preserve concurrent commit'
save('staging-validation.json',{'base_commit':base,'dedicated_index':str(INDEX),'selected_count':len(selected)+1,'package_file_count':len(files),'all_package_blobs_exact_or_matching_lfs_pointer':True,'scoped_shared_blobs_exact':True,'selected_paths':selected,'lfs_records':lfs_records,'new_lfs_paths':lfs_paths})
git('add','-f','--',(H/'staging-validation.json').relative_to(R).as_posix())
print(json.dumps({'base':base,'selected_changes':len(selected)+1,'source_record_files_checked':len(files),'new_lfs_assets':lfs_paths,'new_lfs_MiB':round(sum((R/p).stat().st_size for p in lfs_paths)/1024**2,1),'unrelated_work_preserved':True}),flush=True)
