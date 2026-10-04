"""Prepare a focused Rainline index without replacing shared working files."""
from pathlib import Path
import subprocess, json, hashlib

R=Path('G:/AI/colony')
H=R/'music/rainline-animation-v5'
def git(*args, data=None):
 return subprocess.check_output(['git',*args],cwd=R,input=data)
def digest(b): return hashlib.sha256(b).hexdigest()
def stage_bytes(path, data):
 oid=git('hash-object','-w','--stdin',data=data).decode().strip()
 git('update-index','--add','--cacheinfo',f'100644,{oid},{path}')

assert not git('diff','--cached','--name-only').strip(), 'Index is not empty'
d=json.loads((H/'delivery-v5.json').read_text(encoding='utf-8'))
snapshots={}
for rel,expected in d['fingerprint']['dependencies'].items():
 b=(R/rel).read_bytes();assert digest(b)==expected
 dest=H/'dependency-snapshot'/Path(rel).name
 dest.parent.mkdir(exist_ok=True)
 dest.write_bytes(b)
 snapshots[rel]={'snapshot':dest.relative_to(R).as_posix(),'sha256':expected}
preview='music/rainline-animation-v5/rainline-relay-v5-preview-20s.mp4'
assert digest((R/preview).read_bytes())==d['preview']['sha256']
record={
 'date':'2026-10-05','authorization':'User explicitly requested commit and push.',
 'scope':'Rainline versions 1-5 code/config/masks/records, current package status and v5 twenty-second preview.',
 'preview':{'path':preview,'sha256':d['preview']['sha256'],'bytes':(R/preview).stat().st_size,'storage':'ordinary Git, exact-path exception; below 100 MiB'},
 'dependencies':snapshots,
 'not_included':'Three-repeat review, isolated videos and previous draft videos remain local/reproducible. Other scenes remain unstaged.',
 'approval':'Backup authorization does not establish v5 artistic approval.',
 'remote_verification':'See remote-backup-verification.json when available; preparation alone does not confirm push.'
}
(H/'backup-manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(H/'BACKUP.md').write_text('''# Rainline backup

User requested commit and push on 2026-10-05. This backup includes Rainline revision history, source code, configuration, masks, reports and the latest 20-second v5 preview. Its exact-path ordinary-Git rule preserves the 42 MB video. The 60-second three-repeat review and other draft videos remain local and can be reproduced. Backup is separate from artistic acceptance.

`backup-manifest.json` records preview and dependency hashes. The five dependency snapshots preserve the exact bytes used in validation; on a fresh Windows checkout, compare the recorded SHA-256 values before rendering. If a dependency's checkout line endings differ, restore its bytes from the corresponding snapshot to the recorded path. This does not change its Python behavior. Rainline Python/JSON files and snapshots use `-text` attributes to preserve their recorded bytes.

`remote-backup-verification.json`, when present locally, records verification after the push. Other sessions' working files were preserved; only Rainline portions of shared status files were staged.
''',encoding='utf-8')
ignore=R/'.gitignore';s=ignore.read_text(encoding='utf-8')
assert '!'+preview not in s
ignore.write_text(s+'\n# Rainline v5 preview backup explicitly requested 2026-10-05.\n!'+preview+'\n',encoding='utf-8')
attr=R/'.gitattributes';s=attr.read_text(encoding='utf-8')
attr.write_text(s+'\n# Preserve Rainline hash-bound renderer/config/snapshot bytes.\nmusic/rainline-animation-v*/*.py -text\nmusic/rainline-animation-v*/*.json -text\nmusic/rainline-animation-v5/dependency-snapshot/*.py -text\nmusic/rainline-animation-v1/initial-mask-review/*.json -text\nmusic/rainline-renderer/*.py -text\n'+preview+' -text\n',encoding='utf-8')

# Add a scoped backup note to the current working paragraph only.
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');start=s.index('Current Rainline animation (');end=s.index('\n\n',start)
para=s[start:end].replace('Earlier versions preserved; no credits, commit, push or new remote media backup.','Earlier versions preserved. User explicitly requested commit/push on 2026-10-05; Rainline code/config/masks/records and the exact v5 twenty-second preview are selected for Git backup. See music/rainline-animation-v5/backup-manifest.json and the subsequent local remote-backup-verification.json for actual backup evidence. Review/repeated videos remain local; artistic review is still pending.')
s=s[:start]+para+s[end:];p.write_text(s,encoding='utf-8')
base=git('show','HEAD:AGENTS.md').decode('utf-8')
first,rest=base.split('\n\n',1)
stage_bytes('AGENTS.md',(first+'\n\n'+para+'\n\n'+rest).encode('utf-8'))

base=git('show','HEAD:PRODUCTION_PIPELINE.md').decode('utf-8')
working=(R/'PRODUCTION_PIPELINE.md').read_text(encoding='utf-8')
for prefix in ['Last updated:','| 08 |']:
 old=next(line for line in base.splitlines() if line.startswith(prefix))
 new=next(line for line in working.splitlines() if line.startswith(prefix))
 base=base.replace(old,new,1)
stage_bytes('PRODUCTION_PIPELINE.md',base.encode('utf-8'))
base=json.loads(git('show','HEAD:final/catalog.json'))
working=json.loads((R/'final/catalog.json').read_text(encoding='utf-8'))
entry=next(e for e in working if e['folder']=='08-rainline-relay')
base=[entry if e['folder']=='08-rainline-relay' else e for e in base]
stage_bytes('final/catalog.json',(json.dumps(base,indent=2)+'\n').encode('utf-8'))
paths=['.gitignore','.gitattributes','final/08-rainline-relay/README.md','final/08-rainline-relay/manifest.json','final/08-rainline-relay/animation-proposal-prompt-v1.txt','music/prepare_rainline_proposal_prompt.py','music/rainline-renderer']
paths += [f'music/rainline-animation-v{i}' for i in range(1,6)]
git('add','--',*paths)
staged=git('diff','--cached','--name-only').decode().splitlines()
for path in staged:
 assert path in ['AGENTS.md','PRODUCTION_PIPELINE.md','final/catalog.json','.gitignore','.gitattributes','music/prepare_rainline_proposal_prompt.py'] or path.startswith(('music/rainline-','final/08-rainline-relay/')),path
 assert (R/path).stat().st_size<100*1024*1024,path
assert preview in staged
for path in [preview,'music/rainline-animation-v5/scene-plan-v5.json','music/rainline-renderer/render_rainline.py']:
 assert git('show',':'+path)==(R/path).read_bytes(),path
print(f'Staged {len(staged)} scoped files; exact preview/config/renderer bytes verified')
