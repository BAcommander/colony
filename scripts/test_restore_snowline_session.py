import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from restore_snowline_session import digest, restore, target_path


class RestoreTests(unittest.TestCase):
    def fixture(self, folder):
        package = folder / 'package'
        package.mkdir()
        name = 'exports/sfx/snowline-receiver-2026-11-02/example.wav'
        payload = b'original source bytes'
        archive = package / 'media.zip'
        with zipfile.ZipFile(archive, 'x') as z:
            z.writestr(name, payload)
        manifest = {'archive': {'file': archive.name, 'bytes': archive.stat().st_size,
                                'sha256': digest(archive)},
                    'members': [{'path': name, 'bytes': len(payload),
                                 'sha256': hashlib.sha256(payload).hexdigest()}]}
        (package / 'media-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        return package, name, payload

    def test_round_trip_and_idempotent_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            package, name, payload = self.fixture(base)
            root = base / 'restored'
            self.assertEqual(restore(package, root)['files_restored'], 1)
            self.assertEqual((root / name).read_bytes(), payload)
            self.assertEqual(restore(package, root, True)['files_restored'], 0)

    def test_different_existing_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            package, name, _ = self.fixture(base)
            root = base / 'restored'
            existing = root / name
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b'new local work')
            with self.assertRaisesRegex(RuntimeError, 'nothing overwritten'):
                restore(package, root)
            self.assertEqual(existing.read_bytes(), b'new local work')

    def test_missing_lfs_and_unsafe_destinations_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            package, _, _ = self.fixture(base)
            (package / 'media.zip').write_bytes(b'version https://git-lfs.github.com/spec/v1')
            with self.assertRaisesRegex(RuntimeError, 'Git LFS pointer'):
                restore(package, base / 'restored')
            for name in ['../outside', '/absolute', 'C:/outside',
                         'exports/sfx/snowline-receiver-2026-11-02/../../outside',
                         'exports/other/file.wav']:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    target_path(base, name)


if __name__ == '__main__':
    unittest.main()
