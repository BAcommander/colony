from pathlib import Path
import json,hashlib,subprocess,re
R=Path('G:/AI/colony');H=R/'music/shoreless-animation-v3';T=R/'music/.local/shoreless-backup-2026-10-06';T.mkdir(parents=True,exist_ok=True)
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
assert not git('diff','--cached','--name-only').strip(),'Preserve pre-existing staged work'
deps={};(H/'dependency-snapshot').mkdir(exist_ok=True)
d=json.loads((H/'delivery-v3.json').read_text())
for name in ['render_floodplain.py','water_surface.py','ambient_effects.py']:
 src=R/'scripts'/name;target=H/'dependency-snapshot'/name
 assert sha(src)==d['fingerprint']['dependencies']['scripts/'+name]
 target.write_bytes(src.read_bytes());deps['scripts/'+name]={'snapshot':target.relative_to(R).as_posix(),'sha256':sha(target)}
video=R/d['preview']['path'];assert sha(video)==d['preview']['sha256']
manifest={'date':'2026-10-06','authorization':'User explicitly requested commit and push.','scope':'Shoreless versions 1-3 source/config/masks/records, the v3 sixty-second preview, scene 09 status and reusable animation knowledge bank.','preview':{'path':video.relative_to(R).as_posix(),'sha256':sha(video),'bytes':video.stat().st_size,'storage':'ordinary Git with exact-path exception; below 100 MiB'},'dependencies':deps,'not_included':'Three-minute review, isolated/older draft videos and regenerated environment cache remain local. Other scenes remain unstaged.','approval':'Backup request does not establish visual acceptance of v3.','remote_verification':'See local remote-backup-verification.json after independent remote fetch/hash checks.'}
save(H/'backup-manifest.json',manifest)
(H/'BACKUP.md').write_text('''# Shoreless backup scope

The user requested commit and push on 2026-10-06. This backup selects v1–v3 render code, configurations, masks, feedback, technical reports and inspection stills, the exact v3 sixty-second 720p preview, current scene 09 records and the reusable animation knowledge bank.

The preview is ordinary Git with an exact-path ignore exception. Hash-bound Python/JSON and dependency snapshots have byte-preserving attributes. The immutable clean artwork was already tracked. The three shared renderer dependencies are also preserved verbatim under dependency-snapshot/; compare their hashes before reproducing, and restore those exact bytes to their listed scripts/ paths in an isolated restore checkout if needed.

The three-minute review, older/isolated videos and environment cache stay local and reproducible. This request authorizes backup, not artistic acceptance or a new 4K/music delivery. Other scenes' local edits are preserved and excluded from this commit. Shared tracker/catalog/instruction changes are staged only for Shoreless and the knowledge bank.

See backup-manifest.json for expected hashes. A later local remote-backup-verification.json records the actual commit, remote-fetch evidence and recovered hashes; this preparation is not evidence of a completed push.
''',encoding='utf-8')
rp=R/'.gitignore';s=rp.read_text();rule='!music/shoreless-animation-v3/shoreless-colony-v3-preview-60s.mp4'
if rule not in s:rp.write_text(s+'\n# Shoreless v3 minute preview backup explicitly requested 2026-10-06.\n'+rule+'\n',encoding='utf-8')
rp=R/'.gitattributes';s=rp.read_text();rule='music/shoreless-animation-v*/**/*.py -text'
if rule not in s:rp.write_text(s+'\n# Preserve Shoreless hash-bound code/config and dependency snapshot bytes.\nmusic/shoreless-animation-v*/*.py -text\nmusic/shoreless-animation-v*/*.json -text\n'+rule+'\nmusic/shoreless-animation-v*/**/*.json -text\nmusic/shoreless-animation-v3/shoreless-colony-v3-preview-60s.mp4 -text\n',encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');old=next(x for x in s.splitlines() if x.startswith('Current Shoreless animation ('))
new=old.replace('V1/v2 and prior scenes preserved; no credits, commit or push.','V1/v2 and prior scenes preserved; no credits spent. User explicitly requested commit/push on 2026-10-06; source/config/masks/records, knowledge bank and the exact v3 minute preview are selected for backup. See music/shoreless-animation-v3/backup-manifest.json and the later local remote-backup-verification.json for actual remote evidence. Review videos and the environment cache remain local.')
rp.write_text(s.replace(old,new,1),encoding='utf-8')
rp=H/'README.md';s=rp.read_text(encoding='utf-8');s=s.replace('No paid generation, commit or push.','No paid generation. The subsequent explicit commit/push request selects this package and the exact minute preview for backup; see [backup scope](BACKUP.md) and backup-manifest.json.');rp.write_text(s,encoding='utf-8')
# Build index-only versions of shared documents from HEAD. Working files retain all other sessions.
index_versions={}
base=git('show','HEAD:AGENTS.md').decode();current=(R/'AGENTS.md').read_text(encoding='utf-8')
shore=next(x for x in current.splitlines() if x.startswith('Current Shoreless animation ('))
bank=next(x for x in current.splitlines() if x.startswith('Animation knowledge bank ('))
head,rest=base.split('\n\n',1);base=head+'\n\n'+shore+'\n\n'+rest
base=base.replace('Production planning:',bank+'\n\nProduction planning:',1);index_versions['AGENTS.md']=base
base=git('show','HEAD:PRODUCTION_PIPELINE.md').decode();current=(R/'PRODUCTION_PIPELINE.md').read_text(encoding='utf-8')
for prefix in ['Last updated:','| 09 |']:
 old=next(x for x in base.splitlines() if x.startswith(prefix));new=next(x for x in current.splitlines() if x.startswith(prefix));base=base.replace(old,new,1)
bank=next(x for x in current.splitlines() if x.startswith('Before any animation plan or revision,'));base=base.replace('## Where we are',bank+'\n\n## Where we are',1);index_versions['PRODUCTION_PIPELINE.md']=base
base=json.loads(git('show','HEAD:final/catalog.json'));current=json.loads((R/'final/catalog.json').read_text())
entry=next(x for x in current if x['folder']=='09-offshore-night-office')
for j,x in enumerate(base):
 if x['folder']=='09-offshore-night-office':base[j]=entry
index_versions['final/catalog.json']=json.dumps(base,indent=2)+'\n'
for name,content in index_versions.items():(T/name.replace('/','__')).write_text(content,encoding='utf-8')
save(T/'index-versions.json',{n:str(T/n.replace('/','__')) for n in index_versions})
tracked=git('ls-files','-z').decode().split('\0');save(T/'worktree-before-stage.json',{p:sha(R/p) for p in tracked if p and (R/p).is_file()})
print('Prepared exact preview backup, dependencies and selective shared-document staging files.')
