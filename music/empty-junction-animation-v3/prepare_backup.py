"""Record requested WIP backup, keeping unrelated live-scene work unstaged."""
from pathlib import Path
import json,hashlib,shutil,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1]
def read(p):return p.read_text(encoding='utf-8')
def write(p,t):p.write_text(t,encoding='utf-8')
def load(p):return json.loads(read(p))
def save(p,v):write(p,json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args,data=None):return subprocess.run(['git',*args],cwd=R,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
def stage_content(path,text):
 oid=git('hash-object','-w','--stdin',data=text.encode('utf-8')).decode().strip()
 git('update-index','--add','--cacheinfo',f'100644,{oid},{path}')
def main():
 feedback='commit and push this version, it still needs work.'
 p=H/'feedback.json';v=load(p);v['v3_feedback']=feedback;v['status']='Needs further visual work; backup requested, not approved';save(p,v)
 p=H/'visual-review.json';v=load(p);v['status']='needs_further_work';v['user_feedback']=feedback;v['user_approved']=False;save(p,v)
 p=H/'delivery-v3.json';v=load(p);v['status']='Work-in-progress checkpoint; user says it still needs work';v['feedback_v3']=feedback;v['remote_backup']={'status':'Requested; verify using backup-manifest.json and local remote-backup-verification.json'};save(p,v)
 dependencies={}
 for name,expected in v['fingerprint']['files'].items():
  source=R/name;assert sha(source)==expected,name
  if name.startswith('scripts/') or name.startswith('music/saltline-') or name.startswith('music/farpoint-'):
   dest=H/'dependency-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
   dependencies[name]={'snapshot':dest.relative_to(R).as_posix(),'sha256':sha(dest)}
 preview=R/v['preview']['path'];assert sha(preview)==v['preview']['sha256']
 save(H/'backup-manifest.json',{'date':'2026-10-07','authorization':feedback,'scope':'Empty Junction v1-v3 code/config/masks/reports and diagnostics, current scene records, exact v3 minute preview and dependency snapshots','approval':'Work in progress; still needs work. No visual acceptance or 4K authorization inferred.','preview':{'path':preview.relative_to(R).as_posix(),'sha256':sha(preview),'bytes':preview.stat().st_size,'storage':'ordinary Git with exact-path exception'},'dependencies':dependencies,'not_included':'Three-minute repeat, isolated and older draft videos, Python caches, and unrelated live-scene work remain local.','remote_verification':'Local remote-backup-verification.json will record independent fetch and byte/hash checks after push.'})
 p=H/'README.md';t=read(p).replace('V3 is awaiting playback review; no 4K acceptance is implied.','User requested commit/push and said v3 still needs work. This is a work-in-progress checkpoint, not visual acceptance; 4K remains gated.')
 t=t.replace('No image generation, paid services, new models, music, assembly, commit/push or remote backup this pass.','No image generation, paid services, new models, music or assembly. User explicitly requested commit/push of this version; the exact minute preview, code/config/masks/records and dependency snapshots are selected for backup. See backup-manifest.json and the local remote-backup-verification.json for verified remote evidence. The repeated review and other draft videos remain local.')
 t+='\nFor a restored checkout, compare delivery fingerprints before rendering. If a shared dependency has changed or undergone line-ending conversion, restore its exact bytes from the path mapped in backup-manifest.json within an isolated reproduction checkout. Do not overwrite newer shared code in the active project.\n'
 write(p,t)
 p=R/'final/11-empty-junction/manifest.json';m=load(p);m['animation']['status']='V3 work in progress; user says it still needs work; Git backup requested';m['animation']['user_approved']=False;m['animation']['backup_record']='music/empty-junction-animation-v3/backup-manifest.json';m['motion_preparation']['status']='V3 implemented and technically checked; further visual work required';save(p,m)
 p=R/'final/11-empty-junction/README.md';t=read(p).replace('User review pending; 4K follows acceptance','User says v3 still needs work and requested commit/push; 4K follows acceptance').replace('No audio, assembly or remote backup this pass.','No audio or assembly. Exact v3 minute and reproduction files selected for Git backup; see the v3 backup manifest and local remote verification.');write(p,t)
 p=R/'AGENTS.md';t=read(p);a=t.index('Current Empty Junction animation');b=t.index('\n\n',a);paragraph=t[a:b]
 paragraph=paragraph.replace('V3 user review pending;','User says v3 still needs work; it is not visually approved.').replace('no image generation, paid tools, new models, commit/push or remote backup this pass.','no image generation, paid tools or new models. User explicitly requested commit/push of v3 on 2026-10-07. Exact minute preview, code/config/masks/records and dependency snapshots selected for Git backup; see backup-manifest.json and subsequent local remote-backup-verification.json for actual remote evidence. Repeated/older draft videos remain local.')
 t=t[:a]+paragraph+t[b:];write(p,t)
 head=git('show','HEAD:AGENTS.md').decode('utf-8')
 pos=head.index('\n\n')+2;stage_content('AGENTS.md',head[:pos]+paragraph+'\n\n'+head[pos:])
 p=R/'PRODUCTION_PIPELINE.md';t=read(p)
 old=next(l for l in t.splitlines() if l.startswith('| 11 |'))
 new=old.replace('Review [v3 full preview]','V3 still needs work; backup requested. Continue from [v3 checkpoint]')
 t=t.replace(old,new).replace('Full minute awaits user playback review.','V3 still needs visual work; backup requested.');write(p,t)
 head=git('show','HEAD:PRODUCTION_PIPELINE.md').decode('utf-8');old=next(l for l in head.splitlines() if l.startswith('| 11 |'));head=head.replace(old,new)
 head=head.replace('## Proposed motion direction for scenes 04–10','## Motion direction for scenes 04–11')
 row=next(l for l in t.splitlines() if l.startswith('| 11 Empty Junction |'));pos=head.index('\n',head.index('| 10 Farpoint |'));head=head[:pos]+'\n'+row+head[pos:]
 stage_content('PRODUCTION_PIPELINE.md',head)
 p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';t=read(p);a=t.index('### 11 The Empty Junction');b=t.index('## Render and delivery improvements',a);section=t[a:b]
 section=section.replace('Technical gates passed; stills inspected, continuous playback and user acceptance pending.','Technical gates passed; assistant inspected stills. User then requested commit/push but explicitly said v3 still needs work. Treat it as an unapproved checkpoint, not an accepted motion reference.')
 t=t[:a]+section+t[b:];t=t.replace('Empty Junction 11 has a technically checked v3 motion candidate awaiting user review.','Empty Junction 11 has a technically checked v3 checkpoint that the user says still needs work.');write(p,t)
 exclude=R/'.git/info/exclude';t=read(exclude) if exclude.exists() else '';entry='/music/empty-junction-animation-v3/remote-backup-verification.json'
 if entry not in t:write(exclude,t+'\n'+entry+'\n')
 print('WIP feedback and backup manifest saved; only Empty Junction parts of shared tracker files staged.')
if __name__=='__main__':main()
