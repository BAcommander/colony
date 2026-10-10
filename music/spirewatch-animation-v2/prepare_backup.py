import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('G:/AI/colony')
HERE = ROOT / 'music/spirewatch-animation-v2'
DIRS = ['music/digital-city-concepts-v1', 'music/spirewatch-animation-v1', 'music/spirewatch-animation-v2']
PREVIEW = 'music/spirewatch-animation-v2/spirewatch-v2-preview-60s.mp4'
FEEDBACK = "User said \"it's getting better\" and requested commit/push on 2026-10-11. Positive progress checkpoint; further refinement remains open, not final artistic approval."

def git(*args, data=None):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], input=data)

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def write(path, value):
    (ROOT / path).write_text(value, encoding='utf-8', newline='\n')

def edit_json(path, **updates):
    value = json.loads(read(path))
    value.update(updates)
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def stage_content(path, value):
    blob = git('hash-object', '-w', '--stdin', data=value.encode('utf-8')).decode().strip()
    git('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}')

assert not git('diff', '--cached', '--name-only').strip(), 'Index must be empty before scoped staging'
edit_json('music/digital-city-concepts-v1/current-direction.json', status='V2 positive progress checkpoint; backup requested', latest_feedback=FEEDBACK)
edit_json('music/spirewatch-animation-v2/visual-review.json', status='Positive progress checkpoint; refinement remains open', latest_user_feedback=FEEDBACK, scope='Positive comparative feedback and backup authorization; no final artistic approval inferred')
write('music/spirewatch-animation-v2/user-feedback-2026-10-11.json', json.dumps({'date': '2026-10-11', 'verbatim': "it's getting better, commit and push", 'scope': FEEDBACK}, indent=2) + '\n')
p = 'music/spirewatch-animation-v2/README.md'
s = read(p).replace('preview; user visual review pending.', 'preview. User says “it\'s getting better”; saved as a positive progress checkpoint, with further refinement open.')
s = s.replace('No music, 4K master, long assembly, upload, paid service, new model, commit or push in this delivery. New media remain local.', 'No music, 4K master, long assembly, upload, paid service or new model in this delivery. User requested commit/push on 2026-10-11. Source art, code/configuration, masks, inspection/history records and the exact v2 minute preview are selected for Git backup; repeated reviews and intermediate videos remain local. See backup-manifest.json and the subsequent local remote-backup-verification.json for actual remote evidence. package-manifest.json preserves the earlier delivery inventory; backup-manifest.json records this checkpoint.')
write(p, s)

p = 'AGENTS.md'
s = read(p)
old = next(x for x in s.split('\n\n') if x.startswith('Current Spirewatch animation'))
new = old.replace('V2 awaits user visual verdict; implementation authorization is not acceptance.', 'User now says “it\'s getting better” and explicitly requests commit/push (2026-10-11): positive progress checkpoint, not final artistic approval.')
new = new.replace('No 4K, new music, long assembly, commit, push, paid service or remote media backup.', 'No 4K, new music, long assembly or paid service. Source/art/config/masks/history records and the exact v2 minute preview are selected for Git backup; see music/spirewatch-animation-v2/backup-manifest.json and subsequent local remote-backup-verification.json for remote evidence. Repeated/older/intermediate videos remain local.')
write(p, s.replace(old, new))
base = git('show', 'HEAD:' + p).decode('utf-8')
head, rest = base.split('\n\n', 1)
stage_content(p, head + '\n\n' + new + '\n\n' + rest)

p = 'PRODUCTION_PIPELINE.md'
s = read(p)
start = s.index('## Unnumbered city concept — Spirewatch')
end = s.index('## Next concept exploration', start)
old = s[start:end]
new = old.replace('User visual review is next;', 'User says “it\'s getting better” and requested commit/push on 2026-10-11; further refinement remains open;')
new = new.replace('No catalog number, commit, push or remote media backup; other releases unchanged.', 'No catalog number. Current minute preview and scene source/history/records are selected for backup; see the v2 backup manifest and subsequent local remote verification receipt. Repeated/intermediate videos remain local; other releases unchanged.')
write(p, s[:start] + new + s[end:])
base = git('show', 'HEAD:' + p).decode('utf-8')
stage_content(p, base.replace('## Next concept exploration', new + '## Next concept exploration', 1))

p = 'creative/ANIMATION_KNOWLEDGE_BANK.md'
s = read(p)
start = s.index('## Spirewatch animation candidate')
section = s[start:].replace('**V1 needs substantial improvement; v2 delivered for user review.**', '**V1 needs substantial improvement; v2 is a positive progress checkpoint.**').replace('No v2 artistic verdict yet.', 'On 2026-10-11 the user said “it\'s getting better” and requested commit/push. Preserve this comparative verdict without treating v2 as finally approved.')
write(p, s[:start] + section)
base = git('show', 'HEAD:' + p).decode('utf-8')
stage_content(p, base.rstrip() + '\n\n' + section)

p = '.gitignore'
s = read(p)
s += '\n# Spirewatch v2 checkpoint: exact preview; reviews/intermediates stay local\n!' + PREVIEW + '\n/music/spirewatch-animation-v2/remote-backup-verification.json\n'
write(p, s)
p = '.gitattributes'
s = read(p)
s += '\n# Preserve fingerprinted Spirewatch source and records byte for byte\n' + '\n'.join(d + '/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol' for d in DIRS) + '\n'
write(p, s)
git('add', '--', '.gitignore', '.gitattributes', *DIRS)
paths = git('diff', '--cached', '--name-only', '-z').decode().split('\0')
records = []
for path in filter(None, paths):
    if path in ['AGENTS.md', 'PRODUCTION_PIPELINE.md', 'creative/ANIMATION_KNOWLEDGE_BANK.md']:
        continue  # scoped index contents differ from preserved unrelated working edits
    data = git('show', ':' + path)
    assert len(data) < 100 * 1024 * 1024, path
    assert data == (ROOT / path).read_bytes(), 'Byte preservation failed: ' + path
    records.append({'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
manifest = {'date': '2026-10-11', 'feedback': FEEDBACK, 'scope': 'Spirewatch artwork candidates, animation v1/v2 source/config/masks/history/inspection records, exact current v2 minute preview. Unrelated Farpoint working changes preserved unstaged.', 'local_only': 'Repeated/older/isolated/intermediate videos and Python caches. Existing delivery inventory is historical.', 'files': records, 'shared_documents': ['AGENTS.md: Spirewatch paragraph only', 'PRODUCTION_PIPELINE.md: Spirewatch section only', 'creative/ANIMATION_KNOWLEDGE_BANK.md: Spirewatch lessons only'], 'self_excluded': True, 'remote_evidence': 'remote-backup-verification.json (local receipt after push)'}
write('music/spirewatch-animation-v2/backup-manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
git('add', '--', 'music/spirewatch-animation-v2/backup-manifest.json')
print(json.dumps({'staged_files': len(records) + 4, 'bytes': sum(x['bytes'] for x in records), 'preview': next(x for x in records if x['path'] == PREVIEW)}, indent=2))
