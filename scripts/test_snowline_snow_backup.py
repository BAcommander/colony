"""Check incremental byte reuse, exact restore, conflicts and hostile metadata."""
import contextlib
import importlib.util
import io
import json
import random
import shutil
import tempfile
import unittest
from pathlib import Path

from restore_snowline_snow_session import restore_continuation

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('snow_delta_builder', ROOT / 'music/snowline-snow-2026-11-03/build_media.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def fixture(folder):
    checkout = folder / 'checkout'
    export = checkout / 'exports/13-below-the-snowline'
    export.mkdir(parents=True)
    raw = random.Random(17).randbytes(100000)
    base_file = export / 'base.bin'
    base_file.write_bytes(raw)
    source = ROOT / 'scripts/restore_snowline_snow_session.py'
    (checkout / 'scripts').mkdir()
    shutil.copyfile(source, checkout / 'scripts'/ source.name)
    base = checkout / 'music/snowline-sound-design-2026-11-03'
    package = checkout / 'music/snowline-snow-2026-11-03'
    with contextlib.redirect_stdout(io.StringIO()):
        builder.base_builder.build(checkout, base)
        (export / 'new-a.bin').write_bytes(b'new prefix' + raw + b'new tail')
        (export / 'new-b.bin').write_bytes(b'new prefix' + raw + b'new tail')
        (export / 'empty.bin').write_bytes(b'')
        manifest = builder.build(checkout, package)
    return checkout, package, export, manifest


class DeltaBackupTests(unittest.TestCase):
    def test_reuse_exact_roundtrip_and_idempotence(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            checkout, package, export, m = fixture(folder)
            self.assertEqual(m['file_count'], 3)
            self.assertLess(m['new_payload_bytes'], 15000)
            destination = folder / 'restored'
            result = restore_continuation(package, checkout, destination)
            self.assertEqual(result['files_restored'], 3)
            for source in export.glob('new-*.bin'):
                self.assertEqual(source.read_bytes(), (destination / source.relative_to(checkout)).read_bytes())
            self.assertEqual(restore_continuation(package, checkout, destination, True)['files_restored'], 0)

    def test_conflict_refusal_preserves_local_work(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            checkout, package, export, _ = fixture(folder)
            destination = folder / 'restored'
            conflict = destination / (export / 'new-a.bin').relative_to(checkout)
            conflict.parent.mkdir(parents=True)
            conflict.write_bytes(b'local work')
            with self.assertRaisesRegex(RuntimeError, 'Nothing overwritten'):
                restore_continuation(package, checkout, destination)
            self.assertEqual(conflict.read_bytes(), b'local work')
            self.assertEqual(len(list(conflict.parent.iterdir())), 1)

    def test_corrupt_delta_detected(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            checkout, package, _, _ = fixture(folder)
            delta = next(package.glob('*.bin'))
            raw = bytearray(delta.read_bytes())
            raw[0] ^= 1
            delta.write_bytes(raw)
            with self.assertRaisesRegex(RuntimeError, 'SHA-256 mismatch'):
                restore_continuation(package, checkout, folder / 'restored')

    def test_unsafe_or_duplicate_source_metadata_cannot_modify_base(self):
        for mode in ('traversal', 'duplicate'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as name:
                folder = Path(name)
                checkout, package, _, m = fixture(folder)
                base_source = checkout / m['packs'][0]['repository_file']
                before = base_source.read_bytes()
                if mode == 'traversal':
                    m['packs'][0]['repository_file'] = '../outside.bin'
                else:
                    m['packs'].append(m['packs'][0].copy())
                (package / 'media-manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):
                    restore_continuation(package, checkout, folder / 'restored')
                self.assertEqual(base_source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
