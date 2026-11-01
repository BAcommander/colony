"""Select today's authored work and reproducible-source media without broad staging."""
from pathlib import Path
import subprocess, json, hashlib
H=Path(__file__).resolve().parent;R=H.parents[1]
SCOPES=['final/12-deepwell-station/upload-2026-11-01','music/deepwell-final-hour-v1','music/deepwell-production-2026-11-01','music/deepwell-thumbnail-v2','music/empty-junction-animation-v6','music/empty-junction-final-hour-v1','music/empty-junction-final-hour-v2','music/prompt-learnings-2026-11-01','music/sfx-library','music/production-backup-2026-11-01']
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def lines(raw):return [x.decode('utf-8') for x in raw.split(b'\0') if x]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 assert not git('diff','--cached','--name-only').strip(),'Existing staged work: review before adding'
 assert git('branch','--show-current').decode().strip()=='codex/empty-junction-backup-2026-11-01'
 C=H/'cache';C.mkdir(exist_ok=True)
 media=[]
 dp=R/'music/deepwell-production-2026-11-01'
 media += list((dp/'sources').glob('*.mp4'))+list((dp/'sources').glob('*.mp3'))+list((dp/'review').glob('*.mp3'))
 for p in dp.glob('combined-review-v*'):media+=list(p.glob('*.mp3'))
 # Keep accepted lossless review as build_hour.py's precise prefix control.
 media += [dp/'combined-review-v4/Deepwell-both-music-water-wind-pump-8min-v4.flac']
 media += list((R/'music/sfx-library/assets').glob('*.mp3'))+list((R/'music/sfx-library/previews').glob('*.mp3'))
 media += [R/'music/empty-junction-animation-v6/Empty-Junction-v6-30s-720p.mp4',R/'music/empty-junction-animation-v6/Empty-Junction-v6-with-approved-audio-30s-720p.mp4']
 media += [R/'music/empty-junction-final-hour-v1/masters'/f'Empty-Junction-v6-{mode}-60s-4K.mp4' for mode in ['wind','quiet']]
 media += [R/'music/deepwell-final-hour-v1/masters/Deepwell-v4-20s-4K.mp4',R/'music/empty-junction-final-hour-v2/Empty-Junction-more-frequent-SFX-check-6min.mp3']
 for p in media:assert p.is_file(),p
 media=sorted({p.relative_to(R).as_posix() for p in media})
 attr=R/'.gitattributes'
 with attr.open('a',encoding='utf-8',newline='') as f:
  f.write('\n# All-day production backup requested 2026-11-01; preserve fingerprinted bytes.\n')
  for scope in SCOPES:f.write(scope+'/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n')
  f.write('AGENTS.md whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n')
  f.write('final/12-deepwell-station/manifest.json -text\n')
  for p in media:f.write(p+' filter=lfs diff=lfs merge=lfs -text\n')
 modified=lines(git('diff','--name-only','-z'))
 untracked=lines(git('ls-files','--others','--exclude-standard','-z','--',*SCOPES))
 selected=sorted(set(modified+untracked+media))
 assert not any('/cache/' in p or '/render-cache/' in p or '/verification-cache/' in p or p.startswith('exports/') for p in selected)
 assert all(not p.endswith(('.f32','.pyc')) for p in selected)
 # Record media choices and size before staging; secret scan emits paths only.
 suspicious=[]
 import re
 for name in selected:
  p=R/name
  if p.suffix.lower() in ['.py','.cjs','.json','.md','.txt','.html'] and p.stat().st_size<10_000_000:
   text=p.read_text(encoding='utf-8',errors='replace')
   if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{35,}|sk-(?:proj-)?[A-Za-z0-9_-]{40,}|AKIA[0-9A-Z]{16})',text):suspicious.append(name)
 assert not suspicious,('Potential literal credential needs inspection',suspicious)
 selection={'date':'2026-11-01','request':'commit and push all todays work','branch':git('branch','--show-current').decode().strip(),'base_commit':git('rev-parse','HEAD').decode().strip(),'scopes':SCOPES,'selected_paths':selected,'lfs_paths':media,'exclusions':['Full-hour video/audio exports under exports/ remain local under existing repository media policy.','Render caches, raw PCM, repeated-cycle masters, duplicate intermediate FLACs and analysis body-window cache remain regenerable local files.','Pre-existing unrelated Rainline/Shoreless/Farpoint audition files and Spirewatch render caches are not today\'s work.'],'secret_scan':'No credential-shaped literal found in selected authored text.','lfs_total_bytes':sum((R/p).stat().st_size for p in media)}
 (H/'selection.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
 selected+=['music/production-backup-2026-11-01/selection.json']
 (C/'paths.nul').write_bytes(b'\0'.join(p.encode() for p in sorted(set(selected)))+b'\0')
 print(json.dumps({'selected_paths':len(set(selected)),'lfs_paths':len(media),'lfs_mb':round(selection['lfs_total_bytes']/1e6,1),'largest_media':sorted([{'path':p,'mb':round((R/p).stat().st_size/1e6,1)} for p in media],key=lambda x:-x['mb'])[:5]},indent=2))
if __name__=='__main__':main()
