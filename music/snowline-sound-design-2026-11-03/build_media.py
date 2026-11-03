"""Build a lossless, content-deduplicated backup of ALL November 3 Snowline exports.

No codec or audio processing: content-aligned binary chunks are stored once.
Use a NEW output folder. See RESUME.md; restore uses only Python's standard library.
"""
import argparse
import gzip
import hashlib
import json
import mmap
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from restore_snowline_nov3 import PREFIXES, digest

# Expected cut spacing ~1KB plus the minimum512bytes. Cuts depend on content,
# so unchanged FLAC/MP3 regions can be shared despite shifted byte offsets.
ANCHOR = re.compile(b'\xa7[' + b''.join(re.escape(bytes([i])) for i in range(1, 256, 4)) + b']')
MIN_CHUNK, MAX_CHUNK, PACK_LIMIT = 512, 16384, 512 * 1024 * 1024


def blocks(path):
    if not path.stat().st_size:
        return
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        pos = 0
        for match in ANCHOR.finditer(data):
            cut = match.start()
            if cut - pos < MIN_CHUNK:
                continue
            while cut - pos > MAX_CHUNK:
                yield data[pos:pos + MAX_CHUNK]
                pos += MAX_CHUNK
            if cut - pos >= MIN_CHUNK:
                yield data[pos:cut]
                pos = cut
        while len(data) - pos > MAX_CHUNK:
            yield data[pos:pos + MAX_CHUNK]
            pos += MAX_CHUNK
        if pos < len(data):
            yield data[pos:]


def build(root, out, files=None):
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob('*.bin')) or (out / 'media-manifest.json').exists() or (out / 'media-index.json.gz').exists():
        raise RuntimeError('Preserve existing package; use a new output directory')
    if files is None:
        files = [p for prefix in PREFIXES for p in (root / prefix).rglob('*') if p.is_file()]
    files = sorted(files, key=lambda p: (-p.stat().st_size, p.as_posix()))
    chunks, known, entries, identical = [], {}, [], {}
    pack, pack_id, offset, pack_paths = None, -1, 0, []
    try:
        for path in files:
            relative = path.relative_to(root).as_posix()
            if not relative.startswith(PREFIXES):
                raise ValueError('Outside the explicit backup scope: ' + relative)
            h, size = digest(path), path.stat().st_size
            entry = {'path': relative, 'bytes': size, 'sha256': h}
            if h in identical:
                entry['duplicate_of'] = identical[h]
            else:
                identical[h] = relative
                ids, check = [], hashlib.sha256()
                for block in blocks(path):
                    check.update(block)
                    key = hashlib.sha256(block).digest()
                    chunk_id = known.get(key)
                    if chunk_id is None:
                        if pack is None or offset + len(block) > PACK_LIMIT:
                            if pack is not None:
                                pack.close()
                            pack_id += 1
                            pack_path = out / f'media-{pack_id + 1:03d}.bin'
                            pack_paths.append(pack_path)
                            pack = pack_path.open('xb', buffering=1024 * 1024)
                            offset = 0
                        chunk_id = len(chunks)
                        known[key] = chunk_id
                        chunks.append([pack_id, offset, len(block)])
                        pack.write(block)
                        offset += len(block)
                    ids.append(chunk_id)
                if check.hexdigest() != h:
                    raise RuntimeError('Source changed while packing: ' + relative)
                entry['chunks'] = ids
            entries.append(entry)
            if len(entries) % 25 == 0:
                print(f'Packed {len(entries)}/{len(files)} files; {len(chunks)} unique chunks', flush=True)
    finally:
        if pack is not None:
            pack.close()
    entries.sort(key=lambda e: e['path'])
    index_path = out / 'media-index.json.gz'
    with index_path.open('xb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
        data = json.dumps({'schema_version': 1, 'chunks': chunks, 'files': entries}, separators=(',', ':')).encode()
        zipped.write(data)
    info = lambda p: {'file': p.name, 'bytes': p.stat().st_size, 'sha256': digest(p)}
    manifest = {'format': 'snowline-content-chunks-v1', 'date': '2026-11-03',
                'scope': 'Every file under the three listed November3 export roots, including earlier mixes, stems, short tests and the interrupted internal-path check. No audio re-encoding.',
                'source_roots': list(PREFIXES), 'file_count': len(entries),
                'original_bytes': sum(e['bytes'] for e in entries), 'unique_chunk_count': len(chunks),
                'index': info(index_path), 'packs': [info(p) for p in pack_paths],
                'members': [{k: e[k] for k in ('path', 'bytes', 'sha256')} for e in entries],
                'builder_sha256': digest(Path(__file__)),
                'restore_script_sha256': digest(ROOT / 'scripts/restore_snowline_nov3.py'),
                'older_dependency_checkpoint': 'music/snowline-sound-design-2026-11-02/media-manifest.json'}
    (out / 'media-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ('file_count', 'original_bytes', 'unique_chunk_count', 'packs')}, indent=2))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.out.resolve())
