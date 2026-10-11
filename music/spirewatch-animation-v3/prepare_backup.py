"""Stage only the requested Spirewatch checkpoint; preserve unrelated working edits."""
from pathlib import Path
import json,hashlib,subprocess
R=Path('G:/AI/colony');H=R/'music/spirewatch-animation-v3'
PREVIEW='music/spirewatch-animation-v3/spirewatch-v3-preview-60s.mp4'
def git(*a,data=None):return subprocess.check_output(['git','-C',str(R),*a],input=data)
def read(p):return (R/p).read_text(encoding='utf-8')
def write(p,s):(R/p).write_text(s,encoding='utf-8',newline='\n')
def save(p,v):write(p,json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def stage(p,s):
 blob=git('hash-object','-w','--stdin',data=s.encode()).decode().strip()
 git('update-index','--add','--cacheinfo',f'100644,{blob},{p}')
assert not git('diff','--cached','--name-only').strip()
backup='User explicitly requested commit/push on 2026-10-11. Current v3 minute preview, source/config/masks, diagnostics/history records and learnings selected for Git backup. Repeated/older/isolated/intermediate videos remain local. See backup-manifest.json and subsequent local remote-backup-verification.json for actual remote evidence. Backup authorization does not imply artistic approval.'
p='music/spirewatch-animation-v3/README.md';s=read(p)
s=s.replace('V3 backup has not been requested/performed in this revision; v2\'s earlier backup does not cover these files.',backup)
write(p,s)
p='music/spirewatch-animation-v3/delivery-v3.json';v=json.loads(read(p));v['backup']=backup;save(p,v)
p='music/spirewatch-animation-v3/user-feedback-2026-10-11.json';v=json.loads(read(p));v['backup_request']='so commit and push';v['backup_scope']=backup;save(p,v)
p='music/digital-city-concepts-v1/current-direction.json';v=json.loads(read(p));v['backup_request']='V3 checkpoint commit/push requested 2026-10-11; see v3 backup records';save(p,v)
p='AGENTS.md';s=read(p);start=s.index('Current Spirewatch animation');end=s.index('\n\n',start)
section=s[start:end].replace('No new music, 4K, long assembly, paid service, commit or push for v3; prior v2 remote backup does not include v3.', 'No new music, 4K, long assembly or paid service. '+backup.replace('See backup-manifest.json','See music/spirewatch-animation-v3/backup-manifest.json'))
write(p,s[:start]+section+s[end:]);base=git('show','HEAD:'+p).decode();a=base.index('Current Spirewatch animation');b=base.index('\n\n',a);stage(p,base[:a]+section+base[b:])
p='PRODUCTION_PIPELINE.md';s=read(p);a=s.index('## Unnumbered city concept');b=s.index('## Next concept exploration',a)
section=s[a:b].replace('v3 media/code/records are local.', 'v3 current minute preview, code/config/masks/history records and learnings are selected for the requested backup; see v3 backup-manifest.json and subsequent local remote verification receipt. Repeated/intermediate videos remain local.')
write(p,s[:a]+section+s[b:]);base=git('show','HEAD:'+p).decode();a=base.index('## Unnumbered city concept');b=base.index('## Next concept exploration',a);stage(p,base[:a]+section+base[b:])
p='creative/ANIMATION_KNOWLEDGE_BANK.md';s=read(p);marker='## Spirewatch animation candidate';base=git('show','HEAD:'+p).decode();stage(p,base[:base.index(marker)]+s[s.index(marker):])
p='.gitignore';write(p,read(p)+'\n# Spirewatch v3 exact current preview; repeated/intermediate media stay local\n!'+PREVIEW+'\n/music/spirewatch-animation-v3/remote-backup-verification.json\n')
p='.gitattributes';write(p,read(p)+'\n# Preserve source fingerprints for the Spirewatch lighting checkpoint\nmusic/spirewatch-animation-v3/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\nmusic/setup_spirewatch_v3.py -text\n')
git('add','--','.gitignore','.gitattributes','music/spirewatch-animation-v3','music/setup_spirewatch_v3.py','music/digital-city-concepts-v1/current-direction.json')
files=[];shared=['AGENTS.md','PRODUCTION_PIPELINE.md','creative/ANIMATION_KNOWLEDGE_BANK.md']
for p in filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')):
 data=git('show',':'+p)
 assert len(data)<100*1024*1024,p
 if p not in shared:assert data==(R/p).read_bytes(),p
 files.append({'path':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'scoped_index_content':p in shared})
save('music/spirewatch-animation-v3/backup-manifest.json',{'date':'2026-10-11','request':'so commit and push','scope':backup,'unrelated_work':'Earlier Farpoint and other work preserved unstaged; shared docs include only Spirewatch changes','files':files,'self_excluded':True,'remote_evidence':'remote-backup-verification.json (local receipt after successful push)'})
git('add','--','music/spirewatch-animation-v3/backup-manifest.json')
print(json.dumps({'files':len(files)+1,'bytes':sum(x['bytes'] for x in files),'preview':next(x for x in files if x['path']==PREVIEW)},indent=2))
