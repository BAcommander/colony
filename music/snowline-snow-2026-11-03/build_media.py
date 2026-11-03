"""Pack every post-checkpoint Snowline export, reusing unchanged base chunks."""
import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from restore_snowline_nov3 import PREFIXES, digest

spec = importlib.util.spec_from_file_location('snowline_base_builder', ROOT / 'music/snowline-sound-design-2026-11-03/build_media.py')
base_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_builder)


def build(root, out):
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'media-manifest.json').exists() or any(out.glob('*.bin')):
        raise ValueError('Use a fresh package directory')
    base_folder = root / 'music/snowline-sound-design-2026-11-03'
    base_manifest = json.loads((base_folder / 'media-manifest.json').read_text())
    for e in base_manifest['packs'] + [base_manifest['index']]:
        p = base_folder / e['file']
        if p.stat().st_size != e['bytes'] or digest(p) != e['sha256']:
            raise ValueError('Base package differs: ' + str(p))
    with gzip.open(base_folder / base_manifest['index']['file'], 'rt') as stream:
        base_index = json.load(stream)
    chunks = base_index['chunks']
    old = {e['path']: e for e in base_manifest['members']}
    files = []
    for prefix in PREFIXES:
        for p in (root / prefix).rglob('*'):
            if not p.is_file():
                continue
            relative, h = p.relative_to(root).as_posix(), digest(p)
            if relative in old:
                if p.stat().st_size != old[relative]['bytes'] or h != old[relative]['sha256']:
                    raise ValueError('Previously backed media changed: ' + relative)
            else:
                files.append((p, h))
    files.sort(key=lambda item: (-item[0].stat().st_size, item[0].as_posix()))
    print(f'All{len(old)} base members unchanged; packing{len(files)} new files.', flush=True)
    known = {}
    with ExitStack() as stack:
        handles = [stack.enter_context((base_folder / p['file']).open('rb', buffering=1024 * 1024)) for p in base_manifest['packs']]
        for i, (pack_id, offset, size) in enumerate(chunks):
            handles[pack_id].seek(offset)
            block = handles[pack_id].read(size)
            if len(block) != size:
                raise ValueError('Truncated base chunk')
            known[hashlib.sha256(block).digest()] = i
    print(f'Indexed{len(known)} verified base chunks for byte-exact reuse.', flush=True)
    packs = [dict(e, file=f'base-{i + 1:03d}.bin', repository_file=(base_folder / e['file']).relative_to(root).as_posix())
             for i, e in enumerate(base_manifest['packs'])]
    entries, duplicates, new_paths = [], {}, []
    pack, pack_id, offset = None, len(packs) - 1, 0
    try:
        for path, h in files:
            relative = path.relative_to(root).as_posix()
            entry = {'path': relative, 'bytes': path.stat().st_size, 'sha256': h}
            if h in duplicates:
                entry['duplicate_of'] = duplicates[h]
            else:
                duplicates[h] = relative
                ids, check = [], hashlib.sha256()
                for block in base_builder.blocks(path):
                    check.update(block)
                    key = hashlib.sha256(block).digest()
                    chunk_id = known.get(key)
                    if chunk_id is None:
                        if pack is None or offset + len(block) > base_builder.PACK_LIMIT:
                            if pack is not None:
                                pack.close()
                            pack_id += 1
                            path_new = out / f'snow-delta-{len(new_paths) + 1:03d}.bin'
                            new_paths.append(path_new)
                            pack = path_new.open('xb', buffering=1024 * 1024)
                            offset = 0
                        chunk_id = len(chunks)
                        known[key] = chunk_id
                        chunks.append([pack_id, offset, len(block)])
                        pack.write(block)
                        offset += len(block)
                    ids.append(chunk_id)
                if check.hexdigest() != h:
                    raise ValueError('Source changed while packing: ' + relative)
                entry['chunks'] = ids
            entries.append(entry)
            if len(entries) % 25 == 0:
                print(f'Packed{len(entries)}/{len(files)} new files.', flush=True)
    finally:
        if pack is not None:
            pack.close()
    info = lambda p: {'file': p.name, 'repository_file': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)}
    packs += [info(p) for p in new_paths]
    # Only retain chunk/pack records actually used by the new files.
    used = sorted({i for e in entries for i in e.get('chunks', [])})
    remap = {old_id: new_id for new_id, old_id in enumerate(used)}
    chunks = [chunks[i] for i in used]
    used_packs = sorted({c[0] for c in chunks})
    pack_remap = {old_id: new_id for new_id, old_id in enumerate(used_packs)}
    packs = [packs[i] for i in used_packs]
    for chunk in chunks:
        chunk[0] = pack_remap[chunk[0]]
    for entry in entries:
        if 'chunks' in entry:
            entry['chunks'] = [remap[i] for i in entry['chunks']]
    entries.sort(key=lambda e: e['path'])
    index = out / 'media-index.json.gz'
    with index.open('xb') as stream, gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as zipped:
        zipped.write(json.dumps({'schema_version': 1, 'chunks': chunks, 'files': entries}, separators=(',', ':')).encode())
    manifest = {'format': 'snowline-content-chunks-v1', 'continuation_format': 'snowline-snow-delta-v1',
                'date': '2026-11-03', 'file_count': len(entries), 'unique_chunk_count': len(chunks),
                'original_bytes': sum(e['bytes'] for e in entries), 'packs': packs, 'index': info(index),
                'members': [{k: e[k] for k in ('path', 'bytes', 'sha256')} for e in entries],
                'scope': 'Every new export after the earlier271-file checkpoint, including all snow trials and fullV6. All earlier members were verified unchanged. No audio re-encoding.',
                'base_manifest': {'file': (base_folder / 'media-manifest.json').relative_to(root).as_posix(),
                                  'sha256': digest(base_folder / 'media-manifest.json')},
                'new_payload_bytes': sum(p.stat().st_size for p in new_paths),
                'builder_sha256': digest(Path(__file__)),
                'restore_script_sha256': digest(root / 'scripts/restore_snowline_snow_session.py')}
    (out / 'media-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ('file_count', 'original_bytes', 'new_payload_bytes', 'unique_chunk_count')}, indent=2))
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    build(a.root.resolve(), a.out.resolve())
