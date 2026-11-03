"""Restore every November 3 Snowline media file using Python's standard library."""
import argparse
import gzip
import hashlib
import json
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'music/snowline-sound-design-2026-11-03'
PREFIXES = ('exports/sfx/snowline-creak-2026-11-03/',
            'exports/sfx/snowline-18min-2026-11-03/',
            'exports/13-below-the-snowline/')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_target(root, relative):
    parts = PurePosixPath(relative)
    if (not relative or parts.is_absolute() or '..' in parts.parts or
            '\\' in relative or ':' in relative or not relative.startswith(PREFIXES)):
        raise ValueError(f'Unexpected media destination: {relative}')
    target = root.joinpath(*parts.parts).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f'Media destination escapes root: {relative}')
    return target


def checked_package_file(package, entry):
    name = entry['file']
    if not name or '/' in name or '\\' in name or ':' in name or name in ('.', '..'):
        raise ValueError(f'Unsafe package filename: {name}')
    path = package / name
    if not path.is_file() or path.stat().st_size != entry['bytes']:
        raise RuntimeError(f'Media missing or still an LFS pointer: {name}. See RESUME.md.')
    if digest(path) != entry['sha256']:
        raise RuntimeError(f'Package SHA-256 mismatch: {name}')
    return path


def restore(package, root, verify_only=False):
    manifest = json.loads((package / 'media-manifest.json').read_text(encoding='utf-8'))
    if manifest['format'] != 'snowline-content-chunks-v1':
        raise ValueError('Unknown package format')
    index_file = checked_package_file(package, manifest['index'])
    packs = [checked_package_file(package, p) for p in manifest['packs']]
    with gzip.open(index_file, 'rt', encoding='utf-8') as stream:
        index = json.load(stream)
    if index['schema_version'] != 1:
        raise ValueError('Unknown index schema')
    entries, chunks = index['files'], index['chunks']
    if len(entries) != manifest['file_count'] or len(chunks) != manifest['unique_chunk_count']:
        raise ValueError('Index count mismatch')
    summaries = [{k: e[k] for k in ('path', 'bytes', 'sha256')} for e in entries]
    if summaries != manifest['members']:
        raise ValueError('Index members differ from readable manifest')
    for pack_id, offset, size in chunks:
        if (not 0 <= pack_id < len(packs) or offset < 0 or size <= 0 or
                offset + size > manifest['packs'][pack_id]['bytes']):
            raise ValueError('Chunk lies outside its pack')
    by_path = {e['path']: e for e in entries}
    if len(by_path) != len(entries):
        raise ValueError('Duplicate destination in media index')
    destinations, conflicts, missing = [], [], []
    for entry in entries:
        target = safe_target(root, entry['path'])
        source = by_path.get(entry.get('duplicate_of'), entry)
        if 'chunks' not in source:
            raise ValueError('Invalid duplicate reference')
        ids = source['chunks']
        if any(not isinstance(i, int) or not 0 <= i < len(chunks) for i in ids):
            raise ValueError('Unknown chunk reference')
        if sum(chunks[i][2] for i in ids) != entry['bytes']:
            raise ValueError(f'Chunk lengths differ: {entry["path"]}')
        destinations.append((entry, target, ids))
        if target.exists():
            if not target.is_file() or target.stat().st_size != entry['bytes'] or digest(target) != entry['sha256']:
                conflicts.append(entry['path'])
        else:
            missing.append(entry['path'])
    if conflicts:
        raise RuntimeError('Nothing overwritten; existing files differ. Use --root with an empty folder. Conflicts: ' + ', '.join(conflicts[:8]))
    if verify_only and missing:
        raise RuntimeError(f'{len(missing)} files missing; run without --verify-only to restore.')
    restored = 0
    with ExitStack() as stack:
        handles = [stack.enter_context(p.open('rb', buffering=1024 * 1024)) for p in packs]
        for entry, target, ids in destinations:
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Verify a temporary file before publishing it. A hard link creates the
            # destination atomically without overwriting a concurrent local write.
            fd, temp_name = tempfile.mkstemp(prefix='.snowline-restore-', dir=target.parent)
            temp = Path(temp_name)
            try:
                h = hashlib.sha256()
                with os.fdopen(fd, 'wb', buffering=1024 * 1024) as output:
                    for i in ids:
                        pack_id, offset, size = chunks[i]
                        source = handles[pack_id]
                        source.seek(offset)
                        data = source.read(size)
                        if len(data) != size:
                            raise RuntimeError('Short pack read')
                        h.update(data)
                        output.write(data)
                if h.hexdigest() != entry['sha256']:
                    raise RuntimeError(f'Restored SHA-256 mismatch: {entry["path"]}')
                os.link(temp, target)
            finally:
                temp.unlink(missing_ok=True)
            restored += 1
            if restored % 25 == 0:
                print(f'Restored {restored}/{len(missing)} files', flush=True)
    return {'files_verified': len(entries), 'files_restored': restored,
            'original_bytes': sum(e['bytes'] for e in entries),
            'package_bytes': sum(p['bytes'] for p in manifest['packs']) + manifest['index']['bytes'],
            'root': str(root.resolve()), 'all_file_hashes_match': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(restore(args.package, args.root, args.verify_only), indent=2))


if __name__ == '__main__':
    main()
