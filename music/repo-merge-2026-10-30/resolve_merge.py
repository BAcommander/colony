"""Resolve additive shared-document conflicts while retaining both histories."""
from pathlib import Path
import re,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1]
pattern=rb'^<<<<<<< HEAD\r*\n(.*?)^=======\r*\n(.*?)^>>>>>>> [^\r\n]+\r*\n'
records=[]
for name in ['.gitattributes','AGENTS.md','PRODUCTION_PIPELINE.md','creative/MUSIC_WORKFLOW.md']:
    p=R/name;raw=p.read_bytes()
    saved=H/'merge-conflicts-original'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(raw)
    def resolve(m):
        ours,theirs=m.group(1),m.group(2)
        if name=='.gitattributes':return ours+b'\n'+theirs
        if name=='creative/MUSIC_WORKFLOW.md':
            assert b'Updated 2026-10-21.' in ours and b'Updated 2026-10-13.' in theirs
            return theirs.replace(b'Updated 2026-10-13.',b'Updated 2026-10-30.')
        return theirs+b'\n'+ours
    out,count=re.subn(pattern,resolve,raw,flags=re.M|re.S)
    assert count==1,(name,count)
    assert not re.search(rb'^(<<<<<<<|=======|>>>>>>>)',out,re.M)
    with p.open('r+b') as f:f.write(out);f.truncate()
    records.append({'path':name,'resolution':'Keep both additive sections; newest learning records first. Music workflow header advanced to October 30.'})
subprocess.run(['git','-C',str(R),'add','--',*[x['path'] for x in records]],check=True)
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only','--diff-filter=U']).strip()
(H/'merge-resolutions.json').write_text(json.dumps(records,indent=2)+'\n')
print('Four conflicts resolved; both branches retained, no unmerged paths.')
