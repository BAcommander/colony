"""Prepare this chat's exact backup scope without staging unrelated work."""
from pathlib import Path
import hashlib,json,shutil,subprocess,datetime,ast,re

REPO=Path(r'G:\AI\colony')
HERE=Path(__file__).resolve().parent
INDEX=HERE/'.local'/'index-versions'
INDEX.mkdir(parents=True,exist_ok=True)

def git(*args):
    result=subprocess.run(['git','-C',str(REPO),*map(str,args)],capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace'))
    return result.stdout

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''): h.update(block)
    return h.hexdigest()

assert datetime.date(2026,10,25).strftime('%A')=='Sunday'
head=git('rev-parse','HEAD').decode().strip()
assert not git('diff','--cached','--name-only'), 'Existing staged work; do not touch it.'

# Preserve user-supplied reference evidence without altering pixels.
evidence=REPO/'music'/'thumbnail-text-evidence-2026-10-21'
evidence.mkdir(exist_ok=True)
for src,name in [(Path(r'C:\Users\jazzs\OneDrive\Documents\ShareX\Screenshots\2026-10\chrome_MprESj3CZL.png'),'thumbnail-change-history.png'),
                 (Path(r'C:\Users\jazzs\AppData\Local\Temp\codex-clipboard-89da00b4-e7c5-4108-94ea-bb50e8d94b5e.png'),'reference-thumbnail-with-text.png')]:
    dest=evidence/name
    if not dest.exists(): shutil.copy2(src,dest)
    assert digest(src)==digest(dest)

promptdir=REPO/'music'/'illuminated-horizon-ambient-insert-v1'
original=(promptdir/'prompt.txt').read_text()
future=original.replace("Match the reference's synth palette and harmonic centre. ",'')
(promptdir/'prompt-v2-no-audio-reference.txt').write_text(future,encoding='utf-8')

music_note=(
"Illuminated Horizon / ambient-middle experiment (2026-10-21): user likes the original synth music but wants a less rhythmic middle and a gradual return. Original audio is 8:30; source MP4 and hashes are preserved in music/illuminated-horizon-slow-middle-v1/. User rejected v1 whole-mix slowdown as audibly stretched and v2 spectral reconstruction as a drone. AudioSep's genuine 45-second, three-prompt neural test selected almost the whole mix; subtracting it left remainders 22.03/23.40/51.85 dB below original RMS. Strict weight loading, negative-query controls and zero-lag checks passed; that is a failed musical separation, not a successful breakdown. SAM Audio has not run: access/sign-in helpers are prepared, authentication/model approval pending. User supplied eight-second Open Horizon; reports the arpeggio persists with the original as reference. Next manual generation attempt is planned for Sunday 2026-10-25 after the user's stated credit refresh: omit the arpeggiated audio reference, describe synth colour in text and retain changing harmony/sparse melody; confirm duration/budget then. The eight-second prompt records the earlier budget, not a Sunday duration commitment. No automatic spend or reminder authorized. See music/illuminated-horizon-backup-2026-10-21/README.md and backup-manifest.json; all session-authored packages, source copies and rejected/test media are selected for the requested backup. Downloaded models/libraries, credentials and regenerable PCM remain local. Backup and signal checks do not imply artistic acceptance.\n\n")

thumb_note=(
"Thumbnail evidence (2026-10-21): supplied third-party change-history screenshot reports VPH 47.9 to 24.9 (-48%) after a clean scene gained a large STAR WARS title. The graph had already declined before the change; this is sequential observational evidence, not a causal A/B result. Treat scene-only or title-only thumbnails as test candidates alongside approved branding; do not automatically replace approved artwork. Prefer a concurrent YouTube thumbnail test, hold title/art/crop/brightness steady when isolating typography, and assess impressions/CTR/traffic context plus watch-time share. Evidence and interpretation: music/thumbnail-text-evidence-2026-10-21/README.md.\n\n")

learning=(
"## Stereo-master arrangement experiments — Illuminated Horizon, 2026-10-21\n\n"
"- Slowing a finished stereo mix is not a composed breakdown. User rejected the pitch-preserving tempo edit because the stretching was audible. Spectral sustain/resynthesis suppressed measured pulse energy but was rejected as a drone: numeric gates do not establish musical detail or quality.\n"
"- Source separation can only expose existing material. If the repeating synth carries most harmony/melody, removing it cannot reveal a rich ambient arrangement. Test a short, genuine neural separation before building an interface or processing the full track. Listen to original, extracted estimate and remainder at one shared gain; independently normalizing a nearly empty remainder hides collateral removal.\n"
"- AudioSep was tested on original 3:20–4:05 with context and three descriptions; estimated targets correlated 0.99688–0.999997 with the original. Remainders fell 22.03–51.85 dB in RMS. Negative queries and strict checkpoint/zero-lag checks support a discrimination limitation on this sample. This is not a separation success. SAM Audio remains untested pending gated-model access.\n"
"- User reports original-reference conditioning brings back the unwanted arpeggio, including the eight-second Open Horizon insert. Audio reference guides groove/instrumentation as well as timbre; text exclusions do not guarantee selective transfer. For the next contrast test, omit that audio reference and describe the palette in text, then check harmonic compatibility and joins. Do not infer key from prominent spectral peaks or claim listening from signal analysis.\n"
"- User plans to resume Sunday 2026-10-25 after credits refresh. Earlier remaining budget was eight seconds; confirm the next duration instead of carrying that limit forward automatically. No assistant spending, generation, scheduled reminder, full-track remix or artistic approval is authorized by the backup request.\n\n"
"Exact files, feedback and backup scope: [session checkpoint](../music/illuminated-horizon-backup-2026-10-21/README.md). [Official reference guidance checked 2026-10-21](https://elevenlabs.io/docs/overview/capabilities/music/best-practices).\n\n")

def after_heading(text,heading,addition):
    marker=heading+'\n\n'
    assert marker in text, heading
    if addition in text: return text
    return text.replace(marker,marker+addition,1)

transforms={
 'AGENTS.md':lambda s:after_heading(s,'# Ambient Colony — working instructions', 'Current '+music_note+thumb_note),
 'creative/MUSIC_WORKFLOW.md':lambda s:after_heading(after_heading(s.replace('Updated 2026-10-13.','Updated 2026-10-21.',1),'## Current state',music_note),'## Evidence and analysis discipline',learning),
 'PRODUCTION_PIPELINE.md':lambda s:after_heading(s,'## Where we are',music_note),
 'final/THUMBNAIL_STYLE.md':lambda s:after_heading(s,'## Identity','2026-10-21 testing note: '+thumb_note),
}

# Preserve any other chat's current worktree changes. Stageable memory versions
# contain only our addition applied to HEAD, leaving their edits out of our commit.
index_versions={}
for name,transform in transforms.items():
    path=REPO/name
    for attempt in range(3):
        raw=path.read_bytes()
        text=raw.decode('utf-8-sig').replace('\r\n','\n')
        changed=transform(text).encode('utf-8')
        if path.read_bytes()!=raw: continue
        path.write_bytes(changed)
        break
    else: raise RuntimeError('Concurrent changes while updating '+name)
    base=git('show','HEAD:'+name).decode('utf-8-sig').replace('\r\n','\n')
    version=INDEX/name.replace('/','__')
    version.write_text(transform(base),encoding='utf-8',newline='')
    index_versions[name]=str(version)

attribute_block=('\n# Exact-byte session backup requested 2026-10-21: music experiments.\n'
 'music/illuminated-horizon-*/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n'
 'music/sam-audio-separation-test-v1/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n'
 'music/thumbnail-text-evidence-2026-10-21/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n'
 'music/illuminated-horizon-*/*.log -text -diff\n')
lfs_paths=[
 'music/illuminated-horizon-slow-middle-v1/Illuminated-Horizon-Slow-Middle-v1.wav',
 'music/illuminated-horizon-slow-middle-v1/history/internal-unrepaired/Illuminated-Horizon-Slow-Middle-v1.wav',
 'music/illuminated-horizon-ambient-middle-v2/Illuminated-Horizon-Ambient-Middle-v2.wav']
attribute_block+=''.join(p+' filter=lfs diff=lfs merge=lfs -text\n' for p in lfs_paths)
ignore_block=('\n# User-requested music session checkpoint, 2026-10-21.\n'
 '!music/illuminated-horizon-slow-middle-v1/source-original.mp4\n'
 '!music/illuminated-horizon-ambient-insert-v1/Open_Horizon_2026-10-21T155714.mp4\n'
 '/music/illuminated-horizon-separation-test-v1/*-target-raw.f32\n'
 '/music/illuminated-horizon-backup-2026-10-21/remote-backup-verification.json\n')
for name,block in [('.gitattributes',attribute_block),('.gitignore',ignore_block)]:
    path=REPO/name
    current=path.read_text(encoding='utf-8')
    if block not in current: path.write_text(current.rstrip()+'\n'+block,encoding='utf-8',newline='')
    base=git('show','HEAD:'+name).decode('utf-8')
    value=base if block in base else base.rstrip()+'\n'+block
    version=INDEX/name.replace('/','__')
    version.write_text(value,encoding='utf-8',newline='')
    index_versions[name]=str(version)

folders=['illuminated-horizon-slow-middle-v1','illuminated-horizon-ambient-middle-v2',
 'illuminated-horizon-separation-test-v1','illuminated-horizon-ambient-insert-v1',
 'sam-audio-separation-test-v1','thumbnail-text-evidence-2026-10-21',HERE.name]
files=[];excluded=[]
for folder in folders:
    for p in sorted((REPO/'music'/folder).rglob('*')):
        if not p.is_file(): continue
        relative=p.relative_to(REPO).as_posix()
        if any(v in p.parts for v in ('__pycache__','.local')) or p.suffix in ('.pyc','.f32') or p.name in ('backup-manifest.json','remote-backup-verification.json'):
            excluded.append({'path':relative,'reason':'regenerable cache, local Git preparation, self-manifest or post-push evidence'})
            continue
        if p.suffix=='.py': ast.parse(p.read_text(encoding='utf-8-sig'))
        if p.suffix=='.json': json.loads(p.read_text(encoding='utf-8-sig'))
        if p.suffix in ('.py','.md','.txt','.json','.cmd'):
            assert not re.search(rb'\bhf_[A-Za-z0-9]{25,}',p.read_bytes()),relative
        assert p.stat().st_size<=100*1024**2 or relative in lfs_paths, relative
        files.append({'path':relative,'bytes':p.stat().st_size,'sha256':digest(p),
                      'storage':'git-lfs' if relative in lfs_paths else 'git'})
for path,version in index_versions.items():
    p=Path(version)
    files.append({'path':path,'bytes':p.stat().st_size,'sha256':digest(p),'storage':'git',
                  'note':'Only session addition on HEAD is staged; unrelated worktree changes stay local.'})

manifest={'requested_by_user':True,'scope':'All session-authored packages, source copies, rejected/test media and supplied thumbnail evidence; memory updates only for this session.',
 'date':'2026-10-21','resume_date':'2026-10-25','base_commit':head,'branch':'main',
 'remote':git('remote','get-url','origin').decode().strip(),'files':files,
 'manifest_path':'music/'+HERE.name+'/backup-manifest.json',
 'manifest_self_hash':'Excluded from own file table; verify exact committed manifest separately.',
 'excluded':excluded,'additional_exclusions':['music/.local model checkpoints, downloaded code/libraries and credentials','Unrelated pending Farpoint/Spirewatch/other-scene changes','Large unrelated long-form exports'],
 'lfs_paths':lfs_paths,'index_versions':index_versions,
 'ordinary_bytes':sum(v['bytes'] for v in files if v['storage']=='git'),
 'lfs_bytes':sum(v['bytes'] for v in files if v['storage']=='git-lfs'),
 'notes':['Commit/push request does not approve rejected music edits or the separation result.',
          'No Sunday automation or paid generation is requested.',
          'Remote backup is confirmed only by later independent fetch/content hash verification.']}
(HERE/'backup-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'base':head,'files':len(files),'git_bytes':manifest['ordinary_bytes'],
                  'lfs_bytes':manifest['lfs_bytes'],'lfs_paths':lfs_paths},indent=2))
