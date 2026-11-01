"""Select only this scene's authored records, original samples and approved loop."""
from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];B=H/'backup';B.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
media=sorted([*(H/'sources').glob('*.mp4'),*(H/'paired-loop-v1').glob('*.mp3'),*(H/'paired-loop-v1').glob('*.flac')])
attrs=R/'.gitattributes';raw=attrs.read_bytes();lines=[]
for p in media:
    rel=p.relative_to(R).as_posix();line=rel+' filter=lfs diff=lfs merge=lfs -text'
    if line.encode() not in raw:lines.append(line)
history_rule='music/below-the-snowline-production-2026-11-01/history/** -whitespace'
if history_rule.encode() not in raw:lines.append(history_rule)
if lines:attrs.write_bytes(raw+b'\n# Approved Below the Snowline music and source history.\n'+('\n'.join(lines)+'\n').encode())
shared=['.gitattributes','AGENTS.md','PRODUCTION_PIPELINE.md','final/README.md','final/13-below-the-snowline/README.md','final/13-below-the-snowline/description.txt','final/13-below-the-snowline/youtube-title.txt','final/13-below-the-snowline/youtube-tags.txt','final/13-below-the-snowline/music/README.md','final/13-below-the-snowline/music/generation-record.json','creative/music/november-2026/README.md','creative/music/november-2026/month-plan.json']
selection={'branch':git('branch','--show-current'),'remote':git('remote','get-url','origin'),'source_and_record_directories':[H.relative_to(R).as_posix(),'music/hoth-reference-analysis-2026-11-01'],'shared_files':shared,'media':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'storage':'lfs'} for p in media],'excluded':['all cache directories including official Hoth reference audio','unrelated untracked media','full-hour renders (none created)'],'authority':'User accepts paired track and explicitly requests push plus scene record updates','scope':'Approved9min master, listening copy, both join checks, four supplied source files including earlier60s intake, analysis/prompts/provenance and updated scene records'}
(B/'selection.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
(B/'.gitignore').write_text('cache/\nremote-backup-verification.json\n',encoding='utf-8')
subprocess.run(['git','add','--',*shared,*selection['source_and_record_directories']],cwd=R,check=True)
subprocess.run(['git','add','-f','--',*[m['path'] for m in selection['media']]],cwd=R,check=True)
files=[]
for path in git('diff','--cached','--name-only').splitlines():
    p=R/path;blob=subprocess.check_output(['git','show',':'+path],cwd=R)
    if blob.startswith(b'version https://git-lfs.github.com/spec/v1'):
        digest=sha(p);assert ('oid sha256:'+digest).encode() in blob;storage='lfs'
    else:
        digest=hashlib.sha256(blob).hexdigest();storage='git'
    files.append({'path':path,'sha256':digest,'bytes':p.stat().st_size if storage=='lfs' else len(blob),'storage':storage})
manifest={'branch':selection['branch'],'files':files,'note':'Hash values for ordinary Git files describe staged blobs after line-ending handling. Manifest omits itself to avoid circular hash.'}
(B/'backup-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
subprocess.run(['git','add','--',(B/'backup-manifest.json').relative_to(R).as_posix()],cwd=R,check=True)
print(json.dumps({'files':len(files)+1,'media':len(media),'media_bytes':sum(p.stat().st_size for p in media),'branch':selection['branch']}))
