"""Update current status and stage exactly the authorized production packages."""
from pathlib import Path
import subprocess,json,hashlib,shutil,ast
H=Path(__file__).resolve().parent;R=H.parents[1]
S=R/'music/below-the-snowline-wind-review-2026-11-02';D=R/'music/deepwell-claim-review-2026-11-02'
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def read(p):return p.read_bytes().decode('utf-8-sig')
def write(p,s):p.write_bytes(s.encode('utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def save(p,d):write(p,json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def prepend_once(p,marker,paragraph):
 s=read(p)
 if marker not in s:
  i=s.index('\n');write(p,s[:i+1]+'\n'+paragraph+'\n\n'+s[i+1:])

media=sorted([p for p in S.iterdir() if p.suffix in ['.flac','.mp3','.mp4']]+[p for p in (D/'replacement-v1').iterdir() if p.suffix in ['.flac','.mp3']])
validated={}
for p,key in [(S/'delivery-validation.json','outputs'),(D/'replacement-v1/validation.json','output_files')]:
 for x in json.loads(read(p))[key]:validated[str(Path(x['path']))]=x['sha256']
for p in media:assert sha(p)==validated[str(p)],p
(D/'evidence').mkdir(exist_ok=True)
evidence=D/'evidence/claim-screenshot.png'
if not evidence.exists():shutil.copy2(D/'cache/claim-screenshot.png',evidence)
claim=json.loads(read(D/'claim-record.json'));claim['screenshot_evidence']={'path':'evidence/claim-screenshot.png','sha256':sha(evidence)};save(D/'claim-record.json',claim)
attrs=R/'.gitattributes';text=read(attrs);lines=[]
for p in media:
 line=p.relative_to(R).as_posix()+' filter=lfs diff=lfs merge=lfs -text'
 if line not in text:lines.append(line)
if lines:write(attrs,text+'\n# 2026-11-02 production source and review media.\n'+'\n'.join(lines)+'\n')
note='Production update and backup request(2026-11-02): user requests commit/push after Snowline wind-in-scene preview. music/below-the-snowline-wind-review-2026-11-02/ adds original library wind at+4.85dB to the approved9min pair, events20–80/200–260/380–440s,8s rise/12s fall; full mix/stem and2min/9min720p V2 previews technically verified. Wind balance/animation review pending. music/deepwell-claim-review-2026-11-02/ records the Good Energy/Flowstate claim and user-approved replacement of Waterworks30–51s in all10 occurrences, with6s handles. Revised1h4K video v2-audio-revised delivered: all108000 video packets unchanged, complete AAC comparison passed. Fresh YouTube checks pending; no claim clearance or upload inferred. Commit/push includes sources/review media/recipes/records; full-hour exports remain local. Actual remote verification: music/production-backup-2026-11-02/remote-backup-verification.json. Preserve unrelated work and shared main.'
prepend_once(R/'AGENTS.md','Production update and backup request(2026-11-02)',note)
prepend_once(R/'final/13-below-the-snowline/README.md','Wind-in-scene audition(2026-11-02)','Wind-in-scene audition(2026-11-02): [two-minute and full nine-minute scene previews](../../music/below-the-snowline-wind-review-2026-11-02/README.md) pair the approved music with the saved wind at the accepted Deepwell starting level. One-minute passages/two-minute gaps. Technical checks pass; new wind balance remains awaiting user review.')
pipeline=R/'PRODUCTION_PIPELINE.md';text=read(pipeline)
lines=text.splitlines(keepends=True)
for i,line in enumerate(lines):
 if line.startswith('| 12 |'):lines[i]='| 12 | [Deepwell Station](final/12-deepwell-station/README.md) | V4 retained; revised hour has identical video packets | Claim passage replaced in all10 repeats; user accepts revised audio | Revised1h4K v2 ready for reupload; fresh YouTube checks pending |\n'
 if line.startswith('| 13 |'):lines[i]='| 13 | [Below the Snowline](final/13-below-the-snowline/README.md) | V2 scene reused in2min/9min wind auditions; artistic review pending | Approved9min music; wind+4.85dB candidate with60s on/120s off | Review wind-in-scene balance and thumbnail; full-length4K assembly pending |\n'
write(pipeline,''.join(lines))
dirs=[S.relative_to(R).as_posix(),D.relative_to(R).as_posix(),H.relative_to(R).as_posix(),'final/12-deepwell-station/upload-2026-11-02']
shared=['.gitattributes','AGENTS.md','PRODUCTION_PIPELINE.md','final/12-deepwell-station/README.md','final/13-below-the-snowline/README.md']
selection={'date':'2026-11-02','authority':'User: commit and push','branch':git('branch','--show-current'),'directories':dirs,'shared_files':shared,'media':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in media],'full_hour_exports_included':False,'unrelated_untracked_files_included':False}
save(H/'selection.json',selection)
subprocess.run(['git','add','--',*shared,*dirs],cwd=R,check=True)
subprocess.run(['git','add','-f','--',*[x['path'] for x in selection['media']]],cwd=R,check=True)
records=[]
for name in git('diff','--cached','--name-only').splitlines():
 assert name in shared or any(name.startswith(d+'/') for d in dirs),name
 if name.endswith('/backup-manifest.json'):continue
 p=R/name;blob=subprocess.check_output(['git','show',':'+name],cwd=R)
 if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8-sig'))
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 if blob.startswith(b'version https://git-lfs.github.com/spec/v1'):
  digest=sha(p);assert ('oid sha256:'+digest).encode() in blob;storage='lfs';size=p.stat().st_size
 else:digest=hashlib.sha256(blob).hexdigest();storage='git';size=len(blob)
 records.append({'path':name,'sha256':digest,'bytes':size,'storage':storage})
save(H/'backup-manifest.json',{'branch':selection['branch'],'files':records,'self_hash_omitted':True,'git_hash_scope':'Staged bytes after Git line-ending normalization'})
subprocess.run(['git','add','--',(H/'backup-manifest.json').relative_to(R).as_posix()],cwd=R,check=True)
print(json.dumps({'staged_files':len(records)+1,'lfs_files':len(media),'media_bytes':sum(p.stat().st_size for p in media),'original_validation_hashes_verified':True}))
