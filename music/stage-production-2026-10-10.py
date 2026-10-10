from pathlib import Path
import subprocess,json,hashlib
R=Path('G:/AI/colony');B=R/'music/production-backup-2026-10-10'
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode('utf-8')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
tool='284c6a756322f47d003ad7c6986d851870b99f4f'
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');note=f'Current backup request (2026-10-10): User requested commit/push and saving all learnings, then improved Shoreless tags. Music workflow now records approved Rainline rain and Shoreless water balances, plateau review, separate joins, amplitude reductions and listener-oriented tags. Animation knowledge bank records exact-source 4K delivery, colour preservation, loop verification and slow MP4 finalization. Colony tool SFX implementation is pushed to slideshow main at {tool}; its source still matched the existing 54 passing tests/build evidence before commit. Production code/records and four short 4K masters are selected for Colony Git/LFS backup; see music/production-backup-2026-10-10/scope.json and the later local remote-verification.json for actual remote evidence. Large combined videos, full music sources, intermediate PCM and caches remain local; a Git records backup is not a remote backup of these long media. Earlier no-push statements describe the original delivery sessions.'
s=s.replace('\n\n','\n\n'+note+'\n\n',1);s=s.replace('Tool source changes are in that separate repository, uncommitted.',f'Tool source changes subsequently committed and pushed at {tool}; see Current backup request.');p.write_text(s,encoding='utf-8')
p=R/'music/colony-sfx-update/backup-2026-10-10.json';p.write_text(json.dumps({'repository':'https://github.com/BAcommander/slideshow','commit':tool,'branch':'main','ls_remote_verified':True,'source_matched_prior_tested_build':True,'tests':'43 regression + 11 real-audio SFX tests passed during implementation; source hashes unchanged at commit preparation.','executable':'Local dist/Colony.exe; binary not in Git.'},indent=2)+'\n',encoding='utf-8')
modified=[p for p in git('diff','--name-only','-z').split('\0') if p]
unknown=[p for p in git('ls-files','--others','--exclude-standard','-z').split('\0') if p]
allowed={'.py','.json','.md','.txt','.png','.jpg'}
special={'music/shared-rain-overlay/Gentle_continuous_ra_#2-1791634292024.mp3','final/09-offshore-night-office/music/water-mix-v1/Clear_ocean_water_re_#1-1791650516724.mp3'}
scope=json.loads((B/'scope.json').read_text());special.update(x['path'] for x in scope['masters'])
selected=sorted(set(modified+[p for p in unknown if Path(p).suffix.lower() in allowed or p in special]))
assert all(p.startswith(('music/','final/','creative/')) or p in ['AGENTS.md','PRODUCTION_PIPELINE.md','.gitignore','.gitattributes'] for p in selected)
files=[{'path':p,'bytes':(R/p).stat().st_size,'sha256':sha(R/p)} for p in selected]
manifest=B/'files.json';manifest.write_text(json.dumps({'files':files,'excluded_untracked':[p for p in unknown if p not in selected],'tool_commit':tool},indent=2)+'\n',encoding='utf-8')
selected.append(manifest.relative_to(R).as_posix())
# Exact list, no wildcard staging of audio intermediates or cached data.
for i in range(0,len(selected),60):subprocess.run(['git','add','--',*selected[i:i+60]],cwd=R,check=True)
print(json.dumps({'selected_files':len(selected),'excluded_untracked':[p for p in unknown if p not in selected]},indent=2))
