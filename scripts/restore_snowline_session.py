"""Restore the portable Snowline checkpoint using only Python's standard library."""
import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'music' / 'snowline-sound-design-2026-11-02'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def target_path(root, relative):
    parts = PurePosixPath(relative)
    if parts.is_absolute() or '..' in parts.parts or '\\' in relative or ':' in relative:
        raise ValueError(f'Unsafe archive member: {relative}')
    if not (relative.startswith('exports/sfx/snowline-receiver-2026-11-02/') or
            relative.startswith('exports/restored-snowline-2026-11-02/')):
        raise ValueError(f'Unexpected restore destination: {relative}')
    target = root.joinpath(*parts.parts).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f'Restore destination escapes root: {relative}')
    return target


def restore(package, root, verify_only=False):
    manifest = json.loads((package / 'media-manifest.json').read_text(encoding='utf-8'))
    archive = package / manifest['archive']['file']
    if not archive.is_file() or archive.stat().st_size != manifest['archive']['bytes']:
        raise RuntimeError('Media archive missing or still a Git LFS pointer. Run the git lfs pull command in RESUME.md.')
    if digest(archive) != manifest['archive']['sha256']:
        raise RuntimeError('Media archive SHA-256 mismatch; fetch a fresh LFS copy.')
    entries = manifest['members']
    destinations = [(entry, target_path(root, entry['path'])) for entry in entries]
    conflicts = []
    missing = []
    for entry, target in destinations:
        if target.exists():
            if not target.is_file() or target.stat().st_size != entry['bytes'] or digest(target) != entry['sha256']:
                conflicts.append(entry['path'])
        else:
            missing.append(entry['path'])
    if conflicts:
        raise RuntimeError('Existing files differ; nothing overwritten. Keep your local work and restore with --root to an empty folder. Conflicts: ' + ', '.join(conflicts[:8]))
    if verify_only and missing:
        raise RuntimeError(f'{len(missing)} files missing; run without --verify-only to restore.')
    restored = 0
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != {e['path'] for e in entries} or len(z.namelist()) != len(entries):
            raise RuntimeError('Archive membership differs from manifest.')
        for entry, target in destinations:
            info = z.getinfo(entry['path'])
            if info.file_size != entry['bytes']:
                raise RuntimeError(f'Archive size differs: {entry["path"]}')
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects local files, including concurrent writes.
            with z.open(info) as source, target.open('xb') as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            if digest(target) != entry['sha256']:
                raise RuntimeError(f'Restored hash mismatch: {target}')
            restored += 1
    return {'files_verified': len(entries), 'files_restored': restored,
            'uncompressed_bytes': sum(e['bytes'] for e in entries),
            'archive_sha256': manifest['archive']['sha256'], 'root': str(root.resolve())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Alternative empty restore root')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    try:
        result = restore(PACKAGE, args.root, args.verify_only)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print(f'Snowline restore: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    print('Resume: music/snowline-sound-design-2026-11-02/RESUME.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
