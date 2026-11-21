import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify_bundle = load_module('transfer_verify_bundle', ROOT / 'fab_sampling_offline_port_kit' / 'verify_bundle.py')
pack_transfer = load_module('transfer_pack_transfer', ROOT / 'fab_sampling_offline_port_kit' / 'pack_transfer.py')


class TransferKitTests(unittest.TestCase):
    def _fixture_kit(self, folder: Path) -> tuple[Path, Path]:
        kit = folder / 'kit'
        kit.mkdir()
        source = kit / 'custom' / 'path' / 'sample'
        source.mkdir(parents=True)
        (source / '.git').mkdir()
        (source / 'LICENSE').write_text('MIT')
        repo = 'example/sample'
        url = 'https://github.com/example/sample.git'
        manifest = {'repositories': [{'repo': repo, 'stage': 'core', 'url': url}]}
        (kit / 'repos.json').write_text(json.dumps(manifest))
        lock = {'entries': [{
            'repo': repo, 'status': 'CLONED_PENDING_AUDIT', 'path': 'custom/path/sample',
            'sha': 'a' * 40, 'url': url, 'license_files': ['LICENSE'],
        }]}
        (kit / 'repos.lock.json').write_text(json.dumps(lock))
        return kit, source

    def test_verifier_uses_custom_relative_lock_path_and_checks_origin(self):
        with tempfile.TemporaryDirectory() as d:
            kit, source = self._fixture_kit(Path(d))
            commands = [
                type('Result', (), {'returncode': 0, 'stdout': 'a' * 40 + '\n'})(),
                type('Result', (), {'returncode': 0, 'stdout': 'https://github.com/example/sample.git\n'})(),
            ]
            with patch.object(verify_bundle.subprocess, 'run', side_effect=commands):
                verified, failures = verify_bundle.verify(kit)
            self.assertEqual(verified, ['example/sample'], failures)
            self.assertEqual(failures, [])

    def test_verifier_rejects_path_traversal_in_lock(self):
        with tempfile.TemporaryDirectory() as d:
            kit, _ = self._fixture_kit(Path(d))
            lock_path = kit / 'repos.lock.json'
            for unsafe_path in ('../outside', '..\\outside', 'C:/outside'):
                with self.subTest(path=unsafe_path):
                    lock = json.loads(lock_path.read_text())
                    lock['entries'][0]['path'] = unsafe_path
                    lock_path.write_text(json.dumps(lock))
                    verified, failures = verify_bundle.verify(kit)
                    self.assertEqual(verified, [])
                    self.assertIn('invalid or unsafe lock path', failures[0])

    def test_pack_refuses_to_overwrite_existing_archive_or_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            kit = folder / 'kit'
            kit.mkdir()
            (kit / 'README.md').write_text('transfer fixture')
            archive = folder / 'bundle.zip'
            with patch.object(pack_transfer, 'ROOT', kit):
                with patch.object(pack_transfer.subprocess, 'run',
                                  return_value=type('Result', (), {'returncode': 0})()):
                    pack_transfer.pack(archive, allow_incomplete=True)
                original = archive.read_bytes()
                with self.assertRaises(FileExistsError):
                    pack_transfer.pack(archive, allow_incomplete=True)
            self.assertEqual(archive.read_bytes(), original)
            self.assertTrue(Path(str(archive) + '.sha256').is_file())

    def test_pack_rejects_symlinks_and_output_inside_kit(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            kit = folder / 'kit'
            kit.mkdir()
            (kit / 'README.md').write_text('transfer fixture')
            outside = folder / 'outside.txt'
            outside.write_text('must not be packaged')
            (kit / 'linked.txt').symlink_to(outside)
            with patch.object(pack_transfer, 'ROOT', kit):
                with self.assertRaisesRegex(ValueError, 'outside the kit'):
                    pack_transfer.pack(kit / 'nested.zip', allow_incomplete=True)
                with patch.object(pack_transfer.subprocess, 'run',
                                  return_value=type('Result', (), {'returncode': 0})()):
                    with self.assertRaisesRegex(ValueError, 'symlink'):
                        pack_transfer.pack(folder / 'bundle.zip', allow_incomplete=True)
            self.assertFalse((folder / 'bundle.zip').exists())


if __name__ == '__main__':
    unittest.main()
