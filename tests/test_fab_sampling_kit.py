import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'fab_sampling_offline_port_kit'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fetch_repos = load_module('fab_fetch_repos', KIT / 'fetch_repos.py')
verify_bundle = load_module('fab_verify_bundle', KIT / 'verify_bundle.py')
pack_transfer = load_module('fab_pack_transfer', KIT / 'pack_transfer.py')


class FabSamplingKitTests(unittest.TestCase):
    def test_fetch_requires_explicit_candidate_selection_before_any_git_call(self):
        with patch.object(sys, 'argv', ['fetch_repos.py']):
            with patch.object(fetch_repos, 'git') as git:
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        fetch_repos.main()
        git.assert_not_called()

    def test_exact_candidate_selection_is_subset_and_manifest_ordered(self):
        selected = fetch_repos.select_repositories(
            repo_names=['unionai-oss/pandera', 'tobymao/sqlglot'])
        self.assertEqual([item['repo'] for item in selected], ['tobymao/sqlglot', 'unionai-oss/pandera'])

    def test_invalid_or_conflicting_candidate_selection_fails_closed(self):
        for kwargs in (
            {},
            {'repo_names': ['tobymao/sqlglot', 'tobymao/sqlglot']},
            {'repo_names': ['unknown/project']},
            {'stage': 'core', 'repo_names': ['tobymao/sqlglot']},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                fetch_repos.select_repositories(**kwargs)

    def test_all_candidates_require_an_explicit_stage_flag(self):
        self.assertEqual(len(fetch_repos.select_repositories(stage='all')), len(fetch_repos.CANDIDATES))

    def _make_partial_lock(self, root: Path):
        sha = 'a' * 40
        repos = [
            {'repo': 'example/one', 'url': 'https://github.com/example/one.git'},
            {'repo': 'example/two', 'url': 'https://github.com/example/two.git'},
        ]
        (root / 'repos.json').write_text(json.dumps({'repositories': repos}), encoding='utf-8')
        repo_path = root / 'sources' / 'example__one'
        (repo_path / '.git').mkdir(parents=True)
        (repo_path / 'LICENSE').write_text('MIT', encoding='utf-8')
        lock = {'entries': [{
            'repo': 'example/one',
            'url': repos[0]['url'],
            'status': 'CLONED_PENDING_AUDIT',
            'path': 'sources/example__one',
            'sha': sha,
            'license_files': ['LICENSE'],
        }]}
        (root / 'repos.lock.json').write_text(json.dumps(lock), encoding='utf-8')
        return repos, sha, repo_path

    def test_partial_lock_verifies_selected_subset_only_when_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repos, sha, repo_path = self._make_partial_lock(root)

            def git_result(args, **kwargs):
                output = sha if args[-1] == 'HEAD' else repos[0]['url']
                return subprocess.CompletedProcess(args, 0, output + '\n', '')

            with patch.object(verify_bundle.subprocess, 'run', side_effect=git_result):
                verified, failures = verify_bundle.verify(root, allow_incomplete=True)
                strict_verified, strict_failures = verify_bundle.verify(root)

            self.assertEqual(verified, ['example/one'])
            self.assertEqual(failures, [])
            self.assertEqual(strict_verified, ['example/one'])
            self.assertTrue(any('PARTIAL_LOCK' in failure for failure in strict_failures))

    def test_verifier_rejects_unknown_lock_ids_before_running_git(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_partial_lock(root)
            lock_path = root / 'repos.lock.json'
            lock = json.loads(lock_path.read_text(encoding='utf-8'))
            lock['entries'][0]['repo'] = 'unlisted/repo'
            lock_path.write_text(json.dumps(lock), encoding='utf-8')
            with patch.object(verify_bundle.subprocess, 'run') as run:
                verified, failures = verify_bundle.verify(root, allow_incomplete=True)
            self.assertEqual(verified, [])
            self.assertTrue(any('absent from repos.json' in failure for failure in failures))
            run.assert_not_called()

    def test_packer_still_runs_subset_verifier(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            kit_root = parent / 'kit'
            kit_root.mkdir()
            (kit_root / 'README.md').write_text('staged kit', encoding='utf-8')
            target = parent / 'partial.zip'
            completed = subprocess.CompletedProcess([], 0, '', '')
            with patch.object(pack_transfer, 'ROOT', kit_root):
                with patch.object(pack_transfer.subprocess, 'run', return_value=completed) as run:
                    pack_transfer.pack(target, allow_incomplete=True)
            self.assertIn('--allow-incomplete', run.call_args.args[0])
            self.assertTrue(target.is_file())
            self.assertTrue(Path(str(target) + '.sha256').is_file())

    def test_packer_refuses_partial_archive_when_subset_verification_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            kit_root = parent / 'kit'
            kit_root.mkdir()
            (kit_root / 'README.md').write_text('staged kit', encoding='utf-8')
            target = parent / 'partial.zip'
            failed = subprocess.CompletedProcess([], 2, '', '')
            with patch.object(pack_transfer, 'ROOT', kit_root):
                with patch.object(pack_transfer.subprocess, 'run', return_value=failed):
                    with self.assertRaises(ValueError):
                        pack_transfer.pack(target, allow_incomplete=True)
            self.assertFalse(target.exists())
            self.assertFalse(Path(str(target) + '.sha256').exists())

    def test_local_partial_transfer_uses_real_git_then_verifies_after_extract(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            kit_root = parent / 'fab_sampling_offline_port_kit'
            source = kit_root / 'sources' / 'example__one'
            source.mkdir(parents=True)
            (source / 'LICENSE').write_text('MIT\n', encoding='utf-8')
            (source / 'README.md').write_text('synthetic fixture only\n', encoding='utf-8')
            git = ['git', '-C', str(source)]
            subprocess.run([*git, 'init'], check=True, capture_output=True, text=True, timeout=10)
            subprocess.run([*git, 'config', 'user.name', 'Golden Test'], check=True,
                           capture_output=True, text=True, timeout=10)
            subprocess.run([*git, 'config', 'user.email', 'golden-test@example.invalid'], check=True,
                           capture_output=True, text=True, timeout=10)
            subprocess.run([*git, 'add', 'LICENSE', 'README.md'], check=True,
                           capture_output=True, text=True, timeout=10)
            subprocess.run([*git, 'commit', '-m', 'synthetic source'], check=True,
                           capture_output=True, text=True, timeout=10)
            subprocess.run([*git, 'remote', 'add', 'origin', str(source)], check=True,
                           capture_output=True, text=True, timeout=10)
            head = subprocess.run([*git, 'rev-parse', 'HEAD'], check=True,
                                  capture_output=True, text=True, timeout=10).stdout.strip()
            manifest = {'repositories': [
                {'repo': 'example/one', 'url': str(source)},
                {'repo': 'example/two', 'url': 'https://github.com/example/two.git'},
            ]}
            (kit_root / 'repos.json').write_text(json.dumps(manifest), encoding='utf-8')
            lock = {'entries': [{
                'repo': 'example/one', 'url': str(source), 'status': 'CLONED_PENDING_AUDIT',
                'path': 'sources/example__one', 'sha': head, 'license_files': ['LICENSE'],
            }]}
            (kit_root / 'repos.lock.json').write_text(json.dumps(lock), encoding='utf-8')
            shutil.copy2(KIT / 'verify_bundle.py', kit_root / 'verify_bundle.py')
            archive = parent / 'partial-transfer.zip'

            with patch.object(pack_transfer, 'ROOT', kit_root):
                pack_transfer.pack(archive, allow_incomplete=True)

            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(parent / 'extracted')
            extracted = parent / 'extracted' / kit_root.name
            verified, failures = verify_bundle.verify(extracted, allow_incomplete=True)
            self.assertEqual(verified, ['example/one'])
            self.assertEqual(failures, [])


if __name__ == '__main__':
    unittest.main()
