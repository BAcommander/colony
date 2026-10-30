"""Record exact local work before the user-requested main merge."""
from pathlib import Path
import subprocess,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[1]
def git(*a):return subprocess.check_output(['git','-C',str(R),*a])
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
assert not (H/'before.json').exists(),'Preservation record already exists'
assert not git('diff','--cached','--name-only').strip(),'Existing staging needs separate preservation'
tracked=[n for n in git('diff','--name-only','-z').decode().split('\0') if n]
untracked=[n for n in git('ls-files','--others','--exclude-standard','-z').decode().split('\0') if n and not n.startswith('music/repo-merge-2026-10-30/')]
rows=[]
for n in tracked+untracked:
    p=R/n
    if n in tracked:
        dest=H/'tracked-originals'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    rows.append({'path':n,'tracked_edit':n in tracked,'bytes':p.stat().st_size,'sha256':sha(p)})
(H/'working-changes.patch').write_bytes(git('diff','--binary'))
state={'head':git('rev-parse','HEAD').decode().strip(),'branch':git('branch','--show-current').decode().strip(),'incoming':git('rev-parse','origin/codex/concept-brainstorms-2026-10-27').decode().strip(),'files':rows,'tracked_edits':len(tracked),'untracked_files':len(untracked)}
(H/'before.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preserved_tracked_edits':len(tracked),'hashed_untracked_files':len(untracked),'snapshot':str(H/'before.json')},indent=2))
