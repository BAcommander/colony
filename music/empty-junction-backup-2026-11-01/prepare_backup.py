from pathlib import Path
import subprocess,json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACKAGES=['music/empty-junction-animation-v4','music/empty-junction-animation-v5','music/empty-junction-music-v1','music/empty-junction-visual-revision-v1']
DOCS=['AGENTS.md','PRODUCTION_PIPELINE.md','creative/ANIMATION_KNOWLEDGE_BANK.md','final/11-empty-junction/README.md','final/11-empty-junction/manifest.json','final/11-empty-junction/youtube-title.txt']
VIDEOS=[
 'music/empty-junction-animation-v4/Empty-Junction-v4-wind-minute-720p.mp4',
 'music/empty-junction-animation-v4/Empty-Junction-v4-quiet-minute-720p.mp4',
 'music/empty-junction-animation-v4/Empty-Junction-v4-with-approved-audio-4min-720p.mp4',
 'music/empty-junction-animation-v4/cabin_exhaust-v4-isolated-8s.mp4',
 'music/empty-junction-animation-v4/yard_powder-v4-isolated-8s.mp4',
 'music/empty-junction-animation-v5/Empty-Junction-v5-60s-720p.mp4',
 'music/empty-junction-animation-v5/Empty-Junction-v5-with-approved-audio-60s-720p.mp4',
 'music/empty-junction-animation-v5/Empty-Junction-v4-v5-details-20s.mp4',
 'music/empty-junction-music-v1/sources/Signal_Cabin_Wait_2026-10-31T161557.mp4',
 'music/empty-junction-music-v1/sources/Quiet_Signal_Cabin_2026-10-31T161557.mp4']
def append_once(path,heading,body):
 old=path.read_bytes();assert heading.encode() not in old
 with path.open('ab') as f:f.write(('\n'+heading+'\n'+body+'\n').encode())
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
 append_once(ROOT/'.gitignore','# Empty Junction checkpoint requested 2026-11-01.', '\n'.join('!'+p for p in VIDEOS)+'\n/music/empty-junction-backup-2026-11-01/remote-backup-verification.json')
 local=ROOT/'music/empty-junction-music-v1/.gitignore';raw=local.read_bytes();assert b'/review/' in raw
 local.write_bytes(raw.replace(b'/review/',b'/review/*\n!/review/*.mp3',1))
 media=VIDEOS+[p.relative_to(ROOT).as_posix() for d in ['sources','review'] for p in (ROOT/'music/empty-junction-music-v1'/d).glob('*.mp3')]
 body='\n'.join(p+'/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol' for p in PACKAGES+['music/empty-junction-backup-2026-11-01'])
 body+='\n'+ '\n'.join(p+' filter=lfs diff=lfs merge=lfs -text' for p in media)
 body+='\nfinal/11-empty-junction/manifest.json -text\nfinal/11-empty-junction/youtube-title.txt -text'
 append_once(ROOT/'.gitattributes','# Exact Junction source/records and selected LFS media, 2026-11-01.',body)
 files=set(git('ls-files','--others','--exclude-standard','-z','--',*PACKAGES).decode().split('\0'))-{''}
 files.update(DOCS+['.gitattributes','.gitignore'])
 assert set(media)<=files
 assert not any('/.cache/' in p or '/media/' in p or p.endswith(('.f32','.pyc')) for p in files)
 records=[];images=0
 for rel in sorted(files):
  p=ROOT/rel;raw=p.read_bytes()
  if p.suffix.lower() in ('.png','.jpg','.jpeg'):
   with Image.open(p) as im:im.verify()
   images+=1
  records.append({'path':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'storage':'lfs' if rel in media else 'git'})
 result={'requested':'commit and push','date':'2026-11-01','scope':'All authored Junction session artwork, thumbnail variants, supplied music/SFX sources, recipes, reviews, animation v4/v5 and lessons.','user_audio_balance_approved':True,'user_v5_animation_approved':False,'files':records,'image_files_verified':images,'lfs_files':len(media),'bytes':sum(r['bytes'] for r in records),'excluded':['Hour-long exports and duplicated delivery media','Raw PCM/render caches and Python bytecode','Derived repeated-cycle videos','Aborted/internal encoding trial videos; code and diagnostic history retained','Unrelated Rainline, Shoreless, Farpoint and Spirewatch working files'],'remote_verified':False}
 (HERE/'backup-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 (HERE/'stage-paths.txt').write_text('\n'.join(sorted(files|{HERE.relative_to(ROOT).as_posix()}))+'\n')
 print(json.dumps({k:result[k] for k in ['image_files_verified','lfs_files','bytes']})+' files='+str(len(files)))
if __name__=='__main__':main()
