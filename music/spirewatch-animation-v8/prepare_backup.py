"""Stage the requested Spirewatch checkpoint while preserving unrelated work."""
from pathlib import Path
import hashlib, json, subprocess

ROOT = Path('G:/AI/colony')
PKG = ROOT / 'music/spirewatch-animation-v8'
def git(*args, data=None):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], input=data)
def digest(data):
    return hashlib.sha256(data).hexdigest()
def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

assert not git('diff', '--cached', '--name-only').strip(), 'Existing index must be preserved'
assert git('rev-parse', 'HEAD') == git('rev-parse', 'origin/main')
for name, text in {
    '.gitattributes': '\n# Preserve exact Spirewatch rebuild and finishing checkpoint bytes.\nmusic/spirewatch-animation-v[4-8]/** -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\nmusic/spirewatch-artwork-rebuild-v1/** -text\n',
    '.gitignore': '\n# Current Spirewatch finishing preview; older/repeated/intermediate videos stay local.\n!music/spirewatch-animation-v8/spirewatch-v8-preview-60s.mp4\nmusic/spirewatch-animation-v8/remote-backup-verification.json\n'
}.items():
    with (ROOT / name).open('a', encoding='utf-8', newline='') as f:
        f.write(text)

note = 'Backup requested 2026-10-21: current v8 minute preview plus v4–v8 source, artwork, thumbnail, masks, diagnostics, feedback and learnings selected. Older/repeated/isolated/intermediate videos remain local. See music/spirewatch-animation-v8/backup-manifest.json and subsequent local remote-backup-verification.json for scope and remote evidence. Delivery-time uncommitted statements below are historical; backup does not imply artistic approval.'
p = ROOT / 'AGENTS.md'
s = p.read_text(encoding='utf-8')
s = s.replace('User v8 review pending; no music/4K/long assembly/commit/push.', 'User v8 review pending; no music/4K/long assembly. ' + note, 1)
p.write_text(s, encoding='utf-8')
p = ROOT / 'PRODUCTION_PIPELINE.md'
s = p.read_text(encoding='utf-8').replace('Earlier versions preserved. Unnumbered, local/uncommitted/unpushed.', 'Earlier versions preserved. Unnumbered. ' + note, 1)
p.write_text(s, encoding='utf-8')
p = PKG / 'README.md'
p.write_text(p.read_text(encoding='utf-8') + '\n## Requested backup\n\n' + note + '\n', encoding='utf-8')
p = ROOT / 'music/digital-city-concepts-v1/current-direction.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['backup_request'] = note
save(p, d)

# Build index-only versions of shared documents, retaining unrelated local edits.
shared = ['AGENTS.md', 'PRODUCTION_PIPELINE.md', 'creative/ANIMATION_KNOWLEDGE_BANK.md']
staged = {}
for name in shared:
    base = git('show', 'HEAD:' + name).decode('utf-8')
    work = (ROOT / name).read_text(encoding='utf-8')
    if name == 'AGENTS.md':
        work = '\n\n'.join(p for p in work.split('\n\n') if not p.startswith('Current Farpoint music/production (2026-10-10):'))
        prefix = 'Current Farpoint animation (2026-10-07):'
        old = next(p for p in base.split('\n\n') if p.startswith(prefix))
        work = '\n\n'.join(old if p.startswith(prefix) else p for p in work.split('\n\n'))
    elif name == 'PRODUCTION_PIPELINE.md':
        old = next(line for line in base.splitlines() if line.startswith('| 10 |'))
        work = '\n'.join(old if line.startswith('| 10 |') else line for line in work.splitlines()) + '\n'
    else:
        prefix = 'For videos 12–14,'
        old = next(p for p in base.split('\n\n') if p.startswith(prefix))
        work = '\n\n'.join(old if p.startswith(prefix) else p for p in work.split('\n\n') if not p.startswith('Farpoint dependency preservation (2026-10-10):'))
    staged[name] = work.encode('utf-8')

selected, excluded = [], []
preview = 'music/spirewatch-animation-v8/spirewatch-v8-preview-60s.mp4'
for folder in [*(ROOT / f'music/spirewatch-animation-v{v}' for v in range(4, 9)), ROOT / 'music/spirewatch-artwork-rebuild-v1']:
    for p in sorted(folder.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        omit = '__pycache__' in p.parts or 'render-parts' in p.parts or p.suffix in {'.pyc', '.npy', '.f32'} or (p.suffix in {'.mp4', '.mov', '.wav', '.flac'} and rel != preview)
        if p.name in {'backup-manifest.json', 'remote-backup-verification.json'}:
            continue
        (excluded if omit else selected).append(rel)
selected += ['.gitattributes', '.gitignore', 'music/digital-city-concepts-v1/current-direction.json']
selected += shared
records = []
for rel in selected:
    data = staged.get(rel, (ROOT / rel).read_bytes())
    assert len(data) < 100 * 1024**2, rel
    records.append({'path': rel, 'bytes': len(data), 'sha256': digest(data), 'index_only_scoped_document': rel in staged})
assert next(x['sha256'] for x in records if x['path'] == preview) == json.loads((PKG / 'delivery-v8.json').read_text())['preview_sha256']
save(PKG / 'backup-manifest.json', {'date': '2026-10-21', 'base_commit': git('rev-parse','HEAD').decode().strip(), 'scope': note, 'files': records, 'excluded_local_files': excluded, 'unrelated_changes': 'Farpoint documents/media preserved unstaged; existing music experiment commit preserved. Shared document index versions contain only Spirewatch changes.'})
ordinary = [p for p in selected if p not in staged] + ['music/spirewatch-animation-v8/backup-manifest.json']
for start in range(0, len(ordinary), 50):
    git('add', '--', *ordinary[start:start+50])
for name, content in staged.items():
    oid = git('hash-object', '-w', '--stdin', data=content).decode().strip()
    git('update-index', '--cacheinfo', '100644', oid, name)
for rec in records:
    actual = git('show', ':' + rec['path'])
    assert digest(actual) == rec['sha256'], rec['path']
print(json.dumps({'selected_files':len(records)+1, 'selected_bytes':sum(x['bytes'] for x in records), 'excluded_files':len(excluded), 'staged_hashes_verified':True}))
