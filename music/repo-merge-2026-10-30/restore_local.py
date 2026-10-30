"""Restore original local edits with three-way integration of changed shared files."""
from pathlib import Path
import json,hashlib,subprocess,difflib
H=Path(__file__).resolve().parent;R=H.parents[1]
state=json.loads((H/'before.json').read_text())
def git(*a):return subprocess.check_output(['git','-C',str(R),*a])
def normalized(raw):return raw.replace(b'\r',b'')
def write(p,raw):
    with p.open('r+b') as f:f.write(raw);f.truncate()
original_names={x['path'] for x in state['files']}
newline_only=[]
for name in [n for n in git('diff','--name-only','-z').decode().split('\0') if n]:
    if name in original_names:continue
    committed=git('show','HEAD:'+name);current=(R/name).read_bytes()
    assert normalized(current)==normalized(committed),('Unexpected post-merge semantic change; preserve and inspect',name)
    newline_only.append((name,committed))
outputs=[];reports=[]
for row in state['files']:
    if not row['tracked_edit']:continue
    name=row['path'];local=(H/'tracked-originals'/name).read_bytes()
    assert hashlib.sha256(local).hexdigest()==row['sha256']
    base=git('show',state['head']+':'+name);merged=git('show','HEAD:'+name)
    if normalized(base)==normalized(merged):
        outputs.append((name,local));reports.append({'path':name,'method':'Exact original local bytes restored','sha256':row['sha256']})
    elif name in ['AGENTS.md','PRODUCTION_PIPELINE.md']:
        old_lines=normalized(base).splitlines(keepends=True);new_lines=normalized(merged).splitlines(keepends=True)
        ops=[op for op in difflib.SequenceMatcher(None,old_lines,new_lines,autojunk=False).get_opcodes() if op[0]!='equal']
        assert all(op[0]=='insert' for op in ops),ops
        addition=b''.join(b''.join(new_lines[op[3]:op[4]]) for op in ops)
        assert b'2026-10-30' in addition
        head_end=local.index(b'\n')+1
        out=local[:head_end]+b'\n'+addition+local[head_end:]
        assert out.replace(b'\n'+addition,b'',1)==local
        outputs.append((name,out));reports.append({'path':name,'method':'Original local bytes retained as a whole, with the merged branch additive memory block inserted after the title','sha256':hashlib.sha256(out).hexdigest()})
    else:
        work=H/'local-three-way'/name.replace('/','__');work.mkdir(parents=True,exist_ok=True)
        for label,raw in [('merged',merged),('base',base),('local',local)]: (work/label).write_bytes(normalized(raw))
        p=subprocess.run(['git','merge-file','-p',str(work/'merged'),str(work/'base'),str(work/'local')],capture_output=True)
        (work/'result').write_bytes(p.stdout)
        assert p.returncode==0,('Local edit needs explicit conflict resolution',name,str(work/'result'))
        outputs.append((name,p.stdout));reports.append({'path':name,'method':'Conflict-free three-way merge of original local delta onto committed merge','sha256':hashlib.sha256(p.stdout).hexdigest()})
for name,raw in newline_only:write(R/name,raw)
for name,raw in outputs:write(R/name,raw)
assert not git('diff','--cached','--name-only').strip(),'Local work should remain unstaged'
record={'introduced_newline_only_changes_fixed':len(newline_only),'tracked_edit_restorations':reports,'recovery_stash':'9498687c633a37fd31f73cbdf0a257f7753bd55f','stash_retained':True}
(H/'local-restoration.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'newline_only_checkout_differences_fixed':len(newline_only),'local_tracked_edits_restored':len(outputs),'three_way_combined':sum('three-way' in x['method'] for x in reports)},indent=2))
