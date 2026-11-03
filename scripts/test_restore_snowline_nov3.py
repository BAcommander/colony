"""Exercise backup round trips, conflict refusal, corruption and safe paths."""
import importlib.util
import json
import random
import tempfile
import unittest
from pathlib import Path
from restore_snowline_nov3 import restore, safe_target

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('snowline_pack', ROOT / 'music/snowline-sound-design-2026-11-03/build_media.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class RestoreTests(unittest.TestCase):
    def make_package(self, base):
        source = base / 'source'
        folder = source / 'exports/sfx/snowline-creak-2026-11-03'
        folder.mkdir(parents=True)
        data = random.Random(13).randbytes(180000)
        (folder / 'original.bin').write_bytes(data)
        (folder / 'identical.bin').write_bytes(data)
        (folder / 'shifted.bin').write_bytes(b'changed prefix' + data)
        (folder / 'empty.bin').write_bytes(b'')
        package = base / 'package'
        old_limit = builder.PACK_LIMIT
        try:
            builder.PACK_LIMIT = 50000
            manifest = builder.build(source, package)
        finally:
            builder.PACK_LIMIT = old_limit
        self.assertGreater(len(manifest['packs']), 1)
        self.assertLess(sum(p['bytes'] for p in manifest['packs']), len(data) * 1.1)
        return source, package, folder

    def test_exact_roundtrip_duplicate_shift_empty_and_idempotence(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            source, package, folder = self.make_package(base)
            destination = base / 'restored'
            self.assertEqual(restore(package, destination)['files_restored'], 4)
            for original in folder.iterdir():
                self.assertEqual(original.read_bytes(), (destination / original.relative_to(source)).read_bytes())
            self.assertEqual(restore(package, destination, True)['files_restored'], 0)

    def test_conflict_preflight_preserves_local_work_and_creates_nothing(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            source, package, folder = self.make_package(base)
            destination = base / 'restored'
            conflict = destination / (folder / 'original.bin').relative_to(source)
            conflict.parent.mkdir(parents=True)
            conflict.write_bytes(b'local work')
            with self.assertRaisesRegex(RuntimeError, 'Nothing overwritten'):
                restore(package, destination)
            self.assertEqual(conflict.read_bytes(), b'local work')
            self.assertEqual(len(list(conflict.parent.iterdir())), 1)

    def test_corrupt_pack_detected_before_writing(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            _, package, _ = self.make_package(base)
            pack = package / 'media-001.bin'
            data = bytearray(pack.read_bytes())
            data[0] ^= 1
            pack.write_bytes(data)
            with self.assertRaisesRegex(RuntimeError, 'SHA-256 mismatch'):
                restore(package, base / 'restored')
            self.assertFalse((base / 'restored').exists())

    def test_path_traversal_and_unexpected_roots_rejected(self):
        for path in ('../outside', 'exports/sfx/snowline-creak-2026-11-03/../../../../outside',
                     'C:/outside', '/exports/sfx/snowline-creak-2026-11-03/file',
                     'exports/other/file', 'exports/sfx/snowline-creak-2026-11-03/file:stream'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_target(ROOT, path)


if __name__ == '__main__':
    unittest.main()
