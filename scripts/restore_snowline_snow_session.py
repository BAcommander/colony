"""Restore the snow continuation, reusing verified November3 base media packs."""
import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath

from restore_snowline_nov3 import restore

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'music/snowline-snow-2026-11-03'
ALLOWED = ('music/snowline-sound-design-2026-11-03/', 'music/snowline-snow-2026-11-03/')


def materialize_package(package, checkout, temporary):
    manifest = json.loads((package / 'media-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('continuation_format') != 'snowline-snow-delta-v1':
        raise ValueError('Unknown continuation package')
    seen = set()
    for entry in manifest['packs'] + [manifest['index']]:
        name = entry['file']
        if not name or '/' in name or '\\' in name or ':' in name or name in ('.', '..'):
            raise ValueError('Unsafe package filename')
        if name in seen:
            raise ValueError('Duplicate package filename')
        seen.add(name)
        relative = entry['repository_file']
        parts = PurePosixPath(relative)
        if (parts.is_absolute() or '..' in parts.parts or '\\' in relative or ':' in relative or
                not relative.startswith(ALLOWED)):
            raise ValueError('Unexpected pack source: ' + relative)
        source = checkout.joinpath(*parts.parts).resolve()
        if not source.is_relative_to(checkout.resolve()) or not source.is_file():
            raise RuntimeError('Missing package source; run the LFS pull command in RESUME.md: ' + relative)
        if source.stat().st_size != entry['bytes']:
            raise RuntimeError('Missing media or an LFS pointer: ' + relative)
        target = temporary / name
        try:
            os.link(source, target)
        except OSError:
            # Exclusive creation also prevents overwriting a prior hard link.
            with source.open('rb') as input_file, target.open('xb') as output_file:
                shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
    (temporary / 'media-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')


def restore_continuation(package, checkout, destination, verify_only=False):
    scratch = checkout / '.local'
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='snow-media-links-', dir=scratch) as name:
        temporary = Path(name).resolve()
        # Verify the cleanup scope before TemporaryDirectory removes its tree.
        if not temporary.is_relative_to(scratch.resolve()):
            raise ValueError('Temporary restore directory escaped the workspace')
        materialize_package(package, checkout, temporary)
        return restore(temporary, destination, verify_only)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT, help='Destination root; conflicts are never overwritten')
    p.add_argument('--checkout', type=Path, default=ROOT, help='Checkout containing base and continuation packages')
    p.add_argument('--package', type=Path, default=PACKAGE)
    p.add_argument('--verify-only', action='store_true')
    a = p.parse_args()
    print(json.dumps(restore_continuation(a.package.resolve(), a.checkout.resolve(), a.root.resolve(), a.verify_only), indent=2))
