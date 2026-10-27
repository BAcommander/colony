"""Stage only the requested publication package and shared memory additions."""
from pathlib import Path
import hashlib, json, os, subprocess, tempfile, shutil
H=Path(__file__).resolve().parent
R=H.parents[1]
P=R/'music/spirewatch-upload-v1'
INDEX=Path(tempfile.gettempdir())/'colony-spirewatch-upload-2026-10-27.index'
assert not INDEX.exists(), 'Inspect an existing dedicated index before reusing it'
ENV=dict(os.environ,GIT_INDEX_FILE=str(INDEX))
def git(*args,env=None,input=None):
    p=subprocess.run(['git','-C',str(R),*args],env=env,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def save(name,obj): (H/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def digest(b): return hashlib.sha256(b).hexdigest()
assert git('branch','--show-current').strip()==b'main'
base=git('rev-parse','HEAD').decode().strip()
notes={
 'AGENTS.md': '\nSpirewatch publication pack (2026-10-27): music/spirewatch-upload-v1/ holds the ready-to-copy 65-character title, 82-word description with AI credit/sign-off/three hashtags, 426-character Studio tag line and unchanged original thumbnail JPG/PNG. Link the publication pack whenever delivering the final video: rendering alone leaves upload preparation incomplete. Describe the real Horizon/Stillness pulse-and-space arrangement, focus/work/study/reading and TRON-inspired aesthetic; do not promise beatless music, continuous environmental sound or official soundtrack status. Preserve the existing thumbnail; typography evidence was not causal. Detailed reusable lessons and requested backup scope: music/spirewatch-upload-backup-2026-10-27/LESSONS.txt and backup-manifest.json; actual push evidence is the later local remote-backup-verification.json. No upload or new artistic approval. Long final media remain local.\n',
 'creative/MUSIC_WORKFLOW.md': '\n\n## Publication packaging lessons - 2026-10-27\n\nDeliver title, scene-led description, separate Studio tags, existing upload JPEG/PNG and the actual final-video path together; link the pack from the production record and memory. Spirewatch uses TRON-inspired ambient music for focus, with Horizon pulse alternating with more spacious Stillness, rather than a beatless/sleep or continuous environmental-audio promise. Retain the exact channel sign-off, accurate AI credit and three relevant hashtags; use listener-oriented tags below the project 500-character limit without unsupported search-performance claims. Preserve the existing thumbnail and its approval scope: sequential typography evidence was not causal. Current pack: ../music/spirewatch-upload-v1/README.txt; detailed lessons and backup scope: ../music/spirewatch-upload-backup-2026-10-27/LESSONS.txt. A local pack, Git backup, upload and full playback approval are separate states.\n',
 '.gitattributes':'\n# Exact Spirewatch publication files and hash-bound backup records.\nmusic/spirewatch-upload-v1/** -text\nmusic/spirewatch-upload-backup-2026-10-27/** -text\n',
 '.gitignore':'\n# Post-push receipt for the Spirewatch publication pack.\n/music/spirewatch-upload-backup-2026-10-27/remote-backup-verification.json\n'
}
shared={}
for name,note in notes.items():
    raw=(R/name).read_bytes()
    addition=note.encode('utf-8')
    assert addition not in raw, 'Memory already added; inspect before repeating'
    with (R/name).open('ab') as stream:
        stream.write(addition)
    shared[name]=git('show','HEAD:'+name)+addition
save('memory-update.json',{'date':'2026-10-27','scope':'Append only the recorded Spirewatch publication lesson/rules to working and HEAD-based staged versions. Preserve all pre-existing unrelated bytes.','additions':notes})
m=json.loads((P/'manifest.json').read_text(encoding='utf-8'))
m['status']='User requested commit/push 2026-10-27; consult music/spirewatch-upload-backup-2026-10-27/remote-backup-verification.json for the actual result. No YouTube upload.'
for name in m['files']:
    b=(P/name).read_bytes();m['files'][name]={'sha256':digest(b),'bytes':len(b)}
(P/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert len((P/'youtube-tags.txt').read_text().strip())==426
for name,v in m['thumbnail_sources'].items(): assert digest((P/name).read_bytes())==v['sha256']
git('read-tree',base,env=ENV)
for name,raw in shared.items():
    oid=git('hash-object','-w','--stdin',input=raw).decode().strip()
    git('update-index','--add','--cacheinfo','100644',oid,name,env=ENV)
files=sorted(p for p in P.iterdir() if p.is_file())+[R/'music/spirewatch-final-two-hours-v1/README.md']
manifest={'date':'2026-10-27','base_commit':base,'package_files':[{'path':p.relative_to(R).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for p in files],'shared_additions':list(notes),'limits':'Long video/audio remain local. No upload; no new artistic approval. Unrelated working changes excluded.'}
save('backup-manifest.json',manifest)
save('staging-validation.json',{'base_commit':base,'dedicated_index':str(INDEX),'scope':'Spirewatch publication pack, backup records and scoped shared memory/rules only'})
shutil.copyfile(R/'music/spirewatch-backup-2026-10-26/commit_checkpoint.py',H/'commit_checkpoint.py')
files+=sorted(p for p in H.iterdir() if p.is_file() and p.name!='remote-backup-verification.json')
git('add','--',*[p.relative_to(R).as_posix() for p in files],env=ENV)
for p in files:
    name=p.relative_to(R).as_posix()
    assert git('show',':'+name,env=ENV)==p.read_bytes(), 'Raw staged bytes differ: '+name
print(git('diff','--cached','--stat',env=ENV).decode())
print('Dedicated staged files validated; unrelated default index untouched.')
