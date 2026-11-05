"""Select current review media and adapt the proven exact remote-restore workflow."""
from pathlib import Path
import json
B=Path(__file__).resolve().parent;R=B.parents[1]
def append(path,value):path.write_bytes(path.read_bytes()+value.encode())
def main():
    folders=['music/cyberpunk-apartment-animation-v4','music/gate-camp-animation-v3','music/scene-animation-core','music/scene16-17-first-draft-assets']
    media=sorted(p.relative_to(R).as_posix() for f in folders[:2] for p in (R/f).glob('*.mp4') if 'proof' not in p.name.lower())
    append(R/'.gitattributes','\n# Requested scene16/17 checkpoint: preserve fingerprinted bytes.\n'+''.join('/'+f+'/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n' for f in folders+[B.relative_to(R).as_posix()])+''.join('/'+p+' filter=lfs diff=lfs merge=lfs -text\n' for p in media))
    append(R/'.gitignore','\n# Requested scene16/17 current visual review package.\n'+''.join('!/'+p+'\n' for p in media)+'/'+B.relative_to(R).as_posix()+'/remote-backup-verification.json\n')
    policy={'authority':'User: commit and push everything, then investigate animation18.','branch':'main','include':'All authored scene16/17 plans, current minutes and linked detail/join reviews, generated assets/provenance, code/settings/validation and shared learnings.','media':media,'excluded_local':'Gate-proof-8s, superseded city proofs, .local render history/caches and Python bytecode; no full-length exports in this task.','artistic_review':'pending; backup is not approval','future18':'Investigate after this checkpoint is pushed; no release18 assignment yet.'}
    (B/'selection-policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    source=R/'music/production-backup-2026-11-05-crater-rim'
    text=(source/'build_manifest.py').read_text()
    text=text.replace("git(['ls-files', '-z', 'final/14-crater-rim-survey/']).decode('utf-8').strip('\\0').split('\\0')","['final/16-cyberpunk-apartment/artwork-v3.png','creative/brainstorm/2026-10-27-three-worlds/e1-gate-camp/concept-v1.png']")
    text=text.replace('User requests saving all continuation details, commit and push.','User requests committing and pushing all scene16/17 drafts, assets and learnings.')
    text=text.replace("path.startswith(tuple(f'music/crater-rim-animation-v{i}/' for i in range(2, 6)))","path.startswith(('music/cyberpunk-apartment-animation-v4/','music/gate-camp-animation-v3/','music/scene-animation-core/','music/scene16-17-first-draft-assets/'))")
    (B/'build_manifest.py').write_text(text)
    text=(source/'verify_remote.py').read_text().replace('crater-rim-2026-11-05-','scenes16-17-2026-11-05-')
    text=text.replace('Checking the independently restored continuation package and six native V5 states','Checking both independently restored scene renderers, source geometry and review links')
    text=text.replace('music/crater-rim-animation-v5/validate_long_version_plan.py','music/scene-animation-core/validate_geometry.py').replace(",'--check-only'",'')
    text=text.replace("resumed=json.loads(check.stdout.strip().splitlines()[-1]);assert resumed['status']=='passed'","resumed=json.loads(check.stdout);assert resumed['missing']==[]")
    (B/'verify_remote.py').write_text(text)
    print(json.dumps({'media_files':len(media),'backup_folder':B.relative_to(R).as_posix()}))
if __name__=='__main__':main()
